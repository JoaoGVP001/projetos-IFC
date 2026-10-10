import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function SignUpSuccessPage() {
  return (
    <div className="flex min-h-screen w-full items-center justify-center p-6 bg-muted/30">
      <div className="w-full max-w-md">
        <div className="flex flex-col gap-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-primary mb-2">Atena</h1>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Conta Criada com Sucesso!</CardTitle>
              <CardDescription>Você já pode fazer login</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center py-6">
                <div className="text-6xl mb-4">✅</div>
                <p className="text-muted-foreground">
                  Sua conta foi criada com sucesso! Clique no botão abaixo para fazer login e começar sua jornada de
                  aprendizado.
                </p>
              </div>
              <Button asChild className="w-full">
                <Link href="/auth/login">Ir para Login</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
