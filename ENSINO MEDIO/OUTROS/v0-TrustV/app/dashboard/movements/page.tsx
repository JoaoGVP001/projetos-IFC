import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { MovementsList } from "@/components/movements/movements-list"
import { AuthGuard } from "@/components/auth/auth-guard"

export default async function MovementsPage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  return (
    <AuthGuard requiredRole={["admin", "seller"]}>
      <div className="container mx-auto py-6 px-4">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Movimentações de Estoque</h1>
            <p className="text-gray-600 mt-1">Gerencie entradas, saídas e ajustes de inventário</p>
          </div>
        </div>
        <MovementsList />
      </div>
    </AuthGuard>
  )
}
