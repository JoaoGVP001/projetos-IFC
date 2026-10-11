import { afterEach, describe, it, expect, vi } from "vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  act,
} from "@testing-library/react";
import { Practice } from "./Activities";
import type { Tentativa } from "./activities-model";
import { api } from "./bridge";
vi.mock("./bridge", () => ({ api: vi.fn() }));
function tentativa(formato = "aberta"): Tentativa {
  return {
    id: "t",
    atividade_id: "a",
    versao: 1,
    versao_atual: 1,
    inicio: "2026-10-11 12:00:00",
    fim: null,
    estado: "andamento",
    posicao: 0,
    editavel: true,
    snapshot: {
      caderno: "Geral",
      fontes: [],
      conteudo: {
        titulo: "Lista teste",
        descricao: "",
        objetivo: "Praticar",
        assuntos: "Funções",
        etiquetas: "",
        dificuldade: "basica",
        exercicios: [
          {
            id: "q",
            enunciado: "Calcule $x^2$.",
            formato: formato as "aberta",
            assunto: "",
            dificuldade: "basica",
            alternativas: [],
            referencias: [],
            tolerancia: "0.01",
            solucao_disponivel: true,
          },
        ],
      },
    },
    respostas: {},
    resultado: {},
    resumo: {
      total: 1,
      respondidas: 0,
      objetivas: 0,
      acertos: 0,
      erros: 0,
      nao_avaliadas: 1,
      dicas: 0,
      solucoes: 0,
    },
  };
}
const props = {
  onUpdate: vi.fn(),
  notify: vi.fn(),
  busy: false,
  onBack: vi.fn(),
  onAI: vi.fn(),
  onChat: vi.fn(),
};
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  vi.useRealTimers();
  delete window.cadernoMatStudyDraft;
  delete window.cadernoMatFlushStudy;
});
describe("Prática persistente", () => {
  it("renderiza fórmula sem revelar gabarito", () => {
    const { container } = render(<Practice {...props} attempt={tentativa()} />);
    expect(container.querySelector(".katex")).toBeTruthy();
    expect(screen.queryByText("Solução registrada")).toBeNull();
    expect(screen.getByText("Revelar solução")).toBeTruthy();
  });
  it("salva o último rascunho explicitamente antes do debounce", async () => {
    const t = tentativa();
    vi.mocked(api).mockResolvedValue(t);
    render(<Practice {...props} attempt={t} />);
    fireEvent.change(screen.getByLabelText(/^Sua resposta/), {
      target: { value: "Minha resposta $x$" },
    });
    expect(window.cadernoMatStudyDraft?.resposta).toBe("Minha resposta $x$");
    await act(async () => {
      await window.cadernoMatFlushStudy?.();
    });
    expect(api).toHaveBeenCalledWith("tentativa_salvar", {
      id: "t",
      exercicio: "q",
      resposta: "Minha resposta $x$",
      posicao: 0,
    });
  });
  it("preserva falso como resposta real", () => {
    render(<Practice {...props} attempt={tentativa("vf")} />);
    fireEvent.click(screen.getByLabelText("Falso"));
    expect(window.cadernoMatStudyDraft?.resposta).toBe(false);
  });
  it("explicita tolerância e não interpreta expressões", () => {
    render(<Practice {...props} attempt={tentativa("numerica")} />);
    expect(screen.getByText(/Tolerância absoluta: 0.01/)).toBeTruthy();
  });
  it("finalizada é somente leitura e discursiva não vira erro", () => {
    const t = tentativa();
    t.estado = "finalizada";
    t.resumo.respondidas = 1;
    t.resultado.q = {
      estado: "sem_gabarito",
      justificativa: "Revisão necessária",
    };
    t.snapshot.conteudo.exercicios[0].resposta = "";
    render(<Practice {...props} attempt={t} />);
    expect(
      (screen.getByLabelText(/^Sua resposta/) as HTMLTextAreaElement).readOnly,
    ).toBe(true);
    expect(screen.getByText("Não avaliadas")).toBeTruthy();
    expect(
      screen.getByText("Sem gabarito", { selector: ".badge" }),
    ).toBeTruthy();
    expect(screen.queryByText("Finalizar tentativa")).toBeNull();
  });
  it("marca feedback de resposta anterior e versão diferente", () => {
    const t = tentativa();
    t.versao_atual = 2;
    t.respostas.q = {
      resposta: "Nova",
      feedbacks: [
        {
          texto: "Orientação",
          provedor: "gemini",
          modelo: "simulado",
          resposta_avaliada: "Antiga",
        },
      ],
    };
    render(<Practice {...props} attempt={t} />);
    expect(screen.getByText(/uma resposta anterior/)).toBeTruthy();
    expect(screen.getByText(/exercícios da versão 1/)).toBeTruthy();
    expect(screen.getByText(/sem nota ou verificação definitiva/)).toBeTruthy();
  });
});
