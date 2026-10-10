CREATE EXTENSION IF NOT EXISTS vector;--> statement-breakpoint
CREATE EXTENSION IF NOT EXISTS unaccent;--> statement-breakpoint
CREATE EXTENSION IF NOT EXISTS pg_trgm;--> statement-breakpoint
CREATE TYPE "public"."answer_grounding" AS ENUM('fundamentada', 'insuficiente', 'conflitante', 'erro');--> statement-breakpoint
CREATE TYPE "public"."confidentiality" AS ENUM('publico', 'interno', 'restrito');--> statement-breakpoint
CREATE TYPE "public"."document_status" AS ENUM('processando', 'rascunho', 'publicado', 'erro', 'arquivado');--> statement-breakpoint
CREATE TYPE "public"."feedback_type" AS ENUM('resolveu', 'nao_resolveu', 'correcao');--> statement-breakpoint
CREATE TYPE "public"."job_status" AS ENUM('pendente', 'processando', 'concluido', 'erro', 'cancelado');--> statement-breakpoint
CREATE TYPE "public"."source_type" AS ENUM('help', 'small_bdc', 'zweb_bdc', 'interno');--> statement-breakpoint
CREATE TYPE "public"."knowledge_system" AS ENUM('small', 'zweb', 'interno', 'compartilhado');--> statement-breakpoint
CREATE TYPE "public"."user_role" AS ENUM('admin', 'editor', 'atendente');--> statement-breakpoint
CREATE TABLE "categorias" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nome" varchar(160) NOT NULL,
	"slug" varchar(180) NOT NULL,
	"sistema" "knowledge_system" NOT NULL,
	"parent_id" uuid,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "documento_chunks" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"documento_id" uuid NOT NULL,
	"ordem" integer NOT NULL,
	"secao" varchar(500),
	"pagina" integer,
	"texto" text NOT NULL,
	"token_count" integer NOT NULL,
	"metadata" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"embedding" vector(1536),
	"embedding_model" varchar(160),
	"chunker_version" varchar(80) NOT NULL,
	"search_vector" "tsvector",
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "documento_relacionamentos" (
	"origem_id" uuid NOT NULL,
	"destino_id" uuid NOT NULL,
	"tipo" varchar(80) NOT NULL,
	"peso" integer DEFAULT 0 NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "documento_relacionamentos_origem_id_destino_id_tipo_pk" PRIMARY KEY("origem_id","destino_id","tipo"),
	CONSTRAINT "documento_relacionamento_nao_reflexivo" CHECK ("documento_relacionamentos"."origem_id" <> "documento_relacionamentos"."destino_id")
);
--> statement-breakpoint
CREATE TABLE "documento_tags" (
	"documento_id" uuid NOT NULL,
	"tag_id" uuid NOT NULL,
	CONSTRAINT "documento_tags_documento_id_tag_id_pk" PRIMARY KEY("documento_id","tag_id")
);
--> statement-breakpoint
CREATE TABLE "documentos" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"fonte_id" uuid NOT NULL,
	"categoria_id" uuid,
	"titulo" varchar(500) NOT NULL,
	"slug" varchar(520) NOT NULL,
	"sistema" "knowledge_system" NOT NULL,
	"modulo" varchar(180),
	"tipo_mime" varchar(160),
	"storage_key" text,
	"url_origem" text,
	"external_id" varchar(300),
	"texto_normalizado" text,
	"checksum" varchar(64) NOT NULL,
	"versao" integer DEFAULT 1 NOT NULL,
	"status" "document_status" DEFAULT 'processando' NOT NULL,
	"confidencialidade" "confidentiality" DEFAULT 'interno' NOT NULL,
	"publicado_em" timestamp with time zone,
	"deleted_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "favoritos" (
	"usuario_id" uuid NOT NULL,
	"documento_id" uuid NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "favoritos_usuario_id_documento_id_pk" PRIMARY KEY("usuario_id","documento_id")
);
--> statement-breakpoint
CREATE TABLE "feedbacks" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"usuario_id" uuid NOT NULL,
	"documento_id" uuid,
	"resposta_id" uuid,
	"tipo" "feedback_type" NOT NULL,
	"comentario" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "feedbacks_um_alvo" CHECK (num_nonnulls("feedbacks"."documento_id", "feedbacks"."resposta_id") = 1)
);
--> statement-breakpoint
CREATE TABLE "fontes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nome" varchar(180) NOT NULL,
	"tipo" "source_type" NOT NULL,
	"sistema" "knowledge_system" NOT NULL,
	"url_base" text,
	"politica_acesso" text,
	"ativo" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "importacoes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"fonte_id" uuid NOT NULL,
	"status" "job_status" DEFAULT 'pendente' NOT NULL,
	"iniciada_em" timestamp with time zone,
	"finalizada_em" timestamp with time zone,
	"totais" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"erro" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "pesquisas" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"usuario_id" uuid,
	"termo" text NOT NULL,
	"filtros" jsonb DEFAULT '{}'::jsonb NOT NULL,
	"quantidade_resultados" integer NOT NULL,
	"latencia_ms" integer NOT NULL,
	"ocorrido_em" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "rag_resposta_fontes" (
	"resposta_id" uuid NOT NULL,
	"chunk_id" uuid NOT NULL,
	"posicao" integer NOT NULL,
	"score" varchar(40) NOT NULL,
	"trecho_exibido" text NOT NULL,
	CONSTRAINT "rag_resposta_fontes_resposta_id_chunk_id_pk" PRIMARY KEY("resposta_id","chunk_id")
);
--> statement-breakpoint
CREATE TABLE "rag_respostas" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"usuario_id" uuid,
	"pergunta" text NOT NULL,
	"resposta" text NOT NULL,
	"sistema" "knowledge_system" NOT NULL,
	"modelo" varchar(160) NOT NULL,
	"prompt_version" varchar(80) NOT NULL,
	"status_fundamentacao" "answer_grounding" NOT NULL,
	"latencia_ms" integer NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "tags" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nome" varchar(120) NOT NULL,
	"slug" varchar(140) NOT NULL,
	"sistema" "knowledge_system" NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "tarefas_ingestao" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"documento_id" uuid,
	"tipo" varchar(80) NOT NULL,
	"status" "job_status" DEFAULT 'pendente' NOT NULL,
	"tentativas" integer DEFAULT 0 NOT NULL,
	"disponivel_em" timestamp with time zone DEFAULT now() NOT NULL,
	"erro" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "usuarios" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"nome" varchar(160) NOT NULL,
	"email" varchar(320) NOT NULL,
	"role" "user_role" DEFAULT 'atendente' NOT NULL,
	"ativo" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "visualizacoes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"usuario_id" uuid NOT NULL,
	"documento_id" uuid NOT NULL,
	"ocorrido_em" timestamp with time zone DEFAULT now() NOT NULL,
	"sessao_id" varchar(160),
	"origem_acao" varchar(80) NOT NULL
);
--> statement-breakpoint
CREATE FUNCTION resolvehub_documento_chunks_search_vector_update() RETURNS trigger AS $$
BEGIN
	NEW.search_vector := to_tsvector('portuguese', unaccent(coalesce(NEW.texto, '')));
	RETURN NEW;
