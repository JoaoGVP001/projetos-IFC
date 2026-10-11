## Atualização — atividades e tentativas (11/10/2026)

Leia docs/ATIVIDADES.md. SQLite v6, backup v5 e migração transacional. Editor
manual offline, 4 formatos, autosave/posição, versões imutáveis e histórico.
Correção determinística, revisão manual separada, propostas/dicas/feedback com
Gemini/OpenAI opcionais. Prévia persistente e fontes sempre explícitas. Integração
com chats/materiais conserva IDs e arquivos. Atividades são arquivadas, sem
exclusão definitiva. Dados pessoais permanecem fora do Git.

Novos serviços: atividades.py, tentativas.py, correcao.py e estudo.py. DTOs e
interface em frontend/src/activities-model.ts e Activities.tsx. Não adicione SQL
ou acesso a provedores ao React. Compilar com pnpm build, abrir pelo atalho.
Testes atuais: 116 Python, 15 frontend, pnpm e2e e pnpm e2e:atividades (Qt real,
IA simulada). Documentação anterior abaixo registra a migração visual já entregue.
Próxima etapa: provas/simulados; depois flashcards, qualidade matemática e
exportação. Embeddings e IA local continuam por último.

# Continuidade do CadernoMat — 11/10/2026

## Estado atual e próxima entrega

A interface desktop foi migrada para React + TypeScript + Vite + Tailwind,
com pywebview/Qt. Chats, cadernos, biblioteca, RAG textual, matemática local e
Gemini/OpenAI foram preservados. Markdown/KaTeX, dois temas, lateral recolhível,
menus por teclado e prévia do envio seguem um sistema visual comum.

O pacote permanece tutor_calculo, banco SQLite v5 e repositório caderno-mat.
Não houve nova migração de esquema nesta entrega. Atividades e tentativas por
caderno são a próxima etapa; provas/simulados, busca semântica e IA local vêm
depois, conforme [Planejamento](PLANEJAMENTO.md).

## Atualizar e abrir

Feche a janela, execute git pull origin main, instale requirements.txt e abra
pelo atalho CadernoMat ou ./iniciar_desktop.sh. Assets compilados estão no Git;
usuários não precisam de Node. Windows usa o script iniciar_desktop.ps1 com
.venv\Scripts\python.exe e WebView2, ainda pendente de validação real.

Python 3.12+, pywebview e, neste Linux, PySide6/Qt WebEngine. Tkinter não é
necessário para a interface nova; requirements-legado.txt e --legado permitem
abrir a versão anterior. Não abra as duas interfaces no mesmo banco ao mesmo
tempo. Tesseract é opcional para OCR; não foi instalado nenhum modelo local.

Para editar a interface: Node 24/pnpm 11, pnpm install --frozen-lockfile,
pnpm test e pnpm build na pasta frontend. Reinicie com --debug para verificar
na WebView. O Vite no navegador não possui a ponte Python.

## Arquitetura, persistência e cuidados

[Interface](docs/INTERFACE.md) descreve os contratos e a estratégia de threads.
[Design](docs/DESIGN.md) define tokens/componentes.
[Materiais](docs/MATERIAIS.md) e [Cadernos](docs/CADERNOS.md) registram regras.

servico.py coordena operações e tarefas; ponte.py expõe somente request e usa
seletor nativo. Cada operação cria e fecha sua conexão SQLite na própria thread.
Mutação e snapshots usam RLock; tarefas gravam com conexão própria. Não desative
check_same_thread. Não exponha shell, SQL, caminhos ou chaves à interface.
Ao fechar, salve o rascunho fora do callback síncrono Qt antes de destruir a
janela, para evitar deadlock.

armazenamento.py, cadernos.py, materiais.py, extracao.py, links.py, ia.py e
app.py mantêm regras existentes. desktop_legado.py e componentes Tk são apenas
compatibilidade. Atividades futuras devem usar IDs estáveis de caderno e
preservar versões de tentativas.

Arquivos, banco, índices e interface.json ficam no diretório CadernoMat do
usuário, fora do Git. Para backup, feche a janela, espere terminar qualquer
worker e copie a pasta de dados. Chaves continuam no .env protegido/ignorado.
Seleção documental é independente por chat; associação a matéria nunca autoriza
envio. Contexto pedagógico, histórico e trechos aparecem separados na prévia.

## Validação e limites

88 testes Python (12 novos de serviço/ponte), 9 testes frontend e fluxo E2E na
janela Qt com IA simulada passaram. Conferidos fechamento/reinício, cadernos,
movimentação, arquivo/restauração, processamento, fontes, sanitização, teclado,
temas e 1000 × 650. Capturas em docs/screenshots usam dados fictícios.

Execute unittest discover -s tests, pnpm test e pnpm e2e. O E2E exige Linux
gráfico/Qt e cria banco temporário. Testes Tk históricos são opcionais sem Tk.
Não faça chamadas reais nos testes nem publique dados pessoais ou credenciais.

Não há streaming/cancelamento, instalador, autoatualização ou virtualização de
históricos extensos. Consultas já iniciadas podem terminar e salvar após fechar;
extração conserva o timeout de 150 segundos. Windows/macOS não foram executados.

---

## Registro historico da fase inicial (nao descreve o estado atual)

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
