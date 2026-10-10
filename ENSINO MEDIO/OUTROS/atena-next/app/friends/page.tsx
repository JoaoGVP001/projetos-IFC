import { createServerClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Users, UserPlus, Trophy } from "lucide-react"

export default async function FriendsPage() {
  const supabase = await createServerClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  const { data: profile } = await supabase.from("profiles").select("role").eq("id", user.id).single()

  if (profile?.role !== "student") {
    redirect("/dashboard")
  }

  // Get friends
  const { data: friendships } = await supabase
    .from("friendships")
    .select(`
      id,
      status,
      friend:friend_id (
        id,
        full_name,
        total_xp,
        level,
        current_streak
      )
    `)
    .eq("user_id", user.id)
    .eq("status", "accepted")

  // Get pending friend requests
  const { data: pendingRequests } = await supabase
    .from("friendships")
    .select(`
      id,
      user:user_id (
        id,
        full_name,
        total_xp,
        level
      )
    `)
    .eq("friend_id", user.id)
    .eq("status", "pending")

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-teal-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Amigos</h1>
            <p className="text-gray-600">Conecte-se com outros estudantes e compare seu progresso</p>
          </div>
          <Button className="gap-2">
            <UserPlus className="h-4 w-4" />
            Adicionar Amigo
          </Button>
        </div>

        {pendingRequests && pendingRequests.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Solicitações Pendentes</CardTitle>
              <CardDescription>{pendingRequests.length} solicitações aguardando resposta</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {pendingRequests.map((request) => (
                  <div key={request.id} className="flex items-center justify-between p-4 rounded-lg border bg-white">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-12 w-12">
                        <AvatarFallback className="bg-gradient-to-br from-purple-500 to-teal-500 text-white">
                          {request.user?.full_name
                            ?.split(" ")
                            .map((n: string) => n[0])
                            .join("")
                            .slice(0, 2) || "ST"}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h3 className="font-semibold text-gray-900">{request.user?.full_name || "Estudante"}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="secondary" className="text-xs">
                            Nível {request.user?.level}
                          </Badge>
                          <span className="text-sm text-gray-600">{request.user?.total_xp?.toLocaleString()} XP</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm">Aceitar</Button>
                      <Button size="sm" variant="outline">
                        Recusar
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Meus Amigos</CardTitle>
            <CardDescription>{friendships?.length || 0} amigos conectados</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {friendships?.map((friendship) => (
                <div
                  key={friendship.id}
                  className="flex items-center justify-between p-4 rounded-lg border bg-white hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center gap-3">
                    <Avatar className="h-14 w-14">
                      <AvatarFallback className="bg-gradient-to-br from-purple-500 to-teal-500 text-white">
                        {friendship.friend?.full_name
                          ?.split(" ")
                          .map((n: string) => n[0])
                          .join("")
                          .slice(0, 2) || "ST"}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold text-gray-900">{friendship.friend?.full_name || "Estudante"}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className="text-xs">
                          Nível {friendship.friend?.level}
                        </Badge>
                        <span className="text-sm text-gray-600">
                          {friendship.friend?.total_xp?.toLocaleString()} XP
                        </span>
                      </div>
                      <div className="flex items-center gap-1 mt-1 text-orange-600">
                        <Trophy className="h-3 w-3" />
                        <span className="text-xs">{friendship.friend?.current_streak} dias de sequência</span>
                      </div>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    Ver Perfil
                  </Button>
                </div>
              ))}

              {(!friendships || friendships.length === 0) && (
                <div className="col-span-2 text-center py-12 text-gray-500">
                  <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Você ainda não tem amigos conectados.</p>
                  <p className="text-sm mt-2">Adicione amigos para comparar seu progresso e se motivar!</p>
                  <Button className="mt-4 gap-2">
                    <UserPlus className="h-4 w-4" />
                    Adicionar Primeiro Amigo
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
