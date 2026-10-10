export function localAccessDenied(request: Request) {
  const requestUrl = new URL(request.url);
  const remoteEnabled = process.env.RESOLVEHUB_ALLOW_REMOTE_UPLOADS === "true";
  const isLocal = ["localhost", "127.0.0.1", "::1"].includes(requestUrl.hostname);

  if (!remoteEnabled && !isLocal) {
    return Response.json(
      { error: "Uploads e arquivos privados estão disponíveis somente no ambiente local até a autenticação ser ativada." },
      { status: 403 },
    );
  }

  if (request.headers.get("sec-fetch-site") === "cross-site") {
    return Response.json({ error: "Acesso cruzado a arquivos privados não autorizado." }, { status: 403 });
  }

  if (request.method !== "GET" && request.method !== "HEAD") {
    const origin = request.headers.get("origin");
    if (origin && origin !== requestUrl.origin) {
      return Response.json({ error: "Origem da solicitação não autorizada." }, { status: 403 });
    }
  }

  return null;
}
