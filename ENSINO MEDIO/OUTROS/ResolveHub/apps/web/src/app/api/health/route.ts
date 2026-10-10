export async function GET() {
  return Response.json({
    status: "ok",
    service: "resolvehub-web",
    timestamp: new Date().toISOString(),
  });
}
