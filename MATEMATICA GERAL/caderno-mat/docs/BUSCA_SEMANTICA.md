# Busca híbrida local — L2

Entrega de 11/10/2026. Busca por palavra e significado nos materiais já extraídos,
independente do provedor que responde ao chat. Modelo de busca e modelo de chat
são distintos: indexar apostilas não treina nenhum deles.

## Usar

1. Abra **Materiais** e expanda **Busca local por significado**.
2. O modelo `qwen3-embedding:0.6b` deve estar instalado no Ollama. Neste notebook
   ele já foi baixado para a pasta de dados. Em outra máquina, use a instalação
   oficial e `ollama pull qwen3-embedding:0.6b`. O programa não baixa modelos.
3. Confira o servidor local e clique **Indexar / retomar e ativar**. Essa ação
   processa os textos extraídos de toda a biblioteca local em CPU. Não copia os
   arquivos para uma API externa nem seleciona fontes automaticamente.
4. Na biblioteca, escolha **Palavra e significado local** e procure pelo assunto
   com suas próprias palavras. Os filtros de caderno, tipo, data, matéria e chat
   são aplicados antes da busca. **Do caderno atual** limita ao caderno aberto.
5. Confira o trecho e abra o material. Para consultá-lo na IA, marque
   **Consultar neste chat** ou selecione-o na prévia da atividade.
6. A prévia do chat/estudo informa a estratégia e eventual degradação para busca
   textual. **Usar busca híbrida nos chats e no estudo** pode ser desativado sem
   excluir materiais ou vetores. A pesquisa da biblioteca também usa FTS quando
   a busca híbrida está desativada.

Se o Ollama estiver desligado, inicie-o pelas configurações de IA ou pela sua
instalação normal. Indexação aceita cancelamento, conserva lotes preparados e
retoma por **Indexar / retomar**. Após reiniciar, trabalhos interrompidos ficam
identificados como incompletos; nenhum envio reinicia sozinho. Novos arquivos ou
reprocessamentos exigem retomar a indexação. A busca textual permanece disponível.

O runtime deste notebook só mantém um modelo carregado. Buscar/indexar embeddings
pode descarregar o chat, aumentando o tempo da próxima resposta. O aplicativo
serializa indexação e consultas de IA; o embedding pede CPU e `keep_alive=0`.
Não alteramos serviços de sistema ou limites de GPU do computador.

## Recuperação e privacidade

Chats buscam somente IDs de materiais marcados naquele chat. Atividades usam
somente a seleção explícita de fontes da prévia. Associação a caderno ou presença
no índice nunca concede autorização documental. Pesquisa da biblioteca permite
explorar o escopo escolhido sem mandar o resultado automaticamente à IA.

A indexação envia ao **Ollama em 127.0.0.1** lotes de até quatro textos extraídos.
A consulta semântica envia somente a pergunta ao modelo de busca; comparação dos
vetores ocorre no Python. URLs remotas, credenciais, redirects e modelos cloud
são bloqueados. Gemini/OpenAI podem receber os trechos posteriormente, apenas
quando forem os provedores escolhidos para responder; a prévia mostra esse destino.
Original, imagens e PDFs binários não são enviados na indexação ou na busca.

FTS5 fornece até 30 candidatos e o índice exato calcula cosseno sobre vetores
normalizados de trechos autorizados. Um limiar heurístico de **0,35** corta
semelhanças baixas; não representa probabilidade de acerto. Reciprocal Rank
Fusion (`k=60`) combina os rankings sem comparar a escala de BM25 com cosseno.
O resultado conserva origem textual/semântica/híbrida. O contexto final mantém
até seis trechos, duas ocorrências por página, IDs M1/M2, páginas e orçamento
existente do provedor. Pedidos gerais ainda podem usar a amostra inicial
explicitamente identificada; isso não representa leitura de todo o documento.

Documento é dado não confiável, sem autorização para shell, ferramentas ou
navegação. Similaridade não prova uma afirmação nem verifica contas. Índice
parcial/corrompido, modelo ausente, timeout ou mudança de pesos causam aviso e
recuperação textual. Nenhuma falha de busca troca o provedor de resposta.

## Armazenamento e confiabilidade

SQLite **v8**, no diretório de dados fora do Git, cria backup **v7** e aplica
migração transacional. Preserva mensagens, cadernos, biblioteca, atividades,
tentativas e preferências existentes. Acrescenta:

