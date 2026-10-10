"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import Link from "next/link"

interface ChampionshipFormProps {
  userId: string
}

export function ChampionshipForm({ userId }: ChampionshipFormProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [subject, setSubject] = useState<
    | "math"
    | "portuguese"
    | "biology"
    | "physics"
    | "chemistry"
    | "history"
    | "geography"
    | "philosophy"
    | "sociology"
    | "english"
  >("math")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [maxParticipants, setMaxParticipants] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    // Validation
    if (!title || !startDate || !endDate) {
      setError("Preencha todos os campos obrigatórios")
      setIsLoading(false)
      return
    }

    const start = new Date(startDate)
    const end = new Date(endDate)
    const now = new Date()

    if (start < now) {
      setError("A data de início deve ser futura")
      setIsLoading(false)
      return
    }

    if (end <= start) {
      setError("A data de término deve ser posterior à data de início")
      setIsLoading(false)
      return
    }

    try {
      const supabase = createClient()

      // Determine status based on start date
      const status = start <= now ? "active" : "upcoming"

      const { error: championshipError } = await supabase.from("championships").insert({
        title,
        description: description || null,
        created_by: userId,
        subject,
        start_date: start.toISOString(),
        end_date: end.toISOString(),
        status,
        max_participants: maxParticipants ? Number.parseInt(maxParticipants) : null,
      })

      if (championshipError) throw championshipError

      router.push("/teacher/championships")
      router.refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar campeonato")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Informações do Campeonato</CardTitle>
          <CardDescription>Preencha os dados do campeonato</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="title">Título do Campeonato</Label>
            <Input
              id="title"
              placeholder="Ex: Desafio de Matemática ENEM 2025"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Descrição</Label>
            <Textarea
              id="description"
              placeholder="Descreva o campeonato e suas regras..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="subject">Matéria</Label>
            <Select value={subject} onValueChange={(value: any) => setSubject(value)}>
              <SelectTrigger id="subject">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="math">Matemática</SelectItem>
                <SelectItem value="portuguese">Português</SelectItem>
                <SelectItem value="biology">Biologia</SelectItem>
                <SelectItem value="physics">Física</SelectItem>
                <SelectItem value="chemistry">Química</SelectItem>
                <SelectItem value="history">História</SelectItem>
                <SelectItem value="geography">Geografia</SelectItem>
                <SelectItem value="philosophy">Filosofia</SelectItem>
                <SelectItem value="sociology">Sociologia</SelectItem>
                <SelectItem value="english">Inglês</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start-date">Data de Início</Label>
              <Input
                id="start-date"
                type="datetime-local"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                min={new Date().toISOString().slice(0, 16)}
                required
                className="block"
              />
              <p className="text-xs text-muted-foreground">Selecione data e hora de início</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="end-date">Data de Término</Label>
              <Input
                id="end-date"
                type="datetime-local"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                min={startDate || new Date().toISOString().slice(0, 16)}
                required
                className="block"
              />
              <p className="text-xs text-muted-foreground">Selecione data e hora de término</p>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="max-participants">Máximo de Participantes (Opcional)</Label>
            <Input
              id="max-participants"
              type="number"
              min="2"
              step="1"
              placeholder="Deixe em branco para ilimitado"
              value={maxParticipants}
              onChange={(e) => setMaxParticipants(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">Mínimo de 2 participantes se definido</p>
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
          {isLoading ? "Criando..." : "Criar Campeonato"}
        </Button>
        <Button asChild type="button" variant="outline" size="lg">
          <Link href="/teacher/championships">Cancelar</Link>
        </Button>
      </div>
    </form>
  )
}
