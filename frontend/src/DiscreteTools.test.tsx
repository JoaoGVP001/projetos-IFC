import { afterEach, it, expect, vi } from "vitest";
import {
  cleanup,
  render,
  screen,
  fireEvent,
  waitFor,
} from "@testing-library/react";
import { DiscreteTools, DiscreteCard } from "./DiscreteTools";
import { api } from "./bridge";
vi.mock("./bridge", () => ({ api: vi.fn() }));
afterEach(() => {
  cleanup();
  vi.resetAllMocks();
});
it("exige prévia de dados, invalida ao editar e só calcula por ação explícita", async () => {
  vi.mocked(api).mockImplementation(async (op) =>
    op === "discreta_materiais"
      ? []
      : op === "discreta_validar"
        ? { A: [1, 2, 3], B: [2, 3, 4] }
        : op === "discreta_executar"
          ? { id: "j" }
          : (null as never),
  );
  render(<DiscreteTools chat="c" notify={vi.fn()} onStarted={vi.fn()} />);
  fireEvent.click(screen.getByText("Carregar exemplo de Discreta"));
  expect(screen.queryByText("Calcular e salvar Discreta")).toBeNull();
  fireEvent.click(screen.getByText("Conferir dados interpretados"));
  await waitFor(() =>
    expect(screen.getByText("Calcular e salvar Discreta")).toBeTruthy(),
  );
  expect(
    vi.mocked(api).mock.calls.some(([op]) => op === "discreta_executar"),
  ).toBe(false);
  fireEvent.change(screen.getByLabelText("Conjunto A"), {
    target: { value: "{1}" },
  });
  expect(screen.queryByText("Calcular e salvar Discreta")).toBeNull();
  fireEvent.click(screen.getByText("Conferir dados interpretados"));
  await waitFor(() => screen.getByText("Calcular e salvar Discreta"));
  fireEvent.click(screen.getByText("Calcular e salvar Discreta"));
  await waitFor(() =>
    expect(api).toHaveBeenCalledWith(
      "discreta_executar",
      expect.objectContaining({
        conversa: "c",
        spec: expect.objectContaining({ A: "{1}" }),
      }),
    ),
  );
});
it("alterna lógica e relações entre conjuntos mostrando os campos aplicáveis", () => {
  vi.mocked(api).mockResolvedValue([] as never);
  render(<DiscreteTools chat="c" notify={vi.fn()} onStarted={vi.fn()} />);
  fireEvent.change(screen.getByLabelText("Ferramenta de Discreta"), {
    target: { value: "logica" },
  });
  expect(screen.getByLabelText("Expressão lógica")).toBeTruthy();
  expect(screen.queryByLabelText("Conjunto A")).toBeNull();
  fireEvent.change(screen.getByLabelText("Ferramenta de Discreta"), {
    target: { value: "relacoes" },
  });
  fireEvent.click(
    screen.getByRole("checkbox", {
      name: "Relação sobre A (origem e destino A)",
    }),
  );
  expect(screen.getByLabelText("Conjunto B")).toBeTruthy();
});
it("tabela textual sem PNG não mostra erro de artefato e oferece explicação separada", async () => {
  vi.mocked(api).mockResolvedValue({
    id: "j",
    tipo: "calculo",
    estado: "concluida",
    resumo: "### Tabela-verdade\nExpressões equivalentes: Sim",
    resultado: { png_disponivel: false, resultados: { equivalentes: true } },
  } as never);
  render(<DiscreteCard id="j" chat="c" notify={vi.fn()} />);
  await waitFor(() =>
    expect(screen.getByText(/Tabela\/resultados registrados/)).toBeTruthy(),
  );
  expect(screen.queryByRole("alert")).toBeNull();
  expect(
    (screen.getByText("Exportar diagrama PNG") as HTMLButtonElement).disabled,
  ).toBe(true);
  expect(screen.getByText("Explicar resultados com IA")).toBeTruthy();
  expect(
    screen.getByText("Resultados, definições e contraexemplos"),
  ).toBeTruthy();
  expect(screen.getByText("Expressões equivalentes: Sim")).toBeTruthy();
});
