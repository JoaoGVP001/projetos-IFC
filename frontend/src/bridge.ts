declare global {
  interface Window {
    pywebview?: {
      api: {
        request: (
          op: string,
          args: Record<string, unknown>,
        ) => Promise<{ ok: boolean; data?: unknown; error?: string }>;
      };
    };
    cadernoMatDraft?: { id: string; texto: string } | null;
  }
}
let fila: Promise<unknown> = Promise.resolve();
async function conectar() {
  if (window.pywebview?.api) return;
  await new Promise<void>((resolve, reject) => {
    const timer = setTimeout(() => {
      window.removeEventListener("pywebviewready", pronto);
      reject(
        new Error(
          "A conexão com o Python não iniciou. Abra pelo atalho CadernoMat.",
        ),
      );
    }, 15000);
    function pronto() {
      clearTimeout(timer);
      resolve();
    }
    window.addEventListener("pywebviewready", pronto, { once: true });
  });
}
export function api<T = unknown>(
  op: string,
  args: Record<string, unknown> = {},
): Promise<T> {
  const resultado = fila
    .catch(() => undefined)
    .then(async () => {
      await conectar();
      const r = await window.pywebview!.api.request(op, args);
      if (!r.ok) throw new Error(r.error || "Não foi possível concluir.");
      return r.data as T;
    });
  fila = resultado;
  return resultado;
}
