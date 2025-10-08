import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"

export default async function TeacherQuestionsPage({
  searchParams,
}: {
  searchParams: Promise<{ subject?: string }>
}) {
  const params = await searchParams
  const supabase = await createClient()

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser()

  if (userError || !user) {
    redirect("/auth/login")
  }

  const { data: profile } = await supabase.from("profiles").select("*").eq("id", user.id).single()

  if (!profile || profile.role !== "teacher") {
    redirect("/dashboard")
  }

  // Get questions created by this teacher
  const query = supabase
    .from("questions")
    .select(
      `
      *,
      topics (
        title,
        learning_paths (
          title,
          subject
        )
      )
    `,
    )
    .eq("created_by", user.id)
    .order("created_at", { ascending: false })

  const { data: questions } = await query

  // Filter by subject if provided
  const filteredQuestions = params.subject
    ? questions?.filter((q) => q.topics?.learning_paths?.subject === params.subject)
    : questions

  // Count by subject
  const mathCount = questions?.filter((q) => q.topics?.learning_paths?.subject === "math").length || 0
  const portugueseCount = questions?.filter((q) => q.topics?.learning_paths?.subject === "portuguese").length || 0
  const biologyCount = questions?.filter((q) => q.topics?.learning_paths?.subject === "biology").length || 0

  const difficultyColors = {
    easy: "bg-green-500/10 text-green-600 border-green-500/20",
    medium: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20",
    hard: "bg-red-500/10 text-red-600 border-red-500/20",
  }

  const difficultyLabels = {
    easy: "Fácil",
    medium: "Médio",
    hard: "Difícil",
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Banco de Questões</h1>
            <p className="text-muted-foreground text-lg">Gerencie suas questões criadas</p>
          </div>
          <Button asChild size="lg">
            <Link href="/teacher/questions/new">+ Nova Questão</Link>
          </Button>
        </div>

        {/* Subject Filter */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className={!params.subject ? "border-primary" : ""}>
            <CardContent className="pt-6">
              <Button asChild variant={!params.subject ? "default" : "ghost"} className="w-full">
                <Link href="/teacher/questions">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{questions?.length || 0}</div>
                    <div className="text-sm">Todas</div>
                  </div>
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card className={params.subject === "math" ? "border-primary" : ""}>
            <CardContent className="pt-6">
              <Button asChild variant={params.subject === "math" ? "default" : "ghost"} className="w-full">
                <Link href="/teacher/questions?subject=math">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{mathCount}</div>
                    <div className="text-sm">Matemática</div>
                  </div>
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card className={params.subject === "portuguese" ? "border-primary" : ""}>
            <CardContent className="pt-6">
              <Button asChild variant={params.subject === "portuguese" ? "default" : "ghost"} className="w-full">
                <Link href="/teacher/questions?subject=portuguese">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{portugueseCount}</div>
                    <div className="text-sm">Português</div>
                  </div>
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card className={params.subject === "biology" ? "border-primary" : ""}>
            <CardContent className="pt-6">
              <Button asChild variant={params.subject === "biology" ? "default" : "ghost"} className="w-full">
                <Link href="/teacher/questions?subject=biology">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{biologyCount}</div>
                    <div className="text-sm">Biologia</div>
                  </div>
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Questions List */}
        <div className="space-y-4">
          {filteredQuestions && filteredQuestions.length > 0 ? (
            filteredQuestions.map((question) => (
              <Card key={question.id} className="hover:shadow-md transition-all">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">{question.topics?.learning_paths?.title}</Badge>
                        <Badge className={difficultyColors[question.difficulty]}>
                          {difficultyLabels[question.difficulty]}
                        </Badge>
                        <Badge variant="secondary">+{question.xp_value} XP</Badge>
                      </div>
                      <CardTitle className="text-lg leading-relaxed">{question.question_text}</CardTitle>
                      <CardDescription className="mt-2">Tópico: {question.topics?.title}</CardDescription>
                    </div>
                    <Button asChild variant="outline" size="sm">
                      <Link href={`/teacher/questions/${question.id}`}>Editar</Link>
                    </Button>
                  </div>
                </CardHeader>
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-6xl mb-4">📝</div>
                <h2 className="text-2xl font-bold mb-2">Nenhuma questão encontrada</h2>
                <p className="text-muted-foreground mb-6">
                  {params.subject
                    ? "Você ainda não criou questões para esta matéria."
                    : "Comece criando sua primeira questão!"}
                </p>
                <Button asChild>
                  <Link href="/teacher/questions/new">Criar Primeira Questão</Link>
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
