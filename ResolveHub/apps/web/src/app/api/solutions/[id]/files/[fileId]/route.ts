import { privateFileResponse } from "@/features/solutions/server/file-response";
import { localAccessDenied } from "@/features/solutions/server/local-access";
import { getUploadedAttachment } from "@/features/solutions/server/repository";
import { isSafeRecordId } from "@/features/solutions/validation";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string; fileId: string }> },
) {
  const denied = localAccessDenied(request);
  if (denied) return denied;
  const { id, fileId } = await params;
  if (!isSafeRecordId(id) || !isSafeRecordId(fileId)) {
    return Response.json({ error: "Arquivo inválido." }, { status: 400 });
  }

  const stored = await getUploadedAttachment(id, fileId);
  if (!stored) return Response.json({ error: "Arquivo não encontrado." }, { status: 404 });
  return privateFileResponse(new Uint8Array(stored.bytes), {
    filename: stored.attachment.name,
    mimeType: stored.attachment.mimeType,
    preview: stored.attachment.preview,
  });
}
