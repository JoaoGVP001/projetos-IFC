"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { User, Bell, Shield, Save } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface UserProfile {
  id: string
  full_name: string
  role: string
  email: string
  is_active: boolean
}

export function SystemSettings() {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [notifications, setNotifications] = useState({
    email: true,
    lowStock: true,
    movements: false,
    reports: true,
  })
  const supabase = createClient()
  const { toast } = useToast()

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
          .select("id, full_name, role, is_active")
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
    } finally {
      setLoading(false)
    }
  }

  const handleSaveProfile = async () => {
    if (!userProfile) return

    setSaving(true)
    try {
      const { error } = await supabase
        .from("user_profiles")
        .update({
          full_name: userProfile.full_name,
        })
        .eq("id", userProfile.id)

      if (error) throw error

      toast({
        title: "Sucesso",
        description: "Perfil atualizado com sucesso",
      })
    } catch (error) {
      console.error("Erro ao salvar perfil:", error)
      toast({
        title: "Erro",
        description: "Não foi possível salvar o perfil",
        variant: "destructive",
      })
    } finally {
      setSaving(false)
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

  if (loading) {
    return <div className="flex justify-center py-8">Carregando configurações...</div>
  }

  return (
    <div className="space-y-6">
      {/* Perfil do Usuário */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Perfil do Usuário
          </CardTitle>
          <CardDescription>Gerencie suas informações pessoais</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {userProfile && (
            <>
              <div className="flex items-center gap-4">
                <Avatar className="h-16 w-16">
                  <AvatarFallback className="bg-blue-100 text-blue-700 text-lg">
                    {userProfile.full_name.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="text-lg font-semibold">{userProfile.full_name}</h3>
                  <p className="text-gray-600">{userProfile.email}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant={getRoleColor(userProfile.role) as any}>{getRoleLabel(userProfile.role)}</Badge>
                    <Badge variant={userProfile.is_active ? "default" : "secondary"}>
                      {userProfile.is_active ? "Ativo" : "Inativo"}
                    </Badge>
                  </div>
                </div>
              </div>

              <Separator />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="fullName">Nome Completo</Label>
                  <Input
                    id="fullName"
                    value={userProfile.full_name}
                    onChange={(e) => setUserProfile({ ...userProfile, full_name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" value={userProfile.email} disabled />
                </div>
              </div>

              <div className="flex justify-end">
                <Button onClick={handleSaveProfile} disabled={saving}>
                  <Save className="h-4 w-4 mr-2" />
                  {saving ? "Salvando..." : "Salvar Perfil"}
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Notificações */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notificações
          </CardTitle>
          <CardDescription>Configure suas preferências de notificação</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="email-notifications">Notificações por Email</Label>
              <p className="text-sm text-gray-500">Receba notificações importantes por email</p>
            </div>
            <Switch
              id="email-notifications"
              checked={notifications.email}
              onCheckedChange={(checked) => setNotifications({ ...notifications, email: checked })}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="low-stock">Alertas de Estoque Baixo</Label>
              <p className="text-sm text-gray-500">Notificações quando produtos estiverem com estoque baixo</p>
            </div>
            <Switch
              id="low-stock"
              checked={notifications.lowStock}
              onCheckedChange={(checked) => setNotifications({ ...notifications, lowStock: checked })}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="movements">Movimentações de Estoque</Label>
              <p className="text-sm text-gray-500">Notificações sobre movimentações de produtos</p>
            </div>
            <Switch
              id="movements"
              checked={notifications.movements}
              onCheckedChange={(checked) => setNotifications({ ...notifications, movements: checked })}
            />
          </div>

          <Separator />

          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="reports">Relatórios Automáticos</Label>
              <p className="text-sm text-gray-500">Receba relatórios periódicos por email</p>
            </div>
            <Switch
              id="reports"
              checked={notifications.reports}
              onCheckedChange={(checked) => setNotifications({ ...notifications, reports: checked })}
            />
          </div>
        </CardContent>
      </Card>

      {/* Segurança */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Segurança
          </CardTitle>
          <CardDescription>Configurações de segurança da conta</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Alterar Senha</Label>
            <p className="text-sm text-gray-500">Para alterar sua senha, você receberá um email com instruções</p>
            <Button variant="outline" size="sm">
              Solicitar Alteração de Senha
            </Button>
          </div>

          <Separator />

          <div className="space-y-2">
            <Label>Sessões Ativas</Label>
            <p className="text-sm text-gray-500">Gerencie suas sessões ativas em diferentes dispositivos</p>
            <Button variant="outline" size="sm">
              Ver Sessões Ativas
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
