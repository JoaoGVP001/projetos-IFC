"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Package, TrendingUp, TrendingDown, AlertTriangle, DollarSign, BarChart3, ArrowRight } from "lucide-react"
import Link from "next/link"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

interface DashboardStats {
  totalProducts: number
  lowStockProducts: number
  totalMovements: number
  totalValue: number
}

interface RecentMovement {
  id: string
  movement_type: string
  quantity: number
  movement_date: string
  products: {
    name: string
    sku: string
  }
}

interface LowStockProduct {
  id: string
  name: string
  sku: string
  current_stock: number
  min_stock: number
  unit_of_measure: string
}

export function DashboardOverview() {
  const [stats, setStats] = useState<DashboardStats>({
    totalProducts: 0,
    lowStockProducts: 0,
    totalMovements: 0,
    totalValue: 0,
  })
  const [recentMovements, setRecentMovements] = useState<RecentMovement[]>([])
  const [lowStockProducts, setLowStockProducts] = useState<LowStockProduct[]>([])
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Buscar estatísticas gerais
      const [productsResult, movementsResult, lowStockResult, recentMovementsResult] = await Promise.all([
        supabase.from("products").select("id, current_stock, cost_price").eq("is_active", true),
        supabase.from("inventory_movements").select("id"),
        supabase
          .from("products")
          .select("id, name, sku, current_stock, min_stock, unit_of_measure")
          .eq("is_active", true)
          .lte("current_stock", supabase.rpc("get_min_stock")),
        supabase
          .from("inventory_movements")
          .select(`
            id,
            movement_type,
            quantity,
            movement_date,
            products (
              name,
              sku
            )
          `)
          .order("movement_date", { ascending: false })
          .limit(5),
      ])

      // Calcular estatísticas
      const products = productsResult.data || []
      const totalValue = products.reduce((sum, product) => sum + product.current_stock * product.cost_price, 0)
      const lowStock = products.filter((product) => product.current_stock <= 5) // Simplificado

      setStats({
        totalProducts: products.length,
        lowStockProducts: lowStock.length,
        totalMovements: movementsResult.data?.length || 0,
        totalValue,
      })

      setRecentMovements(recentMovementsResult.data || [])
      setLowStockProducts(lowStock.slice(0, 5) as LowStockProduct[])
    } catch (error) {
      console.error("Erro ao buscar dados do dashboard:", error)
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
      default:
        return <BarChart3 className="h-4 w-4 text-blue-600" />
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

  if (loading) {
    return (
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Visão geral do seu inventário</p>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Produtos</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalProducts}</div>
            <p className="text-xs text-muted-foreground">produtos ativos</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Estoque Baixo</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.lowStockProducts}</div>
            <p className="text-xs text-muted-foreground">produtos com estoque baixo</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Movimentações</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalMovements}</div>
            <p className="text-xs text-muted-foreground">movimentações registradas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {stats.totalValue.toFixed(2)}</div>
            <p className="text-xs text-muted-foreground">valor do estoque</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Movements */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Movimentações Recentes</CardTitle>
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/movements">
                  Ver todas
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {recentMovements.length === 0 ? (
              <p className="text-center text-gray-500 py-4">Nenhuma movimentação recente</p>
            ) : (
              <div className="space-y-4">
                {recentMovements.map((movement) => (
                  <div key={movement.id} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getMovementIcon(movement.movement_type)}
                      <div>
                        <p className="font-medium text-sm">{movement.products?.name}</p>
                        <p className="text-xs text-gray-500">SKU: {movement.products?.sku}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="outline" className="text-xs">
                        {getMovementLabel(movement.movement_type)}
                      </Badge>
                      <p className="text-xs text-gray-500 mt-1">
                        {format(new Date(movement.movement_date), "dd/MM", { locale: ptBR })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Low Stock Products */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                Produtos com Estoque Baixo
              </CardTitle>
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/products">
                  Ver todos
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {lowStockProducts.length === 0 ? (
              <p className="text-center text-gray-500 py-4">Todos os produtos com estoque adequado</p>
            ) : (
              <div className="space-y-4">
                {lowStockProducts.map((product) => (
                  <div key={product.id} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-sm">{product.name}</p>
                      <p className="text-xs text-gray-500">SKU: {product.sku}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-orange-600">
                        {product.current_stock} {product.unit_of_measure}
                      </p>
                      <p className="text-xs text-gray-500">
                        Mín: {product.min_stock} {product.unit_of_measure}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Ações Rápidas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Button asChild className="h-20 flex-col gap-2">
              <Link href="/dashboard/products">
                <Package className="h-6 w-6" />
                Gerenciar Produtos
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-20 flex-col gap-2 bg-transparent">
              <Link href="/dashboard/movements">
                <TrendingUp className="h-6 w-6" />
                Nova Movimentação
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-20 flex-col gap-2 bg-transparent">
              <Link href="/dashboard/reports">
                <BarChart3 className="h-6 w-6" />
                Ver Relatórios
              </Link>
            </Button>
            <Button asChild variant="outline" className="h-20 flex-col gap-2 bg-transparent">
              <Link href="/dashboard/categories">
                <Package className="h-6 w-6" />
                Gerenciar Categorias
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
