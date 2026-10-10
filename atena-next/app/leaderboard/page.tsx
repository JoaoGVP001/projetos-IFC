import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"

export default async function LeaderboardPage() {
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

  // Get top students by XP
  const { data: topByXP } = await supabase
    .from("profiles")
    .select("*")
    .eq("role", "student")
    .order("xp", { ascending: false })
    .limit(50)

  // Get top students by streak
  const { data: topByStreak } = await supabase
    .from("profiles")
    .select("*")
    .eq("role", "student")
    .order("current_streak", { ascending: false })
    .limit(10)

  // Find user's rank
  const userRank = topByXP?.findIndex((p) => p.id === user.id) ?? -1

  const getMedalEmoji = (rank: number) => {
    if (rank === 0) return "🥇"
    if (rank === 1) return "🥈"
    if (rank === 2) return "🥉"
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Ranking</h1>
          <p className="text-muted-foreground text-lg">Veja os melhores estudantes da plataforma</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* User's Position */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Sua Posição</CardTitle>
              <CardDescription>Seu ranking atual no leaderboard</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <div className="text-5xl font-bold text-primary">#{userRank + 1}</div>
                  <div className="text-sm text-muted-foreground mt-1">Posição</div>
                </div>
                <div className="flex-1 grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-secondary">{profile.xp}</div>
                    <div className="text-sm text-muted-foreground">XP Total</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-accent">{profile.level}</div>
                    <div className="text-sm text-muted-foreground">Nível</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-chart-1">{profile.current_streak}</div>
                    <div className="text-sm text-muted-foreground">Sequência</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Top Streak */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Maiores Sequências</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {topByStreak?.slice(0, 5).map((student, index) => {
                const initials = student.full_name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase()
                  .slice(0, 2)

                return (
                  <div key={student.id} className="flex items-center gap-3">
                    <div className="w-8 text-center font-bold text-muted-foreground">{index + 1}</div>
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="text-xs bg-gradient-to-br from-primary to-secondary text-primary-foreground">
                        {initials}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">{student.full_name}</div>
                    </div>
                    <Badge variant="secondary">{student.current_streak} dias</Badge>
                  </div>
                )
              })}
            </CardContent>
          </Card>
        </div>

        {/* Main Leaderboard */}
        <Card>
          <CardHeader>
            <CardTitle>Top 50 Estudantes</CardTitle>
            <CardDescription>Ranking por XP total</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {topByXP?.map((student, index) => {
                const initials = student.full_name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase()
                  .slice(0, 2)
                const medal = getMedalEmoji(index)
                const isCurrentUser = student.id === user.id

                return (
                  <div
                    key={student.id}
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
                        {student.full_name}
                        {isCurrentUser && (
                          <Badge variant="outline" className="ml-2">
                            Você
                          </Badge>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">Nível {student.level}</div>
                    </div>

                    <div className="text-right">
                      <div className="text-2xl font-bold text-primary">{student.xp}</div>
                      <div className="text-sm text-muted-foreground">XP</div>
                    </div>

                    <div className="text-right hidden md:block">
                      <div className="text-lg font-semibold text-secondary">{student.current_streak}</div>
                      <div className="text-sm text-muted-foreground">dias</div>
                    </div>

                    <div className="text-right hidden md:block">
                      <div className="text-lg font-semibold text-accent">{student.total_questions_answered}</div>
                      <div className="text-sm text-muted-foreground">questões</div>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