END
$$ LANGUAGE plpgsql;--> statement-breakpoint
CREATE TRIGGER documento_chunks_search_vector_trigger
BEFORE INSERT OR UPDATE OF texto ON documento_chunks
FOR EACH ROW EXECUTE FUNCTION resolvehub_documento_chunks_search_vector_update();--> statement-breakpoint
ALTER TABLE "documento_chunks" ADD CONSTRAINT "documento_chunks_documento_id_documentos_id_fk" FOREIGN KEY ("documento_id") REFERENCES "public"."documentos"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "documento_relacionamentos" ADD CONSTRAINT "documento_relacionamentos_origem_id_documentos_id_fk" FOREIGN KEY ("origem_id") REFERENCES "public"."documentos"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "documento_relacionamentos" ADD CONSTRAINT "documento_relacionamentos_destino_id_documentos_id_fk" FOREIGN KEY ("destino_id") REFERENCES "public"."documentos"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "documento_tags" ADD CONSTRAINT "documento_tags_documento_id_documentos_id_fk" FOREIGN KEY ("documento_id") REFERENCES "public"."documentos"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "documento_tags" ADD CONSTRAINT "documento_tags_tag_id_tags_id_fk" FOREIGN KEY ("tag_id") REFERENCES "public"."tags"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "documentos" ADD CONSTRAINT "documentos_fonte_id_fontes_id_fk" FOREIGN KEY ("fonte_id") REFERENCES "public"."fontes"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "documentos" ADD CONSTRAINT "documentos_categoria_id_categorias_id_fk" FOREIGN KEY ("categoria_id") REFERENCES "public"."categorias"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "favoritos" ADD CONSTRAINT "favoritos_usuario_id_usuarios_id_fk" FOREIGN KEY ("usuario_id") REFERENCES "public"."usuarios"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "favoritos" ADD CONSTRAINT "favoritos_documento_id_documentos_id_fk" FOREIGN KEY ("documento_id") REFERENCES "public"."documentos"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feedbacks" ADD CONSTRAINT "feedbacks_usuario_id_usuarios_id_fk" FOREIGN KEY ("usuario_id") REFERENCES "public"."usuarios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feedbacks" ADD CONSTRAINT "feedbacks_documento_id_documentos_id_fk" FOREIGN KEY ("documento_id") REFERENCES "public"."documentos"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feedbacks" ADD CONSTRAINT "feedbacks_resposta_id_rag_respostas_id_fk" FOREIGN KEY ("resposta_id") REFERENCES "public"."rag_respostas"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "importacoes" ADD CONSTRAINT "importacoes_fonte_id_fontes_id_fk" FOREIGN KEY ("fonte_id") REFERENCES "public"."fontes"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "pesquisas" ADD CONSTRAINT "pesquisas_usuario_id_usuarios_id_fk" FOREIGN KEY ("usuario_id") REFERENCES "public"."usuarios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "rag_resposta_fontes" ADD CONSTRAINT "rag_resposta_fontes_resposta_id_rag_respostas_id_fk" FOREIGN KEY ("resposta_id") REFERENCES "public"."rag_respostas"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "rag_resposta_fontes" ADD CONSTRAINT "rag_resposta_fontes_chunk_id_documento_chunks_id_fk" FOREIGN KEY ("chunk_id") REFERENCES "public"."documento_chunks"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "rag_respostas" ADD CONSTRAINT "rag_respostas_usuario_id_usuarios_id_fk" FOREIGN KEY ("usuario_id") REFERENCES "public"."usuarios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "tarefas_ingestao" ADD CONSTRAINT "tarefas_ingestao_documento_id_documentos_id_fk" FOREIGN KEY ("documento_id") REFERENCES "public"."documentos"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "visualizacoes" ADD CONSTRAINT "visualizacoes_usuario_id_usuarios_id_fk" FOREIGN KEY ("usuario_id") REFERENCES "public"."usuarios"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "visualizacoes" ADD CONSTRAINT "visualizacoes_documento_id_documentos_id_fk" FOREIGN KEY ("documento_id") REFERENCES "public"."documentos"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE UNIQUE INDEX "categorias_sistema_slug_uidx" ON "categorias" USING btree ("sistema","slug");--> statement-breakpoint
CREATE INDEX "categorias_parent_idx" ON "categorias" USING btree ("parent_id");--> statement-breakpoint
CREATE UNIQUE INDEX "documento_chunks_documento_ordem_uidx" ON "documento_chunks" USING btree ("documento_id","ordem");--> statement-breakpoint
CREATE INDEX "documento_chunks_documento_idx" ON "documento_chunks" USING btree ("documento_id");--> statement-breakpoint
CREATE INDEX "documento_chunks_search_idx" ON "documento_chunks" USING gin ("search_vector");--> statement-breakpoint
CREATE INDEX "documento_chunks_embedding_hnsw_idx" ON "documento_chunks" USING hnsw ("embedding" vector_cosine_ops);--> statement-breakpoint
CREATE INDEX "documento_tags_tag_idx" ON "documento_tags" USING btree ("tag_id");--> statement-breakpoint
CREATE UNIQUE INDEX "documentos_fonte_checksum_uidx" ON "documentos" USING btree ("fonte_id","checksum");--> statement-breakpoint
CREATE INDEX "documentos_sistema_status_idx" ON "documentos" USING btree ("sistema","status");--> statement-breakpoint
CREATE INDEX "documentos_categoria_idx" ON "documentos" USING btree ("categoria_id");--> statement-breakpoint
CREATE INDEX "feedbacks_documento_idx" ON "feedbacks" USING btree ("documento_id");--> statement-breakpoint
CREATE INDEX "feedbacks_resposta_idx" ON "feedbacks" USING btree ("resposta_id");--> statement-breakpoint
CREATE INDEX "pesquisas_ocorrido_em_idx" ON "pesquisas" USING btree ("ocorrido_em");--> statement-breakpoint
CREATE INDEX "pesquisas_zero_resultado_idx" ON "pesquisas" USING btree ("quantidade_resultados","ocorrido_em");--> statement-breakpoint
CREATE UNIQUE INDEX "rag_resposta_fontes_posicao_uidx" ON "rag_resposta_fontes" USING btree ("resposta_id","posicao");--> statement-breakpoint
CREATE INDEX "rag_respostas_usuario_data_idx" ON "rag_respostas" USING btree ("usuario_id","created_at");--> statement-breakpoint
CREATE UNIQUE INDEX "tags_sistema_slug_uidx" ON "tags" USING btree ("sistema","slug");--> statement-breakpoint
CREATE INDEX "tarefas_ingestao_fila_idx" ON "tarefas_ingestao" USING btree ("status","disponivel_em");--> statement-breakpoint
CREATE UNIQUE INDEX "usuarios_email_uidx" ON "usuarios" USING btree ("email");--> statement-breakpoint
CREATE INDEX "visualizacoes_documento_data_idx" ON "visualizacoes" USING btree ("documento_id","ocorrido_em");--> statement-breakpoint
CREATE INDEX "visualizacoes_usuario_data_idx" ON "visualizacoes" USING btree ("usuario_id","ocorrido_em");
