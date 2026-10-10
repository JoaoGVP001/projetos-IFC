import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default async function AuthErrorPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string; error_description?: string }>
}) {
  const params = await searchParams

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-xl">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-bold text-red-600">Erro de Autenticação</CardTitle>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            {params?.error_description ? (
              <p className="text-sm text-gray-600">{params.error_description}</p>
            ) : params?.error ? (
              <p className="text-sm text-gray-600">Código do erro: {params.error}</p>
            ) : (
              <p className="text-sm text-gray-600">Ocorreu um erro não especificado durante a autenticação.</p>
            )}
            <div className="pt-4">
              <Button asChild className="w-full">
                <Link href="/auth/login">Tentar Novamente</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
