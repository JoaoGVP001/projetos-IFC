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
