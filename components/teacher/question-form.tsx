"use client"

import type React from "react"

import type { LearningPath, Topic } from "@/lib/types"
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

interface QuestionFormProps {
  learningPaths: (LearningPath & { topics: Topic[] })[]
  userId: string
}

export function QuestionForm({ learningPaths, userId }: QuestionFormProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [selectedPath, setSelectedPath] = useState<string>("")
  const [selectedTopic, setSelectedTopic] = useState<string>("")
  const [questionText, setQuestionText] = useState("")
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard">("medium")
  const [xpValue, setXpValue] = useState("10")
  const [explanation, setExplanation] = useState("")
  const [options, setOptions] = useState([
    { text: "", isCorrect: false },
    { text: "", isCorrect: false },
    { text: "", isCorrect: false },
    { text: "", isCorrect: false },
  ])

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

    // Validation
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

      // Create question
      const { data: question, error: questionError } = await supabase
        .from("questions")
        .insert({
          topic_id: selectedTopic,
          question_text: questionText,
          question_type: "multiple_choice",
          difficulty,
          xp_value: Number.parseInt(xpValue),
          explanation: explanation || null,
          created_by: userId,
        })
        .select()
        .single()

      if (questionError) throw questionError

      // Create options
      const optionsData = options.map((opt, index) => ({
        question_id: question.id,
        option_text: opt.text,
        is_correct: opt.isCorrect,
        order_index: index,
      }))

      const { error: optionsError } = await supabase.from("question_options").insert(optionsData)

      if (optionsError) throw optionsError

      router.push("/teacher/questions")
      router.refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar questão")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Informações da Questão</CardTitle>
          <CardDescription>Preencha os dados básicos da questão</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Learning Path Selection */}
          <div className="space-y-2">
            <Label htmlFor="learning-path">Matéria</Label>
            <Select value={selectedPath} onValueChange={setSelectedPath}>
              <SelectTrigger id="learning-path">
                <SelectValue placeholder="Selecione a matéria" />
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

          {/* Topic Selection */}
          <div className="space-y-2">
            <Label htmlFor="topic">Tópico</Label>
            <Select value={selectedTopic} onValueChange={setSelectedTopic} disabled={!selectedPath}>
              <SelectTrigger id="topic">
                <SelectValue placeholder="Selecione o tópico" />
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

          {/* Question Text */}
          <div className="space-y-2">
            <Label htmlFor="question-text">Enunciado da Questão</Label>
            <Textarea
              id="question-text"
              placeholder="Digite o enunciado da questão..."
              value={questionText}
              onChange={(e) => setQuestionText(e.target.value)}
              required
              rows={4}
            />
          </div>

          {/* Difficulty and XP */}
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

          {/* Explanation */}
          <div className="space-y-2">
            <Label htmlFor="explanation">Explicação (Opcional)</Label>
            <Textarea
              id="explanation"
              placeholder="Explique a resposta correta..."
              value={explanation}
              onChange={(e) => setExplanation(e.target.value)}
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Options */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Alternativas</CardTitle>
          <CardDescription>Adicione as opções de resposta e marque a correta</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <RadioGroup value={options.findIndex((opt) => opt.isCorrect).toString()}>
            {options.map((option, index) => (
              <div key={index} className="flex items-start gap-3 p-4 border rounded-lg">
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
                    placeholder={`Digite a alternativa ${String.fromCharCode(65 + index)}...`}
                    value={option.text}
                    onChange={(e) => handleOptionChange(index, e.target.value)}
                    required
                  />
                </div>
              </div>
            ))}
          </RadioGroup>
          <p className="text-sm text-muted-foreground">Clique no círculo para marcar a alternativa correta</p>
        </CardContent>
      </Card>

      {error && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
          {error}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <Button type="submit" size="lg" disabled={isLoading} className="flex-1">
          {isLoading ? "Criando..." : "Criar Questão"}
        </Button>
        <Button asChild type="button" variant="outline" size="lg">
          <Link href="/teacher/questions">Cancelar</Link>
        </Button>
      </div>
    </form>
  )
}
