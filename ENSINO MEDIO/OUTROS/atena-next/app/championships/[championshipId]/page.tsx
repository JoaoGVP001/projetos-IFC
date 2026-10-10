import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import Link from "next/link"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"
import { ChampionshipJoinButton } from "@/components/championships/championship-join-button"

export default async function ChampionshipDetailPage({ params }: { params: Promise<{ championshipId: string }> }) {
  const { championshipId } = await params
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

  // Get championship details
  const { data: championship } = await supabase
    .from("championships")
    .select(
      `
      *,
      profiles!championships_created_by_fkey (full_name)
    `,
    )
    .eq("id", championshipId)
    .single()

  if (!championship) {
    redirect("/championships")
  }

  // Get participants with rankings
  const { data: participants } = await supabase
    .from("championship_participants")
    .select(
      `
      *,
      profiles (full_name, level, xp)
    `,
    )
    .eq("championship_id", championshipId)
    .order("score", { ascending: false })

  const isParticipating = participants?.some((p) => p.user_id === user.id)
  const userParticipation = participants?.find((p) => p.user_id === user.id)

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

  const getMedalEmoji = (rank: number) => {
    if (rank === 1) return "🥇"
    if (rank === 2) return "🥈"
    if (rank === 3) return "🥉"
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <Button asChild variant="ghost" className="mb-4">
          <Link href="/championships">← Voltar para Campeonatos</Link>
        </Button>

        {/* Championship Header */}
        <Card className="mb-8">
          <CardHeader>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-2">
                <Badge className={statusColors[championship.status]}>{statusLabels[championship.status]}</Badge>
                <Badge variant="outline">{subjectLabels[championship.subject]}</Badge>
              </div>
              {isParticipating && (
                <Badge variant="default" className="bg-green-500">
                  Você está participando
                </Badge>
              )}
            </div>
            <CardTitle className="text-4xl mb-2">{championship.title}</CardTitle>
            <CardDescription className="text-lg">{championship.description}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-muted-foreground mb-1">Criado por</div>
                <div className="font-semibold">{championship.profiles?.full_name || "Professor"}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground mb-1">Participantes</div>
                <div className="font-semibold">
                  {participants?.length || 0}
                  {championship.max_participants && ` / ${championship.max_participants}`}
                </div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground mb-1">Data de Início</div>
                <div className="font-semibold">{new Date(championship.start_date).toLocaleDateString("pt-BR")}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground mb-1">Data de Término</div>
                <div className="font-semibold">{new Date(championship.end_date).toLocaleDateString("pt-BR")}</div>
              </div>
            </div>

            {!isParticipating && championship.status !== "completed" && (
              <ChampionshipJoinButton championshipId={championship.id} userId={user.id} />
            )}
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* User Position (if participating) */}
          {isParticipating && userParticipation && (
            <Card className="lg:col-span-3">
              <CardHeader>
                <CardTitle>Sua Posição</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <div className="text-5xl font-bold text-primary">#{userParticipation.rank || "-"}</div>
                    <div className="text-sm text-muted-foreground mt-1">Posição</div>
                  </div>
                  <div className="flex-1 grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-secondary">{userParticipation.score}</div>
                      <div className="text-sm text-muted-foreground">Pontos</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-accent">
                        {participants && participants.length > 0
                          ? Math.round(
                              ((participants.length - (userParticipation.rank || participants.length)) /
                                participants.length) *
                                100,
                            )
                          : 0}
                        %
                      </div>
                      <div className="text-sm text-muted-foreground">Melhor que</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-chart-1">
                        {participants && participants[0]
                          ? Math.max(0, participants[0].score - userParticipation.score)
                          : 0}
                      </div>
                      <div className="text-sm text-muted-foreground">Pontos do líder</div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Ranking */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>Ranking</CardTitle>
              <CardDescription>Classificação dos participantes</CardDescription>
            </CardHeader>
            <CardContent>
              {participants && participants.length > 0 ? (
                <div className="space-y-2">
                  {participants.map((participant, index) => {
                    const initials = participant.profiles?.full_name
                      ?.split(" ")
                      .map((n) => n[0])
                      .join("")
                      .toUpperCase()
                      .slice(0, 2)
                    const medal = getMedalEmoji(index + 1)
                    const isCurrentUser = participant.user_id === user.id

                    return (
                      <div
                        key={participant.id}
                        className={`flex items-center gap-4 p-4 rounded-lg border transition-all ${
                          isCurrentUser ? "bg-primary/5 border-primary" : "hover:bg-accent/5"
                        }`}
                      >
                        <div className="w-12 text-center">
                          {medal ? (
                            <span className="text-3xl">{medal}</span>
                          ) : (
                            <span className="text-xl font-bold text-muted-foreground">#{index + 1}</span>
                          )}
                        </div>

                        <Avatar className="h-12 w-12">
                          <AvatarFallback className="bg-gradient-to-br from-primary to-secondary text-primary-foreground">
                            {initials}
                          </AvatarFallback>
                        </Avatar>

                        <div className="flex-1 min-w-0">
                          <div className="font-semibold truncate">
                            {participant.profiles?.full_name}
                            {isCurrentUser && (
                              <Badge variant="outline" className="ml-2">
                                Você
                              </Badge>
                            )}
                          </div>
                          <div className="text-sm text-muted-foreground">
                            Nível {participant.profiles?.level} • {participant.profiles?.xp} XP
                          </div>
                        </div>

                        <div className="text-right">
                          <div className="text-2xl font-bold text-primary">{participant.score}</div>
                          <div className="text-sm text-muted-foreground">pontos</div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <div className="text-4xl mb-2">🏆</div>
                  <p>Nenhum participante ainda</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
