"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Building2, Check, ChevronDown } from "lucide-react"

interface Company {
  id: string
  name: string
  cnpj: string
  is_active: boolean
}

interface CompanySelectorProps {
  onCompanyChange?: (companyId: string) => void
}

export function CompanySelector({ onCompanyChange }: CompanySelectorProps) {
  const [companies, setCompanies] = useState<Company[]>([])
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null)
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    fetchUserCompanies()
  }, [])

  const fetchUserCompanies = async () => {
    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (user) {
        const { data: userCompanies } = await supabase
          .from("user_companies")
          .select(`
            company_id,
            companies (
              id,
              name,
              cnpj,
              is_active
            )
          `)
          .eq("user_id", user.id)
          .eq("is_active", true)

        if (userCompanies) {
          const companiesList = userCompanies.map((uc) => uc.companies).filter(Boolean) as Company[]

          setCompanies(companiesList)

          // Selecionar a primeira empresa por padrão
          if (companiesList.length > 0 && !selectedCompany) {
            setSelectedCompany(companiesList[0])
            onCompanyChange?.(companiesList[0].id)
          }
        }
      }
    } catch (error) {
      console.error("Erro ao buscar empresas:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleCompanySelect = (company: Company) => {
    setSelectedCompany(company)
    onCompanyChange?.(company.id)
  }

  if (loading) {
    return (
      <Button variant="outline" disabled>
        <Building2 className="h-4 w-4 mr-2" />
        Carregando...
      </Button>
    )
  }

  if (companies.length === 0) {
    return (
      <Button variant="outline" disabled>
        <Building2 className="h-4 w-4 mr-2" />
        Nenhuma empresa
      </Button>
    )
  }

  if (companies.length === 1) {
    return (
      <Button variant="outline" disabled>
        <Building2 className="h-4 w-4 mr-2" />
        {selectedCompany?.name || companies[0].name}
      </Button>
    )
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="w-full sm:w-auto bg-transparent">
          <Building2 className="h-4 w-4 mr-2" />
          {selectedCompany?.name || "Selecionar Empresa"}
          <ChevronDown className="h-4 w-4 ml-2" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-64">
        <DropdownMenuLabel>Empresas Disponíveis</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {companies.map((company) => (
          <DropdownMenuItem
            key={company.id}
            onClick={() => handleCompanySelect(company)}
            className="flex items-center justify-between"
          >
            <div className="flex flex-col">
              <span className="font-medium">{company.name}</span>
              <span className="text-xs text-gray-500">CNPJ: {company.cnpj}</span>
            </div>
            {selectedCompany?.id === company.id && <Check className="h-4 w-4" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
