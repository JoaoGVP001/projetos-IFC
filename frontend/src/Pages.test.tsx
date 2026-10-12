import { afterEach, it, expect, vi } from "vitest";
import {
  cleanup,
  render,
  screen,
  fireEvent,
  waitFor,
} from "@testing-library/react";
import { Pages } from "./Pages";
import { api } from "./bridge";
import type { Page, PageContent } from "./pages-model";
import type { Estado } from "./model";
vi.mock("./bridge", () => ({ api: vi.fn() }));
afterEach(() => {
  cleanup();
  vi.resetAllMocks();
  window.cadernoMatPageDraft = null;
  window.cadernoMatFlushPage = undefined;
});
const content: PageContent = {
  titulo: "Derivadas",
  assunto: "Cálculo",
  fundo: "branco",
  secoes: [
    { id: "s1", titulo: "Enunciado", texto: "f(x)=x²", origem: "usuario" },
  ],
};
const state = {
  navegacao: { caderno_id: null },
  cadernos: [],
  revisao: 0,
  pagina: "p",
} as unknown as Estado;
function fixture() {
  let p: Page = {
    id: "p",
    caderno_id: null,
    arquivada: 0,
    editavel: true,
    revisao: 0,
    versao: 0,
    rascunho: structuredClone(content),
    origens: [],
    render: {
      conteudo: structuredClone(content),
      materia: "Geral",
      versao: "rascunho",
      recursos: {},
    },
    versoes: [],
  };
  vi.mocked(api).mockImplementation(async (op, d: any) => {
    if (op === "pagina_obter") return structuredClone(p);
    if (op === "pagina_fontes") return { calculos: [], materiais: [] };
    if (op === "pagina_jobs") return [];
    if (op === "paginas") return { itens: [], total: 0, pagina: 0 };
    if (op === "pagina_rascunho") {
      p = {
        ...p,
        rascunho: structuredClone(d.conteudo),
        revisao: p.revisao + 1,
      };
      return structuredClone(p);
    }
    if (op === "pagina_salvar") {
      p = {
        ...p,
        versao: p.versao + 1,
        versoes: [{ versao: 1, criado: "2026-10-11" }],
      };
      return structuredClone(p);
    }
    return null as never;
  });
  return () => p;
}
it("salva o último caractere antes de criar uma versão, sem substituir o rascunho por dados atrasados", async () => {
  const get = fixture();
  render(<Pages state={state} notify={vi.fn()} seed="p" />);
  await waitFor(() => screen.getByLabelText("Título da página"));
  fireEvent.change(screen.getByLabelText("Título da página"), {
    target: { value: "Derivadas revisadas" },
  });
  fireEvent.click(screen.getByText("Salvar versão"));
  await waitFor(() => expect(get().versao).toBe(1));
  const ops = vi.mocked(api).mock.calls.map(([op]) => op);
  expect(ops.indexOf("pagina_rascunho")).toBeLessThan(
    ops.indexOf("pagina_salvar"),
  );
  expect(get().rascunho.titulo).toBe("Derivadas revisadas");
  expect(window.cadernoMatPageDraft?.revisao).toBe(1);
  expect(screen.getByText("Tudo salvo")).toBeTruthy();
});
it("falha de autosave mantém conteúdo e rascunho recuperável", async () => {
  fixture();
  const normal = vi.mocked(api).getMockImplementation()!;
  const notify = vi.fn();
  vi.mocked(api).mockImplementation((op, d) =>
    op === "pagina_rascunho"
      ? Promise.reject(Error("Falha simulada"))
      : normal(op, d),
  );
  render(<Pages state={state} notify={notify} seed="p" />);
  await waitFor(() => screen.getByLabelText("Conteúdo da seção 1"));
  fireEvent.change(screen.getByLabelText("Conteúdo da seção 1"), {
    target: { value: "Meu último caractere: !" },
  });
  await waitFor(() => expect(notify).toHaveBeenCalledWith("Falha simulada"), {
    timeout: 2000,
  });
  expect(window.cadernoMatPageDraft?.conteudo.secoes[0].texto).toBe(
    "Meu último caractere: !",
  );
  expect(
    (screen.getByLabelText("Conteúdo da seção 1") as HTMLTextAreaElement).value,
  ).toBe("Meu último caractere: !");
});
it("mostra editor de seções e exige versão salva para exportar", async () => {
  fixture();
  render(<Pages state={state} notify={vi.fn()} seed="p" />);
  await waitFor(() => screen.getByLabelText("Título da página"));
  expect(
    (screen.getByText("Gerar PDF e PNG") as HTMLButtonElement).disabled,
  ).toBe(true);
  fireEvent.click(screen.getByText("Adicionar seção"));
  expect(screen.getByLabelText("Conteúdo da seção 2")).toBeTruthy();
  fireEvent.change(screen.getByLabelText("Título da seção 2"), {
    target: { value: "Resumo" },
  });
  fireEvent.click(screen.getByLabelText("Subir seção 2"));
  expect(
    (screen.getByLabelText("Título da seção 1") as HTMLInputElement).value,
  ).toBe("Resumo");
  await window.cadernoMatFlushPage?.();
});
it("organização local é uma prévia explícita sem consultar IA e aplica apenas o trabalho", async () => {
  const get = fixture();
  const normal = vi.mocked(api).getMockImplementation()!;
  vi.mocked(api).mockImplementation(async (op, d: any) => {
    if (op === "pagina_organizar")
      return {
        id: "j",
        tipo: "organizacao",
        estado: "concluida",
        erro: "",
        previa: { destino: "Local", avisos: [] },
        resultado: structuredClone(content),
      } as never;
    if (op === "pagina_aceitar") return get() as never;
    return normal(op, d);
  });
  render(<Pages state={state} notify={vi.fn()} seed="p" />);
  await waitFor(() => screen.getByLabelText("Preservar seção 1"));
  fireEvent.click(screen.getByLabelText("Preservar seção 1"));
  fireEvent.click(screen.getByText("Preparar organização local"));
  await waitFor(() =>
    screen.getByText("Aplicar organização preservando o original"),
  );
  expect(
    screen.getByText("Texto preservado integral · sem renderização"),
  ).toBeTruthy();
  expect(api).toHaveBeenCalledWith("pagina_organizar", {
    id: "p",
    secoes: ["s1"],
    modo: "local",
  });
  expect(
    vi
      .mocked(api)
      .mock.calls.some(
        ([op]) => op === "pagina_consultar" || op === "pagina_aceitar",
      ),
  ).toBe(false);
  fireEvent.click(
    screen.getByText("Aplicar organização preservando o original"),
  );
  await waitFor(() =>
    expect(api).toHaveBeenCalledWith("pagina_aceitar", {
      id: "p",
      trabalho: "j",
    }),
  );
});
it("recusa por IDs é acessível e mantém disponível o fluxo local", async () => {
  fixture();
  const normal = vi.mocked(api).getMockImplementation()!;
  vi.mocked(api).mockImplementation(async (op, d) =>
    op === "pagina_organizar"
      ? ({
          id: "j",
          tipo: "rotulos",
          estado: "erro",
          erro: "IDs fora da ordem obrigatória",
          previa: { destino: "Ollama", avisos: [] },
        } as never)
      : normal(op, d),
  );
  render(<Pages state={state} notify={vi.fn()} seed="p" />);
  await waitFor(() => screen.getByLabelText("Preservar seção 1"));
  fireEvent.click(screen.getByLabelText("Preservar seção 1"));
  fireEvent.click(screen.getByText("Preparar rótulos com IA"));
  await waitFor(() =>
    expect(screen.getByRole("alert").textContent).toContain(
      "ordem obrigatória",
    ),
  );
  expect(
    screen.queryByText("Aplicar organização preservando o original"),
  ).toBeNull();
  expect(
    (screen.getByText("Preparar organização local") as HTMLButtonElement)
      .disabled,
  ).toBe(false);
});
