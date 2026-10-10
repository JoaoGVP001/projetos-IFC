import { createServerClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Trophy, TrendingUp, Target, Award } from "lucide-react"

export default async function TeacherStudentsPage() {
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

  // Get all students with their stats
  const { data: students } = await supabase
    .from("profiles")
    .select(`
      id,
      full_name,
      total_xp,
      level,
      current_streak,
      longest_streak,
      questions_answered,
      correct_answers
    `)
    .eq("role", "student")
    .order("total_xp", { ascending: false })

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-teal-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Gerenciar Estudantes</h1>
          <p className="text-gray-600">Acompanhe o desempenho e progresso dos seus alunos</p>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Total de Alunos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">{students?.length || 0}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">XP Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-teal-600">
                {students?.reduce((sum, s) => sum + (s.total_xp || 0), 0).toLocaleString()}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Questões Respondidas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600">
                {students?.reduce((sum, s) => sum + (s.questions_answered || 0), 0).toLocaleString()}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Taxa de Acerto Média</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {students && students.length > 0
                  ? Math.round(
                      students.reduce((sum, s) => {
                        const rate = s.questions_answered > 0 ? (s.correct_answers / s.questions_answered) * 100 : 0
                        return sum + rate
                      }, 0) / students.length,
                    )
                  : 0}
                %
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Lista de Estudantes</CardTitle>
            <CardDescription>Visualize o desempenho individual de cada aluno</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {students?.map((student, index) => {
                const accuracy =
                  student.questions_answered > 0
                    ? Math.round((student.correct_answers / student.questions_answered) * 100)
                    : 0

                return (
                  <div
                    key={student.id}
                    className="flex items-center justify-between p-4 rounded-lg border bg-white hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-3">
                        {index < 3 && (
                          <Trophy
                            className={`h-6 w-6 ${
                              index === 0 ? "text-yellow-500" : index === 1 ? "text-gray-400" : "text-orange-600"
                            }`}
                          />
                        )}
                        <Avatar className="h-12 w-12">
                          <AvatarFallback className="bg-gradient-to-br from-purple-500 to-teal-500 text-white">
                            {student.full_name
                              ?.split(" ")
                              .map((n) => n[0])
                              .join("")
                              .slice(0, 2) || "ST"}
                          </AvatarFallback>
                        </Avatar>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{student.full_name || "Estudante"}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="secondary" className="text-xs">
                            Nível {student.level}
                          </Badge>
                          <span className="text-sm text-gray-600">{student.total_xp?.toLocaleString()} XP</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      <div className="text-center">
                        <div className="flex items-center gap-1 text-orange-600 mb-1">
                          <Target className="h-4 w-4" />
                          <span className="text-sm font-medium">Sequência</span>
                        </div>
                        <p className="text-2xl font-bold text-gray-900">{student.current_streak}</p>
                        <p className="text-xs text-gray-500">dias</p>
                      </div>

                      <div className="text-center">
                        <div className="flex items-center gap-1 text-teal-600 mb-1">
                          <TrendingUp className="h-4 w-4" />
                          <span className="text-sm font-medium">Acertos</span>
                        </div>
                        <p className="text-2xl font-bold text-gray-900">{accuracy}%</p>
                        <p className="text-xs text-gray-500">
                          {student.correct_answers}/{student.questions_answered}
                        </p>
                      </div>

                      <div className="text-center">
                        <div className="flex items-center gap-1 text-purple-600 mb-1">
                          <Award className="h-4 w-4" />
                          <span className="text-sm font-medium">Questões</span>
                        </div>
                        <p className="text-2xl font-bold text-gray-900">{student.questions_answered}</p>
                        <p className="text-xs text-gray-500">respondidas</p>
                      </div>
                    </div>
                  </div>
                )
              })}

              {(!students || students.length === 0) && (
                <div className="text-center py-12 text-gray-500">
                  <p>Nenhum estudante cadastrado ainda.</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
