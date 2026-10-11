# IA local integrada — L1

Entrega de 11/10/2026. O Ollama agora participa dos chats e serviços de estudo
na interface React do CadernoMat. O piloto de terminal continua separado.
O notebook Ubuntu/RTX 3050 Laptop 6 GB foi validado; Windows ainda requer aceite
no computador de casa. Não há embeddings, visão, gráficos ou imagens nesta fase.

## Usar

Abra **CadernoMat** pelo atalho habitual. Em **Configurações de IA**, escolha
**IA local · Ollama** e a tag `qwen3.5:4b-q4_K_M` instalada neste notebook.
Use **Testar conexão e listar modelos**, escolha 4.096 tokens e salve.
O perfil menor oferece 2.048 tokens; o tempo limite aceita 30–600 segundos.
A primeira resposta inclui o carregamento dos pesos e pode demorar mais.

“Somente esta conversa” conserva a escolha por chat. “Padrão” atende conversas
que herdam a configuração; “usar o padrão” remove a preferência específica.
Alterar o modelo não modifica respostas antigas, cadernos ou anexos. As respostas
registram provedor e modelo efetivamente utilizados.

O runtime deve estar em `http://127.0.0.1:11434` ou outra porta de loopback.
Não aceita host remoto, credenciais na URL, proxy ou redirecionamento.
**Iniciar runtime do piloto** inicia apenas a instalação previamente preparada
no diretório de dados deste notebook. Em outras máquinas, abra o Ollama instalado.
Esse botão não instala drivers, baixa modelos ou cria serviços de sistema.

