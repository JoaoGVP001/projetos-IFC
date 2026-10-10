"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Plus, Search, TrendingUp, TrendingDown, RotateCcw, Settings, FileText } from "lucide-react"
import { MovementForm } from "./movement-form"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

interface Movement {
  id: string
  movement_type: "entry" | "exit" | "return" | "adjustment"
  quantity: number
  unit_cost: number
  total_cost: number
  document_number: string
  document_type: string
  supplier_customer: string
  invoice_number: string
  invoice_date: string
  notes: string
  movement_date: string
  created_at: string
  products: {
    name: string
    sku: string
    unit_of_measure: string
  }
  user_profiles: {
    full_name: string
  }
}

export function MovementsList() {
  const [movements, setMovements] = useState<Movement[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [typeFilter, setTypeFilter] = useState("all")
  const [showForm, setShowForm] = useState(false)
  const supabase = createClient()

  useEffect(() => {
    fetchMovements()
  }, [])

  const fetchMovements = async () => {
    try {
      const { data, error } = await supabase
        .from("inventory_movements")
        .select(`
          *,
          products (
            name,
            sku,
            unit_of_measure
          ),
          user_profiles!inventory_movements_created_by_fkey (
            full_name
          )
        `)
        .order("movement_date", { ascending: false })

      if (error) throw error
      setMovements(data || [])
    } catch (error) {
      console.error("Erro ao buscar movimentações:", error)
    } finally {
      setLoading(false)
    }
  }

  const filteredMovements = movements.filter((movement) => {
    const matchesSearch =
      movement.products?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      movement.products?.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
      movement.supplier_customer?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      movement.document_number?.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesType = typeFilter === "all" || movement.movement_type === typeFilter

    return matchesSearch && matchesType
  })

  const getMovementIcon = (type: string) => {
    switch (type) {
      case "entry":
        return <TrendingUp className="h-4 w-4 text-green-600" />
      case "exit":
        return <TrendingDown className="h-4 w-4 text-red-600" />
      case "return":
        return <RotateCcw className="h-4 w-4 text-blue-600" />
      case "adjustment":
        return <Settings className="h-4 w-4 text-orange-600" />
      default:
        return <FileText className="h-4 w-4" />
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filtros e busca */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex flex-col sm:flex-row gap-4 flex-1">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Buscar movimentações..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-full sm:w-48">
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
        </div>
        <Button onClick={() => setShowForm(true)} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Nova Movimentação
        </Button>
      </div>

      {/* Lista de movimentações */}
      {filteredMovements.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma movimentação encontrada</h3>
            <p className="text-gray-600 text-center mb-4">
              {searchTerm || typeFilter !== "all"
                ? "Tente ajustar os filtros de busca"
                : "Comece registrando sua primeira movimentação"}
            </p>
            {!searchTerm && typeFilter === "all" && (
              <Button onClick={() => setShowForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Registrar Movimentação
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredMovements.map((movement) => (
            <Card key={movement.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-center gap-3">
                      {getMovementIcon(movement.movement_type)}
                      <div>
                        <h3 className="font-semibold text-lg">{movement.products?.name}</h3>
                        <p className="text-sm text-gray-600">SKU: {movement.products?.sku}</p>
                      </div>
                      <Badge variant={getMovementColor(movement.movement_type) as any}>
                        {getMovementLabel(movement.movement_type)}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Quantidade</p>
                        <p className="font-medium">
                          {movement.movement_type === "exit" ? "-" : "+"}
                          {movement.quantity} {movement.products?.unit_of_measure}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-600">Custo Unitário</p>
                        <p className="font-medium">R$ {movement.unit_cost?.toFixed(2) || "0,00"}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Custo Total</p>
                        <p className="font-medium">R$ {movement.total_cost?.toFixed(2) || "0,00"}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Data</p>
                        <p className="font-medium">
                          {format(new Date(movement.movement_date), "dd/MM/yyyy", { locale: ptBR })}
                        </p>
                      </div>
                    </div>

                    {(movement.supplier_customer || movement.document_number) && (
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-sm">
                        {movement.supplier_customer && (
                          <div>
                            <p className="text-gray-600">Fornecedor/Cliente</p>
                            <p className="font-medium">{movement.supplier_customer}</p>
                          </div>
                        )}
                        {movement.document_number && (
                          <div>
                            <p className="text-gray-600">Documento</p>
                            <p className="font-medium">
                              {movement.document_type} {movement.document_number}
                            </p>
                          </div>
                        )}
                      </div>
                    )}

                    {movement.notes && (
                      <div>
                        <p className="text-gray-600 text-sm">Observações</p>
                        <p className="text-sm">{movement.notes}</p>
                      </div>
                    )}
                  </div>

                  <div className="text-right text-sm text-gray-600">
                    <p>Registrado por</p>
                    <p className="font-medium">{movement.user_profiles?.full_name}</p>
                    <p className="text-xs">
                      {format(new Date(movement.created_at), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Modal do formulário */}
      {showForm && (
        <MovementForm
          onClose={() => setShowForm(false)}
          onSave={() => {
            fetchMovements()
            setShowForm(false)
          }}
        />
      )}
    </div>
  )
}
