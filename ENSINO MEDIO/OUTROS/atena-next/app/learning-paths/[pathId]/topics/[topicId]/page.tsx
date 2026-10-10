import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { DashboardNav } from "@/components/dashboard/dashboard-nav"
import { TopicPractice } from "@/components/learning/topic-practice"

export default async function TopicPracticePage({
  params,
}: {
  params: Promise<{ pathId: string; topicId: string }>
}) {
  const { pathId, topicId } = await params
  const supabase = await createClient()

  const {
    data: { user },
    error: userError,
  } = await supabase.auth.getUser()

  if (userError || !user) {
    redirect("/auth/login")
  }

  const { data: profile } = await supabase.from("profiles").select("*").eq("id", user.id).single()

  if (!profile) {
    redirect("/auth/login")
  }

  // Get topic
  const { data: topic } = await supabase.from("topics").select("*").eq("id", topicId).single()

  if (!topic) {
    redirect("/learning-paths")
  }

  // Get learning path
  const { data: learningPath } = await supabase.from("learning_paths").select("*").eq("id", pathId).single()

  if (!learningPath) {
    redirect("/learning-paths")
  }

  // Get questions for this topic
  const { data: questions, error: questionsError } = await supabase
    .from("questions")
    .select(
      `
      *,
      question_options (*)
    `,
    )
    .eq("topic_id", topicId)
    .order("created_at")

  console.log("[v0] Fetched questions for topic:", topicId)
  console.log("[v0] Questions data:", questions)
  console.log("[v0] Questions error:", questionsError)

  // Get user progress
  const { data: progress } = await supabase
    .from("user_topic_progress")
    .select("*")
    .eq("user_id", user.id)
    .eq("topic_id", topicId)
    .single()

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5">
      <DashboardNav profile={profile} />

      <TopicPractice
        topic={topic}
        learningPath={learningPath}
        questions={questions || []}
        progress={progress}
        userId={user.id}
      />
    </div>
  )
}
