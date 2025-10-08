export type UserRole = "student" | "teacher"
export type SubjectType = "math" | "portuguese" | "biology"
export type QuestionDifficulty = "easy" | "medium" | "hard"
export type ChampionshipStatus = "upcoming" | "active" | "completed"

export interface Profile {
  id: string
  email: string
  full_name: string
  role: UserRole
  avatar_url?: string
  xp: number
  level: number
  current_streak: number
  longest_streak: number
  last_activity_date?: string
  total_questions_answered: number
  correct_answers: number
  created_at: string
  updated_at: string
}

export interface LearningPath {
  id: string
  subject: SubjectType
  title: string
  description?: string
  icon?: string
  order_index: number
  created_at: string
}

export interface Topic {
  id: string
  learning_path_id: string
  title: string
  description?: string
  order_index: number
  xp_reward: number
  created_at: string
}

export interface Question {
  id: string
  topic_id: string
  question_text: string
  question_type: string
  difficulty: QuestionDifficulty
  xp_value: number
  explanation?: string
  created_by?: string
  created_at: string
}

export interface QuestionOption {
  id: string
  question_id: string
  option_text: string
  is_correct: boolean
  order_index: number
}

export interface UserTopicProgress {
  id: string
  user_id: string
  topic_id: string
  is_completed: boolean
  questions_answered: number
  correct_answers: number
  xp_earned: number
  last_practiced_at?: string
  completed_at?: string
}

export interface Achievement {
  id: string
  title: string
  description: string
  icon: string
  requirement_type: string
  requirement_value: number
  xp_reward: number
  created_at: string
}

export interface Championship {
  id: string
  title: string
  description?: string
  created_by?: string
  subject: SubjectType
  start_date: string
  end_date: string
  status: ChampionshipStatus
  max_participants?: number
  created_at: string
}
