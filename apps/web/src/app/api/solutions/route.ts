import { z } from "zod";

import { localAccessDenied } from "@/features/solutions/server/local-access";
import {
  createUploadedSolution,
  getSolutionSnapshot,
} from "@/features/solutions/server/repository";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const solutionInput = z.object({
  title: z.string().trim().min(3).max(180),
  system: z.enum(["Small Commerce", "ZWeb", "Interno"]),
  procedure: z.string().trim().max(20_000),
});

function errorResponse(error: unknown) {
  const message = error instanceof Error ? error.message : "Não foi possível salvar a solução.";
  return Response.json({ error: message }, { status: 400 });
}

export async function GET(request: Request) {
  const denied = localAccessDenied(request);
  if (denied) return denied;
  return Response.json(await getSolutionSnapshot(), {
    headers: { "Cache-Control": "private, no-store" },
  });
}

export async function POST(request: Request) {
  const denied = localAccessDenied(request);
  if (denied) return denied;

  try {
    const contentLength = Number(request.headers.get("content-length") || 0);
    if (contentLength > 101 * 1024 * 1024) {
      return Response.json({ error: "O envio ultrapassa o limite total de 100 MB." }, { status: 413 });
    }
    const form = await request.formData();
    const input = solutionInput.parse({
      title: form.get("title"),
      system: form.get("system"),
      procedure: form.get("procedure"),
    });
    const files = form.getAll("files").filter((value): value is File => value instanceof File && value.size > 0);
    if (!input.procedure && files.length === 0) {
      return Response.json({ error: "Informe um procedimento ou anexe ao menos um arquivo." }, { status: 400 });
    }
    const solution = await createUploadedSolution({ ...input, files });
    return Response.json({ solution }, { status: 201 });
  } catch (error) {
    return errorResponse(error);
  }
}
