import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"

export default async function AchievementsPage() {
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

  // Get all achievements
  const { data: achievements } = await supabase.from("achievements").select("*").order("requirement_value")

  // Get user's earned achievements
  const { data: userAchievements } = await supabase
    .from("user_achievements")
    .select("achievement_id, earned_at")
    .eq("user_id", user.id)

  const earnedAchievementIds = new Set(userAchievements?.map((ua) => ua.achievement_id) || [])

  // Calculate progress for each achievement
  const achievementsWithProgress = achievements?.map((achievement) => {
    const isEarned = earnedAchievementIds.has(achievement.id)
    const earnedDate = userAchievements?.find((ua) => ua.achievement_id === achievement.id)?.earned_at

    let currentValue = 0
    let progressPercentage = 0

    if (!isEarned) {
      switch (achievement.requirement_type) {
        case "questions_answered":
          currentValue = profile.total_questions_answered
          break
        case "streak":
          currentValue = profile.current_streak
          break
        case "correct_streak":
          currentValue = 0 // Would need to track this separately
          break
        case "level":
          currentValue = profile.level
          break
        case "championships_won":
          currentValue = 0 // Would need to track this
          break
      }

      progressPercentage = Math.min((currentValue / achievement.requirement_value) * 100, 100)
    } else {
      progressPercentage = 100
    }

    return {
      ...achievement,
      isEarned,
      earnedDate,
      currentValue,
      progressPercentage,
    }
  })

  const earnedCount = achievementsWithProgress?.filter((a) => a.isEarned).length || 0
  const totalCount = achievementsWithProgress?.length || 0
  const totalXpFromAchievements =
    achievementsWithProgress?.filter((a) => a.isEarned).reduce((sum, a) => sum + a.xp_reward, 0) || 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Conquistas</h1>
          <p className="text-muted-foreground text-lg">Desbloqueie badges e ganhe XP extra</p>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Conquistas Desbloqueadas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-primary mb-2">
                {earnedCount}/{totalCount}
              </div>
              <Progress value={(earnedCount / totalCount) * 100} className="h-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">XP de Conquistas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-secondary">{totalXpFromAchievements} XP</div>
              <p className="text-sm text-muted-foreground mt-2">Ganho com badges</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Próxima Conquista</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-accent">
                {achievementsWithProgress?.find((a) => !a.isEarned)?.title || "Todas desbloqueadas!"}
              </div>
              <p className="text-sm text-muted-foreground mt-2">Continue progredindo</p>
            </CardContent>
          </Card>
        </div>

        {/* Achievements Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {achievementsWithProgress?.map((achievement) => (
            <Card
              key={achievement.id}
              className={`transition-all ${
                achievement.isEarned
                  ? "border-primary bg-gradient-to-br from-primary/5 to-secondary/5"
                  : "opacity-75 grayscale"
              }`}
            >
              <CardHeader>
                <div className="flex items-start justify-between mb-2">
                  <div
                    className={`text-5xl ${achievement.isEarned ? "animate-bounce-slow" : "opacity-50"}`}
                    style={{ animationDuration: "3s" }}
                  >
                    {achievement.icon}
                  </div>
                  {achievement.isEarned && (
                    <Badge variant="default" className="bg-green-500">
                      Desbloqueado
                    </Badge>
                  )}
                </div>
                <CardTitle className="text-xl">{achievement.title}</CardTitle>
                <CardDescription>{achievement.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Recompensa</span>
                  <Badge variant="secondary">+{achievement.xp_reward} XP</Badge>
                </div>

                {!achievement.isEarned && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Progresso</span>
                      <span className="font-medium">
                        {achievement.currentValue}/{achievement.requirement_value}
                      </span>
                    </div>
                    <Progress value={achievement.progressPercentage} className="h-2" />
                  </div>
                )}

                {achievement.isEarned && achievement.earnedDate && (
                  <div className="text-sm text-muted-foreground">
                    Desbloqueado em {new Date(achievement.earnedDate).toLocaleDateString("pt-BR")}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
