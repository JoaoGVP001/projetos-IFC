import type { Profile } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import Link from "next/link"
import { DashboardNav } from "./dashboard-nav"

interface TeacherDashboardProps {
  profile: Profile
}

export function TeacherDashboard({ profile }: TeacherDashboardProps) {
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
                    <div className="inline-block mt-2 px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium">
                      Professor
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="space-y-1">
                      <div className="text-2xl font-bold text-primary">0</div>
                      <div className="text-sm text-muted-foreground">Questões Criadas</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-2xl font-bold text-secondary">0</div>
                      <div className="text-sm text-muted-foreground">Campeonatos</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-2xl font-bold text-accent">0</div>
                      <div className="text-sm text-muted-foreground">Estudantes Alcançados</div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Ações Rápidas</h2>
          <div className="grid md:grid-cols-4 gap-4">
            <Button asChild size="lg" className="h-auto py-6">
              <Link href="/teacher/questions/new" className="flex flex-col items-center gap-2">
                <span className="text-2xl">➕</span>
                <span>Criar Questão</span>
              </Link>
            </Button>
            <Button asChild size="lg" variant="secondary" className="h-auto py-6">
              <Link href="/teacher/championships/new" className="flex flex-col items-center gap-2">
                <span className="text-2xl">🏆</span>
                <span>Novo Campeonato</span>
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="h-auto py-6 bg-transparent">
              <Link href="/teacher/students" className="flex flex-col items-center gap-2">
                <span className="text-2xl">👥</span>
                <span>Ver Estudantes</span>
              </Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="h-auto py-6 bg-transparent">
              <Link href="/teacher/analytics" className="flex flex-col items-center gap-2">
                <span className="text-2xl">📊</span>
                <span>Análises</span>
              </Link>
            </Button>
          </div>
        </div>

        {/* Management Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Banco de Questões</CardTitle>
              <CardDescription>Gerencie suas questões e contribua para o aprendizado</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Matemática</div>
                  <div className="text-sm text-muted-foreground">0 questões</div>
                </div>
                <Button asChild variant="ghost" size="sm">
                  <Link href="/teacher/questions?subject=math">Ver</Link>
                </Button>
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Português</div>
                  <div className="text-sm text-muted-foreground">0 questões</div>
                </div>
                <Button asChild variant="ghost" size="sm">
                  <Link href="/teacher/questions?subject=portuguese">Ver</Link>
                </Button>
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Biologia</div>
                  <div className="text-sm text-muted-foreground">0 questões</div>
                </div>
                <Button asChild variant="ghost" size="sm">
                  <Link href="/teacher/questions?subject=biology">Ver</Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Campeonatos Ativos</CardTitle>
              <CardDescription>Acompanhe suas competições em andamento</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <div className="text-4xl mb-2">🏆</div>
                <p>Nenhum campeonato ativo</p>
                <Button asChild className="mt-4">
                  <Link href="/teacher/championships/new">Criar Primeiro Campeonato</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
