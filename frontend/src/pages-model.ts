export type PageContent = {
  titulo: string;
  assunto: string;
  fundo: "branco" | "pautado" | "quadriculado";
  secoes: {
    id: string;
    titulo: string;
    texto: string;
    origem: "usuario" | "ia" | "ferramenta";
    recurso?: string;
    rotulo?: string;
    rotulo_origem?: "local" | "ia";
  }[];
};
export type PageResource = {
  id: string;
  resumo: string;
  imagem?: string | null;
  rotulo: string;
};
export type PageRender = {
  conteudo: PageContent;
  materia: string;
  versao: number | string;
  recursos: Record<string, PageResource>;
  referencias?: {
    nome: string;
    pagina?: number | null;
    unidade?: string;
    aviso?: string;
    origem?: string;
    url?: string;
  }[];
  avisos?: string[];
  origens?: {
    tipo: string;
    id: string | number;
    titulo: string;
    versao?: number;
    questao?: string;
  }[];
};
export type Page = {
  id: string;
  caderno_id: string | null;
  arquivada: number;
  editavel: boolean;
  revisao: number;
  versao: number;
  rascunho: PageContent;
  versoes: { versao: number; criado: string }[];
  render: PageRender;
  origens: unknown[];
};
export type PageJob = {
  id: string;
  tipo: string;
  estado: string;
  erro: string;
  pagina_id: string;
  versao: number;
  resultado?: PageContent | null;
  previa?: Record<string, any>;
  manifesto?: { folhas: number; avisos: string[] } | null;
};
declare global {
  interface Window {
    cadernoMatPageDraft?: {
      id: string;
      conteudo: PageContent;
      revisao: number;
    } | null;
    cadernoMatFlushPage?: () => Promise<void>;
    cadernoMatExportStatus?: {
      ok: boolean;
      folhas?: number;
      erro?: string;
      avisos?: string[];
    };
  }
}
export const emptyPage = (): PageContent => ({
  titulo: "Nova página",
  assunto: "",
  fundo: "branco",
  secoes: [
    {
      id: crypto.randomUUID(),
      titulo: "Enunciado",
      texto: "",
      origem: "usuario",
    },
  ],
});
