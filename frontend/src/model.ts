export type Caderno = {
  id: string;
  nome: string;
  descricao: string;
  objetivo: string;
  nivel: string;
  assuntos: string;
  orientacao: string;
  preferencia: string;
  arquivado: number;
  ordem: number;
};
export type Chat = {
  id: string;
  titulo: string;
  rascunho: string;
  caderno_id: string | null;
  fixada: number;
  arquivada: number;
};
export type Metrics = {
  modelo?: string;
  perfil?: string;
  segundos?: number;
  tokens_saida?: number | null;
  num_predict?: number;
  tokens_s?: number | null;
  primeiro_token_s?: number | null;
  done_reason?: string | null;
  frame_final?: boolean;
  carga_s?: number | null;
  entrada_s?: number | null;
  geracao_s?: number | null;
  memoria?: {
    rss_aplicativo_max?: number | null;
    rss_filhos_aplicativo_max?: number | null;
    rss_ollama_max?: number | null;
    swap_usada_max?: number | null;
    ram_disponivel_min?: number | null;
  };
  dispositivo?: { processador: string };
};
export type Mensagem = {
  metricas?: Metrics;
  interrupcao?: { mensagem: string; motivo: string } | null;
  origem_consulta?: string | null;
  origem_mensagem?: number | null;
  id: number;
  papel: "user" | "assistant";
  texto: string;
  estado: string;
  provedor: string;
  modelo: string;
  criado: string;
  consulta_id?: string | null;
};
export type Material = {
  id: string;
  nome: string;
  tipo: string;
  tamanho: number;
  url: string;
  estado: string;
  estado_rotulo: string;
  aviso: string;
  metodo: string;
  materia: string;
  assunto: string;
  etiquetas: string;
  origem_id: string | null;
  origem_titulo: string;
  criado: string;
  cadernos: string[];
  anexado: boolean;
  selecionado: boolean;
  processando: boolean;
  ocorrencias?: { pagina: number; texto: string; selecao: string }[];
};
export type Config = {
  provedor: string;
  modelo?: string;
  padrao?: string;
  escopo?: string;
  local?: {
    url: string;
    modelo: string;
    contexto: number;
    timeout: number;
    perfil?: string;
  } | null;
  provedores: Record<
    string,
    {
      modelo: string;
      configurada: boolean;
      local?: boolean;
      url?: string;
      contexto?: number;
      timeout?: number;
      perfil?: string;
    }
  >;
};
export type DiagnosticoLocal = {
  versao: string;
  modelos: {
    name: string;
    size: number;
    digest: string;
    details?: { quantization_level: string };
  }[];
  capacidades: string[];
  carregado: boolean;
  modelo_disponivel: boolean;
  aviso: string;
  dispositivo?: {
    estado: string;
    processador: string;
    size: number | null;
    size_vram: number | null;
    contexto: number | null;
  };
  memoria?: {
    ram_total: number | null;
    ram_disponivel: number | null;
    swap_usada: number | null;
  };
};
export type Orcamento = {
  perfil_nome?: string;
  perfil?: string;
  timeout?: number;
  contexto: number;
  entrada_estimada: number;
  reserva_saida: number;
  margem: number;
  metodo: string;
  pares_omitidos: number;
  trechos_omitidos: number;
  trechos_abreviados: number;
};
export type Estado = {
  pagina?: string | null;
  paginas_chat?: {
    id: string;
    titulo: string;
    versao: number;
    mensagem: number;
  }[];
  calculos?: {
    id: string;
    versao?: string;
    tipo: string;
    estado: string;
    mensagem_id: number | null;
    erro: string;
  }[];
  estudo: import("./activities-model").EstudoNav;
  revisao: number;
  cadernos: Caderno[];
  navegacao: {
    caderno_id: string | null;
    conversa_id: string | null;
    arquivados: number;
  };
  conversas: Chat[];
  conversa: Chat | null;
  mensagens: Mensagem[];
  anexos: Material[];
  config: Config;
  preferencias: { tema: "claro" | "escuro"; recolhida: boolean };
  ocupado: boolean;
  tarefas: {
    id: string;
    tipo: string;
    estado: string;
    conversa: string;
    parcial?: string;
    cancelavel?: boolean;
    cancelando?: boolean;
    modelo?: string;
    provedor?: string;
  }[];
};
export type Filtros = {
  busca: string;
  tipo: string;
  materia: string;
  dias: number;
  caderno: string | null;
  so_chat: boolean;
  modo?: "texto" | "hibrida";
  pagina: number;
};
export type ListaMateriais = {
  itens: Material[];
  total: number;
  pagina: number;
  materias: string[];
  recuperacao?: Recuperacao;
};
export type Detalhe = {
  material: Material;
  paginas: number[];
  texto: string;
  imagem: string | null;
  aviso_previa: string;
};
export type Previa = {
  token?: string;
  provedor: string;
  modelo: string;
  pedagogia: string;
  mensagem: string;
  historico: { role: string; content: string }[];
  fontes:
    | {
        referencia: string;
        nome: string;
        pagina: number;
        texto: string;
        tipo: string;
        aviso?: string;
      }[]
    | null;
  originais_enviados: boolean;
  instrucoes?: string;
  orcamento?: Orcamento | null;
  destino?: string;
  recuperacao?: Recuperacao;
  local?: Config["local"];
};

export type Recuperacao = {
  metodo?: string;
  aviso?: string;
  escopo?: string;
  indexados?: number;
};
export type StatusSemantica = {
  habilitada: number;
  url: string;
  modelo: string;
  digest: string;
  dimensao: number;
  perfil: string;
  total: number;
  indexados: number;
  pendentes: number;
  cpu: boolean;
  limite: number;
  trabalho: null | {
    estado: string;
    feitos: number;
    total: number;
    erro: string;
  };
};
