import type { Profile } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import Link from "next/link"
import { DashboardNav } from "./dashboard-nav"

interface StudentDashboardProps {
  profile: Profile
}

export function StudentDashboard({ profile }: StudentDashboardProps) {
  const levelProgress = ((profile.xp % 100) / 100) * 100
  const initials = profile.full_name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)

  return (
    <div className="min-h-screen bg-muted/30">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8">
        {/* Profile Header */}
        <div className="mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col md:flex-row items-center md:items-start gap-6">
                <Avatar className="h-24 w-24 border-4 border-primary/20">
                  <AvatarFallback className="text-2xl bg-primary text-primary-foreground">{initials}</AvatarFallback>
                </Avatar>

                <div className="flex-1 text-center md:text-left space-y-4">
                  <div>
                    <h1 className="text-3xl font-bold">{profile.full_name}</h1>
                    <p className="text-muted-foreground">{profile.email}</p>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="space-y-1">
                      <div className="text-2xl font-bold text-primary">Nível {profile.level}</div>
                      <div className="text-sm text-muted-foreground">Nível Atual</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-2xl font-bold text-secondary">{profile.xp} XP</div>
                      <div className="text-sm text-muted-foreground">Experiência</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-2xl font-bold text-accent">{profile.current_streak} dias</div>
                      <div className="text-sm text-muted-foreground">Sequência Atual</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-2xl font-bold text-chart-1">{profile.total_questions_answered}</div>
                      <div className="text-sm text-muted-foreground">Questões</div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Progresso para Nível {profile.level + 1}</span>
                      <span className="font-medium">{profile.xp % 100}/100 XP</span>
                    </div>
                    <Progress value={levelProgress} className="h-3" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Taxa de Acerto</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-primary">
                {profile.total_questions_answered > 0
                  ? Math.round((profile.correct_answers / profile.total_questions_answered) * 100)
                  : 0}
                %
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                {profile.correct_answers} de {profile.total_questions_answered} corretas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Maior Sequência</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-secondary">{profile.longest_streak} dias</div>
              <p className="text-sm text-muted-foreground mt-1">Seu recorde pessoal</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Última Atividade</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-accent">
                {profile.last_activity_date
                  ? new Date(profile.last_activity_date).toLocaleDateString("pt-BR")
                  : "Nunca"}
              </div>
              <p className="text-sm text-muted-foreground mt-1">Continue estudando!</p>
            </CardContent>
          </Card>
        </div>

        {/* Action Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="border-primary/20 hover:border-primary/40 transition-colors">
            <CardHeader>
              <CardTitle>Trilhas de Aprendizado</CardTitle>
              <CardDescription>Continue seus estudos nas matérias do ENEM</CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild className="w-full" size="lg">
                <Link href="/learning-paths">Começar a Estudar</Link>
              </Button>
            </CardContent>
          </Card>

          <Card className="border-secondary/20 hover:border-secondary/40 transition-colors">
            <CardHeader>
              <CardTitle>Campeonatos</CardTitle>
              <CardDescription>Participe de competições e suba no ranking</CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild className="w-full" size="lg" variant="secondary">
                <Link href="/championships">Ver Campeonatos</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
