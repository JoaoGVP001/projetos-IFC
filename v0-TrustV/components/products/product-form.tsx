"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface Product {
  id: string
  sku: string
  name: string
  description: string
  unit_of_measure: string
  cost_price: number
  sale_price: number
  current_stock: number
  min_stock: number
  max_stock: number
  is_active: boolean
  category_id: string
  ncm: string
  cfop: string
  icms_rate: number
  ipi_rate: number
  pis_rate: number
  cofins_rate: number
}

interface Category {
  id: string
  name: string
}

interface ProductFormProps {
  product?: Product | null
  onClose: () => void
  onSave: () => void
}

export function ProductForm({ product, onClose, onSave }: ProductFormProps) {
  const [formData, setFormData] = useState({
    sku: "",
    name: "",
    description: "",
    unit_of_measure: "UN",
    cost_price: 0,
    sale_price: 0,
    min_stock: 0,
    max_stock: 0,
    is_active: true,
    category_id: "",
    ncm: "",
    cfop: "",
    icms_rate: 0,
    ipi_rate: 0,
    pis_rate: 0,
    cofins_rate: 0,
  })

  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const supabase = createClient()

  useEffect(() => {
    fetchCategories()

    if (product) {
      setFormData({
        sku: product.sku,
        name: product.name,
        description: product.description || "",
        unit_of_measure: product.unit_of_measure,
        cost_price: product.cost_price,
        sale_price: product.sale_price,
        min_stock: product.min_stock,
        max_stock: product.max_stock || 0,
        is_active: product.is_active,
        category_id: product.category_id || "",
        ncm: product.ncm || "",
        cfop: product.cfop || "",
        icms_rate: product.icms_rate,
        ipi_rate: product.ipi_rate,
        pis_rate: product.pis_rate,
        cofins_rate: product.cofins_rate,
      })
    }
  }, [product])

  const fetchCategories = async () => {
    try {
      const { data, error } = await supabase
        .from("product_categories")
        .select("id, name")
        .eq("is_active", true)
        .order("name")

      if (error) throw error
      setCategories(data || [])
    } catch (error) {
      console.error("Erro ao buscar categorias:", error)
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.sku.trim()) newErrors.sku = "SKU é obrigatório"
    if (!formData.name.trim()) newErrors.name = "Nome é obrigatório"
    if (formData.cost_price < 0) newErrors.cost_price = "Preço de custo deve ser positivo"
    if (formData.sale_price < 0) newErrors.sale_price = "Preço de venda deve ser positivo"
    if (formData.min_stock < 0) newErrors.min_stock = "Estoque mínimo deve ser positivo"

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setLoading(true)

    try {
      const {
        data: { user },
      } = await supabase.auth.getUser()

      if (!user) throw new Error("Usuário não autenticado")

      // Buscar company_id do usuário
      const { data: userCompany } = await supabase
        .from("user_companies")
        .select("company_id")
        .eq("user_id", user.id)
        .single()

      if (!userCompany) throw new Error("Empresa não encontrada")

      const productData = {
        ...formData,
        company_id: userCompany.company_id,
        updated_by: user.id,
        ...(product ? {} : { created_by: user.id }),
      }

      if (product) {
        const { error } = await supabase.from("products").update(productData).eq("id", product.id)

        if (error) throw error
      } else {
        const { error } = await supabase.from("products").insert([productData])

        if (error) throw error
      }

      onSave()
    } catch (error) {
      console.error("Erro ao salvar produto:", error)
      setErrors({ submit: "Erro ao salvar produto. Tente novamente." })
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: "" }))
    }
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{product ? "Editar Produto" : "Novo Produto"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="basic">Informações Básicas</TabsTrigger>
              <TabsTrigger value="pricing">Preços e Estoque</TabsTrigger>
              <TabsTrigger value="fiscal">Informações Fiscais</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="sku">SKU *</Label>
                  <Input
                    id="sku"
                    value={formData.sku}
                    onChange={(e) => handleInputChange("sku", e.target.value)}
                    placeholder="Código do produto"
                  />
                  {errors.sku && <p className="text-sm text-red-600">{errors.sku}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="name">Nome *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                    placeholder="Nome do produto"
                  />
                  {errors.name && <p className="text-sm text-red-600">{errors.name}</p>}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Descrição</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange("description", e.target.value)}
                  placeholder="Descrição detalhada do produto"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="category">Categoria</Label>
                  <Select
                    value={formData.category_id}
                    onValueChange={(value) => handleInputChange("category_id", value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione uma categoria" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="unit">Unidade de Medida</Label>
                  <Select
                    value={formData.unit_of_measure}
                    onValueChange={(value) => handleInputChange("unit_of_measure", value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UN">Unidade</SelectItem>
                      <SelectItem value="KG">Quilograma</SelectItem>
                      <SelectItem value="G">Grama</SelectItem>
                      <SelectItem value="L">Litro</SelectItem>
                      <SelectItem value="ML">Mililitro</SelectItem>
                      <SelectItem value="M">Metro</SelectItem>
                      <SelectItem value="CM">Centímetro</SelectItem>
                      <SelectItem value="M2">Metro Quadrado</SelectItem>
                      <SelectItem value="M3">Metro Cúbico</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="active"
                  checked={formData.is_active}
                  onCheckedChange={(checked) => handleInputChange("is_active", checked)}
                />
                <Label htmlFor="active">Produto ativo</Label>
              </div>
            </TabsContent>

            <TabsContent value="pricing" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="cost_price">Preço de Custo (R$)</Label>
                  <Input
                    id="cost_price"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.cost_price}
                    onChange={(e) => handleInputChange("cost_price", Number.parseFloat(e.target.value) || 0)}
                  />
                  {errors.cost_price && <p className="text-sm text-red-600">{errors.cost_price}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="sale_price">Preço de Venda (R$)</Label>
                  <Input
                    id="sale_price"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.sale_price}
                    onChange={(e) => handleInputChange("sale_price", Number.parseFloat(e.target.value) || 0)}
                  />
                  {errors.sale_price && <p className="text-sm text-red-600">{errors.sale_price}</p>}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="min_stock">Estoque Mínimo</Label>
                  <Input
                    id="min_stock"
                    type="number"
                    step="0.001"
                    min="0"
                    value={formData.min_stock}
                    onChange={(e) => handleInputChange("min_stock", Number.parseFloat(e.target.value) || 0)}
                  />
                  {errors.min_stock && <p className="text-sm text-red-600">{errors.min_stock}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="max_stock">Estoque Máximo</Label>
                  <Input
                    id="max_stock"
                    type="number"
                    step="0.001"
                    min="0"
                    value={formData.max_stock}
                    onChange={(e) => handleInputChange("max_stock", Number.parseFloat(e.target.value) || 0)}
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="fiscal" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="ncm">NCM</Label>
                  <Input
                    id="ncm"
                    value={formData.ncm}
                    onChange={(e) => handleInputChange("ncm", e.target.value)}
                    placeholder="Código NCM"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="cfop">CFOP</Label>
                  <Input
                    id="cfop"
                    value={formData.cfop}
                    onChange={(e) => handleInputChange("cfop", e.target.value)}
                    placeholder="Código CFOP"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="icms_rate">Alíquota ICMS (%)</Label>
                  <Input
                    id="icms_rate"
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={formData.icms_rate}
                    onChange={(e) => handleInputChange("icms_rate", Number.parseFloat(e.target.value) || 0)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ipi_rate">Alíquota IPI (%)</Label>
                  <Input
                    id="ipi_rate"
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={formData.ipi_rate}
                    onChange={(e) => handleInputChange("ipi_rate", Number.parseFloat(e.target.value) || 0)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="pis_rate">Alíquota PIS (%)</Label>
                  <Input
                    id="pis_rate"
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={formData.pis_rate}
                    onChange={(e) => handleInputChange("pis_rate", Number.parseFloat(e.target.value) || 0)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="cofins_rate">Alíquota COFINS (%)</Label>
                  <Input
                    id="cofins_rate"
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                    value={formData.cofins_rate}
                    onChange={(e) => handleInputChange("cofins_rate", Number.parseFloat(e.target.value) || 0)}
                  />
                </div>
              </div>
            </TabsContent>
          </Tabs>

          {errors.submit && <div className="text-sm text-red-600 bg-red-50 p-3 rounded-md">{errors.submit}</div>}

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button type="button" variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Salvando..." : product ? "Atualizar" : "Criar"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
