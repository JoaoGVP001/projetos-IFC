import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

export default async function TeacherClassesPage() {
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

  // Get teacher's classes with student count
  const { data: classes } = await supabase
    .from("classes")
    .select(
      `
      *,
      class_students (count)
    `,
    )
    .eq("teacher_id", user.id)
    .order("created_at", { ascending: false })

  return (
    <div className="min-h-screen bg-background">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Minhas Turmas</h1>
            <p className="text-muted-foreground">Gerencie suas turmas e alunos</p>
          </div>
          <Button asChild size="lg">
            <Link href="/teacher/classes/new">+ Nova Turma</Link>
          </Button>
        </div>

        {!classes || classes.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <div className="text-6xl mb-4">👥</div>
              <h2 className="text-2xl font-bold mb-2">Nenhuma turma criada</h2>
              <p className="text-muted-foreground mb-6">Crie sua primeira turma para começar a gerenciar alunos.</p>
              <Button asChild size="lg">
                <Link href="/teacher/classes/new">Criar Primeira Turma</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {classes.map((classItem: any) => (
              <Link key={classItem.id} href={`/teacher/classes/${classItem.id}`}>
                <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                  <CardHeader>
                    <div className="flex items-start justify-between mb-2">
                      <CardTitle className="text-xl">{classItem.name}</CardTitle>
                      <Badge variant="secondary">{classItem.class_students[0]?.count || 0} alunos</Badge>
                    </div>
                    <CardDescription className="line-clamp-2">
                      {classItem.description || "Sem descrição"}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Código de Acesso:</span>
                        <Badge variant="outline" className="font-mono text-base">
                          {classItem.access_code}
                        </Badge>
                      </div>
                      {classItem.max_students && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Limite:</span>
                          <span>
                            {classItem.class_students[0]?.count || 0} / {classItem.max_students}
                          </span>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
