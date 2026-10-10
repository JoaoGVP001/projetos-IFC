import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { DashboardOverview } from "@/components/dashboard/dashboard-overview"
import { AuthGuard } from "@/components/auth/auth-guard"

export default async function DashboardPage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  return (
    <AuthGuard>
      <DashboardOverview />
    </AuthGuard>
  )
}
