"use client"

import type React from "react"

import type { LearningPath, Question, QuestionOption, Topic } from "@/lib/types"
import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import Link from "next/link"

interface QuestionEditFormProps {
  question: Question & { question_options: QuestionOption[]; topics: Topic & { learning_paths: LearningPath } }
  learningPaths: (LearningPath & { topics: Topic[] })[]
  userId: string
}

export function QuestionEditForm({ question, learningPaths, userId }: QuestionEditFormProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [selectedPath, setSelectedPath] = useState<string>(question.topics.learning_paths.id)
  const [selectedTopic, setSelectedTopic] = useState<string>(question.topic_id)
  const [questionText, setQuestionText] = useState(question.question_text)
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">(question.difficulty)
  const [xpValue, setXpValue] = useState(question.xp_value.toString())
  const [explanation, setExplanation] = useState(question.explanation || "")
  const [options, setOptions] = useState(
    question.question_options
      .sort((a, b) => a.order_index - b.order_index)
      .map((opt) => ({
        id: opt.id,
        text: opt.option_text,
        isCorrect: opt.is_correct,
      })),
  )

  const selectedPathData = learningPaths.find((p) => p.id === selectedPath)
  const availableTopics = selectedPathData?.topics || []

  const handleOptionChange = (index: number, text: string) => {
    const newOptions = [...options]
    newOptions[index].text = text
    setOptions(newOptions)
  }

  const handleCorrectOptionChange = (index: number) => {
    const newOptions = options.map((opt, i) => ({
      ...opt,
      isCorrect: i === index,
    }))
    setOptions(newOptions)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    if (!selectedTopic) {
      setError("Selecione um tópico")
      setIsLoading(false)
      return
    }

    if (options.some((opt) => !opt.text.trim())) {
      setError("Preencha todas as alternativas")
      setIsLoading(false)
      return
    }

    if (!options.some((opt) => opt.isCorrect)) {
      setError("Marque a alternativa correta")
      setIsLoading(false)
      return
    }

    try {
      const supabase = createClient()

      // Update question
      const { error: questionError } = await supabase
        .from("questions")
        .update({
          topic_id: selectedTopic,
          question_text: questionText,
          difficulty,
          xp_value: Number.parseInt(xpValue),
          explanation: explanation || null,
        })
        .eq("id", question.id)

      if (questionError) throw questionError

      // Update options
      for (let i = 0; i < options.length; i++) {
        const { error: optionError } = await supabase
          .from("question_options")
          .update({
            option_text: options[i].text,
            is_correct: options[i].isCorrect,
          })
          .eq("id", options[i].id)

        if (optionError) throw optionError
      }

      router.push("/teacher/questions")
      router.refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao atualizar questão")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm("Tem certeza que deseja excluir esta questão?")) return

    setIsLoading(true)
    try {
      const supabase = createClient()
      const { error } = await supabase.from("questions").delete().eq("id", question.id)

      if (error) throw error

      router.push("/teacher/questions")
      router.refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao excluir questão")
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Informações da Questão</CardTitle>
          <CardDescription>Edite os dados da questão</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="learning-path">Matéria</Label>
            <Select value={selectedPath} onValueChange={setSelectedPath}>
              <SelectTrigger id="learning-path">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {learningPaths.map((path) => (
                  <SelectItem key={path.id} value={path.id}>
                    {path.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="topic">Tópico</Label>
            <Select value={selectedTopic} onValueChange={setSelectedTopic}>
              <SelectTrigger id="topic">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {availableTopics.map((topic) => (
                  <SelectItem key={topic.id} value={topic.id}>
                    {topic.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="question-text">Enunciado da Questão</Label>
            <Textarea
              id="question-text"
              value={questionText}
              onChange={(e) => setQuestionText(e.target.value)}
              required
              rows={4}
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="difficulty">Dificuldade</Label>
              <Select value={difficulty} onValueChange={(value: any) => setDifficulty(value)}>
                <SelectTrigger id="difficulty">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="easy">Fácil</SelectItem>
                  <SelectItem value="medium">Médio</SelectItem>
                  <SelectItem value="hard">Difícil</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="xp-value">Valor em XP</Label>
              <Input
                id="xp-value"
                type="number"
                min="1"
                value={xpValue}
                onChange={(e) => setXpValue(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="explanation">Explicação (Opcional)</Label>
            <Textarea id="explanation" value={explanation} onChange={(e) => setExplanation(e.target.value)} rows={3} />
          </div>
        </CardContent>
      </Card>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Alternativas</CardTitle>
          <CardDescription>Edite as opções de resposta</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <RadioGroup value={options.findIndex((opt) => opt.isCorrect).toString()}>
            {options.map((option, index) => (
              <div key={option.id} className="flex items-start gap-3 p-4 border rounded-lg">
                <RadioGroupItem
                  value={index.toString()}
                  id={`option-${index}`}
                  onClick={() => handleCorrectOptionChange(index)}
                  className="mt-3"
                />
                <div className="flex-1 space-y-2">
                  <Label htmlFor={`option-text-${index}`} className="text-base">
                    Alternativa {String.fromCharCode(65 + index)}
                  </Label>
                  <Input
                    id={`option-text-${index}`}
                    value={option.text}
                    onChange={(e) => handleOptionChange(index, e.target.value)}
                    required
                  />
                </div>
              </div>
            ))}
          </RadioGroup>
        </CardContent>
      </Card>

      {error && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
          {error}
        </div>
      )}

      <div className="flex gap-4">
        <Button type="submit" size="lg" disabled={isLoading} className="flex-1">
          {isLoading ? "Salvando..." : "Salvar Alterações"}
        </Button>
        <Button asChild type="button" variant="outline" size="lg">
          <Link href="/teacher/questions">Cancelar</Link>
        </Button>
        <Button type="button" variant="destructive" size="lg" onClick={handleDelete} disabled={isLoading}>
          Excluir
        </Button>
      </div>
    </form>
  )
}
