import { privateFileResponse } from "@/features/solutions/server/file-response";
import { getHelpArchiveFile } from "@/features/solutions/server/help-archive";
import { localAccessDenied } from "@/features/solutions/server/local-access";
import { isSafeRecordId } from "@/features/solutions/validation";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const denied = localAccessDenied(request);
  if (denied) return denied;
  const { id } = await params;
  if (!isSafeRecordId(id)) return Response.json({ error: "Fonte inválida." }, { status: 400 });

  try {
    const file = await getHelpArchiveFile(id);
    if (!file) return Response.json({ error: "Esta fonte está bloqueada ou não possui arquivo local." }, { status: 403 });
    return privateFileResponse(file.bytes, file);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Não foi possível abrir o arquivo.";
    return Response.json({ error: message }, { status: 404 });
  }
}
