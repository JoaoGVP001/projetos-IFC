"use client"

import type React from "react"

import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    const supabase = createClient()
    setIsLoading(true)
    setError(null)

    try {
      console.log("[v0] Tentando fazer login com:", email)

      const { data, error: loginError } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      console.log("[v0] Resposta do login:", { data, error: loginError })

      if (loginError) throw loginError

      if (!data.user) {
        throw new Error("Credenciais inválidas")
      }

      console.log("[v0] Login bem-sucedido, usuário:", data.user.id)

      const { data: profile, error: profileError } = await supabase
        .from("profiles")
        .select("*")
        .eq("id", data.user.id)
        .single()

      console.log("[v0] Perfil encontrado:", { profile, error: profileError })

      if (profileError || !profile) {
        console.error("[v0] Perfil não encontrado:", profileError)
        throw new Error("Perfil do usuário não encontrado. Por favor, entre em contato com o suporte.")
      }

      console.log("[v0] Redirecionando para dashboard")
      router.push("/dashboard")
      router.refresh()
    } catch (error: unknown) {
      console.error("[v0] Erro no login:", error)
      setError(error instanceof Error ? error.message : "Erro ao fazer login")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen w-full items-center justify-center p-6 bg-muted/30">
      <div className="w-full max-w-md">
        <div className="flex flex-col gap-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-primary mb-2">Atena</h1>
            <p className="text-muted-foreground">Bem-vindo de volta!</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Login</CardTitle>
              <CardDescription>Entre com seu email e senha</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleLogin}>
                <div className="flex flex-col gap-6">
                  <div className="grid gap-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="seu@email.com"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="password">Senha</Label>
                    <Input
                      id="password"
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                  {error && <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">{error}</div>}
                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? "Entrando..." : "Entrar"}
                  </Button>
                </div>
                <div className="mt-4 text-center text-sm">
                  Não tem uma conta?{" "}
                  <Link href="/auth/signup" className="text-primary hover:underline font-medium">
                    Cadastre-se
                  </Link>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
