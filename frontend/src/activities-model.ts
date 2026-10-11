export type Formato = "aberta" | "escolha" | "vf" | "numerica";
export type Exercicio = {
  id: string;
  enunciado: string;
  formato: Formato;
  assunto: string;
  dificuldade: string;
  alternativas: { id: string; texto: string }[];
  resposta?: string | boolean;
  tolerancia?: string;
  explicacao?: string;
  referencias: { material_id: string; pagina: number | null }[];
  solucao_disponivel?: boolean;
};
export type Conteudo = {
  titulo: string;
  descricao: string;
  assuntos: string;
  etiquetas: string;
  objetivo: string;
  dificuldade: string;
  exercicios: Exercicio[];
};
export type Fonte = { id: string; nome: string; disponivel?: boolean };
export type Atividade = {
  id: string;
  caderno_id: string | null;
  caderno_arquivado: boolean;
  origem_chat: string | null;
  origem_titulo: string;
  origem_disponivel: boolean;
  origem: string;
  proveniencia: { provedor?: string; modelo?: string };
  versao: number;
  conteudo: Conteudo;
  arquivada: number;
  criado: string;
  atualizado: string;
  fontes: Fonte[];
  quantidade?: number;
  formatos?: string[];
  tentativas?: number;
  em_andamento?: string | null;
};
export type Resposta = {
  resposta?: string | boolean | null;
  revelada?: boolean;
  dicas?: Feedback[];
  feedbacks?: Feedback[];
  revisao?: { avaliacao: string; texto: string };
};
export type Feedback = {
  texto: string;
  provedor: string;
  modelo: string;
  resposta_avaliada: string | boolean | null;
};
export type Resumo = {
  total: number;
  respondidas: number;
  objetivas: number;
  acertos: number;
  erros: number;
  nao_avaliadas: number;
  dicas: number;
  solucoes: number;
};
export type Tentativa = {
  id: string;
  atividade_id: string;
  versao: number;
  versao_atual: number;
  inicio: string;
  fim: string | null;
  estado: string;
  posicao: number;
  editavel: boolean;
  snapshot: { conteudo: Conteudo; caderno: string; fontes: Fonte[] };
  respostas: Record<string, Resposta>;
  resultado: Record<string, { estado: string; justificativa: string }>;
  resumo: Resumo;
};
export type Historico = {
  id: string;
  versao: number;
  inicio: string;
  fim: string | null;
  estado: string;
  resumo: Resumo;
};
export type EstudoNav = {
  area: "chat" | "materiais" | "atividades";
  atividade: string | null;
  tentativa: string | null;
};
export type Job = {
  id: string;
  tipo: string;
  estado: string;
  erro: string;
  criado: string;
  resultado: Conteudo | Feedback | null;
  previa: {
    tipo: string;
    provedor: string;
    modelo: string;
    caderno: string | null;
    pedagogia: string;
    pedido: Record<string, unknown>;
    fontes: {
      material_id: string;
      referencia: string;
      nome: string;
      pagina: number | null;
      texto: string;
      selecao: string;
    }[];
    materiais: Fonte[];
    origem_chat: string | null;
    aviso: string;
    tarefa: string;
  };
};
export type StudyDraft = {
  id: string;
  exercicio: string;
  resposta: string | boolean | null;
  posicao: number;
};
export const formatos: Record<Formato, string> = {
  aberta: "Resposta aberta",
  escolha: "Múltipla escolha",
  vf: "Verdadeiro ou falso",
  numerica: "Resposta numérica",
};
export const dificuldades: Record<string, string> = {
  basica: "Básica",
  intermediaria: "Intermediária",
  avancada: "Avançada",
};
export const novaQuestao = (): Exercicio => ({
  id: crypto.randomUUID(),
  enunciado: "",
  formato: "aberta",
  assunto: "",
  dificuldade: "basica",
  alternativas: [],
  resposta: "",
  explicacao: "",
  referencias: [],
});
export const novoConteudo = (): Conteudo => ({
  titulo: "",
  descricao: "",
  assuntos: "",
  etiquetas: "",
  objetivo: "",
  dificuldade: "basica",
  exercicios: [novaQuestao()],
});
export const respondida = (v: unknown) =>
  v !== null && v !== undefined && (typeof v !== "string" || !!v.trim());
declare global {
  interface Window {
    cadernoMatStudyDraft?: StudyDraft | null;
    cadernoMatFlushStudy?: () => Promise<void>;
  }
}
