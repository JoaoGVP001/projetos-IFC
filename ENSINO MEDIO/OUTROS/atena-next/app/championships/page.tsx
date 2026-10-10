import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"

export default async function ChampionshipsPage() {
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

  // Get all championships
  const { data: championships } = await supabase
    .from("championships")
    .select(
      `
      *,
      profiles!championships_created_by_fkey (full_name),
      championship_participants (user_id)
    `,
    )
    .order("start_date", { ascending: false })

  // Separate by status
  const activeChampionships = championships?.filter((c) => c.status === "active") || []
  const upcomingChampionships = championships?.filter((c) => c.status === "upcoming") || []
  const completedChampionships = championships?.filter((c) => c.status === "completed") || []

  const subjectColors = {
    math: "bg-blue-500/10 text-blue-600 border-blue-500/20",
    portuguese: "bg-purple-500/10 text-purple-600 border-purple-500/20",
    biology: "bg-green-500/10 text-green-600 border-green-500/20",
  }

  const subjectLabels = {
    math: "Matemática",
    portuguese: "Português",
    biology: "Biologia",
  }

  const statusColors = {
    active: "bg-green-500",
    upcoming: "bg-yellow-500",
    completed: "bg-gray-500",
  }

  const statusLabels = {
    active: "Em Andamento",
    upcoming: "Em Breve",
    completed: "Finalizado",
  }

  const renderChampionshipCard = (championship: any) => {
    const isParticipating = championship.championship_participants?.some((p: any) => p.user_id === user.id)
    const participantCount = championship.championship_participants?.length || 0

    return (
      <Card key={championship.id} className="hover:shadow-lg transition-all">
        <CardHeader>
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <Badge className={statusColors[championship.status]}>{statusLabels[championship.status]}</Badge>
              <Badge className={subjectColors[championship.subject]}>{subjectLabels[championship.subject]}</Badge>
            </div>
            {isParticipating && (
              <Badge variant="outline" className="border-primary text-primary">
                Inscrito
              </Badge>
            )}
          </div>
          <CardTitle className="text-2xl">{championship.title}</CardTitle>
          <CardDescription>{championship.description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">Criado por:</span>
              <div className="font-medium">{championship.profiles?.full_name || "Professor"}</div>
            </div>
            <div>
              <span className="text-muted-foreground">Participantes:</span>
              <div className="font-medium">
                {participantCount}
                {championship.max_participants && ` / ${championship.max_participants}`}
              </div>
            </div>
            <div>
              <span className="text-muted-foreground">Início:</span>
              <div className="font-medium">{new Date(championship.start_date).toLocaleDateString("pt-BR")}</div>
            </div>
            <div>
              <span className="text-muted-foreground">Término:</span>
              <div className="font-medium">{new Date(championship.end_date).toLocaleDateString("pt-BR")}</div>
            </div>
          </div>

          <Button asChild className="w-full" size="lg">
            <Link href={`/championships/${championship.id}`}>{isParticipating ? "Ver Detalhes" : "Participar"}</Link>
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Campeonatos</h1>
          <p className="text-muted-foreground text-lg">Participe de competições e mostre seu conhecimento</p>
        </div>

        {/* Active Championships */}
        {activeChampionships.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Em Andamento</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {activeChampionships.map(renderChampionshipCard)}
            </div>
          </div>
        )}

        {/* Upcoming Championships */}
        {upcomingChampionships.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Próximos Campeonatos</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {upcomingChampionships.map(renderChampionshipCard)}
            </div>
          </div>
        )}

        {/* Completed Championships */}
        {completedChampionships.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Finalizados</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {completedChampionships.map(renderChampionshipCard)}
            </div>
          </div>
        )}

        {/* Empty State */}
        {championships?.length === 0 && (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="text-6xl mb-4">🏆</div>
              <h2 className="text-2xl font-bold mb-2">Nenhum campeonato disponível</h2>
              <p className="text-muted-foreground">Aguarde novos campeonatos serem criados pelos professores!</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
