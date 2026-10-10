# ResolveHub

Central inteligente de suporte para reunir procedimentos internos, manuais e artigos autorizados do **Small Commerce** e do **ZWeb**.

O produto está sendo construído de forma incremental. A primeira entrega contém a fundação visual, o modelo inicial de dados, a política segura de ingestão e a infraestrutura local. Consulte o [roadmap completo](./ROADMAP_CENTRAL_INTELIGENTE_SUPORTE.md).

## Estado atual

- [x] Roadmap e arquitetura inicial.
- [x] Interface inicial responsiva com separação Small Commerce, ZWeb e Interno.
- [x] Modelo PostgreSQL/pgvector com Drizzle.
- [x] Inventário seguro de ZIP sem extração automática.
- [x] Catálogo pesquisável das 1.037 fontes do Help e links oficiais das BDCs.
- [x] Cadastro persistente de soluções com anexos, acessos e histórico de resultados.
- [x] Visualização local de TXT, PDF, imagens e vídeos permitidos diretamente no site.
- [x] Docker Compose para banco, aplicação e ferramenta de inventário.
- [x] Testes iniciais do ranking híbrido e da política de ingestão.
- [ ] Autenticação e autorização por papéis.
- [ ] Importação revisada para o banco e storage.
- [ ] Pesquisa PostgreSQL e métricas reais.
- [ ] RAG, embeddings e respostas citadas.
- [ ] Sincronização autorizada das BDCs.

## Segurança dos documentos

O arquivo `Help.zip` **não deve ser adicionado ao Git**. O material recebido contém itens que podem ser sensíveis ou executáveis, como certificados, arquivos de senha, bancos de dados, binários e scripts SQL. A ferramenta de inventário apenas lê o índice do ZIP e classifica cada item como importável, revisão obrigatória, adiado ou bloqueado.

Nenhum item bloqueado é extraído ou publicado automaticamente. Veja [Política de ingestão](./docs/security/DATA_INGESTION_POLICY.md).

## Pré-requisitos

- Node.js 24 ou versão compatível com o Next.js definido no lockfile.
- npm 11 ou compatível.
- Python 3.12+ para a ferramenta de ingestão.
- Docker e Docker Compose para PostgreSQL/pgvector.

## Desenvolvimento da interface

```bash
cd apps/web
npm install
npm run dev
```

A aplicação ficará disponível em `http://localhost:3000`.

Para abrir os arquivos permitidos diretamente do pacote original, configure em `apps/web/.env.local`:

```dotenv
STORAGE_ROOT=../../storage
HELP_ARCHIVE_PATH=C:/caminho/Help.zip
RESOLVEHUB_ALLOW_REMOTE_UPLOADS=false
```

Soluções cadastradas, anexos, contadores de acesso e históricos são persistidos em `STORAGE_ROOT`, que permanece fora do Git. Até a autenticação ser implementada, upload e leitura de arquivos privados ficam restritos a `localhost` por padrão.

## Banco local

1. Copie `.env.example` para `.env` e troque as credenciais de desenvolvimento.
2. Inicie os serviços:

```bash
docker compose up -d db
```

3. Gere as migrações quando o schema mudar:

```bash
npm run db:generate
```

Para aplicar a migração inicial no banco local:

```bash
docker compose exec db sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /migrations/0000_tricky_redwing.sql'
```

## Inventário seguro do Help.zip

O comando abaixo gera somente totais agregados e não salva nomes nem conteúdo dos arquivos:

```bash
cd services/ingestion
python -m resolvehub_ingestion.cli inventory --archive "CAMINHO/Help.zip" --output "../../data/reports/help-summary.json"
```

O catálogo exibido pela interface é gerado apenas com metadados revisados. Nomes de arquivos bloqueados, pendentes, não suportados ou com sinais de dados sensíveis são substituídos por identificadores neutros:

```bash
cd services/ingestion
python -m resolvehub_ingestion.cli catalog --archive "CAMINHO/Help.zip" --output "../../apps/web/src/features/workspace/source-catalog.json"
```

Para executar os testes da política:

```bash
cd services/ingestion
python -m unittest discover -s tests -v
```

## Fontes externas

- Small Commerce: <https://bdc.smallsoft.com.br/>
- ZWeb: <https://bdc.zweb.com.br/>

Os conectores devem usar API ou exportação oficial quando disponível. Coleta HTML só será habilitada após validação de termos, permissões e limites. Nenhum controle de acesso será contornado.

## Qualidade

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

## Licença e conteúdo

O código-fonte e os documentos de conhecimento possuem ciclos de acesso diferentes. Publicar este repositório não autoriza publicar documentos internos, dados de clientes ou cópias integrais de conteúdo de terceiros.
