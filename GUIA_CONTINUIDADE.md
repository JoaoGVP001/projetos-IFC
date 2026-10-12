Para continuar em outra máquina, leia primeiro o
[resumo completo e transferência para o PC de casa](docs/TRANSFERENCIA_PC_CASA.md).
Ele consolida as entregas; as seções abaixo preservam o histórico de cada fase.

## Entrega atual — calibração por tarefa (12/10/2026)

Leia docs/CALIBRACAO_IA_LOCAL.md. avaliacao_local.py usa a fachada/orçamento real,
casos fictícios e contratos de atividade/página. Modelos já instalados, máximo
12 consultas/1800 s, checkpoints privados/atômicos, erros/parciais e rubricas
pendentes; não chamar stop/JSON válido de correção matemática. Perfil/configuração
pessoal e acervo não mudam. Roteamento de instruções para saudações exatas evita
converter “Olá” em aula; pedidos com assunto adicional seguem a tarefa normal.

Doze gerações em três rodadas CPU offline, incluindo falhas matemáticas em JSON.
Páginas agora capturam formulas_protegidas na prévia: preservar presença literal
de matemática marcada, ignorando espaços/código, nunca equivalência simbólica.
validar_proposta recusa omissão/reescrita sem mudar rascunho/versões. Legado sem
esse campo continua legível. Novas afirmações ainda podem estar erradas mesmo
com as originais presentes: revisão explícita permanece obrigatória. Sem DDL,
SQLite v11. Não tentar consertar texto da IA automaticamente. 4B continua sem
aceite de fidelidade para página na última rodada. CPU/GPU seguem como antes.

Aceite: 232 Python aprovados/dez opcionais ignorados; Qt com recusa visível,
rascunho e versão preservados, depois proposta válida, PDF/PNG e reinício.
Sem alteração React/CSS/assets; os testes de interface da entrega anterior
continuam referência, sem alegar uma nova rodada dos oito fluxos.

## Entrega atual — estabilidade local (12/10/2026)

Leia docs/ESTABILIDADE_IA_LOCAL.md. SQLite permanece v11. Adapter Ollama guarda
métricas em erros/cancelamentos via exceções tipadas; não misturar erro com texto.
Historico expõe aviso/partes de forma compatível, sem reescrever mensagens antigas.
Perfis em desempenho.py; configurações anteriores são legado, sem sobrescrita.
JSON tem reserva mínima própria; validação de orçamento continua obrigatória.
continuacao.py usa prévia/snapshot/idempotência e revalida configuração/fontes;
perfil curto só vale naquela chamada. Gemini/OpenAI sem streaming também podem
continuar. Não colocar texto parcial no histórico normal ou em system prompt.

Ilustração de indução em worker limitado, sem prova universal, reutiliza IDs/PNGs
L3 e páginas/exportação L4. Rótulos são texto, nunca SVG/comandos gerados. UI em
LocalStudy.tsx separa aviso, métricas, prévia e imagem; fonte da parte é navegável.
Operações pesadas são coordenadas; FTS disponível com aviso quando runtime ocupado.

Aceite real CPU com rede externa bloqueada: respostas 83/95/46 s e confirmação
com caderno completo 99 s/488 tokens. Ganho é resposta menor e terminada; tokens/s
não melhoraram. Relatórios privados fora do Git. Não tocar driver/kernel: módulo
NVIDIA instalado para ABI diferente do kernel ativo; GPU ainda não foi recuperada.
Candidato 1.7B documentado, sem download/benchmark automático. Windows não testado.
Aceite: 218 Python/dez opcionais ignorados, 35 React, oito fluxos Qt; 33 tabelas
e nove arquivos/configurações pessoais iguais por hash.

## Entrega atual — páginas de estudo L4 (11/10/2026)

Leia docs/PAGINAS_ESTUDO.md. SQLite v11, backup v10, seis tabelas próprias; não
confundir paginas_estudo com paginas da extração. paginas.py valida rascunhos,
conflitos e versões; paginas_servico.py coordena origens, IA, biblioteca e jobs.
StudyDocument.tsx compartilha prévia/exportação, com Markdown sanitizado,
KaTeX validado, A4 e paginação de tabelas. exportar_paginas.py roda Qt isolado,
HTTP somente loopback/token, printToPdf e PNG por PDFium. Não imprimir o DOM
de chat arbitrário nem depender de API de impressão do WebView2 sem teste.

