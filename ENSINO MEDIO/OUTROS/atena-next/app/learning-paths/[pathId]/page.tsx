import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"

export default async function LearningPathDetailPage({ params }: { params: Promise<{ pathId: string }> }) {
  const { pathId } = await params
  const supabase = await createClient()

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser()

  if (userError || !user) {
    redirect("/auth/login")
  }

  const { data: profile } = await supabase.from("profiles").select("*").eq("id", user.id).single()

  if (!profile) {
    redirect("/auth/login")
  }

  // Get learning path
  const { data: learningPath } = await supabase.from("learning_paths").select("*").eq("id", pathId).single()

  if (!learningPath) {
    redirect("/learning-paths")
  }

  // Get topics for this path
  const { data: topics } = await supabase.from("topics").select("*").eq("learning_path_id", pathId).order("order_index")

  // Get user progress for each topic
  const topicsWithProgress = await Promise.all(
    (topics || []).map(async (topic) => {
      const { data: progress } = await supabase
        .from("user_topic_progress")
        .select("*")
        .eq("user_id", user.id)
        .eq("topic_id", topic.id)
        .single()

      const { data: questions } = await supabase.from("questions").select("id").eq("topic_id", topic.id)

      return {
        ...topic,
        progress: progress || null,
        totalQuestions: questions?.length || 0,
      }
    }),
  )

  const subjectColors = {
    math: "from-blue-500 to-cyan-500",
    portuguese: "from-purple-500 to-pink-500",
    biology: "from-green-500 to-emerald-500",
  }

  const subjectIcons = {
    math: "📐",
    portuguese: "📚",
    biology: "🧬",
  }

  const completedTopics = topicsWithProgress.filter((t) => t.progress?.is_completed).length
  const totalTopics = topicsWithProgress.length
  const pathProgress = totalTopics > 0 ? (completedTopics / totalTopics) * 100 : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Path Header */}
        <div className="mb-8">
          <Button asChild variant="ghost" className="mb-4">
            <Link href="/learning-paths">← Voltar para Trilhas</Link>
          </Button>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-start gap-6">
                <div
                  className={`w-20 h-20 rounded-full bg-gradient-to-br ${subjectColors[learningPath.subject]} flex items-center justify-center text-4xl flex-shrink-0`}
                >
                  {subjectIcons[learningPath.subject]}
                </div>

                <div className="flex-1 space-y-4">
                  <div>
                    <h1 className="text-3xl font-bold mb-2">{learningPath.title}</h1>
                    <p className="text-muted-foreground">{learningPath.description}</p>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Progresso Geral</span>
                      <span className="font-medium">
                        {completedTopics}/{totalTopics} tópicos concluídos
                      </span>
                    </div>
                    <Progress value={pathProgress} className="h-3" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Topics List */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Tópicos</h2>

          {topicsWithProgress.map((topic, index) => {
            const isCompleted = topic.progress?.is_completed || false
            const questionsAnswered = topic.progress?.questions_answered || 0
            const correctAnswers = topic.progress?.correct_answers || 0
            const accuracy = questionsAnswered > 0 ? Math.round((correctAnswers / questionsAnswered) * 100) : 0

            return (
              <Card
                key={topic.id}
                className={`hover:shadow-md transition-all ${isCompleted ? "border-green-500/50 bg-green-500/5" : ""}`}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary">
                          {index + 1}
                        </div>
                        <CardTitle className="text-xl">{topic.title}</CardTitle>
                        {isCompleted && (
                          <Badge variant="default" className="bg-green-500">
                            ✓ Concluído
                          </Badge>
                        )}
                      </div>
                      <CardDescription>{topic.description}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex gap-6 text-sm">
                      <div>
                        <span className="text-muted-foreground">Questões: </span>
                        <span className="font-medium">{topic.totalQuestions}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">XP: </span>
                        <span className="font-medium text-primary">+{topic.xp_reward}</span>
                      </div>
                      {questionsAnswered > 0 && (
                        <div>
                          <span className="text-muted-foreground">Acertos: </span>
                          <span className="font-medium text-green-600">{accuracy}%</span>
                        </div>
                      )}
                    </div>

                    <Button asChild>
                      <Link href={`/learning-paths/${pathId}/topics/${topic.id}`}>
                        {questionsAnswered > 0 ? "Continuar" : "Começar"}
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}

          {topicsWithProgress.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center text-muted-foreground">
                <div className="text-4xl mb-4">📚</div>
                <p>Nenhum tópico disponível ainda.</p>
                <p className="text-sm mt-2">Em breve novos conteúdos serão adicionados!</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
