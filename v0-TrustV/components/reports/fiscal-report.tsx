"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon, Download, FileText } from "lucide-react"
import { format, startOfMonth, endOfMonth } from "date-fns"
import { ptBR } from "date-fns/locale"
import { cn } from "@/lib/utils"
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts"

interface FiscalData {
  totalIcms: number
  totalIpi: number
  totalPis: number
  totalCofins: number
  totalTaxes: number
  monthlyTaxes: Array<{
    month: string
    icms: number
    ipi: number
    pis: number
    cofins: number
  }>
}

export function FiscalReport() {
  const [fiscalData, setFiscalData] = useState<FiscalData>({
    totalIcms: 0,
    totalIpi: 0,
    totalPis: 0,
    totalCofins: 0,
    totalTaxes: 0,
    monthlyTaxes: [],
  })
  const [dateRange, setDateRange] = useState({
    from: startOfMonth(new Date()),
    to: endOfMonth(new Date()),
  })
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    fetchFiscalData()
  }, [dateRange])

  const fetchFiscalData = async () => {
    try {
      const { data: movementsData, error } = await supabase
        .from("inventory_movements")
        .select("*")
        .gte("movement_date", dateRange.from.toISOString())
        .lte("movement_date", dateRange.to.toISOString())

      if (error) throw error

      const movements = movementsData || []

      // Calcular totais de impostos
      const totalIcms = movements.reduce((sum, m) => sum + (m.icms_value || 0), 0)
      const totalIpi = movements.reduce((sum, m) => sum + (m.ipi_value || 0), 0)
      const totalPis = movements.reduce((sum, m) => sum + (m.pis_value || 0), 0)
      const totalCofins = movements.reduce((sum, m) => sum + (m.cofins_value || 0), 0)

      // Impostos mensais (simplificado para demonstração)
      const monthlyMap = new Map()
      movements.forEach((movement) => {
        const month = format(new Date(movement.movement_date), "MM/yyyy")
        if (!monthlyMap.has(month)) {
          monthlyMap.set(month, { icms: 0, ipi: 0, pis: 0, cofins: 0 })
        }
        const monthData = monthlyMap.get(month)
        monthData.icms += movement.icms_value || 0
        monthData.ipi += movement.ipi_value || 0
        monthData.pis += movement.pis_value || 0
        monthData.cofins += movement.cofins_value || 0
      })

      const monthlyTaxes = Array.from(monthlyMap.entries()).map(([month, data]) => ({
        month,
        ...data,
      }))

      setFiscalData({
        totalIcms,
        totalIpi,
        totalPis,
        totalCofins,
        totalTaxes: totalIcms + totalIpi + totalPis + totalCofins,
        monthlyTaxes,
      })
    } catch (error) {
      console.error("Erro ao buscar dados fiscais:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filtros de data */}
      <Card>
        <CardHeader>
          <CardTitle>Período de Análise</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn("justify-start text-left font-normal", !dateRange.from && "text-muted-foreground")}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {dateRange.from ? format(dateRange.from, "dd/MM/yyyy", { locale: ptBR }) : "Data inicial"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={dateRange.from}
                  onSelect={(date) => date && setDateRange((prev) => ({ ...prev, from: date }))}
                  initialFocus
                />
              </PopoverContent>
            </Popover>

            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn("justify-start text-left font-normal", !dateRange.to && "text-muted-foreground")}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {dateRange.to ? format(dateRange.to, "dd/MM/yyyy", { locale: ptBR }) : "Data final"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={dateRange.to}
                  onSelect={(date) => date && setDateRange((prev) => ({ ...prev, to: date }))}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
        </CardContent>
      </Card>

      {/* Resumo de impostos */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">ICMS</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {fiscalData.totalIcms.toFixed(2)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">IPI</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {fiscalData.totalIpi.toFixed(2)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">PIS</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {fiscalData.totalPis.toFixed(2)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">COFINS</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {fiscalData.totalCofins.toFixed(2)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total</CardTitle>
            <FileText className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">R$ {fiscalData.totalTaxes.toFixed(2)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Gráfico de impostos mensais */}
      <Card>
        <CardHeader>
          <CardTitle>Impostos por Mês</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={fiscalData.monthlyTaxes}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="icms" stackId="a" fill="#8884d8" name="ICMS" />
              <Bar dataKey="ipi" stackId="a" fill="#82ca9d" name="IPI" />
              <Bar dataKey="pis" stackId="a" fill="#ffc658" name="PIS" />
              <Bar dataKey="cofins" stackId="a" fill="#ff7300" name="COFINS" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Informações adicionais */}
      <Card>
        <CardHeader>
          <CardTitle>Informações Fiscais</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Observações Importantes</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Os valores apresentados são baseados nas movimentações registradas no período</li>
                <li>• Consulte sempre um contador para validação dos cálculos fiscais</li>
                <li>• Mantenha todos os documentos fiscais organizados para auditoria</li>
              </ul>
            </div>

            <div className="flex gap-2">
              <Button variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar Relatório Fiscal
              </Button>
              <Button variant="outline">
                <FileText className="h-4 w-4 mr-2" />
                Gerar SPED
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
