import { afterEach, it, expect, vi } from "vitest";
import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";
import { ConsultedSources } from "./ConsultedSources";
import { api } from "./bridge";
vi.mock("./bridge", () => ({ api: vi.fn() }));
afterEach(() => {
  cleanup();
  vi.resetAllMocks();
});
const source = {
  referencia: "M1",
  nome: "Aula.pdf",
  texto: "Trecho exato: $n>=1$.",
  tipo: "pdf",
  pagina: 2,
  unidade: "página",
  metodo: "Texto parcial",
  aviso: "Figura não interpretada",
  citada: true,
  estado_atual: "atual",
  aviso_atual: "",
  original_disponivel: true,
  envio_exato: true,
};
async function show(f = source, model = true) {
  vi.mocked(api).mockResolvedValue({
    mensagem: 7,
    pergunta: "Confira f(x)=x^2.",
    fontes: [f],
    envio_exato: true,
    aviso: "Citação não verifica a resposta.",
    consulta_modelo: model,
  });
  const onCheck = vi.fn();
  render(
    <ConsultedSources
      mensagem={7}
      editable
      notify={vi.fn()}
      onCheck={onCheck}
    />,
  );
  const details = screen.getByText(
    "Conferir fontes e operações",
  ).parentElement!;
  details.setAttribute("open", "");
  fireEvent(details, new Event("toggle"));
  await waitFor(() =>
    screen.getByText(
      model
        ? "Trecho exato enviado"
        : "Trecho preparado · não enviado ao modelo",
    ),
  );
  return onCheck;
}
it("não chama um snapshot preparado de trecho enviado quando a proteção bloqueou a consulta", async () => {
  await show(source, false);
  expect(screen.queryByText("Trecho exato enviado")).toBeNull();
  expect(screen.getByText(source.texto)).toBeTruthy();
});
it("mostra snapshot, página, aviso e abre a fonte por mensagem/referência", async () => {
  await show();
  expect(screen.getByText(source.texto)).toBeTruthy();
  expect(screen.getByText(/página 2/)).toBeTruthy();
  expect(screen.getByText(/Figura não interpretada/)).toBeTruthy();
  fireEvent.click(screen.getByText("Abrir arquivo original"));
  expect(api).toHaveBeenCalledWith("consulta_original", {
    mensagem: 7,
    referencia: "M1",
  });
});
it("fonte removida conserva texto e desabilita abertura do original", async () => {
  await show({
    ...source,
    estado_atual: "removido",
    original_disponivel: false,
    aviso_atual: "Material removido; trecho histórico preservado.",
  });
  expect(screen.getByText(source.texto)).toBeTruthy();
  expect(
    (screen.getByText("Abrir arquivo original") as HTMLButtonElement).disabled,
  ).toBe(true);
});
it("abre ferramenta explicitamente com vínculo e pedido, sem executar automaticamente", async () => {
  const check = await show();
  fireEvent.click(screen.getByText("Conferir operação de Discreta"));
  expect(check).toHaveBeenCalledWith("discreta", {
    mensagem: 7,
    pedido: "Confira f(x)=x^2.",
  });
  expect(
    vi
      .mocked(api)
      .mock.calls.some(
        ([op]) => op === "discreta_executar" || op === "math_executar",
      ),
  ).toBe(false);
});
