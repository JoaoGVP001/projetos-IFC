"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, TrendingDown, RotateCcw, Settings } from "lucide-react"
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
  notes: string
  movement_date: string
  created_at: string
  user_profiles: {
    full_name: string
  }
}

interface ProductMovementsProps {
  productId: string
}

export function ProductMovements({ productId }: ProductMovementsProps) {
  const [movements, setMovements] = useState<Movement[]>([])
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    fetchMovements()
  }, [productId])

  const fetchMovements = async () => {
    try {
      const { data, error } = await supabase
        .from("inventory_movements")
        .select(`
          *,
          user_profiles!inventory_movements_created_by_fkey (
            full_name
          )
        `)
        .eq("product_id", productId)
        .order("movement_date", { ascending: false })

      if (error) throw error
      setMovements(data || [])
    } catch (error) {
      console.error("Erro ao buscar movimentações:", error)
    } finally {
      setLoading(false)
    }
  }

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
        return null
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

  if (movements.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <TrendingUp className="h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma movimentação encontrada</h3>
          <p className="text-gray-600 text-center">Este produto ainda não possui movimentações registradas.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {movements.map((movement) => (
        <Card key={movement.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getMovementIcon(movement.movement_type)}
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{getMovementLabel(movement.movement_type)}</h3>
                    <Badge variant={getMovementColor(movement.movement_type) as any}>
                      {movement.movement_type === "exit" ? "-" : "+"}
                      {movement.quantity}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">
                    {format(new Date(movement.movement_date), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                  </p>
                </div>
              </div>

              <div className="text-right">
                <p className="font-medium">R$ {movement.total_cost?.toFixed(2) || "0,00"}</p>
                <p className="text-sm text-gray-600">R$ {movement.unit_cost?.toFixed(2) || "0,00"} / unidade</p>
              </div>
            </div>

            {(movement.supplier_customer || movement.document_number || movement.notes) && (
              <div className="mt-4 pt-4 border-t space-y-2">
                {movement.supplier_customer && (
                  <p className="text-sm">
                    <span className="text-gray-600">Fornecedor/Cliente:</span> {movement.supplier_customer}
                  </p>
                )}
                {movement.document_number && (
                  <p className="text-sm">
                    <span className="text-gray-600">Documento:</span> {movement.document_type}{" "}
                    {movement.document_number}
                  </p>
                )}
                {movement.notes && (
                  <p className="text-sm">
                    <span className="text-gray-600">Observações:</span> {movement.notes}
                  </p>
                )}
              </div>
            )}

            <div className="mt-4 pt-4 border-t">
              <p className="text-xs text-gray-500">
                Registrado por {movement.user_profiles?.full_name} em{" "}
                {format(new Date(movement.created_at), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
              </p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