O diagnóstico usa `/api/version`, `/api/tags`, `/api/ps` e `/api/show`. Verifica
pesos instalados e capacidade de texto; tags cloud e modelos com metadados
remotos são bloqueados. Capacidades anunciadas como visão/ferramentas não
significam que o aplicativo implementa esses recursos. A consulta usa a
[API nativa `/api/chat`](https://docs.ollama.com/api/chat), nunca um endpoint
OpenAI presumido. [Lista oficial de modelos](https://docs.ollama.com/api/tags).

Gemini/OpenAI continuam disponíveis com a chave pessoal de cada provedor.
Nenhum erro local troca para nuvem. Inclusive o fallback do botão **Resolver**
usa a seleção capturada da conversa; o exemplo de continuidade por partes
continua determinístico, via SymPy, sem consulta de IA.

## Contexto, materiais e prévia

A prévia mostra destino, modelo, instruções, contexto pedagógico, pergunta,
pares recentes completos e os trechos efetivamente escolhidos. O orçamento
local inclui todos esses textos, reserva de saída e margem de 256 tokens.
Sem tokenizer exato, a estimativa é bytes UTF-8/2 mais overhead de mensagens;
isso é uma aproximação conservadora, não garantia universal de contagem.
Fontes são priorizadas sobre histórico antigo, limitadas/abreviadas com aviso;
os IDs e páginas permanecem identificáveis. A pergunta não é truncada: se ela
e as instruções não couberem, a consulta é recusada antes do envio.

Reutiliza a extração/OCR e a busca FTS existentes. Somente materiais marcados
para o chat entram na recuperação. Nos serviços de estudo, a seleção é explícita
na prévia. Texto documental é dado não confiável, nunca autorização para shell,
URLs ou outros acessos. Falta de extração/relevância é informada; nenhuma leitura
de páginas ausentes é alegada. Citações inexistentes são sinalizadas pelo Python.
Os arquivos originais, imagens e PDFs completos não são enviados ao Ollama.

## Streaming, cancelamento e persistência

No chat local, o texto aparece progressivamente, identificado como parcial.
**Cancelar resposta** fecha a conexão ativa com o runtime. O texto já recebido
fica identificado como cancelado/incompleto, fora do próximo contexto.
Pesos podem continuar na memória pelo keep-alive de dois minutos.
Gemini/OpenAI mantêm o fluxo anterior, sem streaming/cancelamento nesta entrega.

**Repetir consulta** reutiliza a pergunta original sem duplicar a mensagem do
aluno. Cada requisição tem ID persistente; repetir o mesmo ID não gera outro
envio. Alterações de configuração ou desmarcação/exclusão de fontes exigem nova
prévia. Rascunhos posteriores são preservados. Interrupção do processo recupera
a consulta como incompleta na próxima abertura, sem chamar o provedor novamente.

SQLite **v7** cria backup **v6**, aplica DDL transacional e acrescenta `chat_ia`
e `consultas_ia`. IDs, mensagens, versões/tentativas e índices anteriores são
conservados. Consultas guardam snapshots, estado, parcial, proveniência e métricas.
As preferências sem chaves ficam em `ia.json` no diretório de dados; chaves
online continuam no `.env` protegido. Nada disso entra no Git.

## Atividades, dicas e feedback

O perfil local aceita gerar **1–3 questões** em lista curta, nos quatro formatos
existentes. Usa esquema JSON de tipos/formatos e o validador Python existente.
JSON inválido, limite de saída ou cancelamento não viram atividades concluídas.
Uma proposta válida precisa ser revisada e salva explicitamente no editor.
Dicas e feedback ficam vinculados à tentativa, com provedor/modelo registrados.
O fluxo manual e a correção determinística continuam disponíveis offline.

O modelo permanece experimental em matemática. No aceite inicial, o gabarito
de 2+2 estava certo, mas o feedback inventou uma analogia falsa envolvendo o
conjunto `{2,2}` e inferiu raciocínio não apresentado pelo aluno. O prompt foi
reduzido e restringido à evidência observada, sem declarar domínio a partir de
uma alternativa. Isso não substitui os avaliadores/verificadores de L3.
Respostas e gabaritos de IA continuam exigindo revisão.

O teste numérico da alternativa aceita os delimitadores `$...$` permitidos
pelo produto, registra o valor original e remove apenas esses delimitadores
para conferir 2+2. Essa normalização do aceite não altera a avaliação estrita
do [piloto inicial](PILOTO_LOCAL.md).

## Validação e reprodução

Testes Python cobrem endpoint restrito, modelo remoto camuflado, orçamento,
HTTP streaming fragmentado, cancelamento de socket bloqueado, idempotência,
repetição sem usuário duplicado, recuperação, preferências por chat, migração
v6/rollback/backup, RAG, geração/dicas/feedback e ausência de fallback online.
Os testes anteriores Gemini/OpenAI continuam ativos.

Interface: testes React, build e três fluxos Qt com dados fictícios — chat e
materiais, atividades, integração Ollama com HTTP simulado. O aceite **real**
também passou na janela Qt com modelo instalado, RAG/citação, cancelamento,
repetição e reinício. A rede externa estava bloqueada por namespace Linux;
o sandbox WebEngine foi mantido. Os aplicativos do usuário mantiveram sua rede.
Geração de uma questão 2+2, dica, feedback e reinício usam o serviço real em um
banco temporário no mesmo isolamento. Não são um benchmark de qualidade geral.

Resultado: **137 testes Python aprovados**, 10 testes opcionais do Tk legado
ignorados e **18 testes React aprovados**. Build e fluxos Qt anteriores passaram.
No banco pessoal, a migração v6→v7 conservou o conteúdo das 20 tabelas existentes,
com integridade referencial válida e `.env` inalterado. Neste notebook, Ollama
foi definido como padrão; preferências específicas de conversas prevalecem.

O aceite de estudo conserva a proposta bruta e registra separadamente se o
pedido 2+2 e seu gabarito foram atendidos. Para exercitar persistência, dicas e
feedback, simula explicitamente a revisão obrigatória no editor, salvando a
questão conhecida e a alternativa 4 no banco fictício. Isso não certifica a
proposta original. A rodada final acertou esse gabarito, mas o feedback ainda
teve uma observação pedagógica inadequada; qualidade matemática/pedagógica
continua pendente de avaliação independente em L3.

```bash
.venv/bin/python -m unittest discover -s tests -v
cd frontend
pnpm test
pnpm build
pnpm e2e
pnpm e2e:atividades
pnpm e2e:local
```

Aceite real, opcional e sem download (exige Node no PATH, sessão gráfica, modelo
preparado, `unshare --keep-caps`, `ip` e CUDA funcionando):

```bash
scripts/testar_integracao_offline_linux.sh
# Apenas a geração/dica/feedback de estudo:
scripts/testar_integracao_offline_linux.sh --so-estudo
```

O isolamento usa o UID atual, sem mapear o Qt para root ou desativar seu sandbox.
Os relatórios fictícios do estudo ficam em `ia-local/relatorios/`, fora do Git.
As capturas `local-*-real.png` mostram o modelo real com dados fictícios.
Não contêm chaves ou dados pessoais.

## Próximas etapas

Medir o PC Windows separadamente. Expandir a avaliação matemática independente
e ferramentas verificáveis; embeddings/busca híbrida são L2, cálculos/gráficos
L3, páginas exportáveis L4 e visão/ilustrações L5. Segunda opinião online continua
uma escolha explícita: trocar provedor, conferir nova prévia e enviar.
