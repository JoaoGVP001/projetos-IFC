import { afterEach, it, expect, vi } from "vitest";
import {
  cleanup,
  render,
  screen,
  fireEvent,
  waitFor,
} from "@testing-library/react";
import { ResponseStatus, Adjustment } from "./LocalStudy";
import { Markdown } from "./Markdown";
import type { Mensagem } from "./model";
afterEach(cleanup);
it("mostra proteção local sem inventar execução e mantém rascunho recusado em texto simples", () => {
  const m = {
    texto: "Aviso seguro.",
    estado: "erro",
    metricas: {
      consulta_modelo: false,
      qualidade: {
        estado: "recusada",
        titulo: "Resposta retida",
        aviso: "Citação alterada.",
        verificacao_matematica: "não realizada",
        rascunho_recusado: "<script>roubar()</script> $2+2=5$",
      },
    },
  } as Mensagem;
  render(<ResponseStatus m={m} />);
  expect(screen.getByText("Resposta retida")).toBeTruthy();
  expect(screen.getByText(/nenhuma chamada ao modelo/)).toBeTruthy();
  expect(screen.getByText(/Verificação matemática/)).toBeTruthy();
  expect(screen.queryByText("Detalhes da execução")).toBeNull();
  const pre = screen.getByText("<script>roubar()</script> $2+2=5$");
  expect(pre.tagName).toBe("PRE");
  expect(pre.querySelector("script")).toBeNull();
});
it("mantém aviso fora do código truncado e distingue falta de métricas de zero", () => {
  const m = {
    texto: "```mermaid\nA-->B",
    estado: "incompleta",
    modelo: "4b",
    interrupcao: {
      motivo: "limite_saida",
      mensagem: "Limite de saída atingido.",
    },
    metricas: {
      tokens_saida: 1024,
      num_predict: 1024,
      segundos: 164,
      done_reason: "length",
    },
  } as Mensagem;
  render(
    <>
      <Markdown texto={m.texto} />
      <ResponseStatus m={m} />
    </>,
  );
  expect(screen.getByRole("status").querySelector("code")).toBeNull();
  expect(screen.getByText("Limite de saída atingido.")).toBeTruthy();
  expect(screen.getByText(/Velocidade indisponível/)).toBeTruthy();
  expect(screen.getByText(/saída 1024\/1024 tokens/)).toBeTruthy();
});
it("prévia aguarda ação e permite tentar novamente se o envio falhar", async () => {
  const send = vi.fn().mockResolvedValue(false);
  render(
    <Adjustment
      data={{
        id: "p",
        acao: "continuar",
        provedor: "ollama",
        modelo: "4b",
        pergunta: "Dados selecionados",
        instrucoes: "Instruções",
        fontes: null,
        orcamento: null,
        origem: 1,
      }}
      onSend={send}
    />,
  );
  expect(send).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText("Enviar esta parte"));
  await waitFor(() =>
    expect(
      (screen.getByText("Enviar esta parte") as HTMLButtonElement).disabled,
    ).toBe(false),
  );
  fireEvent.click(screen.getByText("Enviar esta parte"));
  expect(send).toHaveBeenCalledTimes(2);
});
