"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import Link from "next/link"

interface ClassFormProps {
  userId: string
}

export function ClassForm({ userId }: ClassFormProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [maxStudents, setMaxStudents] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    if (!name.trim()) {
      setError("O nome da turma é obrigatório")
      setIsLoading(false)
      return
    }

    try {
      const supabase = createClient()

      // Generate access code
      const { data: accessCodeData, error: accessCodeError } = await supabase.rpc("generate_class_access_code")

      if (accessCodeError) throw accessCodeError

      // Create class
      const { error: classError } = await supabase.from("classes").insert({
        name: name.trim(),
        description: description.trim() || null,
        teacher_id: userId,
        access_code: accessCodeData,
        max_students: maxStudents ? Number.parseInt(maxStudents) : null,
      })

      if (classError) throw classError

      router.push("/teacher/classes")
      router.refresh()
    } catch (err) {
      console.error("[v0] Error creating class:", err)
      setError(err instanceof Error ? err.message : "Erro ao criar turma")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Informações da Turma</CardTitle>
          <CardDescription>Preencha os dados básicos da turma</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name">Nome da Turma</Label>
            <Input
              id="name"
              placeholder="Ex: 3º Ano A - Manhã"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Descrição (Opcional)</Label>
            <Textarea
              id="description"
              placeholder="Descreva a turma, horários, objetivos..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="max-students">Máximo de Alunos (Opcional)</Label>
            <Input
              id="max-students"
              type="number"
              min="1"
              step="1"
              placeholder="Deixe em branco para ilimitado"
              value={maxStudents}
              onChange={(e) => setMaxStudents(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">Defina um limite de alunos para a turma</p>
          </div>

          <div className="p-4 bg-muted rounded-lg">
            <p className="text-sm text-muted-foreground">
              <strong>Código de Acesso:</strong> Será gerado automaticamente após criar a turma. Os alunos usarão este
              código para entrar na turma.
            </p>
          </div>
        </CardContent>
      </Card>

      {error && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
          {error}
        </div>
      )}

      <div className="flex gap-4">
        <Button type="submit" size="lg" disabled={isLoading} className="flex-1">
          {isLoading ? "Criando..." : "Criar Turma"}
        </Button>
        <Button asChild type="button" variant="outline" size="lg">
          <Link href="/teacher/classes">Cancelar</Link>
        </Button>
      </div>
    </form>
  )
}
