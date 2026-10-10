import { createServerClient } from "@/lib/supabase/server"
import { redirect } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bell, Trophy, Award, Users, BookOpen } from "lucide-react"

export default async function NotificationsPage() {
  const supabase = await createServerClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  const { data: notifications } = await supabase
    .from("notifications")
    .select("*")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false })
    .limit(50)

  // Mark all as read
  if (notifications && notifications.length > 0) {
    await supabase.from("notifications").update({ read: true }).eq("user_id", user.id).eq("read", false)
  }

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "achievement":
        return <Award className="h-5 w-5 text-yellow-500" />
      case "championship":
        return <Trophy className="h-5 w-5 text-purple-500" />
      case "friend":
        return <Users className="h-5 w-5 text-teal-500" />
      case "level_up":
        return <BookOpen className="h-5 w-5 text-orange-500" />
      default:
        return <Bell className="h-5 w-5 text-gray-500" />
    }
  }

  const getNotificationColor = (type: string) => {
    switch (type) {
      case "achievement":
        return "border-l-yellow-500"
      case "championship":
        return "border-l-purple-500"
      case "friend":
        return "border-l-teal-500"
      case "level_up":
        return "border-l-orange-500"
      default:
        return "border-l-gray-500"
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-teal-50 p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Notificações</h1>
          <p className="text-gray-600">Acompanhe suas conquistas e atualizações</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Todas as Notificações</CardTitle>
            <CardDescription>{notifications?.length || 0} notificações no total</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {notifications?.map((notification) => (
                <div
                  key={notification.id}
                  className={`flex items-start gap-4 p-4 rounded-lg border-l-4 bg-white hover:shadow-md transition-shadow ${getNotificationColor(notification.type)}`}
                >
                  <div className="mt-1">{getNotificationIcon(notification.type)}</div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-semibold text-gray-900">{notification.title}</h3>
                      {!notification.read && (
                        <Badge variant="secondary" className="text-xs">
                          Nova
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                    <p className="text-xs text-gray-400 mt-2">
                      {new Date(notification.created_at).toLocaleDateString("pt-BR", {
                        day: "2-digit",
                        month: "long",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </div>
              ))}

              {(!notifications || notifications.length === 0) && (
                <div className="text-center py-12 text-gray-500">
                  <Bell className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Nenhuma notificação ainda.</p>
                  <p className="text-sm mt-2">Você receberá notificações sobre conquistas, campeonatos e mais!</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
