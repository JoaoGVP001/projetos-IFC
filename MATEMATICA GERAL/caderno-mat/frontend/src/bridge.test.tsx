import { afterEach, it, expect, vi } from "vitest";
afterEach(() => {
  delete window.pywebview;
  vi.resetModules();
});
it("serializa chamadas sem perder a fila quando uma falha", async () => {
  const eventos: string[] = [];
  window.pywebview = {
    api: {
      request: vi.fn(async (op) => {
        eventos.push(op);
        await new Promise((r) => setTimeout(r, 10));
        if (op === "falhar") return { ok: false, error: "Falha prevista" };
        return { ok: true, data: op };
      }),
    },
  };
  const { api } = await import("./bridge");
  const resultados = await Promise.allSettled([
    api("primeira"),
    api("falhar"),
    api("terceira"),
  ]);
  expect(eventos).toEqual(["primeira", "falhar", "terceira"]);
  expect(resultados[1].status).toBe("rejected");
  expect(resultados[2]).toEqual({ status: "fulfilled", value: "terceira" });
});
it("aguarda a ponte estar pronta em vez de simular dados", async () => {
  const { api } = await import("./bridge");
  const pedido = api("estado");
  await new Promise((r) => setTimeout(r, 5));
  window.pywebview = {
    api: { request: vi.fn(async () => ({ ok: true, data: { revisao: 1 } })) },
  };
  window.dispatchEvent(new Event("pywebviewready"));
  expect(await pedido).toEqual({ revisao: 1 });
});
it("Qt com API criada ainda espera o canal e o evento de prontidão", async () => {
  const request = vi.fn(async () => ({ ok: true, data: "pronto" }));
  window.pywebview = { platform: "qtwebengine", api: { request } };
  const { api } = await import("./bridge");
  const p = api("estado");
  await new Promise((r) => setTimeout(r, 5));
  expect(request).not.toHaveBeenCalled();
  window.pywebview._QWebChannel = {};
  window.dispatchEvent(new Event("pywebviewready"));
  expect(await p).toBe("pronto");
  expect(request).toHaveBeenCalledTimes(1);
});
it("Qt cujo evento já ocorreu conecta imediatamente pelo canal existente", async () => {
  const request = vi.fn(async () => ({ ok: true, data: "pronto" }));
  window.pywebview = {
    platform: "qtwebengine",
    _QWebChannel: {},
    api: { request },
  };
  const { api } = await import("./bridge");
  expect(await api("estado")).toBe("pronto");
});
