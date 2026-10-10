"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Badge } from "@/components/ui/badge"
import { CalendarIcon, Download, TrendingUp, TrendingDown } from "lucide-react"
import { format, subDays, startOfMonth, endOfMonth } from "date-fns"
import { ptBR } from "date-fns/locale"
import { cn } from "@/lib/utils"
import {
  Line,
  LineChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Bar,
  BarChart,
} from "recharts"

interface MovementData {
  totalMovements: number
  totalEntries: number
  totalExits: number
  totalValue: number
  dailyMovements: Array<{
    date: string
    entries: number
    exits: number
    value: number
  }>
  typeDistribution: Array<{
    type: string
    count: number
    value: number
  }>
}

interface Movement {
  id: string
  movement_type: string
  quantity: number
  unit_cost: number
  total_cost: number
  movement_date: string
  document_number: string
  supplier_customer: string
  products: {
    name: string
    sku: string
  }
}

export function MovementsReport() {
  const [movementData, setMovementData] = useState<MovementData>({
    totalMovements: 0,
    totalEntries: 0,
    totalExits: 0,
    totalValue: 0,
    dailyMovements: [],
    typeDistribution: [],
  })
  const [movements, setMovements] = useState<Movement[]>([])
  const [dateRange, setDateRange] = useState({
    from: startOfMonth(new Date()),
    to: endOfMonth(new Date()),
  })
  const [typeFilter, setTypeFilter] = useState("all")
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    fetchMovementsData()
  }, [dateRange])

  const fetchMovementsData = async () => {
    try {
      const { data: movementsData, error } = await supabase
        .from("inventory_movements")
        .select(`
          *,
          products (
            name,
            sku
          )
        `)
        .gte("movement_date", dateRange.from.toISOString())
        .lte("movement_date", dateRange.to.toISOString())
        .order("movement_date", { ascending: false })

      if (error) throw error

      const movements = movementsData || []
      setMovements(movements)

      // Calcular estatísticas
      const totalEntries = movements.filter((m) => m.movement_type === "entry").length
      const totalExits = movements.filter((m) => m.movement_type === "exit").length
      const totalValue = movements.reduce((sum, m) => sum + (m.total_cost || 0), 0)

      // Distribuição por tipo
      const typeMap = new Map()
      movements.forEach((movement) => {
        const type = movement.movement_type
        if (!typeMap.has(type)) {
          typeMap.set(type, { count: 0, value: 0 })
        }
        const typeData = typeMap.get(type)
        typeData.count += 1
        typeData.value += movement.total_cost || 0
      })

      const typeDistribution = Array.from(typeMap.entries()).map(([type, data]) => ({
        type: getMovementLabel(type),
        count: data.count,
        value: data.value,
      }))

      // Movimentações diárias
      const dailyMap = new Map()
      movements.forEach((movement) => {
        const date = format(new Date(movement.movement_date), "dd/MM")
        if (!dailyMap.has(date)) {
          dailyMap.set(date, { entries: 0, exits: 0, value: 0 })
        }
        const dayData = dailyMap.get(date)
        if (movement.movement_type === "entry") {
          dayData.entries += 1
        } else if (movement.movement_type === "exit") {
          dayData.exits += 1
        }
        dayData.value += movement.total_cost || 0
      })

      const dailyMovements = Array.from(dailyMap.entries()).map(([date, data]) => ({
        date,
        entries: data.entries,
        exits: data.exits,
        value: data.value,
      }))

      setMovementData({
        totalMovements: movements.length,
        totalEntries,
        totalExits,
        totalValue,
        dailyMovements,
        typeDistribution,
      })
    } catch (error) {
      console.error("Erro ao buscar dados de movimentações:", error)
    } finally {
      setLoading(false)
    }
  }

  const getMovementLabel = (type: string) => {
    switch (type) {
      case "entry":
        return "Entrada"
      case "exit":
        return "Saída"
      case "return":
        return "Devolução"
      case "adjustment":
        return "Ajuste"
      default:
        return type
    }
  }

  const getMovementColor = (type: string) => {
    switch (type) {
      case "entry":
        return "default"
      case "exit":
        return "destructive"
      case "return":
        return "secondary"
      case "adjustment":
        return "outline"
      default:
        return "default"
    }
  }

  const filteredMovements = movements.filter((movement) => {
    if (typeFilter !== "all" && movement.movement_type !== typeFilter) {
      return false
    }
    return true
  })

  const exportToCSV = () => {
    const headers = [
      "Data",
      "Tipo",
      "Produto",
      "SKU",
      "Quantidade",
      "Custo Unitário",
      "Custo Total",
      "Documento",
      "Fornecedor/Cliente",
    ]
    const csvData = filteredMovements.map((movement) => [
      format(new Date(movement.movement_date), "dd/MM/yyyy"),
      getMovementLabel(movement.movement_type),
      movement.products?.name || "",
      movement.products?.sku || "",
      movement.quantity,
      (movement.unit_cost || 0).toFixed(2),
      (movement.total_cost || 0).toFixed(2),
      movement.document_number || "",
      movement.supplier_customer || "",
    ])

    const csvContent = [headers, ...csvData].map((row) => row.join(",")).join("\n")
    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "relatorio-movimentacoes.csv"
    a.click()
    window.URL.revokeObjectURL(url)
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
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
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

            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setDateRange({ from: subDays(new Date(), 7), to: new Date() })}>
                Últimos 7 dias
              </Button>
              <Button variant="outline" onClick={() => setDateRange({ from: subDays(new Date(), 30), to: new Date() })}>
                Últimos 30 dias
              </Button>
              <Button
                variant="outline"
                onClick={() => setDateRange({ from: startOfMonth(new Date()), to: endOfMonth(new Date()) })}
              >
                Este mês
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Estatísticas principais */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Movimentações</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{movementData.totalMovements}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Entradas</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{movementData.totalEntries}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Saídas</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{movementData.totalExits}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {movementData.totalValue.toFixed(2)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Movimentações Diárias</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={movementData.dailyMovements}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="entries" stroke="#82ca9d" name="Entradas" />
                <Line type="monotone" dataKey="exits" stroke="#8884d8" name="Saídas" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Distribuição por Tipo</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={movementData.typeDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8884d8" name="Quantidade" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Lista de movimentações */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <CardTitle>Lista de Movimentações</CardTitle>
            <div className="flex gap-2">
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filtrar por tipo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os tipos</SelectItem>
                  <SelectItem value="entry">Entradas</SelectItem>
                  <SelectItem value="exit">Saídas</SelectItem>
                  <SelectItem value="return">Devoluções</SelectItem>
                  <SelectItem value="adjustment">Ajustes</SelectItem>
                </SelectContent>
              </Select>

              <Button onClick={exportToCSV} variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Exportar CSV
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Data</th>
                  <th className="text-left p-2">Tipo</th>
                  <th className="text-left p-2">Produto</th>
                  <th className="text-right p-2">Quantidade</th>
                  <th className="text-right p-2">Valor Total</th>
                  <th className="text-left p-2">Documento</th>
                </tr>
              </thead>
              <tbody>
                {filteredMovements.map((movement) => (
                  <tr key={movement.id} className="border-b hover:bg-gray-50">
                    <td className="p-2">{format(new Date(movement.movement_date), "dd/MM/yyyy")}</td>
                    <td className="p-2">
                      <Badge variant={getMovementColor(movement.movement_type) as any}>
                        {getMovementLabel(movement.movement_type)}
                      </Badge>
                    </td>
                    <td className="p-2">
                      <div>
                        <p className="font-medium">{movement.products?.name}</p>
                        <p className="text-xs text-gray-500">{movement.products?.sku}</p>
                      </div>
                    </td>
                    <td className="p-2 text-right">{movement.quantity}</td>
                    <td className="p-2 text-right font-medium">R$ {(movement.total_cost || 0).toFixed(2)}</td>
                    <td className="p-2">
                      {movement.document_number && (
                        <div>
                          <p className="text-xs">{movement.document_number}</p>
                          <p className="text-xs text-gray-500">{movement.supplier_customer}</p>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
