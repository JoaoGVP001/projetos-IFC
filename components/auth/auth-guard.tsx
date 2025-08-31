"use client"

import type React from "react"

import { createClient } from "@/lib/supabase/client"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import type { User } from "@supabase/supabase-js"

interface AuthGuardProps {
  children: React.ReactNode
  requiredRole?: string[]
  fallback?: React.ReactNode
}

export function AuthGuard({ children, requiredRole, fallback }: AuthGuardProps) {
  const [user, setUser] = useState<User | null>(null)
  const [userProfile, setUserProfile] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const supabase = createClient()

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const {
          data: { user },
        } = await supabase.auth.getUser()

        if (!user) {
          router.push("/auth/login")
          return
        }

        setUser(user)

        // Buscar perfil do usuário se necessário
        if (requiredRole) {
          const { data: profile } = await supabase.from("user_profiles").select("role").eq("id", user.id).single()

          if (profile) {
            setUserProfile(profile)

            // Verificar se o usuário tem o papel necessário
            if (!requiredRole.includes(profile.role)) {
              router.push("/unauthorized")
              return
            }
          }
        }
      } catch (error) {
        console.error("Erro ao verificar autenticação:", error)
        router.push("/auth/login")
      } finally {
        setLoading(false)
      }
    }

    checkAuth()

    // Escutar mudanças na autenticação
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === "SIGNED_OUT" || !session) {
        router.push("/auth/login")
      }
    })

    return () => subscription.unsubscribe()
  }, [router, supabase, requiredRole])

  if (loading) {
    return (
      fallback || (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )
    )
  }

  if (!user) {
    return null
  }

  return <>{children}</>
}
