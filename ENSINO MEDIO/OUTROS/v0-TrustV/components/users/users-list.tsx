"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { InviteUserForm } from "./invite-user-form"
import { Search, UserPlus, Edit, Mail } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
  companies: {
    id: string
    name: string
    role: string
  }[]
}

export function UsersList() {
  const [users, setUsers] = useState<User[]>([])
  const [filteredUsers, setFilteredUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false)
  const supabase = createClient()

  useEffect(() => {
    fetchUsers()
  }, [])

  useEffect(() => {
    const filtered = users.filter(
      (user) =>
        user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()),
    )
    setFilteredUsers(filtered)
  }, [users, searchTerm])

  const fetchUsers = async () => {
    try {
      const {
        data: { user: currentUser },
      } = await supabase.auth.getUser()

      if (currentUser) {
        // Buscar perfil do usuário atual
        const { data: currentProfile } = await supabase
          .from("user_profiles")
          .select("role")
          .eq("id", currentUser.id)
          .single()

        let usersQuery = supabase.from("user_profiles").select(`
            id,
            full_name,
            role,
            is_active,
            created_at,
            users!inner(email)
          `)

        // Se não for site_admin, mostrar apenas usuários das mesmas empresas
        if (currentProfile?.role !== "site_admin") {
          const { data: userCompanies } = await supabase
            .from("user_companies")
            .select("company_id")
            .eq("user_id", currentUser.id)

          if (userCompanies) {
            const companyIds = userCompanies.map((uc) => uc.company_id)

            const { data: companyUsers } = await supabase
              .from("user_companies")
              .select("user_id")
              .in("company_id", companyIds)

            if (companyUsers) {
              const userIds = companyUsers.map((cu) => cu.user_id)
              usersQuery = usersQuery.in("id", userIds)
            }
          }
        }

        const { data: usersData } = await usersQuery.order("full_name")

        if (usersData) {
          // Buscar empresas de cada usuário
          const usersWithCompanies = await Promise.all(
            usersData.map(async (user) => {
              const { data: userCompanies } = await supabase
                .from("user_companies")
                .select(`
                  role,
                  companies (
                    id,
                    name
                  )
                `)
                .eq("user_id", user.id)
                .eq("is_active", true)

              return {
                id: user.id,
                email: user.users.email,
                full_name: user.full_name,
                role: user.role,
                is_active: user.is_active,
                created_at: user.created_at,
                companies:
                  userCompanies?.map((uc) => ({
                    id: uc.companies.id,
                    name: uc.companies.name,
                    role: uc.role,
                  })) || [],
              }
            }),
          )

          setUsers(usersWithCompanies)
        }
      }
    } catch (error) {
      console.error("Erro ao buscar usuários:", error)
    } finally {
      setLoading(false)
    }
  }

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "site_admin":
        return "Admin Sistema"
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
    return <div className="flex justify-center py-8">Carregando usuários...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Buscar usuários..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        <Dialog open={isInviteDialogOpen} onOpenChange={setIsInviteDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <UserPlus className="h-4 w-4 mr-2" />
              Convidar Usuário
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Convidar Novo Usuário</DialogTitle>
              <DialogDescription>Envie um convite para um novo usuário se juntar à plataforma</DialogDescription>
            </DialogHeader>
            <InviteUserForm
              onSuccess={() => {
                setIsInviteDialogOpen(false)
                fetchUsers()
              }}
            />
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Lista de Usuários</CardTitle>
          <CardDescription>Gerencie os usuários e suas permissões no sistema</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Usuário</TableHead>
                <TableHead>Perfil</TableHead>
                <TableHead>Empresas</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Criado em</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredUsers.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-blue-100 text-blue-700">
                          {user.full_name.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{user.full_name}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getRoleColor(user.role) as any}>{getRoleLabel(user.role)}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {user.companies.map((company) => (
                        <Badge key={company.id} variant="outline" className="text-xs">
                          {company.name}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={user.is_active ? "default" : "secondary"}>
                      {user.is_active ? "Ativo" : "Inativo"}
                    </Badge>
                  </TableCell>
                  <TableCell>{new Date(user.created_at).toLocaleDateString("pt-BR")}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Mail className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {filteredUsers.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500">Nenhum usuário encontrado</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
