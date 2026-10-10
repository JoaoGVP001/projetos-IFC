import { sql } from "drizzle-orm";
import {
  boolean,
  check,
  customType,
  index,
  integer,
  jsonb,
  pgEnum,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uniqueIndex,
  uuid,
  varchar,
  vector,
} from "drizzle-orm/pg-core";

const timestamps = {
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).defaultNow().notNull(),
};

const searchVector = customType<{ data: string }>({
  dataType() {
    return "tsvector";
  },
});

export const userRoleEnum = pgEnum("user_role", ["admin", "editor", "atendente"]);
export const sourceTypeEnum = pgEnum("source_type", ["help", "small_bdc", "zweb_bdc", "interno"]);
export const systemEnum = pgEnum("knowledge_system", ["small", "zweb", "interno", "compartilhado"]);
export const documentStatusEnum = pgEnum("document_status", ["processando", "rascunho", "publicado", "erro", "arquivado"]);
export const confidentialityEnum = pgEnum("confidentiality", ["publico", "interno", "restrito"]);
export const feedbackTypeEnum = pgEnum("feedback_type", ["resolveu", "nao_resolveu", "correcao"]);
export const answerGroundingEnum = pgEnum("answer_grounding", ["fundamentada", "insuficiente", "conflitante", "erro"]);
export const jobStatusEnum = pgEnum("job_status", ["pendente", "processando", "concluido", "erro", "cancelado"]);

export const usuarios = pgTable("usuarios", {
  id: uuid("id").defaultRandom().primaryKey(),
  nome: varchar("nome", { length: 160 }).notNull(),
  email: varchar("email", { length: 320 }).notNull(),
  role: userRoleEnum("role").default("atendente").notNull(),
  ativo: boolean("ativo").default(true).notNull(),
  ...timestamps,
}, (table) => [uniqueIndex("usuarios_email_uidx").on(table.email)]);

export const fontes = pgTable("fontes", {
  id: uuid("id").defaultRandom().primaryKey(),
  nome: varchar("nome", { length: 180 }).notNull(),
  tipo: sourceTypeEnum("tipo").notNull(),
  sistema: systemEnum("sistema").notNull(),
  urlBase: text("url_base"),
  politicaAcesso: text("politica_acesso"),
  ativo: boolean("ativo").default(true).notNull(),
  ...timestamps,
});

export const categorias = pgTable("categorias", {
  id: uuid("id").defaultRandom().primaryKey(),
  nome: varchar("nome", { length: 160 }).notNull(),
  slug: varchar("slug", { length: 180 }).notNull(),
  sistema: systemEnum("sistema").notNull(),
  parentId: uuid("parent_id"),
  ...timestamps,
}, (table) => [
  uniqueIndex("categorias_sistema_slug_uidx").on(table.sistema, table.slug),
  index("categorias_parent_idx").on(table.parentId),
]);

export const documentos = pgTable("documentos", {
  id: uuid("id").defaultRandom().primaryKey(),
  fonteId: uuid("fonte_id").notNull().references(() => fontes.id),
  categoriaId: uuid("categoria_id").references(() => categorias.id),
  titulo: varchar("titulo", { length: 500 }).notNull(),
  slug: varchar("slug", { length: 520 }).notNull(),
  sistema: systemEnum("sistema").notNull(),
  modulo: varchar("modulo", { length: 180 }),
  tipoMime: varchar("tipo_mime", { length: 160 }),
  storageKey: text("storage_key"),
  urlOrigem: text("url_origem"),
  externalId: varchar("external_id", { length: 300 }),
  textoNormalizado: text("texto_normalizado"),
  checksum: varchar("checksum", { length: 64 }).notNull(),
  versao: integer("versao").default(1).notNull(),
  status: documentStatusEnum("status").default("processando").notNull(),
  confidencialidade: confidentialityEnum("confidencialidade").default("interno").notNull(),
  publicadoEm: timestamp("publicado_em", { withTimezone: true }),
  deletedAt: timestamp("deleted_at", { withTimezone: true }),
  ...timestamps,
}, (table) => [
  uniqueIndex("documentos_fonte_checksum_uidx").on(table.fonteId, table.checksum),
  index("documentos_sistema_status_idx").on(table.sistema, table.status),
  index("documentos_categoria_idx").on(table.categoriaId),
]);

