"use client"

import type { LearningPath, Question, QuestionOption, Topic, UserTopicProgress } from "@/lib/types"
import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"

interface TopicPracticeProps {
  topic: Topic
  learningPath: LearningPath
  questions: (Question & { question_options: QuestionOption[] })[]
  progress: UserTopicProgress | null
  userId: string
}

export function TopicPractice({ topic, learningPath, questions, progress, userId }: TopicPracticeProps) {
  const router = useRouter()
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedOption, setSelectedOption] = useState<string | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [sessionStats, setSessionStats] = useState({
    answered: 0,
    correct: 0,
    xpEarned: 0,
  })

  const currentQuestion = questions[currentQuestionIndex]
  const hasQuestions = questions.length > 0

  console.log("[v0] TopicPractice - Total questions:", questions.length)
  console.log("[v0] TopicPractice - Current question:", currentQuestion)
  if (currentQuestion) {
    console.log("[v0] TopicPractice - Current question options:", currentQuestion.question_options)
  }

  const handleOptionSelect = (optionId: string) => {
    if (!showResult) {
      setSelectedOption(optionId)
    }
  }

  const handleSubmitAnswer = async () => {
    if (!selectedOption || !currentQuestion) return

    const supabase = createClient()
    const correctOption = currentQuestion.question_options.find((opt) => opt.is_correct)
    const isAnswerCorrect = selectedOption === correctOption?.id

    setIsCorrect(isAnswerCorrect)
    setShowResult(true)

    const xpEarned = isAnswerCorrect ? currentQuestion.xp_value : 0

    // Save answer
    await supabase.from("user_answers").insert({
      user_id: userId,
      question_id: currentQuestion.id,
      selected_option_id: selectedOption,
      is_correct: isAnswerCorrect,
      xp_earned: xpEarned,
    })

    // Update session stats
    setSessionStats((prev) => ({
      answered: prev.answered + 1,
      correct: prev.correct + (isAnswerCorrect ? 1 : 0),
      xpEarned: prev.xpEarned + xpEarned,
    }))

    // Update or create progress
    const newQuestionsAnswered = (progress?.questions_answered || 0) + 1
    const newCorrectAnswers = (progress?.correct_answers || 0) + (isAnswerCorrect ? 1 : 0)
    const newXpEarned = (progress?.xp_earned || 0) + xpEarned

    if (progress) {
      await supabase
        .from("user_topic_progress")
        .update({
          questions_answered: newQuestionsAnswered,
          correct_answers: newCorrectAnswers,
          xp_earned: newXpEarned,
          last_practiced_at: new Date().toISOString(),
        })
        .eq("id", progress.id)
    } else {
      await supabase.from("user_topic_progress").insert({
        user_id: userId,
        topic_id: topic.id,
        questions_answered: newQuestionsAnswered,
        correct_answers: newCorrectAnswers,
        xp_earned: newXpEarned,
        last_practiced_at: new Date().toISOString(),
      })
    }

    // Update user profile XP and correct answers
    await supabase.rpc("increment_user_xp", {
      user_id: userId,
      xp_amount: xpEarned,
    })

    if (isAnswerCorrect) {
      await supabase.rpc("increment_correct_answers", {
        user_id: userId,
      })
    }

    await supabase.rpc("update_user_streak", {
      p_user_id: userId,
    })

    await supabase.rpc("check_and_award_achievements", {
      p_user_id: userId,
    })
  }

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
      setSelectedOption(null)
      setShowResult(false)
      setIsCorrect(false)
    } else {
      router.push(`/learning-paths/${learningPath.id}`)
      router.refresh()
    }
  }

  if (!hasQuestions) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Button asChild variant="ghost" className="mb-4">
          <Link href={`/learning-paths/${learningPath.id}`}>← Voltar</Link>
        </Button>

        <Card>
          <CardContent className="py-12 text-center">
            <div className="text-6xl mb-4">📝</div>
            <h2 className="text-2xl font-bold mb-2">Nenhuma questão disponível</h2>
            <p className="text-muted-foreground mb-6">Este tópico ainda não possui questões cadastradas.</p>
            <Button asChild>
              <Link href={`/learning-paths/${learningPath.id}`}>Voltar para Trilha</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <Button asChild variant="ghost" className="mb-4">
          <Link href={`/learning-paths/${learningPath.id}`}>← Voltar</Link>
        </Button>

        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">{topic.title}</h1>
            <p className="text-muted-foreground">{topic.description}</p>
          </div>
          <Badge variant="secondary" className="text-lg px-4 py-2">
            {currentQuestionIndex + 1} / {questions.length}
          </Badge>
        </div>

        <Progress value={((currentQuestionIndex + 1) / questions.length) * 100} className="h-2" />
      </div>

      {/* Session Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold text-primary">{sessionStats.answered}</div>
            <div className="text-sm text-muted-foreground">Respondidas</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold text-green-600">{sessionStats.correct}</div>
            <div className="text-sm text-muted-foreground">Corretas</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4 text-center">
            <div className="text-2xl font-bold text-secondary">{sessionStats.xpEarned} XP</div>
            <div className="text-sm text-muted-foreground">Ganhos</div>
          </CardContent>
        </Card>
      </div>

      {/* Question Card */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between mb-2">
            <Badge variant="outline">{currentQuestion.difficulty}</Badge>
            <Badge variant="secondary">+{currentQuestion.xp_value} XP</Badge>
          </div>
          <CardTitle className="text-xl leading-relaxed">{currentQuestion.question_text}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {currentQuestion.question_options
            .sort((a, b) => a.order_index - b.order_index)
            .map((option) => {
              const isSelected = selectedOption === option.id
              const isCorrectOption = option.is_correct

              let buttonClass = "w-full justify-start text-left h-auto py-4 px-6"

              if (showResult) {
                if (isCorrectOption) {
                  buttonClass += " bg-green-500/20 border-green-500 hover:bg-green-500/20"
                } else if (isSelected && !isCorrectOption) {
                  buttonClass += " bg-destructive/20 border-destructive hover:bg-destructive/20"
                }
              } else if (isSelected) {
                buttonClass += " bg-primary/20 border-primary"
              }

              return (
                <Button
                  key={option.id}
                  variant="outline"
                  className={buttonClass}
                  onClick={() => handleOptionSelect(option.id)}
                  disabled={showResult}
                >
                  <span className="text-base">{option.option_text}</span>
                </Button>
              )
            })}
        </CardContent>
      </Card>

      {/* Result Card */}
      {showResult && (
        <Card className={isCorrect ? "border-green-500 bg-green-500/5" : "border-destructive bg-destructive/5"}>
          <CardHeader>
            <CardTitle className={isCorrect ? "text-green-600" : "text-destructive"}>
              {isCorrect ? "✓ Correto!" : "✗ Incorreto"}
            </CardTitle>
            {currentQuestion.explanation && <CardDescription>{currentQuestion.explanation}</CardDescription>}
          </CardHeader>
          <CardContent>
            <Button onClick={handleNextQuestion} className="w-full" size="lg">
              {currentQuestionIndex < questions.length - 1 ? "Próxima Questão" : "Finalizar"}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Submit Button */}
      {!showResult && (
        <Button onClick={handleSubmitAnswer} disabled={!selectedOption} className="w-full" size="lg">
          Confirmar Resposta
        </Button>
      )}
    </div>
  )
}
