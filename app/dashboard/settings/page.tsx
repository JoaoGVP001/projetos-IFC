import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { SystemSettings } from "@/components/settings/system-settings"
import { AuthGuard } from "@/components/auth/auth-guard"

export default async function SettingsPage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  return (
    <AuthGuard>
      <div className="container mx-auto py-6 px-4">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Configurações</h1>
            <p className="text-gray-600 mt-1">Gerencie suas preferências e configurações do sistema</p>
          </div>
        </div>
        <SystemSettings />
      </div>
    </AuthGuard>
  )
}
