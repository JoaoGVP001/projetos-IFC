import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import Link from "next/link"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"

export default async function LearningPathsPage() {
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

  // Get all learning paths
  const { data: learningPaths } = await supabase.from("learning_paths").select("*").order("order_index")

  // Get user progress for each path
  const progressData = await Promise.all(
    (learningPaths || []).map(async (path) => {
      const { data: topics } = await supabase.from("topics").select("id").eq("learning_path_id", path.id)

      const { data: completedTopics } = await supabase
        .from("user_topic_progress")
        .select("id")
        .eq("user_id", user.id)
        .eq("is_completed", true)
        .in(
          "topic_id",
          (topics || []).map((t) => t.id),
        )

      return {
        pathId: path.id,
        totalTopics: topics?.length || 0,
        completedTopics: completedTopics?.length || 0,
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Trilhas de Aprendizado</h1>
          <p className="text-muted-foreground text-lg">Escolha uma matéria e comece a estudar para o ENEM</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {learningPaths?.map((path) => {
            const progress = progressData.find((p) => p.pathId === path.id)
            const progressPercentage =
              progress && progress.totalTopics > 0 ? (progress.completedTopics / progress.totalTopics) * 100 : 0

            return (
              <Card
                key={path.id}
                className="hover:shadow-lg transition-all hover:scale-105 border-2 hover:border-primary/50"
              >
                <CardHeader>
                  <div
                    className={`w-16 h-16 rounded-full bg-gradient-to-br ${subjectColors[path.subject]} flex items-center justify-center text-3xl mb-4`}
                  >
                    {subjectIcons[path.subject]}
                  </div>
                  <CardTitle className="text-2xl">{path.title}</CardTitle>
                  <CardDescription className="text-base">{path.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Progresso</span>
                      <span className="font-medium">
                        {progress?.completedTopics || 0}/{progress?.totalTopics || 0} tópicos
                      </span>
                    </div>
                    <Progress value={progressPercentage} className="h-2" />
                  </div>

                  <Button asChild className="w-full" size="lg">
                    <Link href={`/learning-paths/${path.id}`}>{progressPercentage > 0 ? "Continuar" : "Começar"}</Link>
                  </Button>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}
