import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"
import { QuestionEditForm } from "@/components/teacher/question-edit-form"

export default async function EditQuestionPage({ params }: { params: Promise<{ questionId: string }> }) {
  const { questionId } = await params
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

  // Get question with options
  const { data: question } = await supabase
    .from("questions")
    .select(
      `
      *,
      question_options (*),
      topics (
        *,
        learning_paths (*)
      )
    `,
    )
    .eq("id", questionId)
    .single()

  if (!question || question.created_by !== user.id) {
    redirect("/teacher/questions")
  }

  // Get all learning paths and topics
  const { data: learningPaths } = await supabase
    .from("learning_paths")
    .select(
      `
      *,
      topics (*)
    `,
    )
    .order("order_index")

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">Editar Questão</h1>
        <QuestionEditForm question={question} learningPaths={learningPaths || []} userId={user.id} />
      </div>
    </div>
  )
}