- `semantica_config`: ativação explícita, endpoint, tag, digest, dimensão e perfil.
- `semantica_vetores`: índice publicado; um vetor por trecho, sem duplicar o texto.
- `semantica_preparo`: lotes duráveis ainda não publicados, para cancelamento/retomada.
- `semantica_trabalho`: estado e progresso da última execução.

Cada vetor registra hash de texto+método, versão do extrator/chunking, tag/digest,
1.024 dimensões e normalização L2. Formato float32 little-endian permite mover o
banco entre plataformas. Mudança de digest/perfil/dimensão requer reindexação;
espaços incompatíveis nunca são comparados. Texto alterado invalida vetores; a
remoção de trechos/materiais limpa publicação e preparação via FK/trigger.

Os lotes novos ficam separados até todos os trechos atuais estarem prontos.
Publicação ocorre em uma transação; erro conserva o índice publicado anterior.
Se o acervo mudar durante a preparação, o trabalho pede retomada. Limite inicial:
**20.000 trechos** para o acervo pessoal; consultas de embedding limitadas a
6.000 caracteres, janela 2K e `truncate=false`. Não há FAISS/Qdrant, daemon extra
ou nova dependência Python. Dados e pesos permanecem fora do repositório.

Modelo fixado nesta entrega: Qwen3-Embedding 0.6B Q8_0, aproximadamente 639 MB,
licença Apache 2.0. A instrução de recuperação é aplicada à pergunta; documentos
usam texto sem prefixo. [Pacote Ollama](https://ollama.com/library/qwen3-embedding:0.6b),
[cartão oficial Qwen](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B),
[API `/api/embed`](https://docs.ollama.com/api/embed).

## Testes e reprodução

Testes de backend usam vetores sintéticos para verificar filtragem antes de
comparar, cancelamento/retomada, publicação, cache incremental, mudança de digest,
JSON/dimensão/NaN, restrição local, ausência de chamadas online, migração/rollback,
reprocessamento, exclusão e reinício. Esses testes não medem qualidade do modelo.
React verifica consentimento explícito e cancelamento mesmo com mutações bloqueadas.
O fluxo Qt testa a interface compilada, pesquisa, filtros, autorização e reinício.

```bash
.venv/bin/python -m unittest discover -s tests -v
cd frontend
pnpm test
pnpm build
pnpm e2e:semantica
```

Aceite real opcional, com modelo já instalado, Node no PATH, Qt e ferramentas
Linux `unshare`/`ip`:

```bash
scripts/testar_integracao_offline_linux.sh --semantica
```

Esse script isola somente os processos de teste numa rede de loopback. Captura
a identidade original antes do `unshare` e verifica ausência de conexão externa,
mesmo quando `/proc/1/ns/net` fica ilegível no user namespace. Mantém o sandbox
WebEngine. Os bancos/acervos são fictícios e temporários. O relatório de recuperação
fica em `ia-local/relatorios/l2-recuperacao-real.json`, fora do Git. Inclui a
comparação com FTS em doze perguntas de português/fórmulas, latência, PDF realmente extraído
com fonte na página 8, exclusão e reinício; isso é piloto pequeno de recuperação,
sem certificação de qualidade matemática geral.

Resultado desta entrega: **157 testes Python aprovados**, 10 opcionais Tk
ignorados, **21 testes React aprovados** e fluxo Qt simulado/real. No piloto
real, a busca híbrida acertou o primeiro resultado em **10/12** perguntas versus
**5/12** de FTS; indexação de dez trechos em **5,45 s** e latência mediana
**1,24 s**, incluindo chamadas locais e a comparação textual. Houve dois erros:
o reforço lexical de termos genéricos priorizou limite em vez de derivada, e
uma pergunta abstrata de correspondência priorizou conjuntos em vez de bijeção.
Esses resultados ficam registrados sem transformar falhas em aprovações.
Amostras de RAM disponível e swap constam no relatório; a medição de VRAM
não esteve disponível no namespace deste aceite. Outros aplicativos também
contribuem para os números de memória do sistema.

## Continuidade

Ampliar avaliação com apostilas e fórmulas reais, medir acervos maiores e testar
Windows. Resumos opcionais de conversa, reranker e busca vetorial aproximada
permanecem futuros; a transcrição e o histórico recente continuam preservados.
L3 acrescentará verificadores de matemática e gráficos locais; páginas exportáveis
(L4) e visão/ilustrações (L5) seguem o planejamento próprio.
