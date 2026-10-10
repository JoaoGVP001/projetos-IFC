"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"

interface ChampionshipJoinButtonProps {
  championshipId: string
  userId: string
}

export function ChampionshipJoinButton({ championshipId, userId }: ChampionshipJoinButtonProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleJoin = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const supabase = createClient()

      const { error: joinError } = await supabase.from("championship_participants").insert({
        championship_id: championshipId,
        user_id: userId,
        score: 0,
      })

      if (joinError) throw joinError

      router.refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao participar do campeonato")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-2">
      <Button onClick={handleJoin} disabled={isLoading} size="lg" className="w-full">
        {isLoading ? "Entrando..." : "Participar do Campeonato"}
      </Button>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  )
}
