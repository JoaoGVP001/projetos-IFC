import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"
import { ClassForm } from "@/components/teacher/class-form"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default async function NewClassPage() {
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

  return (
    <div className="min-h-screen bg-background">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <Button asChild variant="ghost" className="mb-6">
          <Link href="/teacher/classes">← Voltar para Turmas</Link>
        </Button>

        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Criar Nova Turma</h1>
          <p className="text-muted-foreground">Preencha os dados para criar uma nova turma</p>
        </div>

        <ClassForm userId={user.id} />
      </div>
    </div>
  )
}
