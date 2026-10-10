import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-muted/30">
      <div className="container mx-auto px-4 py-16">
        <div className="flex flex-col items-center justify-center min-h-[80vh] gap-8">
          {/* Logo and Title */}
          <div className="text-center space-y-4">
            <h1 className="text-6xl font-bold text-balance text-primary">Atena</h1>
            <p className="text-xl text-muted-foreground text-balance max-w-2xl">
              Aprenda de forma gamificada e conquiste seus objetivos no ENEM
            </p>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6 w-full max-w-4xl mt-8">
            <Card className="border-primary/20">
              <CardContent className="pt-6 text-center space-y-2">
                <div className="text-4xl mb-2">📚</div>
                <h3 className="font-semibold text-lg">Trilhas de Aprendizado</h3>
                <p className="text-sm text-muted-foreground">
                  Matemática, Português e Biologia organizados por tópicos
                </p>
              </CardContent>
            </Card>

            <Card className="border-primary/20">
              <CardContent className="pt-6 text-center space-y-2">
                <div className="text-4xl mb-2">🏆</div>
                <h3 className="font-semibold text-lg">Sistema de Conquistas</h3>
                <p className="text-sm text-muted-foreground">Ganhe XP, suba de nível e desbloqueie badges</p>
              </CardContent>
            </Card>

            <Card className="border-primary/20">
              <CardContent className="pt-6 text-center space-y-2">
                <div className="text-4xl mb-2">⚔️</div>
                <h3 className="font-semibold text-lg">Campeonatos</h3>
                <p className="text-sm text-muted-foreground">Compete com outros estudantes e professores</p>
              </CardContent>
            </Card>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mt-8">
            <Button asChild size="lg" className="text-lg px-8">
              <Link href="/auth/signup">Começar Agora</Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="text-lg px-8 bg-transparent">
              <Link href="/auth/login">Já tenho conta</Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
