"use client"

import type React from "react"

import { useState } from "react"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { Send } from "lucide-react"

interface InviteUserFormProps {
  onSuccess?: () => void
}

export function InviteUserForm({ onSuccess }: InviteUserFormProps) {
  const [formData, setFormData] = useState({
    email: "",
    fullName: "",
    role: "",
    message: "",
  })
  const [loading, setLoading] = useState(false)
  const supabase = createClient()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Aqui você implementaria a lógica de convite
      // Por exemplo, enviar um email de convite ou criar um registro de convite pendente

      // Simulação de envio de convite
      await new Promise((resolve) => setTimeout(resolve, 1000))

      toast({
        title: "Convite enviado",
        description: `Convite enviado para ${formData.email} com sucesso`,
      })

      // Reset form
      setFormData({
        email: "",
        fullName: "",
        role: "",
        message: "",
      })

      onSuccess?.()
    } catch (error) {
      console.error("Erro ao enviar convite:", error)
      toast({
        title: "Erro",
        description: "Não foi possível enviar o convite",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email *</Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="fullName">Nome Completo *</Label>
          <Input
            id="fullName"
            value={formData.fullName}
            onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
            required
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="role">Perfil de Acesso *</Label>
        <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
          <SelectTrigger>
            <SelectValue placeholder="Selecione o perfil" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="admin">Administrador</SelectItem>
            <SelectItem value="seller">Vendedor</SelectItem>
            <SelectItem value="accountant">Contador</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="message">Mensagem Personalizada</Label>
        <Textarea
          id="message"
          placeholder="Adicione uma mensagem personalizada ao convite (opcional)"
          value={formData.message}
          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
          rows={3}
        />
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={() => onSuccess?.()}>
          Cancelar
        </Button>
        <Button type="submit" disabled={loading || !formData.email || !formData.fullName || !formData.role}>
          <Send className="h-4 w-4 mr-2" />
          {loading ? "Enviando..." : "Enviar Convite"}
        </Button>
      </div>
    </form>
  )
}