Originais L3 são copiados/conferidos e nunca editados. Exportar só versão salva;
rascunho é independente. IA exige seções/fontes selecionadas, prévia e aplicação
explícita; proposta não salva versão. Soluções ocultas continuam protegidas.
Biblioteca recebe Markdown revisado, sem chat/fonte/embeddings automáticos e
com origem em todos os trechos, inclusive recuperação híbrida. Preservar os
snapshots/arquivos e a distinção entre resultados locais e texto do usuário/IA.

Fechamento drena a fila de autosave e mantém janela aberta em falha. Processos
longos não seguram o lock SQLite. Cancelamento/falha não publica conclusão.
Comandos: unittest, pnpm test/build/e2e:paginas, aceite_paginas_exportacao.py e
scripts/testar_integracao_offline_linux.sh --paginas. Windows não foi testado.
Aceite L4: 207 Python aprovados/dez opcionais ignorados, 33 React, build, seis
fluxos Qt e catorze folhas inspecionadas. Ollama real offline ~72 s, proposta
revisável/exportação e versão anterior preservadas. Migração pessoal v10 → v11
conferiu 27 tabelas antigas/nove arquivos, seis materiais/678 trechos/vetores.

Próximas melhorias: L5, zoom/orientação/quebra de blocos grandes, qualidade de
organização do modelo e empacotamento. Nenhuma geração artística ou treinamento.

## Entrega atual — Matemática Discreta L3 (11/10/2026)

Leia [docs/DISCRETA.md](docs/DISCRETA.md). SQLite v10 com backup v9 acrescenta
questão/tentativa/proposta e comparação separada em calculos. Motor discreta.py
com parser próprio e worker encerrável; discreta_servico.py reutiliza Calculos,
artefatos e provedores. DiscreteTools.tsx exige prévia manual, salva/exporta
resultados e integra fontes/atividades. Não usar eval/exec nem substituir provas
por checagem finita. Propostas copiam somente campos explícitos do pedido ou
fontes incluídas; referência da proposta preserva os materiais consultados.
Comparar gabarito só após revelar/finalizar; jamais sobrescrever notas/snapshots.

Aceite: 196 Python aprovados/10 legados ignorados, 27 React, build e fluxos Qt
Discreta/Cálculo/atividades/chat. Ollama real em namespace sem rede externa,
proposta ~30 s e explicação ~46 s, resultado e PNG preservados ao reiniciar.
Migração pessoal preservou as 26 tabelas e arquivos/configurações, incluindo os
seis materiais/678 trechos do Classroom. Relatórios pessoais fora do Git.
L4 foi entregue acima com composição local e PDF paginado.
Windows ainda precisa de teste real. Atalho CadernoMat permanece o mesmo.

## Entrega atual — matemática local L3 (11/10/2026)

Leia docs/MATEMATICA_LOCAL.md. SQLite v9 com backup v8; calculos.py gerencia
snapshots/artefatos, ferramentas_matematicas.py roda isolado, MathTools.tsx
apresenta formulário/PNG/proposta/explicação. Não avaliar strings como Python.
Preservar árvore original/domínio, tempos/limites, versões e estados separados
de cada operação. Propostas só copiam função/intervalo/ponto explícitos; não
executar automaticamente documentos nem números inventados pelo modelo.
PNG por IDs/hash fora do Git; falhas/cancelamentos não publicam conclusão.
Atalho usa a interface compilada. Discreta e páginas L4 estão entregues acima;
SVG independente continua futuro.
Aceite: 175 Python aprovados/10 opcionais ignorados, 24 React, cinco fluxos Qt.
Comandos: unittest, pnpm test/build/e2e:matematica e aceite Ollama offline em
scripts/testar_integracao_offline_linux.sh --matematica; Windows não foi testado.

## Entrega atual — busca híbrida local L2 (11/10/2026)

