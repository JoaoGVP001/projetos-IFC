> O produto agora se chama CadernoMat. Consulte PLANEJAMENTO.md para a evolucao para chat e cadernos. O registro abaixo descreve etapas anteriores.

> Entrega de materiais (10/10/2026): veja docs/MATERIAIS.md. Instale requirements.txt
> atualizado (pypdf/pypdfium2), SQLite com FTS5 e Tesseract opcional. Dados pessoais
> continuam fora do Git; a migracao v4 cria backup v3. O atalho existente abre a
> versao nova ao reiniciar. Cadernos, embeddings e IA local permanecem planejados.

> Atualizacao em 10/10/2026: consulte PLANEJAMENTO.md e a secao Linux e instrutor
> com IA do README. Agora ha Resolver com IA, configuracao pela interface,
> tratamento de erros e 17 testes. A chamada real continua pendente de chave
> valida com creditos. O registro abaixo descreve a versao inicial.

# Guia de continuidade do Tutor de Calculo I

Este documento registra o estado do projeto em 02/10/2026 para continuar o
desenvolvimento em outro computador. O repositorio e privado:
https://github.com/JoaoGVP001/caderno-mat

## O que ja foi feito

- Aplicativo Python com interface desktop em CustomTkinter e menu alternativo
  no terminal.
- Modos **Resolver**, **Explicar** e **Corrigir**. A interface permite carregar
  um exemplo, limpar a entrada e copiar a resolucao.
- Analise local de continuidade de funcoes por partes usando SymPy. O programa
  calcula o valor da funcao no ponto, os limites laterais e conclui se ela e
  continua, explicando os passos.
- Integracao preparada com a API da OpenAI para perguntas abertas, explicacoes
  e correcao de tentativas. O modelo padrao esta configurado em `ia.py` e pode
  ser alterado por `OPENAI_MODEL`.
- Nove testes automatizados passaram. Os testes da integracao usam um cliente
  simulado; **a chamada real a API ainda nao foi testada**.
- `README.md` contem as instrucoes de uso e um exemplo de entrada.

Exemplo que funciona sem API no modo Resolver:

```text
f(x) = {
sen(x)/x, se x diferente de 0
0, se x = 0
}
em x = 0
```

Nesse caso, o limite e 1 e o valor da funcao no ponto e 0; portanto, ela nao
e continua em `x = 0`.

## Como continuar no notebook Windows

Instale Python 3.12 com Tkinter e Git. No PowerShell:

```powershell
git clone https://github.com/JoaoGVP001/caderno-mat.git
cd caderno-mat
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m tutor_calculo.desktop
```

Para usar o menu de terminal, substitua o ultimo comando por:

```powershell
.\.venv\Scripts\python.exe -m tutor_calculo.app
```

O script `iniciar_desktop.ps1` foi criado para a instalacao de Python desta
maquina original. No notebook, prefira o comando direto acima.

## Chave da API e privacidade

O arquivo `.env` local esta vazio e nao e versionado. Portanto, o exemplo de
continuidade funciona, mas perguntas abertas nos modos Explicar/Corrigir ainda
nao funcionam sem configurar uma chave. Quando decidir usar a API, crie uma
chave no painel da OpenAI e coloque no arquivo `.env` na raiz do projeto:

```text
OPENAI_API_KEY=sua_chave_aqui
```

Nao envie a chave por chat nem a inclua em commits. `.env` e `.venv` estao no
`.gitignore`. A chave criada anteriormente no painel nao foi salva neste
projeto; se nao for usada, revogue-a no painel da OpenAI. O uso da API pode
gerar cobrancas conforme a conta. A chave da API e separada da assinatura do
ChatGPT.

## Limitacoes e proximos passos

1. O analisador local reconhece apenas um subconjunto de expressoes e funcoes
   por partes cujas condicoes comparam `x` com o ponto indicado. Outros tipos
   de exercicio dependem da API.
2. Quando houver chave e credito disponivel, testar uma pergunta real na
   interface e verificar mensagens de erro, acesso ao modelo e custo.
3. Ampliar a resolucao local, com testes, para limites indeterminados, limites
   laterais, limites no infinito e derivadas.
4. Refinar as explicacoes pedagogicas e tratar mais formas de enunciado.

Para enviar novas alteracoes do notebook ao repositorio privado:

```powershell
git status
git add <arquivos-do-projeto>
git commit -m "Descreva a alteracao"
git push origin main
```

Antes de cada commit, confira `git status` para nao incluir dados pessoais ou
segredos. Ao voltar para esta maquina, execute `git pull origin main` dentro
do repositorio.
