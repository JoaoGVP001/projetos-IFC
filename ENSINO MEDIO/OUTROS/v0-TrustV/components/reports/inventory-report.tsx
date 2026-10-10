"use client"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Download, Package, AlertTriangle, TrendingUp } from "lucide-react"
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Pie,
  PieChart,
  Cell,
} from "recharts"

interface InventoryData {
  totalProducts: number
  totalValue: number
  lowStockCount: number
  outOfStockCount: number
  categoryData: Array<{
    name: string
    count: number
    value: number
  }>
  stockLevels: Array<{
    name: string
    current: number
    minimum: number
  }>
}

interface Product {
  id: string
  name: string
  sku: string
  current_stock: number
  min_stock: number
  cost_price: number
  sale_price: number
  unit_of_measure: string
  is_active: boolean
  product_categories?: {
    name: string
  }
}

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"]

export function InventoryReport() {
  const [inventoryData, setInventoryData] = useState<InventoryData>({
    totalProducts: 0,
    totalValue: 0,
    lowStockCount: 0,
    outOfStockCount: 0,
    categoryData: [],
    stockLevels: [],
  })
  const [products, setProducts] = useState<Product[]>([])
  const [categoryFilter, setCategoryFilter] = useState("all")
  const [stockFilter, setStockFilter] = useState("all")
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    fetchInventoryData()
  }, [])

  const fetchInventoryData = async () => {
    try {
      const { data: productsData, error } = await supabase
        .from("products")
        .select(`
          *,
          product_categories (
            name
          )
        `)
        .eq("is_active", true)

      if (error) throw error

      const products = productsData || []
      setProducts(products)

      // Calcular estatísticas
      const totalValue = products.reduce((sum, product) => sum + product.current_stock * product.cost_price, 0)
      const lowStockCount = products.filter((p) => p.current_stock <= p.min_stock && p.current_stock > 0).length
      const outOfStockCount = products.filter((p) => p.current_stock <= 0).length

      // Dados por categoria
      const categoryMap = new Map()
      products.forEach((product) => {
        const categoryName = product.product_categories?.name || "Sem categoria"
        if (!categoryMap.has(categoryName)) {
          categoryMap.set(categoryName, { count: 0, value: 0 })
        }
        const category = categoryMap.get(categoryName)
        category.count += 1
        category.value += product.current_stock * product.cost_price
      })

      const categoryData = Array.from(categoryMap.entries()).map(([name, data]) => ({
        name,
        count: data.count,
        value: data.value,
      }))

      // Níveis de estoque para gráfico
      const stockLevels = products.slice(0, 10).map((product) => ({
        name: product.name.length > 15 ? product.name.substring(0, 15) + "..." : product.name,
        current: product.current_stock,
        minimum: product.min_stock,
      }))

      setInventoryData({
        totalProducts: products.length,
        totalValue,
        lowStockCount,
        outOfStockCount,
        categoryData,
        stockLevels,
      })
    } catch (error) {
      console.error("Erro ao buscar dados de inventário:", error)
    } finally {
      setLoading(false)
    }
  }

  const filteredProducts = products.filter((product) => {
    if (categoryFilter !== "all" && product.product_categories?.name !== categoryFilter) {
      return false
    }

    if (stockFilter === "low" && product.current_stock > product.min_stock) {
      return false
    }

    if (stockFilter === "out" && product.current_stock > 0) {
      return false
    }

    return true
  })

  const getStockStatus = (current: number, min: number) => {
    if (current <= 0) return { label: "Sem estoque", color: "destructive" }
    if (current <= min) return { label: "Estoque baixo", color: "secondary" }
    return { label: "Normal", color: "default" }
  }

  const exportToCSV = () => {
    const headers = [
      "SKU",
      "Nome",
      "Categoria",
      "Estoque Atual",
      "Estoque Mínimo",
      "Unidade",
      "Preço Custo",
      "Preço Venda",
      "Valor Total",
    ]
    const csvData = filteredProducts.map((product) => [
      product.sku,
      product.name,
      product.product_categories?.name || "Sem categoria",
      product.current_stock,
      product.min_stock,
      product.unit_of_measure,
      product.cost_price.toFixed(2),
      product.sale_price.toFixed(2),
      (product.current_stock * product.cost_price).toFixed(2),
    ])

    const csvContent = [headers, ...csvData].map((row) => row.join(",")).join("\n")
    const blob = new Blob([csvContent], { type: "text/csv" })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "relatorio-estoque.csv"
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
      {/* Estatísticas principais */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Produtos</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{inventoryData.totalProducts}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {inventoryData.totalValue.toFixed(2)}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Estoque Baixo</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{inventoryData.lowStockCount}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sem Estoque</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{inventoryData.outOfStockCount}</div>
          </CardContent>
        </Card>
      </div>

      {/* Gráficos */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Produtos por Categoria</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={inventoryData.categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {inventoryData.categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Níveis de Estoque</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={inventoryData.stockLevels}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="current" fill="#8884d8" name="Estoque Atual" />
                <Bar dataKey="minimum" fill="#82ca9d" name="Estoque Mínimo" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Filtros e lista de produtos */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <CardTitle>Lista de Produtos</CardTitle>
            <div className="flex gap-2">
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filtrar por categoria" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas as categorias</SelectItem>
                  {Array.from(new Set(products.map((p) => p.product_categories?.name).filter(Boolean))).map(
                    (category) => (
                      <SelectItem key={category} value={category!}>
                        {category}
                      </SelectItem>
                    ),
                  )}
                </SelectContent>
              </Select>

              <Select value={stockFilter} onValueChange={setStockFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Filtrar por estoque" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos os produtos</SelectItem>
                  <SelectItem value="low">Estoque baixo</SelectItem>
                  <SelectItem value="out">Sem estoque</SelectItem>
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
                  <th className="text-left p-2">SKU</th>
                  <th className="text-left p-2">Nome</th>
                  <th className="text-left p-2">Categoria</th>
                  <th className="text-right p-2">Estoque</th>
                  <th className="text-right p-2">Valor Unit.</th>
                  <th className="text-right p-2">Valor Total</th>
                  <th className="text-center p-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.map((product) => {
                  const stockStatus = getStockStatus(product.current_stock, product.min_stock)
                  const totalValue = product.current_stock * product.cost_price

                  return (
                    <tr key={product.id} className="border-b hover:bg-gray-50">
                      <td className="p-2 font-mono text-xs">{product.sku}</td>
                      <td className="p-2">{product.name}</td>
                      <td className="p-2 text-gray-600">{product.product_categories?.name || "Sem categoria"}</td>
                      <td className="p-2 text-right">
                        {product.current_stock} {product.unit_of_measure}
                      </td>
                      <td className="p-2 text-right">R$ {product.cost_price.toFixed(2)}</td>
                      <td className="p-2 text-right font-medium">R$ {totalValue.toFixed(2)}</td>
                      <td className="p-2 text-center">
                        <Badge variant={stockStatus.color as any}>{stockStatus.label}</Badge>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
