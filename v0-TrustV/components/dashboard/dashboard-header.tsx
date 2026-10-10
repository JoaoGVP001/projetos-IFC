"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { LogoutButton } from "@/components/auth/logout-button"
import { User, Settings } from "lucide-react"

interface UserProfile {
  full_name: string
  role: string
  email: string
}

export function DashboardHeader() {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const supabase = createClient()

  useEffect(() => {
    fetchUserProfile()
  }, [])

  const fetchUserProfile = async () => {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (user) {
        const { data: profile } = await supabase
          .from("user_profiles")
          .select("full_name, role")
          .eq("id", user.id)
          .single()

        if (profile) {
          setUserProfile({
            ...profile,
            email: user.email || "",
          })
        }
      }
    } catch (error) {
      console.error("Erro ao buscar perfil:", error)
    }
  }

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "site_admin":
        return "Administrador do Sistema"
      case "admin":
        return "Administrador"
      case "seller":
        return "Vendedor"
      case "accountant":
        return "Contador"
      default:
        return role
    }
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case "site_admin":
        return "destructive"
      case "admin":
        return "default"
      case "seller":
        return "secondary"
      case "accountant":
        return "outline"
      default:
        return "default"
    }
  }

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex-1" />

          <div className="flex items-center gap-4">
            {userProfile && (
              <div className="hidden sm:flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{userProfile.full_name || "Usuário"}</p>
                  <Badge variant={getRoleColor(userProfile.role) as any} className="text-xs">
                    {getRoleLabel(userProfile.role)}
                  </Badge>
                </div>
              </div>
            )}

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Avatar className="h-8 w-8 cursor-pointer">
                  <AvatarFallback className="bg-blue-100 text-blue-700">
                    {userProfile?.full_name?.charAt(0) || "U"}
                  </AvatarFallback>
                </Avatar>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">{userProfile?.full_name || "Usuário"}</p>
                    <p className="text-xs text-gray-500">{userProfile?.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>
                  <User className="mr-2 h-4 w-4" />
                  Perfil
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  Configurações
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <LogoutButton variant="ghost" size="sm" showIcon={false} />
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  )
}
