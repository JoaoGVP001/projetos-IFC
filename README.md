# Tutor de Calculo I

Aplicativo em Python para estudar limites, continuidade e derivadas. A janela
desktop recebe exercicios e mostra a resolucao. Funcoes por partes no formato
abaixo sao analisadas localmente com SymPy; duvidas abertas e correcao de
tentativas usam a API da OpenAI.

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

## API da OpenAI

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

1. Clique em **Configurar IA** e cole sua chave da API no campo protegido.
   O aplicativo salva a chave somente no `.env` local, ignorado pelo Git.
   Salvar nao faz uma consulta e nao confirma o acesso ao modelo.
2. Selecione **Resolver com IA**, digite o enunciado e clique no botao de envio.
   Esse modo pede ao instrutor que interprete o exercicio, verifique as hipoteses
   e explique a resolucao. Se faltarem dados, ele deve pedir esclarecimento.
3. Use **Explicar** para duvidas conceituais ou **Corrigir** para enviar o
   enunciado junto com sua tentativa. Cada envio e uma consulta independente;
   inclua o contexto necessario, pois ainda nao ha historico de conversa.

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
