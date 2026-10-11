import { afterEach, it, expect, vi } from "vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { MathTools, MathCard } from "./MathTools";
import { api } from "./bridge";
vi.mock("./bridge", () => ({ api: vi.fn() }));
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
const example = {
  expressao: "x^2 - 4*x + 3",
  inicio: "-2",
  fim: "6",
  ponto: "3",
  operacoes: ["grafico", "derivada", "criticos", "tangente"],
};
const job = {
  id: "proposta-1",
  tipo: "proposta",
  estado: "previa",
  mensagem_id: null,
  erro: "",
  previa: {
    destino: "Somente Ollama neste computador",
    aviso: "Sem anexos ou histórico.",
    preparada: { instrucoes: "JSON somente", pergunta: "Pedido explícito" },
  },
};
it("calcula localmente sem consultar IA e informa o intervalo e operações escolhidos", async () => {
  vi.mocked(api).mockResolvedValue({ id: "calc-1" });
  const started = vi.fn();
  render(<MathTools chat="chat-1" onStarted={started} notify={vi.fn()} />);
  fireEvent.click(screen.getByRole("button", { name: "Exemplo da parábola" }));
  fireEvent.click(
    screen.getByRole("button", { name: "Calcular e salvar no chat" }),
  );
  await waitFor(() => expect(started).toHaveBeenCalledOnce());
  expect(api).toHaveBeenCalledExactlyOnceWith("math_executar", {
    conversa: "chat-1",
    spec: example,
  });
});
it("mostra a prévia antes de consultar IA; parâmetros ausentes continuam vazios e nada é calculado", async () => {
  vi.mocked(api).mockImplementation(async (op) => {
    if (op === "math_previa") return job as never;
    if (op === "math_consultar")
      return { ...job, estado: "executando" } as never;
    if (op === "math_obter")
      return {
        ...job,
        estado: "concluida",
        resultado: { ...example, inicio: "", fim: "", ponto: "" },
      } as never;
    throw Error("operação inesperada");
  });
  render(<MathTools chat="chat-1" onStarted={vi.fn()} notify={vi.fn()} />);
  fireEvent.change(screen.getByLabelText("Pedido para IA"), {
    target: { value: "Mostre a derivada da função." },
  });
  fireEvent.click(
    screen.getByRole("button", { name: "Preparar proposta da IA" }),
  );
  await screen.findByText("Somente Ollama neste computador");
  expect(vi.mocked(api).mock.calls.some((c) => c[0] === "math_consultar")).toBe(
    false,
  );
  fireEvent.click(screen.getByRole("button", { name: "Pedir proposta à IA" }));
  await waitFor(
    () =>
      expect(
        (screen.getByLabelText("Função f(x)") as HTMLInputElement).value,
      ).toBe(example.expressao),
    { timeout: 3000 },
  );
  expect(
    (screen.getByLabelText("Início do intervalo") as HTMLInputElement).value,
  ).toBe("");
  expect(
    (screen.getByLabelText("Fim do intervalo") as HTMLInputElement).value,
  ).toBe("");
  expect(vi.mocked(api).mock.calls.some((c) => c[0] === "math_executar")).toBe(
    false,
  );
});
it("reabre proposta persistida e permite exportar gráfico por identificador", async () => {
  vi.mocked(api).mockResolvedValue({
    ...job,
    estado: "concluida",
    resultado: example,
  });
  const first = render(
    <MathTools
      chat="chat-1"
      proposta="proposta-1"
      onStarted={vi.fn()}
      notify={vi.fn()}
    />,
  );
  await waitFor(() =>
    expect((screen.getByLabelText("Ponto x") as HTMLInputElement).value).toBe(
      "3",
    ),
  );
  first.unmount();
  vi.clearAllMocks();
  vi.mocked(api).mockResolvedValue({
    id: "calc-1",
    tipo: "calculo",
    estado: "concluida",
    imagem: "data:image/png;base64,iVBORw0KGgo=",
  });
  render(<MathCard id="calc-1" chat="chat-1" notify={vi.fn()} />);
  await screen.findByRole("img");
  fireEvent.click(screen.getByRole("button", { name: "Exportar PNG" }));
  await waitFor(() =>
    expect(api).toHaveBeenCalledWith("math_exportar", { id: "calc-1" }),
  );
});