export const tags = pgTable("tags", {
  id: uuid("id").defaultRandom().primaryKey(),
  nome: varchar("nome", { length: 120 }).notNull(),
  slug: varchar("slug", { length: 140 }).notNull(),
  sistema: systemEnum("sistema").notNull(),
  ...timestamps,
}, (table) => [uniqueIndex("tags_sistema_slug_uidx").on(table.sistema, table.slug)]);

export const documentoTags = pgTable("documento_tags", {
  documentoId: uuid("documento_id").notNull().references(() => documentos.id, { onDelete: "cascade" }),
  tagId: uuid("tag_id").notNull().references(() => tags.id, { onDelete: "cascade" }),
}, (table) => [primaryKey({ columns: [table.documentoId, table.tagId] }), index("documento_tags_tag_idx").on(table.tagId)]);

export const documentoRelacionamentos = pgTable("documento_relacionamentos", {
  origemId: uuid("origem_id").notNull().references(() => documentos.id, { onDelete: "cascade" }),
  destinoId: uuid("destino_id").notNull().references(() => documentos.id, { onDelete: "cascade" }),
  tipo: varchar("tipo", { length: 80 }).notNull(),
  peso: integer("peso").default(0).notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
}, (table) => [
  primaryKey({ columns: [table.origemId, table.destinoId, table.tipo] }),
  check("documento_relacionamento_nao_reflexivo", sql`${table.origemId} <> ${table.destinoId}`),
]);

