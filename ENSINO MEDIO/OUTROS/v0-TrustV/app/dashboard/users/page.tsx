import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { UsersList } from "@/components/users/users-list"
import { AuthGuard } from "@/components/auth/auth-guard"

export default async function UsersPage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  return (
    <AuthGuard requiredRole={["admin", "site_admin"]}>
      <div className="container mx-auto py-6 px-4">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Usuários</h1>
            <p className="text-gray-600 mt-1">Gerencie os usuários e suas permissões</p>
          </div>
        </div>
        <UsersList />
      </div>
    </AuthGuard>
  )
}
