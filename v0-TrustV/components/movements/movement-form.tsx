"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Calendar } from "@/components/ui/calendar"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { CalendarIcon } from "lucide-react"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"
import { cn } from "@/lib/utils"

interface Product {
  id: string
  name: string
  sku: string
  unit_of_measure: string
  current_stock: number
  cost_price: number
}

interface MovementFormProps {
  onClose: () => void
  onSave: () => void
}

export function MovementForm({ onClose, onSave }: MovementFormProps) {
  const [formData, setFormData] = useState({
    product_id: "",
    movement_type: "entry" as "entry" | "exit" | "return" | "adjustment",
    quantity: 0,
    unit_cost: 0,
    document_number: "",
    document_type: "",
    supplier_customer: "",
    invoice_number: "",
    invoice_date: undefined as Date | undefined,
    movement_date: new Date(),
    cfop: "",
    icms_value: 0,
    ipi_value: 0,
    pis_value: 0,
    cofins_value: 0,
    notes: "",
  })

  const [products, setProducts] = useState<Product[]>([])
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const supabase = createClient()

  useEffect(() => {
    fetchProducts()
  }, [])

  useEffect(() => {
    if (formData.product_id) {
      const product = products.find((p) => p.id === formData.product_id)
      setSelectedProduct(product || null)
      if (product && formData.unit_cost === 0) {
        setFormData((prev) => ({ ...prev, unit_cost: product.cost_price }))
      }
    }
  }, [formData.product_id, products])

  const fetchProducts = async () => {
    try {
      const { data, error } = await supabase
        .from("products")
        .select("id, name, sku, unit_of_measure, current_stock, cost_price")
        .eq("is_active", true)
        .order("name")

      if (error) throw error
      setProducts(data || [])
    } catch (error) {
      console.error("Erro ao buscar produtos:", error)
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.product_id) newErrors.product_id = "Produto é obrigatório"
    if (formData.quantity <= 0) newErrors.quantity = "Quantidade deve ser maior que zero"
    if (formData.unit_cost < 0) newErrors.unit_cost = "Custo unitário deve ser positivo"

    // Validar estoque para saídas
    if (
      (formData.movement_type === "exit" || formData.movement_type === "adjustment") &&
      selectedProduct &&
      formData.quantity > selectedProduct.current_stock
    ) {
      newErrors.quantity = `Estoque insuficiente. Disponível: ${selectedProduct.current_stock}`
    }

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

      const totalCost = formData.quantity * formData.unit_cost

      const movementData = {
        company_id: userCompany.company_id,
        product_id: formData.product_id,
        movement_type: formData.movement_type,
        quantity: formData.quantity,
        unit_cost: formData.unit_cost,
        total_cost: totalCost,
        document_number: formData.document_number || null,
        document_type: formData.document_type || null,
        supplier_customer: formData.supplier_customer || null,
        invoice_number: formData.invoice_number || null,
        invoice_date: formData.invoice_date || null,
        movement_date: formData.movement_date,
        cfop: formData.cfop || null,
        icms_value: formData.icms_value,
        ipi_value: formData.ipi_value,
        pis_value: formData.pis_value,
        cofins_value: formData.cofins_value,
        notes: formData.notes || null,
        created_by: user.id,
      }

      const { error } = await supabase.from("inventory_movements").insert([movementData])

      if (error) throw error

      onSave()
    } catch (error) {
      console.error("Erro ao salvar movimentação:", error)
      setErrors({ submit: "Erro ao salvar movimentação. Tente novamente." })
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

  const totalCost = formData.quantity * formData.unit_cost

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Nova Movimentação de Estoque</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="basic">Informações Básicas</TabsTrigger>
              <TabsTrigger value="document">Documentação</TabsTrigger>
              <TabsTrigger value="fiscal">Informações Fiscais</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="product">Produto *</Label>
                  <Select value={formData.product_id} onValueChange={(value) => handleInputChange("product_id", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione um produto" />
                    </SelectTrigger>
                    <SelectContent>
                      {products.map((product) => (
                        <SelectItem key={product.id} value={product.id}>
                          {product.name} - {product.sku} (Estoque: {product.current_stock} {product.unit_of_measure})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.product_id && <p className="text-sm text-red-600">{errors.product_id}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="movement_type">Tipo de Movimentação *</Label>
                  <Select
                    value={formData.movement_type}
                    onValueChange={(value) => handleInputChange("movement_type", value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="entry">Entrada</SelectItem>
                      <SelectItem value="exit">Saída</SelectItem>
                      <SelectItem value="return">Devolução</SelectItem>
                      <SelectItem value="adjustment">Ajuste</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="quantity">Quantidade *</Label>
                  <Input
                    id="quantity"
                    type="number"
                    step="0.001"
                    min="0"
                    value={formData.quantity}
                    onChange={(e) => handleInputChange("quantity", Number.parseFloat(e.target.value) || 0)}
                  />
                  {errors.quantity && <p className="text-sm text-red-600">{errors.quantity}</p>}
                  {selectedProduct && (
                    <p className="text-xs text-gray-600">
                      Estoque atual: {selectedProduct.current_stock} {selectedProduct.unit_of_measure}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="unit_cost">Custo Unitário (R$)</Label>
                  <Input
                    id="unit_cost"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.unit_cost}
                    onChange={(e) => handleInputChange("unit_cost", Number.parseFloat(e.target.value) || 0)}
                  />
                  {errors.unit_cost && <p className="text-sm text-red-600">{errors.unit_cost}</p>}
                </div>

                <div className="space-y-2">
                  <Label>Custo Total (R$)</Label>
                  <Input value={totalCost.toFixed(2)} disabled className="bg-gray-50" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="movement_date">Data da Movimentação</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          !formData.movement_date && "text-muted-foreground",
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {formData.movement_date ? (
                          format(formData.movement_date, "dd/MM/yyyy", { locale: ptBR })
                        ) : (
                          <span>Selecione uma data</span>
                        )}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={formData.movement_date}
                        onSelect={(date) => handleInputChange("movement_date", date)}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="supplier_customer">Fornecedor/Cliente</Label>
                  <Input
                    id="supplier_customer"
                    value={formData.supplier_customer}
                    onChange={(e) => handleInputChange("supplier_customer", e.target.value)}
                    placeholder="Nome do fornecedor ou cliente"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Observações</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => handleInputChange("notes", e.target.value)}
                  placeholder="Observações sobre a movimentação"
                  rows={3}
                />
              </div>
            </TabsContent>

            <TabsContent value="document" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="document_type">Tipo de Documento</Label>
                  <Select
                    value={formData.document_type}
                    onValueChange={(value) => handleInputChange("document_type", value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="NF">Nota Fiscal</SelectItem>
                      <SelectItem value="NFE">Nota Fiscal Eletrônica</SelectItem>
                      <SelectItem value="CUPOM">Cupom Fiscal</SelectItem>
                      <SelectItem value="RECIBO">Recibo</SelectItem>
                      <SelectItem value="OUTROS">Outros</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="document_number">Número do Documento</Label>
                  <Input
                    id="document_number"
                    value={formData.document_number}
                    onChange={(e) => handleInputChange("document_number", e.target.value)}
                    placeholder="Número do documento"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="invoice_number">Número da Nota Fiscal</Label>
                  <Input
                    id="invoice_number"
                    value={formData.invoice_number}
                    onChange={(e) => handleInputChange("invoice_number", e.target.value)}
                    placeholder="Número da NF"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="invoice_date">Data da Nota Fiscal</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          !formData.invoice_date && "text-muted-foreground",
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {formData.invoice_date ? (
                          format(formData.invoice_date, "dd/MM/yyyy", { locale: ptBR })
                        ) : (
                          <span>Selecione uma data</span>
                        )}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0">
                      <Calendar
                        mode="single"
                        selected={formData.invoice_date}
                        onSelect={(date) => handleInputChange("invoice_date", date)}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="fiscal" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cfop">CFOP</Label>
                <Input
                  id="cfop"
                  value={formData.cfop}
                  onChange={(e) => handleInputChange("cfop", e.target.value)}
                  placeholder="Código CFOP"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="icms_value">Valor ICMS (R$)</Label>
                  <Input
                    id="icms_value"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.icms_value}
                    onChange={(e) => handleInputChange("icms_value", Number.parseFloat(e.target.value) || 0)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ipi_value">Valor IPI (R$)</Label>
                  <Input
                    id="ipi_value"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.ipi_value}
                    onChange={(e) => handleInputChange("ipi_value", Number.parseFloat(e.target.value) || 0)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="pis_value">Valor PIS (R$)</Label>
                  <Input
                    id="pis_value"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.pis_value}
                    onChange={(e) => handleInputChange("pis_value", Number.parseFloat(e.target.value) || 0)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="cofins_value">Valor COFINS (R$)</Label>
                  <Input
                    id="cofins_value"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.cofins_value}
                    onChange={(e) => handleInputChange("cofins_value", Number.parseFloat(e.target.value) || 0)}
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
              {loading ? "Salvando..." : "Registrar Movimentação"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