export const documentoChunks = pgTable("documento_chunks", {
  id: uuid("id").defaultRandom().primaryKey(),
  documentoId: uuid("documento_id").notNull().references(() => documentos.id, { onDelete: "cascade" }),
  ordem: integer("ordem").notNull(),
  secao: varchar("secao", { length: 500 }),
  pagina: integer("pagina"),
  texto: text("texto").notNull(),
  tokenCount: integer("token_count").notNull(),
  metadata: jsonb("metadata").$type<Record<string, unknown>>().default({}).notNull(),
  embedding: vector("embedding", { dimensions: 1536 }),
  embeddingModel: varchar("embedding_model", { length: 160 }),
  chunkerVersion: varchar("chunker_version", { length: 80 }).notNull(),
  searchVector: searchVector("search_vector"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
}, (table) => [
  uniqueIndex("documento_chunks_documento_ordem_uidx").on(table.documentoId, table.ordem),
  index("documento_chunks_documento_idx").on(table.documentoId),
  index("documento_chunks_search_idx").using("gin", table.searchVector),
  index("documento_chunks_embedding_hnsw_idx").using("hnsw", table.embedding.op("vector_cosine_ops")),
]);

export const visualizacoes = pgTable("visualizacoes", {
  id: uuid("id").defaultRandom().primaryKey(),
  usuarioId: uuid("usuario_id").notNull().references(() => usuarios.id),
  documentoId: uuid("documento_id").notNull().references(() => documentos.id),
  ocorridoEm: timestamp("ocorrido_em", { withTimezone: true }).defaultNow().notNull(),
  sessaoId: varchar("sessao_id", { length: 160 }),
  origemAcao: varchar("origem_acao", { length: 80 }).notNull(),
}, (table) => [index("visualizacoes_documento_data_idx").on(table.documentoId, table.ocorridoEm), index("visualizacoes_usuario_data_idx").on(table.usuarioId, table.ocorridoEm)]);

export const favoritos = pgTable("favoritos", {
  usuarioId: uuid("usuario_id").notNull().references(() => usuarios.id, { onDelete: "cascade" }),
  documentoId: uuid("documento_id").notNull().references(() => documentos.id, { onDelete: "cascade" }),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
}, (table) => [primaryKey({ columns: [table.usuarioId, table.documentoId] })]);

export const pesquisas = pgTable("pesquisas", {
  id: uuid("id").defaultRandom().primaryKey(),
  usuarioId: uuid("usuario_id").references(() => usuarios.id),
  termo: text("termo").notNull(),
  filtros: jsonb("filtros").$type<Record<string, unknown>>().default({}).notNull(),
  quantidadeResultados: integer("quantidade_resultados").notNull(),
  latenciaMs: integer("latencia_ms").notNull(),
  ocorridoEm: timestamp("ocorrido_em", { withTimezone: true }).defaultNow().notNull(),
}, (table) => [index("pesquisas_ocorrido_em_idx").on(table.ocorridoEm), index("pesquisas_zero_resultado_idx").on(table.quantidadeResultados, table.ocorridoEm)]);

export const ragRespostas = pgTable("rag_respostas", {
  id: uuid("id").defaultRandom().primaryKey(),
  usuarioId: uuid("usuario_id").references(() => usuarios.id),
  pergunta: text("pergunta").notNull(),
  resposta: text("resposta").notNull(),
  sistema: systemEnum("sistema").notNull(),
  modelo: varchar("modelo", { length: 160 }).notNull(),
  promptVersion: varchar("prompt_version", { length: 80 }).notNull(),
  statusFundamentacao: answerGroundingEnum("status_fundamentacao").notNull(),
  latenciaMs: integer("latencia_ms").notNull(),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
}, (table) => [index("rag_respostas_usuario_data_idx").on(table.usuarioId, table.createdAt)]);

export const ragRespostaFontes = pgTable("rag_resposta_fontes", {
  respostaId: uuid("resposta_id").notNull().references(() => ragRespostas.id, { onDelete: "cascade" }),
  chunkId: uuid("chunk_id").notNull().references(() => documentoChunks.id),
  posicao: integer("posicao").notNull(),
  score: varchar("score", { length: 40 }).notNull(),
  trechoExibido: text("trecho_exibido").notNull(),
}, (table) => [primaryKey({ columns: [table.respostaId, table.chunkId] }), uniqueIndex("rag_resposta_fontes_posicao_uidx").on(table.respostaId, table.posicao)]);

export const feedbacks = pgTable("feedbacks", {
  id: uuid("id").defaultRandom().primaryKey(),
  usuarioId: uuid("usuario_id").notNull().references(() => usuarios.id),
  documentoId: uuid("documento_id").references(() => documentos.id),
  respostaId: uuid("resposta_id").references(() => ragRespostas.id),
  tipo: feedbackTypeEnum("tipo").notNull(),
  comentario: text("comentario"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
}, (table) => [
  check("feedbacks_um_alvo", sql`num_nonnulls(${table.documentoId}, ${table.respostaId}) = 1`),
  index("feedbacks_documento_idx").on(table.documentoId),
  index("feedbacks_resposta_idx").on(table.respostaId),
]);

export const importacoes = pgTable("importacoes", {
  id: uuid("id").defaultRandom().primaryKey(),
  fonteId: uuid("fonte_id").notNull().references(() => fontes.id),
  status: jobStatusEnum("status").default("pendente").notNull(),
  iniciadaEm: timestamp("iniciada_em", { withTimezone: true }),
  finalizadaEm: timestamp("finalizada_em", { withTimezone: true }),
  totais: jsonb("totais").$type<Record<string, number>>().default({}).notNull(),
  erro: text("erro"),
  createdAt: timestamp("created_at", { withTimezone: true }).defaultNow().notNull(),
});

export const tarefasIngestao = pgTable("tarefas_ingestao", {
  id: uuid("id").defaultRandom().primaryKey(),
  documentoId: uuid("documento_id").references(() => documentos.id, { onDelete: "cascade" }),
  tipo: varchar("tipo", { length: 80 }).notNull(),
  status: jobStatusEnum("status").default("pendente").notNull(),
  tentativas: integer("tentativas").default(0).notNull(),
  disponivelEm: timestamp("disponivel_em", { withTimezone: true }).defaultNow().notNull(),
  erro: text("erro"),
  ...timestamps,
}, (table) => [index("tarefas_ingestao_fila_idx").on(table.status, table.disponivelEm)]);
