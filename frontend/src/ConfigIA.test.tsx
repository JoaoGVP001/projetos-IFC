import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ConfigForm } from "./ConfigIA";
import { api } from "./bridge";
import type { Config } from "./model";
vi.mock("./bridge", () => ({ api: vi.fn() }));
afterEach(() => {
  cleanup();
  vi.resetAllMocks();
});
const config: Config = {
  provedor: "gemini",
  modelo: "gemini-teste",
  padrao: "gemini",
  provedores: {
    gemini: { modelo: "gemini-teste", configurada: true },
    openai: { modelo: "openai-teste", configurada: false },
    ollama: {
      modelo: "qwen:4b",
      url: "http://127.0.0.1:11434",
      contexto: 4096,
      timeout: 180,
      configurada: true,
    },
  },
};
describe("Configuração da IA local", () => {
  it("remove a chave do formulário local e salva modelo/perfil por conversa", async () => {
    const save = vi.fn().mockResolvedValue(true);
    render(
      <ConfigForm
        config={config}
        save={save}
        busy={false}
        notify={vi.fn()}
        chat
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /IA local · Ollama/ }));
    expect(screen.queryByText("Chave da API")).toBeNull();
    fireEvent.click(
      screen.getByRole("button", { name: "Salvar configuração" }),
    );
    await waitFor(() =>
      expect(save).toHaveBeenCalledWith({
        provedor: "ollama",
        modelo: "qwen:4b",
        escopo: "chat",
        url: "http://127.0.0.1:11434",
        contexto: 4096,
        timeout: 180,
      }),
    );
  });
  it("diagnostica e mostra modelos sem salvar ou consultar o chat", async () => {
    const save = vi.fn();
    vi.mocked(api).mockResolvedValue({
      versao: "teste",
      modelos: [{ name: "qwen:4b", size: 3000000000 }],
      capacidades: ["completion"],
      carregado: false,
      modelo_disponivel: true,
    });
    render(
      <ConfigForm
        config={config}
        save={save}
        busy={false}
        notify={vi.fn()}
        chat={false}
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /IA local · Ollama/ }));
    fireEvent.click(
      screen.getByRole("button", { name: "Testar conexão e listar modelos" }),
    );
    await waitFor(() =>
      expect(screen.getByRole("status").textContent).toContain(
        "Ollama teste conectado",
      ),
    );
    expect(
      screen.getByRole("option", { name: /qwen:4b · 3.00 GB/ }),
    ).toBeTruthy();
    expect(save).not.toHaveBeenCalled();
    expect(api).toHaveBeenCalledTimes(1);
  });
  it("mantém a configuração online com chave própria", async () => {
    const save = vi.fn().mockResolvedValue(true);
    render(
      <ConfigForm
        config={config}
        save={save}
        busy={false}
        notify={vi.fn()}
        chat={false}
      />,
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Salvar configuração" }),
    );
    await waitFor(() =>
      expect(save).toHaveBeenCalledWith({
        provedor: "gemini",
        modelo: "gemini-teste",
        chave: "",
        escopo: "padrao",
      }),
    );
  });
});
