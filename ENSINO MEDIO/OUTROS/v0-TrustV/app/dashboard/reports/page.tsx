import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { ReportsOverview } from "@/components/reports/reports-overview"
import { AuthGuard } from "@/components/auth/auth-guard"

export default async function ReportsPage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  return (
    <AuthGuard requiredRole={["admin", "accountant"]}>
      <div className="container mx-auto py-6 px-4">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Relatórios</h1>
            <p className="text-gray-600 mt-1">Análises e relatórios do seu inventário</p>
          </div>
        </div>
        <ReportsOverview />
      </div>
    </AuthGuard>
  )
}
