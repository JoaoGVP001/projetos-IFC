# CadernoMat

Assistente pessoal de estudos de matematica em Python, com foco inicial em
Calculo Diferencial e Integral I e Matematica Discreta. A janela
desktop recebe exercicios e mostra a resolucao. Funcoes por partes no formato
abaixo sao analisadas localmente com SymPy; duvidas abertas e correcao de
tentativas usam a API do Gemini ou da OpenAI, conforme o servico escolhido.

## Evolucao planejada

O projeto esta evoluindo para um chat com historico, cadernos por materia,
listas, provas de pratica e simulados. A versao atual ja tem chats com historico
local e contexto recente; cadernos e atividades ainda estao planejados.
Ja e possivel anexar arquivos/links, organizar a biblioteca Materiais, pesquisar
texto extraido e selecionar materiais para consultas com citacoes.
Veja [o planejamento completo](PLANEJAMENTO.md) e o
[registro da fase inicial](HISTORICO_DESENVOLVIMENTO.md).

O pacote interno continua chamado `tutor_calculo` para preservar os comandos
de inicializacao. O nome visivel do produto e CadernoMat.

## Instalacao

Use Python 3.12 com Tkinter. Na pasta deste repositorio, crie o ambiente virtual
e instale as dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Na maquina onde o projeto foi iniciado, o ambiente `.venv` ja esta instalado.
Para abrir a interface desktop nela, execute:

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar_desktop.ps1
```

Em outra instalacao de Python com Tkinter, tambem e possivel abrir diretamente:

```powershell
.\.venv\Scripts\python.exe -m tutor_calculo.desktop
```

Para usar o menu de terminal:

```powershell
.\.venv\Scripts\python.exe -m tutor_calculo.app
```

## API da OpenAI (opcional, paga por uso)

Para os modos **Explicar**, **Corrigir** e perguntas abertas em **Resolver**,
crie um arquivo `.env` na raiz deste repositorio com:

```text
OPENAI_API_KEY=sua_chave_aqui
```

O arquivo `.env` esta no `.gitignore` e nao deve ser enviado ao GitHub. Tambem
e possivel configurar `OPENAI_API_KEY` como variavel de ambiente; ela tem
prioridade sobre o arquivo. O modelo padrao e `gpt-6-astra`; para usar outro,
defina `OPENAI_MODEL` no mesmo arquivo. A API exige uma chave propria da
[plataforma OpenAI](https://developers.openai.com/api/docs/quickstart).

## Exemplo de continuidade

No modo **Resolver**, digite:

```text
f(x) = {
sen(x)/x, se x diferente de 0
0, se x = 0
}
em x = 0
```

O programa compara `f(0)` com os limites laterais. Nesse exemplo, os dois
limites valem `1`, mas `f(0) = 0`; portanto, a funcao nao e continua em `0`.
O botao **Carregar exemplo** preenche esse enunciado automaticamente.

O analisador local aceita expressoes com `x`, numeros, `+`, `-`, `*`, `/`, `^`,
`sen(x)`, `cos(x)`, `tan(x)`, `exp(x)`, `log(x)` e `sqrt(x)`. Nesta versao, as
condicoes dos ramos devem comparar `x` com o ponto indicado. Para outros
enunciados, use a API.

## Testes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes automatizados da integracao com a API usam um cliente simulado e nao
consomem creditos. Uma chamada real depende da chave configurada no `.env`.

## Linux e instrutor com IA

No Ubuntu, use Python com Tkinter (`python3-tk`) e prepare o ambiente:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./iniciar_desktop.sh
```

1. Clique em **Configurar IA** e escolha Gemini ou OpenAI e cole a chave desse servico no campo protegido.
   O aplicativo salva a chave somente no `.env` local, ignorado pelo Git.
   Salvar nao faz uma consulta e nao confirma o acesso ao modelo.
2. Selecione **Resolver com IA**, digite o enunciado e clique no botao de envio.
   Esse modo pede ao instrutor que interprete o exercicio, verifique as hipoteses
   e explique a resolucao. Se faltarem dados, ele deve pedir esclarecimento.
3. Use **Explicar** para duvidas conceituais ou **Corrigir** para enviar o
   enunciado junto com sua tentativa. No desktop, mensagens recentes da mesma conversa sao enviadas como contexto;
   use Novo chat para iniciar um assunto independente.