Leia [docs/BUSCA_SEMANTICA.md](docs/BUSCA_SEMANTICA.md). Novo semantica.py usa
Qwen3-Embedding 0.6B pela API nativa local, CPU/lotes de quatro. SQLite v8 cria
backup v7 e quatro tabelas separando preparação/publicação. Indexar/retomar é
explícito, cancelável, incremental; não autoriza documentos automaticamente.
Busca híbrida usa FTS + cosseno exato + RRF com IDs filtrados antes de comparar.
Preservar hashes, extrator/perfil, tag/digest e dimensão; mudança exige reindexar.
FTS permanece disponível com aviso em falhas. Exclusão/reprocessamento limpa
vetores. React expõe modo de busca, status/progresso, filtros e estratégia na
prévia de chat/estudo. Não adicionar acesso direto ao runtime/SQL no navegador.
Resumos de conversas continuam opcionais para depois; transcrição é preservada.
Próxima entrega técnica: L3, cálculos verificáveis e gráficos, conservando parser
restrito e execução custosa encerrável. Windows ainda precisa de teste real.

## Entrega atual — Ollama integrado (11/10/2026)

Leia [docs/OLLAMA.md](docs/OLLAMA.md). SQLite v7 com backup v6, chat_ia e
consultas_ia; preservar v6, fontes, atividades e tentativas. Ollama agora pode
ser configurado por conversa ou como padrão, sem chave. Metadados/capacidades,
streaming, cancelamento, repetição idempotente e recuperação de parciais.
Orçamento explícito 2K/4K e RAG textual; estudo local 1–3 questões com esquema
JSON, validador, dicas e feedback. Gemini/OpenAI mantêm seu fluxo e não são
fallback. Resolver respeita a escolha capturada inclusive fora do analisador.

Novos módulos: provedores/contratos.py, ollama.py e esquemas.py;
preferencias_ia.py e recuperacao.py; ConfigIA.tsx no React. Dados/chaves/pesos
continuam fora do Git. Somente o runtime previamente preparado pode ser iniciado
pelo botão; não permitir downloads/shell arbitrários por conteúdo documental.
Aceite real Qt em namespace sem rede externa, sandbox ativo; retomada e
cancelamento validados. Aceite de estudo é estrutural com revisão explícita:
respostas do modelo não são certificadas matematicamente. Verificação matemática,
embeddings, gráficos e páginas exportáveis vêm nas etapas seguintes; Windows
precisa de teste no PC real. O atalho CadernoMat abre os assets compilados novos.

## Registro anterior — piloto no notebook (11/10/2026)

Leia [docs/PILOTO_LOCAL.md](docs/PILOTO_LOCAL.md). Ollama 0.40.3 e Qwen3.5-4B
Q4_K_M instalados fora do Git neste Ubuntu/RTX 3050 Laptop 6 GB/RAM classe 8 GB.
Duas rodadas offline reais: 10/14 baseline e 15/18 no perfil revisado. Chat de
terminal utilizável pelo atalho separado IA Local - Testes. Código em
piloto_local.py, launcher iniciar_ia_local.sh e scripts/benchmark_offline_linux.sh.
13 novos testes; 119 aprovados na suíte, 10 opcionais Tk ignorados.

Nenhuma mudança no banco pessoal ou na seleção Gemini/OpenAI. Esse piloto de terminal permanece independente; a integração
posterior está registrada no início deste arquivo. Erro lógico e falhas de formato documentados; priorizar
consistência/verificação. O plano e o diagnóstico Windows permanecem abaixo.

## Registro anterior — planejamento no Windows (11/10/2026)

Leia [docs/IA_LOCAL.md](docs/IA_LOCAL.md) antes da próxima implementação desta
trilha. PC de casa: Windows, 16 GB RAM e RTX 3060 com 8 ou 12 GB VRAM ainda a
confirmar. Conservar React/pywebview, SQLite v6, cadernos, materiais e tentativas.
Integrar Ollama por API local; começar com diagnóstico/piloto e chat completo,
reusar RAG textual, adicionar embeddings depois, então gráficos/páginas de
caderno e, por último, visão/ilustrações opcionais. Sem fork no MVP ou troca
automática para nuvem. O documento registra candidatos, fontes e critérios.

Somente documentação foi alterada nesta revisão. Não há runtime/modelo local
instalado ou integração nova. Windows/WebView2 ainda precisa de validação real.
Provas/simulados continuam no backlog. Os registros de entregas abaixo indicam
o que já funciona; o plano local substitui sua antiga posição obrigatória final.

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
Backlog de produto: provas/simulados, flashcards, qualidade matemática e
exportação. A nova trilha de IA local é detalhada no início deste guia.

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
