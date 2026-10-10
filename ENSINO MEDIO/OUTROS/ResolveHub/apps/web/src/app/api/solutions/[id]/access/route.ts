import { localAccessDenied } from "@/features/solutions/server/local-access";
import { incrementSolutionAccess } from "@/features/solutions/server/repository";
import { isSafeRecordId } from "@/features/solutions/validation";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const denied = localAccessDenied(request);
  if (denied) return denied;
  const { id } = await params;
  if (!isSafeRecordId(id)) return Response.json({ error: "Solução inválida." }, { status: 400 });
  return Response.json({ activity: await incrementSolutionAccess(id) });
}