**Resolver** continua usando o analisador local para funcoes por partes no
formato suportado; perguntas abertas nesse modo usam a API. Para garantir que
um enunciado seja interpretado pela IA, escolha **Resolver com IA**.

Tambem e possivel copiar `.env.example` para `.env` e editar os valores.
Variaveis de ambiente tem prioridade sobre o arquivo. O modelo continua sendo
`gpt-6-astra` e pode ser alterado em Configurar IA.

As consultas tem timeout de 60 segundos, sem repeticao automatica, e limite de
4096 tokens de saida. A aplicacao sinaliza respostas incompletas e apresenta
mensagens especificas para chave recusada, modelo sem acesso, limite de uso e
falhas de conexao. Ela solicita `store=False` na Responses API; isso nao altera
as demais politicas de tratamento de dados da OpenAI.

A assinatura do ChatGPT nao configura este aplicativo: ele utiliza a API e seus
creditos. Para criar ou conferir uma chave, acesse
[API keys](https://platform.openai.com/api-keys). Nao envie a chave pelo chat.

Testes no Linux, incluindo os casos de API simulada:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

O teste de falhas da interface exige Tkinter e e ignorado se ele estiver ausente. Nenhum teste automatico faz
chamadas reais ou consome creditos da API.


## Gemini gratuito ou pago e escolha do servico

Em **Configurar IA**, escolha **Gemini (gratuito ou pago)** ou **OpenAI (API paga)**.
Cada servico tem sua propria chave e modelo. Trocar o servico preserva a chave
anterior; deixe o campo de chave vazio para reutilizar uma chave ja configurada.
Todos os modos de IA usam o servico selecionado. O analisador local continua
funcionando sem chave. Nao ha troca automatica entre provedores apos falhas.

### Comecar sem pagar com Gemini

1. Abra [Google AI Studio — API keys](https://aistudio.google.com/apikey) e crie
   uma chave associada a um projeto **Free Tier**, sem ativar faturamento.
2. Em Configurar IA, escolha Gemini, cole a chave e mantenha o modelo inicial
   `gemini-3.8-flash`, ou informe outro modelo disponivel para sua conta.
3. Salve e envie um exercicio em Resolver com IA.

O uso gratuito tem cotas por modelo e projeto. Ao atingir uma cota, o app
apresenta um erro; ele nao ativa faturamento nem muda para OpenAI automaticamente.
No Free Tier, os dados enviados podem ser usados para melhorar produtos Google.
Confira [precos, modelos e tratamento de dados](https://ai.google.dev/gemini-api/docs/pricing).

Para Gemini pago, configure faturamento no projeto Google AI Studio e use a
chave desse projeto. **Escolher Gemini neste aplicativo nao determina nem
verifica o plano de cobranca**: ele depende do projeto e do modelo no Google.
Os botoes Obter chave e Planos e modelos abrem as paginas oficiais do servico.
O campo de modelo e editavel para usar modelos gratuitos ou pagos disponiveis.

Para OpenAI, configure uma chave propria e creditos de API conforme o modelo.
A integracao utiliza a API; nao faz login com a conta do ChatGPT.

Configuracao manual equivalente no `.env`:

```text
AI_PROVIDER=gemini
GEMINI_API_KEY=sua_chave_google
GEMINI_MODEL=gemini-3.8-flash
OPENAI_API_KEY=sua_chave_openai_opcional
OPENAI_MODEL=gpt-6-astra
```

Use `AI_PROVIDER=openai` para selecionar a OpenAI. Instalacoes antigas sem
AI_PROVIDER mantem OpenAI para compatibilidade. As variaveis de ambiente tem
prioridade sobre o `.env`, inclusive AI_PROVIDER. O cliente Gemini usa HTTPS
com chave no cabecalho, timeout de 60 segundos e nenhuma repeticao automatica.
A integracao com os provedores e de texto: arquivos e imagens sao interpretados
localmente, e somente trechos selecionados sao enviados. Veja a biblioteca abaixo.
Groq e modelos locais ficam para etapas futuras.

## Apresentacao das respostas

O painel renderiza titulos Markdown, negrito, listas, codigo em linha e formulas
LaTeX simples (`$...$`, `$$...$$`, `\(...\)` e `\[...\]`). As formulas sao
renderizadas localmente com MathText; nao e necessario instalar LaTeX.
Notacoes nao suportadas usam uma alternativa em texto, preservando a resposta.
Formulas longas sao reduzidas para caber na largura do painel no momento da
renderizacao. Copiar resolucao copia a resposta original completa, inclusive
Markdown/LaTeX, para reutilizacao em editores que suportem essa formatacao.

As instrucoes de Gemini e OpenAI pedem um Resumo e uma pergunta de pratica em
Sua vez ao concluir explicacoes. As respostas anteriores nao sao regeneradas;
a estrutura exata continua dependendo da resposta do modelo.


## Chats e armazenamento local

A barra lateral permite criar, alternar e renomear chats. O primeiro enunciado
vira o titulo automaticamente. Mensagens e rascunhos sao preservados ao trocar
conversas e fechar o aplicativo. Limpar entrada apaga apenas o rascunho; Copiar
conversa copia a transcricao completa em Markdown/LaTeX.

O banco `historico.sqlite3` fica no diretorio de dados do usuario:

- Linux: `~/.local/share/CadernoMat/` (ou `$XDG_DATA_HOME/CadernoMat`).
- Windows: `%LOCALAPPDATA%/CadernoMat/`.
- macOS: `~/Library/Application Support/CadernoMat/`.

O banco fica fora do repositorio e nao contem as chaves de API. Ha versao de
esquema e backup antes da criacao de esquema em um arquivo ja existente.

Nos modos de IA do desktop, ate dez pares completos recentes sao usados como
contexto, limitados a 16 mil caracteres. Mensagens de erro ficam fora; o historico
completo permanece no banco. O modo Resolver local e o menu de terminal seguem
sem memoria de conversa. Fechar durante uma consulta preserva a pergunta, mas
nao salva a resposta ainda em andamento. Cancelamento de consultas e streaming serao entregues depois.


### Busca, arquivamento e exclusao

A busca da barra lateral procura termos literais no titulo e nas mensagens.
Ver arquivados alterna a lista entre chats ativos e arquivados. Arquivar preserva
mensagens e rascunho; Restaurar permite continuar a conversa. Chats arquivados
ficam sem envio ate serem restaurados. Excluir pede confirmacao e remove o chat
e suas mensagens definitivamente; use Arquivar para preservar o historico.
A atualizacao do banco da versao 1 para 2 cria `historico.sqlite3.v1.backup`
antes da alteracao. Backup e banco ficam no diretorio local de dados do usuario.

### Acoes em cada chat

Ao passar o mouse sobre uma conversa, aparece o botao de tres pontos. Seu menu
permite renomear, fixar/desafixar no topo, arquivar/restaurar e excluir. As acoes
operam sobre o chat escolhido, inclusive quando ele nao e a conversa aberta.
Chats fixados aparecem primeiro e a escolha permanece apos reiniciar.
Titulos longos deslizam durante o hover e voltam ao inicio quando o mouse sai.
Tambem e possivel abrir o menu com o botao direito; Enter abre a conversa e
Espaco abre o menu quando a linha tem foco.

## Anexos e biblioteca Materiais

Use **+ Arquivo** ou **+ Link** no chat. A aba **Materiais** reune os uploads,
mostra tamanho, tipo, origem e processamento e oferece visualizacao, edicao de
materia/assunto/etiquetas, busca textual e filtros. Arquivos, texto e selecoes
persistem apos reiniciar; conteudos iguais reutilizam a mesma copia local.

Suportados: PDF textual, imagens com OCR opcional, TXT/Markdown/CSV/JSON/LOG/TEX,
DOCX e links publicos de HTML/texto/PDF. Outros formatos ficam armazenados, mas
nao sao interpretados pela IA. Limite de 20 MiB por arquivo; OCR exige Tesseract.

Marque **Consultar neste chat**, confira **Previa do envio** e pergunte em um
modo de IA. A recuperacao textual usa somente materiais marcados; Gemini/OpenAI
recebem trechos e referencias, sem os originais binarios. Desmarcar materiais
nao remove informacoes de respostas antigas do historico enviado. A biblioteca
funciona sem API; as consultas continuam sujeitas as cotas do provedor.

Leia [o guia de materiais](docs/MATERIAIS.md) para formatos, limites, OCR,
privacidade, citacoes, armazenamento e arquitetura. A migracao para SQLite v4
preserva chats e cria backup v3. Embeddings e busca semantica ficam para a
proxima fase; cadernos e IA local continuam planejados.
