"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Building2, Save, Plus, Edit } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { formatPhone, formatCNPJ, validateCNPJ, validatePhone } from "@/lib/utils/masks"

interface Company {
  id: string
  name: string
  cnpj: string
  address: string
  phone: string
  email: string
  is_active: boolean
  created_at: string
}

export function CompanySettings() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    cnpj: "",
    address: "",
    phone: "",
    email: "",
    is_active: true,
  })
  const [errors, setErrors] = useState({
    cnpj: "",
    phone: "",
  })
  const supabase = createClient()
  const { toast } = useToast()

  useEffect(() => {
    fetchCompanies()
  }, [])

  const fetchCompanies = async () => {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (user) {
        const { data: profile } = await supabase.from("user_profiles").select("role").eq("id", user.id).single()

        let query = supabase.from("companies").select("*")

        if (profile?.role !== "site_admin") {
          const { data: userCompanies } = await supabase
            .from("user_companies")
            .select("company_id")
            .eq("user_id", user.id)

          if (userCompanies) {
            const companyIds = userCompanies.map((uc) => uc.company_id)
            query = query.in("id", companyIds)
          }
        }

        const { data: companiesData } = await query.order("name")

        if (companiesData) {
          setCompanies(companiesData)
          if (companiesData.length > 0) {
            setSelectedCompany(companiesData[0])
          }
        }
      }
    } catch (error) {
      console.error("Erro ao buscar empresas:", error)
    } finally {
      setLoading(false)
    }
  }

  const validateForm = () => {
    const newErrors = { cnpj: "", phone: "" }
    let isValid = true

    if (formData.cnpj && !validateCNPJ(formData.cnpj)) {
      newErrors.cnpj = "CNPJ inválido"
      isValid = false
    }

    if (formData.phone && !validatePhone(formData.phone)) {
      newErrors.phone = "Telefone inválido"
      isValid = false
    }

    setErrors(newErrors)
    return isValid
  }

  const handleSave = async () => {
    if (!validateForm()) {
      toast({
        title: "Erro de validação",
        description: "Por favor, corrija os campos inválidos",
        variant: "destructive",
      })
      return
    }

    setSaving(true)
    try {
      if (isEditing && selectedCompany) {
        const { error } = await supabase.from("companies").update(formData).eq("id", selectedCompany.id)

        if (error) {
          console.error("[v0] Erro ao atualizar empresa:", error)
          throw error
        }

        toast({
          title: "Sucesso",
          description: "Empresa atualizada com sucesso",
        })
      } else {
        const { data: newCompany, error } = await supabase.from("companies").insert([formData]).select().single()

        if (error) {
          console.error("[v0] Erro ao criar empresa:", error)
          throw error
        }

        const {
          data: { user },
        } = await supabase.auth.getUser()

        if (user && newCompany) {
          const { error: userCompanyError } = await supabase.from("user_companies").insert([
            {
              user_id: user.id,
              company_id: newCompany.id,
              role: "admin",
              is_active: true,
            },
          ])

          if (userCompanyError) {
            console.error("[v0] Erro ao associar usuário à empresa:", userCompanyError)
          }
        }

        toast({
          title: "Sucesso",
          description: "Empresa criada com sucesso",
        })
      }

      setIsDialogOpen(false)
      setIsEditing(false)
      resetForm()
      fetchCompanies()
    } catch (error: any) {
      console.error("[v0] Erro ao salvar empresa:", error)

      let errorMessage = "Não foi possível salvar a empresa"

      if (error?.message?.includes("table") && error?.message?.includes("schema cache")) {
        errorMessage = "Banco de dados não configurado. Entre em contato com o suporte."
      } else if (error?.code === "23505") {
        errorMessage = "CNPJ já cadastrado no sistema"
      } else if (error?.message) {
        errorMessage = `Erro: ${error.message}`
      }

      toast({
        title: "Erro",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setSaving(false)
    }
  }

  const resetForm = () => {
    setFormData({
      name: "",
      cnpj: "",
      address: "",
      phone: "",
      email: "",
      is_active: true,
    })
    setErrors({ cnpj: "", phone: "" })
  }

  const handleEdit = (company: Company) => {
    setFormData({
      name: company.name,
      cnpj: company.cnpj,
      address: company.address,
      phone: company.phone,
      email: company.email,
      is_active: company.is_active,
    })
    setIsEditing(true)
    setIsDialogOpen(true)
  }

  const handleNew = () => {
    resetForm()
    setIsEditing(false)
    setIsDialogOpen(true)
  }

  const handleCNPJChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatCNPJ(e.target.value)
    setFormData({ ...formData, cnpj: formatted })

    if (errors.cnpj) {
      setErrors({ ...errors, cnpj: "" })
    }
  }

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhone(e.target.value)
    setFormData({ ...formData, phone: formatted })

    if (errors.phone) {
      setErrors({ ...errors, phone: "" })
    }
  }

  if (loading) {
    return <div className="flex justify-center py-8">Carregando empresas...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Configurações das Empresas</h2>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={handleNew}>
              <Plus className="h-4 w-4 mr-2" />
              Nova Empresa
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>{isEditing ? "Editar Empresa" : "Nova Empresa"}</DialogTitle>
              <DialogDescription>
                {isEditing ? "Atualize as informações da empresa" : "Preencha os dados da nova empresa"}
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Nome da Empresa</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cnpj">CNPJ</Label>
                  <Input
                    id="cnpj"
                    value={formData.cnpj}
                    onChange={handleCNPJChange}
                    placeholder="00.000.000/0000-00"
                    maxLength={18}
                    className={errors.cnpj ? "border-red-500" : ""}
                  />
                  {errors.cnpj && <p className="text-sm text-red-500">{errors.cnpj}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="address">Endereço</Label>
                <Textarea
                  id="address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone">Telefone</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={handlePhoneChange}
                    placeholder="(00) 00000-0000"
                    maxLength={15}
                    className={errors.phone ? "border-red-500" : ""}
                  />
                  {errors.phone && <p className="text-sm text-red-500">{errors.phone}</p>}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="is_active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
                />
                <Label htmlFor="is_active">Empresa Ativa</Label>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSave} disabled={saving}>
                <Save className="h-4 w-4 mr-2" />
                {saving ? "Salvando..." : "Salvar"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-6">
        {companies.map((company) => (
          <Card key={company.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Building2 className="h-5 w-5" />
                    {company.name}
                  </CardTitle>
                  <CardDescription>CNPJ: {company.cnpj}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={company.is_active ? "default" : "secondary"}>
                    {company.is_active ? "Ativa" : "Inativa"}
                  </Badge>
                  <Button variant="outline" size="sm" onClick={() => handleEdit(company)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-500">Endereço</Label>
                  <p className="text-sm">{company.address || "Não informado"}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-500">Telefone</Label>
                  <p className="text-sm">{company.phone || "Não informado"}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-500">Email</Label>
                  <p className="text-sm">{company.email || "Não informado"}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-500">Criada em</Label>
                  <p className="text-sm">{new Date(company.created_at).toLocaleDateString("pt-BR")}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {companies.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Building2 className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma empresa encontrada</h3>
              <p className="text-gray-500 text-center mb-4">
                Você ainda não tem acesso a nenhuma empresa. Entre em contato com o administrador.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
