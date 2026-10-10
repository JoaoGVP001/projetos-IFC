import { createServerClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart3, TrendingUp, Users, BookOpen } from "lucide-react"

export default async function TeacherAnalyticsPage() {
  const supabase = await createServerClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  const { data: profile } = await supabase.from("profiles").select("role").eq("id", user.id).single()

  if (profile?.role !== "teacher") {
    redirect("/dashboard")
  }

  // Get analytics data
  const { data: students } = await supabase
    .from("profiles")
    .select("id, total_xp, questions_answered, correct_answers")
    .eq("role", "student")

  const { data: questions } = await supabase
    .from("questions")
    .select("id, subject, difficulty")
    .eq("created_by", user.id)

  const { data: championships } = await supabase
    .from("championships")
    .select("id, title, participants_count")
    .eq("created_by", user.id)

  // Calculate subject distribution
  const subjectCounts =
    questions?.reduce(
      (acc, q) => {
        acc[q.subject] = (acc[q.subject] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    ) || {}

  // Calculate difficulty distribution
  const difficultyCounts =
    questions?.reduce(
      (acc, q) => {
        acc[q.difficulty] = (acc[q.difficulty] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    ) || {}

  const totalStudents = students?.length || 0
  const totalQuestions = questions?.length || 0
  const totalChampionships = championships?.length || 0
  const avgAccuracy =
    students && students.length > 0
      ? Math.round(
          students.reduce((sum, s) => {
            const rate = s.questions_answered > 0 ? (s.correct_answers / s.questions_answered) * 100 : 0
            return sum + rate
          }, 0) / students.length,
        )
      : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-teal-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Análises e Relatórios</h1>
          <p className="text-gray-600">Visualize estatísticas e insights sobre suas turmas</p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Estudantes</CardTitle>
                <Users className="h-4 w-4 text-purple-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">{totalStudents}</div>
              <p className="text-xs text-gray-500 mt-1">Total de alunos</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Questões</CardTitle>
                <BookOpen className="h-4 w-4 text-teal-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-teal-600">{totalQuestions}</div>
              <p className="text-xs text-gray-500 mt-1">Criadas por você</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Campeonatos</CardTitle>
                <BarChart3 className="h-4 w-4 text-orange-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600">{totalChampionships}</div>
              <p className="text-xs text-gray-500 mt-1">Organizados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium text-gray-600">Taxa de Acerto</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{avgAccuracy}%</div>
              <p className="text-xs text-gray-500 mt-1">Média geral</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Distribuição por Matéria</CardTitle>
              <CardDescription>Questões criadas por disciplina</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(subjectCounts).map(([subject, count]) => {
                  const percentage = totalQuestions > 0 ? (count / totalQuestions) * 100 : 0
                  const subjectNames: Record<string, string> = {
                    math: "Matemática",
                    portuguese: "Português",
                    biology: "Biologia",
                  }
                  const colors: Record<string, string> = {
                    math: "bg-blue-500",
                    portuguese: "bg-green-500",
                    biology: "bg-purple-500",
                  }

                  return (
                    <div key={subject}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">{subjectNames[subject] || subject}</span>
                        <span className="text-sm text-gray-600">{count} questões</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${colors[subject] || "bg-gray-500"}`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  )
                })}

                {Object.keys(subjectCounts).length === 0 && (
                  <p className="text-center text-gray-500 py-8">Nenhuma questão criada ainda</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Distribuição por Dificuldade</CardTitle>
              <CardDescription>Nível das questões criadas</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(difficultyCounts).map(([difficulty, count]) => {
                  const percentage = totalQuestions > 0 ? (count / totalQuestions) * 100 : 0
                  const difficultyNames: Record<string, string> = {
                    easy: "Fácil",
                    medium: "Médio",
                    hard: "Difícil",
                  }
                  const colors: Record<string, string> = {
                    easy: "bg-green-500",
                    medium: "bg-yellow-500",
                    hard: "bg-red-500",
                  }

                  return (
                    <div key={difficulty}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">
                          {difficultyNames[difficulty] || difficulty}
                        </span>
                        <span className="text-sm text-gray-600">{count} questões</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${colors[difficulty] || "bg-gray-500"}`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  )
                })}

                {Object.keys(difficultyCounts).length === 0 && (
                  <p className="text-center text-gray-500 py-8">Nenhuma questão criada ainda</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Top 10 Estudantes</CardTitle>
            <CardDescription>Alunos com melhor desempenho</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {students
                ?.sort((a, b) => (b.total_xp || 0) - (a.total_xp || 0))
                .slice(0, 10)
                .map((student, index) => {
                  const accuracy =
                    student.questions_answered > 0
                      ? Math.round((student.correct_answers / student.questions_answered) * 100)
                      : 0

                  return (
                    <div key={student.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-bold text-gray-400 w-6">#{index + 1}</span>
                        <div>
                          <p className="font-medium text-gray-900">Estudante {index + 1}</p>
                          <p className="text-sm text-gray-600">{student.total_xp?.toLocaleString()} XP</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-900">{accuracy}% acertos</p>
                        <p className="text-xs text-gray-600">{student.questions_answered} questões</p>
                      </div>
                    </div>
                  )
                })}

              {(!students || students.length === 0) && (
                <p className="text-center text-gray-500 py-8">Nenhum estudante cadastrado ainda</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
