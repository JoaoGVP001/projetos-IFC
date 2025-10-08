import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"

export default async function TeacherChampionshipsPage() {
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

  // Get championships created by this teacher
  const { data: championships } = await supabase
    .from("championships")
    .select(
      `
      *,
      championship_participants (user_id)
    `,
    )
    .eq("created_by", user.id)
    .order("created_at", { ascending: false })

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

  const subjectLabels = {
    math: "Matemática",
    portuguese: "Português",
    biology: "Biologia",
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Meus Campeonatos</h1>
            <p className="text-muted-foreground text-lg">Gerencie os campeonatos que você criou</p>
          </div>
          <Button asChild size="lg">
            <Link href="/teacher/championships/new">+ Novo Campeonato</Link>
          </Button>
        </div>

        {championships && championships.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {championships.map((championship) => {
              const participantCount = championship.championship_participants?.length || 0

              return (
                <Card key={championship.id} className="hover:shadow-lg transition-all">
                  <CardHeader>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className={statusColors[championship.status]}>{statusLabels[championship.status]}</Badge>
                      <Badge variant="outline">{subjectLabels[championship.subject]}</Badge>
                    </div>
                    <CardTitle className="text-xl">{championship.title}</CardTitle>
                    <CardDescription>{championship.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Participantes:</span>
                        <div className="font-medium">
                          {participantCount}
                          {championship.max_participants && ` / ${championship.max_participants}`}
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Término:</span>
                        <div className="font-medium">{new Date(championship.end_date).toLocaleDateString("pt-BR")}</div>
                      </div>
                    </div>

                    <Button asChild className="w-full bg-transparent" variant="outline">
                      <Link href={`/championships/${championship.id}`}>Ver Detalhes</Link>
                    </Button>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="text-6xl mb-4">🏆</div>
              <h2 className="text-2xl font-bold mb-2">Nenhum campeonato criado</h2>
              <p className="text-muted-foreground mb-6">Crie seu primeiro campeonato para engajar os estudantes!</p>
              <Button asChild>
                <Link href="/teacher/championships/new">Criar Primeiro Campeonato</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
