import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Progress } from "@/components/ui/progress"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"

export default async function ProfilePage() {
  const supabase = await createClient()

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser()

  if (userError || !user) {
    redirect("/auth/login")
  }

  const { data: profile, error: profileError } = await supabase.from("profiles").select("*").eq("id", user.id).single()

  if (profileError || !profile) {
    redirect("/auth/login")
  }

  const initials = profile.full_name
    .split(" ")
    .map((n: string) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)

  const levelProgress = ((profile.xp % 100) / 100) * 100

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Meu Perfil</h1>

        {/* Profile Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Informações Pessoais</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
              <Avatar className="h-32 w-32 border-4 border-primary/20">
                <AvatarFallback className="text-4xl bg-gradient-to-br from-primary to-secondary text-primary-foreground">
                  {initials}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 space-y-4 text-center md:text-left">
                <div>
                  <h2 className="text-2xl font-bold">{profile.full_name}</h2>
                  <p className="text-muted-foreground">{profile.email}</p>
                  <div className="inline-block mt-2 px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium">
                    {profile.role === "student" ? "Estudante" : "Professor"}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Nível {profile.level}</span>
                    <span className="font-medium">{profile.xp % 100}/100 XP</span>
                  </div>
                  <Progress value={levelProgress} className="h-3" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle>Estatísticas de Aprendizado</CardTitle>
              <CardDescription>Seu progresso geral</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">XP Total</span>
                <span className="text-2xl font-bold text-primary">{profile.xp}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Nível</span>
                <span className="text-2xl font-bold text-secondary">{profile.level}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Questões Respondidas</span>
                <span className="text-2xl font-bold text-accent">{profile.total_questions_answered}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Respostas Corretas</span>
                <span className="text-2xl font-bold text-chart-1">{profile.correct_answers}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sequências</CardTitle>
              <CardDescription>Mantenha o ritmo de estudos</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Sequência Atual</span>
                <span className="text-2xl font-bold text-primary">{profile.current_streak} dias</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Maior Sequência</span>
                <span className="text-2xl font-bold text-secondary">{profile.longest_streak} dias</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Última Atividade</span>
                <span className="text-lg font-medium text-accent">
                  {profile.last_activity_date
                    ? new Date(profile.last_activity_date).toLocaleDateString("pt-BR")
                    : "Nunca"}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Performance Card */}
        {profile.role === "student" && (
          <Card>
            <CardHeader>
              <CardTitle>Desempenho</CardTitle>
              <CardDescription>Análise da sua taxa de acerto</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-lg text-muted-foreground">Taxa de Acerto Geral</span>
                  <span className="text-4xl font-bold text-primary">
                    {profile.total_questions_answered > 0
                      ? Math.round((profile.correct_answers / profile.total_questions_answered) * 100)
                      : 0}
                    %
                  </span>
                </div>
                <Progress
                  value={
                    profile.total_questions_answered > 0
                      ? (profile.correct_answers / profile.total_questions_answered) * 100
                      : 0
                  }
                  className="h-4"
                />
                <p className="text-sm text-muted-foreground">
                  Você acertou {profile.correct_answers} de {profile.total_questions_answered} questões
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
