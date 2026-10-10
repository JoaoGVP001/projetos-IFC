import { z } from "zod";

import { localAccessDenied } from "@/features/solutions/server/local-access";
import { addSolutionHistory } from "@/features/solutions/server/repository";
import { isSafeRecordId } from "@/features/solutions/validation";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const historyInput = z.object({
  outcome: z.enum(["success", "failure"]),
  note: z.string().trim().max(4_000).default(""),
});

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const denied = localAccessDenied(request);
  if (denied) return denied;
  const { id } = await params;
  if (!isSafeRecordId(id)) return Response.json({ error: "Solução inválida." }, { status: 400 });

  try {
    const input = historyInput.parse(await request.json());
    return Response.json(await addSolutionHistory(id, input), { status: 201 });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Registro inválido.";
    return Response.json({ error: message }, { status: 400 });
  }
}
