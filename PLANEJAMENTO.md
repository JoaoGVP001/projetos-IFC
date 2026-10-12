# CadernoMat — planejamento de produto e desenvolvimento

Atualizado em 12/10/2026.

## Próxima entrega proposta — organização fiel e qualidade

Plano detalhado em [Prompt da próxima etapa](docs/planejamentos/PROMPT_FIDELIDADE_E_QUALIDADE.md).
Entregar primeiro organização local que preserve texto/ordem/fórmulas/recursos,
depois assistência opcional por IDs de blocos, evitando regeneração da resolução.
Avaliar precisão, escapes, orçamento e desempenho por tarefa; GPU administrativa
em trilha separada, sem bloquear CPU. Conservar RAG, atividades, versões e dados.
Essa etapa ainda não está implementada; a calibração abaixo é sua evidência de partida.

## Entregue — calibração por tarefa no notebook

Continuar a estabilidade publicada em 1bcbaba: avaliação reproduzível pela mesma
fachada e orçamento usados no aplicativo, com casos fictícios de indução,
Cálculo, Discreta, consulta documental e JSON. Comparar somente modelos locais
já instalados, sem mudar configuração pessoal, baixar pesos ou alterar drivers.
Limitar chamadas/tempo, salvar resultados e parciais atomicamente fora do Git,
registrar carga/dispositivo antes e durante cada consulta. Separar contrato JSON,
gabarito pontual e revisão matemática da narrativa; não certificar por keywords.

Doze respostas reais offline em CPU, com revisão separada da conclusão do
runtime. Corrigidas orientações de domínio/metadados e a tarefa de saudação
(22 tokens/~6,5 s no último caso). JSON de página revelou alteração matemática:
novas propostas preservam notação marcada da origem e são recusadas se a omitirem
ou reescreverem. Isso não verifica equivalência, prosa ou fórmulas adicionais.
O 4B ainda falhou nesse contrato; geração matemática de páginas exige revisão.
232 testes Python aprovados/dez opcionais ignorados e fluxo Qt de páginas com
erro, rascunho/versão preservados, proposta válida e PDF/PNG. GPU segue indisponível no kernel 7.0.0-38;
reconferida em 12/10, sem mudança administrativa. Windows permanece preparado
em docs/TRANSFERENCIA_PC_CASA.md, sem bloquear a continuidade no notebook.
[Protocolo, resultados e limitações](docs/CALIBRACAO_IA_LOCAL.md).

## Entregue — estabilidade da IA local

Métricas preservadas nas interrupções, avisos separados do Markdown, perfis de
saída por tarefa, continuação/repetição curta explícita com prévia e fontes
autorizadas. Diagnóstico CPU/GPU/memória, benchmark em CPU e ilustração local
limitada de indução reutilizando artefatos e páginas L4. Sem alterações
administrativas: o módulo NVIDIA não está disponível para o kernel ativo.
Resposta de indução completada no piloto em CPU (~99 s / 488 tokens), com
rede externa bloqueada, sem promessa de imagem inexistente. Mantém v11,
configuração antiga e versões L4. Limites e medições detalhados em
[Estabilidade da IA local](docs/ESTABILIDADE_IA_LOCAL.md). Comparação com modelo
menor e correção administrativa do driver seguem separadas.

## Entregue — L4: páginas de estudo e exportação

Editor por caderno com seções Markdown/KaTeX, busca, arquivo/duplicação,
rascunhos com revisão e versões independentes. Prévia no chat e na área de
páginas; origens de mensagens/cálculos/questões, recursos congelados por hash e
proteção de soluções ocultas. SQLite v11 com backup v10; preserva a tabela
paginas da biblioteca. Fechamento drena autosave e mantém o editor aberto em
falha. Exportação isolada/cancelável, A4 paginado, tabelas com cabeçalhos
repetidos, PDF selecionável e PNGs. Valores/hipóteses/verificações L3 não mudam.

Proposta JSON revisável nos três provedores, seções/fontes explícitas e prévia;
nenhuma alteração automática do rascunho, gabarito ou nota. Inclusão explícita
de versão revisada na biblioteca como Markdown, deduplicada/desmarcada e com
proveniência em cada trecho. Qt foi escolhido após prova real de exportação;
Windows/macOS seguem sem aceite. Limites e usos em [Páginas](docs/PAGINAS_ESTUDO.md).
Aceite: 207 Python aprovados/dez opcionais ignorados, 33 React, build e seis
fluxos Qt. Catorze folhas conferidas; casos inválidos recusados. Ollama real em
CPU com rede externa bloqueada (~72 s), versão anterior preservada. Migração
v10 → v11 manteve as 27 tabelas antigas, arquivos/configurações, seis materiais
e 678 trechos/vetores. L5, orientação/zoom e instaladores permanecem futuros.

## Entregue — complemento L3: Matemática Discreta

Reutilizados tarefas/artefatos de Cálculo e o chat React. Entrada manual com
prévia obrigatória, conjuntos/relações finitos e resultados exatos, definições
e contraexemplos. Parser proposicional próprio limitado a seis variáveis,
tabelas-verdade/equivalência e diagramas locais exportáveis. Propostas de IA
revisáveis com fontes selecionadas/parciais e origem persistida; campos
inexistentes/ambíguos ficam em branco. Explicações não alteram resultados.
Vínculos a atividade/versão/questão/tentativa, comparação objetiva separada
após solução revelada ou finalização, preservando gabaritos e notas.
SQLite v10 com backup v9 e rollback nessa entrega. Páginas/PDF L4 entregues acima.
[Uso, limites e validação](docs/DISCRETA.md). Aceite: 196 Python aprovados/dez
legados ignorados, 27 React, build e quatro fluxos Qt. Ollama real com rede
externa bloqueada (~30 s proposta/~46 s explicação), reinício e preservação das
26 tabelas pessoais/arquivos/configurações conferidos.

## Entregue — materiais de disciplinas em PDF e Office

A biblioteca existente é reutilizada para os anexos do Classroom, com associação
ao caderno, assunto/etiquetas, origem, hash para deduplicação e seleção por chat.
Não é treinamento do modelo nem sincronização permanente do Classroom.
Os materiais e relatórios pessoais permanecem fora do repositório.

PPTX ganhou leitura por slide na ordem da apresentação e referências de slides
em chat/atividades. DOCX/PPTX conservam frações, potências, raízes, índices e
delimitadores OMML básicos; sobrescritos/subscritos em runs também são lidos.
Equações desconhecidas são sinalizadas. Imagens e diagramas do Office continuam
fora da interpretação, com estado de texto parcial e acesso ao original.
O limite de PDF/slides passou de 80 para 500, mantendo 20 MiB, um milhão de
caracteres, limites de tempo e OCR de até dez páginas.

Próximas melhorias: leitura de figuras com modelo visual e avaliação de fórmulas
extraídas; importação/sincronização autorizada pelo próprio aplicativo com o
Classroom; preservação da numeração automática completa das listas do Office.
O aplicativo continua compatível com RAG textual e embeddings locais existentes.
[Formatos e uso](docs/MATERIAIS.md).

## Entregue — núcleo L2: busca híbrida local

Reutilizar texto/OCR e IDs de trechos existentes. Adicionar Qwen3-Embedding
0.6B pela API local de Ollama, em CPU e lotes pequenos, sem dependência de
serviços vetoriais. SQLite v8 com backup v7: vetores normalizados, hash de texto,
extrator, perfil, modelo/digest e dimensão; índice de preparação separado para
publicação atômica. Indexação explícita, incremental, cancelável e retomável.

Oferecer busca por palavra/significado na biblioteca, respeitando filtros de
caderno/chat. Nos chats e no estudo, consultar exclusivamente IDs autorizados,
com prévia da estratégia e fallback textual informado quando o índice/runtime
não estiver disponível. Manter seleção documental separada da associação a
cadernos. Exclusão/reprocessamento invalidam também vetores. Medir recuperação
em português e fórmulas e validar reinício, cancelamento e migração antes de
publicar. Resumos de conversas continuam opcionais para uma entrega posterior.

Aceite Qt com pesos reais e rede externa bloqueada: indexação explícita, pesquisa,
filtros, seleção e reinício. Piloto português: híbrida top1 10/12 versus FTS 5/12;
PDF real extraído com fonte na página 8, remoção e reinício verificados.
[Entrega e limites](docs/BUSCA_SEMANTICA.md). Próxima etapa: L3, matemática
verificável e gráficos; manter avaliação de recuperação separada de correção matemática.

## Entregue — L1: Ollama na interface

O runtime já testado foi integrado ao chat React: configuração sem chave, diagnóstico
de conexão/modelos/capacidades, preferência por conversa e orçamento explícito
de contexto. SQLite v7 cria backup v6, consultas persistidas com IDs idempotentes
e recuperação de respostas interrompidas. Streaming e cancelamento mantêm texto
parcial identificado; repetir uma falha conserva a pergunta original.

Reutilizar FTS e fontes autorizadas nos chats e no estudo. Atividades locais
começam com 1–3 questões, esquema JSON e validação existente. Gemini/OpenAI são
opções explícitas e não há fallback. Migração/reinício, isolamento,
cancelamento, contratos Python/React e fluxos Qt validados, incluindo aceite
local real com dados fictícios. [Entrega e limites](docs/OLLAMA.md). A qualidade
matemática continua experimental; não confundir estrutura JSON com gabarito
verificado. Embeddings, gráficos, visão e imagens continuam em L2–L5.

## Piloto executado — IA local no notebook (11/10/2026)

A pedido do usuário sem acesso ao PC de casa, L0 foi iniciado no notebook:
Ubuntu, i5-13420H, RAM de classe 8 GB e RTX 3050 Laptop 6 GB. Ollama 0.40.3
instalado na pasta do usuário, modelo Qwen3.5-4B Q4_K_M e duas rodadas reais em
namespace sem rede externa. Baseline 10/14; perfil revisado 15/18, com um erro
de lógica e duas falhas de formato. Mediana quente de cerca de 36 tokens/s.
Não confundir esse resultado experimental com certificação de matemática.

[Relatório e reprodução](docs/PILOTO_LOCAL.md). Piloto independente de terminal,
atalho separado, arquivos fora do Git e nenhum envio às APIs online. Banco e
configuração pessoal preservados. A integração à interface React (L1) foi entregue depois, conforme seção acima; Windows/RTX 3060 ainda precisa de diagnóstico real.

## Revisão — IA local no PC de casa (11/10/2026)

Plano detalhado em [IA local, gráficos e páginas de estudo](docs/IA_LOCAL.md).
Destino informado: **Windows, 16 GB RAM e RTX 3060 de 8 ou 12 GB VRAM**;
capacidade exata, CPU, driver e disco serão confirmados no PC de casa. Esse
hardware não é o notebook de desenvolvimento inventariado anteriormente.

Decisão: conservar o CadernoMat e integrar Ollama como serviço local, sem fork
do motor no MVP. A trilha proposta é diagnóstico/piloto → chat local persistente
e cancelável → RAG textual existente e depois embeddings → cálculos/gráficos →
páginas exportáveis com aparência de caderno → visão e ilustrações opcionais.
Gemini/OpenAI continuam escolhas explícitas, sem fallback automático para nuvem.
Modelos candidatos e repositórios pesquisados constam no documento; nenhum
modelo foi baixado, instalado ou avaliado na revisão inicial de planejamento.
O piloto posterior no notebook está registrado na seção acima.

A solicitação atual detalha a preparação da IA local como próxima trilha possível.
Provas/simulados continuam no backlog, e não será refeito o que já funciona.
Esta revisão substitui a antiga exigência de esperar toda a etapa 6 para iniciar
o piloto local. Gráficos e exportação exigem suas próprias validações.

## Entrega — interface React desktop

Analise: SQLite v5 e servicos de cadernos/materiais/IA ja estao separados;
`desktop.py` concentrava navegacao, rascunho, tarefas, importacao e preview.
Coordenacao migrada para um servico independente e uma ponte com operacoes
permitidas. Cada operacao abre/fecha sua propria conexao SQLite na thread que a
executa; mutacoes sao serializadas e tarefas recebem snapshots. Mantido esquema
v5, dados existentes e contratos dos provedores, sem novas atividades nesta fase.

Sequencia: (1) servico/ponte e testes; (2) React/TypeScript/Vite/Tailwind e tokens;
(3) chat completo com Markdown/KaTeX; (4) cadernos/menus; (5) biblioteca/previews;
(6) configuracao e previa; (7) build local, atalho e testes de janela/reinicio.
Distribuir assets compilados no repositorio para abrir sem Node ou servidor de
desenvolvimento. Interface e fontes locais, nenhum CDN. pywebview com Qt/PySide6
neste Linux; Windows usa WebView2. Manter modo Tk legado durante transicao.

Riscos: concorrencia da ponte, HTML nao confiavel, caminhos/credenciais expostos,
dependencias de WebView, tarefas interrompidas e regressao do atalho. Validar
contratos, sanitizacao, navegacao, dois temas a 1000x650, fluxo documental/IA
simulada/reinicio, preservacao real do banco e funcionamento do build na janela.
Arquitetura/design documentados e publicacao apos validacao.

Entrega concluida: chats, cadernos e biblioteca completos, Markdown/KaTeX
sanitizado, claro/escuro, lateral recolhivel, configuracoes e previa estruturada.
O atalho abre o build local sem Node; --legado permite transicao. Qt validado
neste Ubuntu, sem Tkinter na rota nova. Fechamento adiado salva rascunho sem
bloquear a thread grafica. Nenhum provedor novo ou atividade foi acrescentado.

Validacao: 88 testes Python, 9 frontend e fluxo completo de janela/reinicio com
IA simulada. Capturas ficticias em docs/screenshots; docs/INTERFACE.md e DESIGN.md
registram contratos e tokens. Esquema v5 e dados existentes preservados.
Proxima entrega: atividades e tentativas por caderno. Streaming/cancelamento,
instaladores, virtualizacao e validacao Windows/macOS seguem pendentes.

## Entrega — cadernos integrados

Analise anterior a implementacao: o banco estava em v4; chats e materiais possuem IDs estaveis, a biblioteca
usa vinculos por conversa e a IA recebe historico/fontes como parametros. A
interface presumia uma conversa aberta, o que exigiu aceitar cadernos vazios.
Os 61 testes de base passaram antes das alteracoes.

Sequencia verificavel desta entrega:

1. SQLite v5 com backup v4 e transacao explicita: cadernos com preferencias,
   conversa.caderno_id opcional e relacao material/cadernos muitos-para-muitos.
   Criar tres cadernos somente na migracao; chats antigos permanecem em Geral.
2. Servico de cadernos para CRUD, ordenacao, arquivo/restauracao e movimentacao
   por ID. Excluir caderno preserva conversas/materiais e a selecao documental.
3. Interface de cadernos na lateral, gerenciamento e estado vazio sem criar
   chats. Filtrar conversas por caderno e conservar rascunhos na navegacao.
4. Biblioteca com filtro/associacoes a cadernos reais. Material importado ou
   reutilizado herda o caderno da conversa; mover chat acrescenta o destino sem
   remover associacoes anteriores. Isso nunca seleciona fontes para a IA.
5. Contexto pedagogico independente de historico/fontes, igual para Gemini e
   OpenAI, mostrado na previa. Validar isolamento, migracao, reinicio e fluxo UI.
6. Documentar, validar dependencias/diff e publicar. Manter o atalho existente.

Dados legados de materia sao associados somente por correspondencia exata
normalizada ou aliases inequivocos dos tres cadernos iniciais. Metadados livres
continuam preservados. Cadernos arquivados sao navegaveis em leitura e nao
alteram o estado individual dos chats. A proxima entrega de produto sera
atividades e tentativas vinculadas ao ID estavel de um caderno; embeddings,
busca semantica e IA local seguem posteriores.

Fluxo entregue: criar caderno, iniciar chat, anexar, selecionar fonte, conferir
previa, consultar IA simulada, mover e reiniciar recuperando todos os dados.
Interface conferida a 1000x650 com nomes longos. Guia em docs/CADERNOS.md.
Validacao final: 76 testes aprovados, incluindo extracao/OCR e fluxos de janela,
sem consultas reais a IA. Dependencias e diff conferidos. Banco local migrado
para v5 com backup v4; verificacao de integridade e comparacao dos registros
e arquivos existentes confirmaram preservacao. Atalho mantido.

## Entrega — anexos, biblioteca e memoria documental

Analise anterior a entrega de materiais (registro historico): a interface Tk concentra o fluxo de chat; Historico usa
SQLite v3 no diretorio de dados do usuario; Gemini e OpenAI recebem somente
texto. Nao existem documentos, indices ou cadernos ainda. Preservaremos esses
contratos e separaremos armazenamento/extracao/recuperacao da interface.

Ordem desta entrega (antecipando materiais da etapa 6):

1. Migrar SQLite com backup v3, mantendo chats, rascunhos e configuracoes.
   Guardar originais fora do Git, deduplicados por SHA-256; registrar origem,
   materias/assuntos/etiquetas, selecao por chat e estados de processamento.
2. Extrair texto localmente (TXT/Markdown/CSV/JSON, DOCX, PDF e OCR opcional),
   com limites de tamanho/paginas, processamento em segundo plano e erros
   recuperaveis. Links publicos HTTP(S) terao copia textual, sem executar scripts.
3. Entregar aba Materiais: anexar arquivo/link, visualizar texto/original,
   editar metadados, pesquisar/filtrar, reutilizar em outro chat e excluir.
   Verificar o fluxo completo incluindo fechar/reabrir e arquivos duplicados.
4. Indexar trechos por pagina com SQLite FTS5 e recuperar somente dos materiais
   selecionados. Mostrar a previa dos trechos enviados; pedir citacoes com nome
   e pagina e tratar documentos como dados nao confiaveis, nunca comandos.
5. Testar migracoes, extracao, deduplicacao, busca, exclusao, reinicio e os dois
   provedores sem chamadas pagas; documentar limites e publicar no GitHub.

Criterios: anexar e consultar localmente sem chave; recuperar os mesmos materiais
apos reiniciar; exclusao limpa indice e selecoes; nenhuma consulta envia o
original binario ou materiais nao selecionados; extracao falha nunca vira texto
inventado. Naquela fase materia era metadado editavel; cadernos foram entregues depois.
OCR depende de Tesseract instalado; explicitar idiomas disponiveis e limitacoes.

Arquitetura futura: extratores produzem paginas, indexacao produz trechos com
proveniencia e uma interface de recuperacao independente do provedor. Embeddings
locais, indice vetorial e busca hibrida entram depois dessa base textual. Nao ha
treinamento de rede neural, nem instalacao de modelo local nesta entrega.

## Objetivo

Transformar o tutor em um chat pessoal de estudos de matematica, com cadernos
por materia, conversas persistentes e atividades de pratica. A experiencia tera
uma barra lateral de organizacao e uma conversa central, semelhante ao fluxo
de chats do ChatGPT. O foco inicial e Calculo Diferencial e Integral I e
Matematica Discreta; outras materias poderao ser adicionadas depois.

Nome do aplicativo: **CadernoMat**. Repositorio: **caderno-mat**.

## Estado atual

Ja existem interface desktop, Gemini e OpenAI com chaves individuais, resolucao
local de continuidade por partes e apresentacao de Markdown/formulas. O usuario
confirmou uma resposta real do Gemini. A validacao desta entrega esta registrada
abaixo. Agora existem chats persistentes, barra lateral, renomeacao, rascunhos e
contexto recente enviado a Gemini/OpenAI. Cadernos, biblioteca e RAG textual
estao implementados. Provas, simulados e acompanhamento de desempenho sao os
proximos passos; cancelamento/streaming do chat ainda permanecem pendentes.

Este planejamento inclui a evolucao principal e uma trilha de IA local e
interface com multiplos modelos, detalhada em docs/IA_LOCAL.md a pedido do
usuario. As funcionalidades abaixo serao implementadas em entregas separadas,
com criterios verificaveis. A revisao no inicio registra a prioridade atual.

## Experiencia planejada

A barra lateral mostrara **Novo chat**, **Cadernos**, busca e configuracoes. Cada
caderno agrupara conversas e atividades da materia. O centro mostrara mensagens
do usuario e da IA em sequencia, com caixa de envio na parte inferior. Uma barra
superior indicara materia, titulo da conversa, provedor e modelo selecionados.

Estrutura inicial sugerida (o usuario podera renomear e reorganizar):

- Preliminares de Matematica: algebra, funcoes, equacoes e trigonometria.
- Calculo Diferencial e Integral I: limites, continuidade, derivadas, aplicacoes
  e integrais.
- Matematica Discreta: logica, conjuntos, relacoes, funcoes, inducao,
  combinatoria e grafos, conforme os conteudos estudados.

Em cada caderno:

- Conversas: duvidas, resolucoes e revisoes.
- Atividades: listas, provas de pratica, simulados e tentativas realizadas.
- Materiais: arquivos e links compartilhados entre cadernos, com selecao por chat.

Uma conversa pertence a um caderno ou a uma area geral. Novo chat inicia um
contexto independente. Selecionar uma conversa recupera suas mensagens.

## Etapa 1 — Fundacao e padronizacao

- [x] Definir nome, escopo e planejamento.
- [x] Atualizar identidade visivel e repositorio.
- [ ] Separar interface, servicos de estudo, provedores de IA e armazenamento.
- [x] Criar SQLite local com migracoes e backup antes de mudancas de esquema.
- [ ] Padronizar componentes, cores, espacamento, fontes e mensagens em portugues.
- [x] Definir pasta de dados do usuario separada do checkout Git, usando o diretorio
  de dados da plataforma. Manter chaves fora do banco e do Git.

Conclusao: dados persistem apos reiniciar; falha de migracao preserva o banco
anterior; configuracao dos provedores existentes continua funcionando.

## Etapa 2 — Chat com historico (primeira entrega utilizavel)

- [x] Barra lateral, Novo chat, lista de conversas e conversa central.
- [x] Salvar mensagens, titulo, datas, resultado da consulta, rascunho e provedor.
- [ ] Adicionar materia e estados persistentes de consulta em andamento.
- [x] Renomear conversas.
- [x] Buscar por titulo/conteudo, arquivar/restaurar e excluir com confirmacao.
- [x] Enviar historico relevante ao Gemini e a OpenAI, com limite de contexto.
- [ ] Respostas progressivas quando suportadas, indicador de envio e cancelar.
- [ ] Copiar mensagem, tentar novamente apos erro e preservar rascunho.
- [ ] Manter renderizacao de formulas e rolagem; exibir falhas de modo recuperavel.

Conclusao: criar dois chats, fechar e reabrir, retomar um deles e perguntar
"explique a segunda etapa" funciona usando seu contexto, sem misturar o outro.
Cancelar ou repetir uma mensagem nao duplica respostas nem corrompe historico.

## Etapa 3 — Cadernos e contexto por materia

- [x] Criar, editar, ordenar, arquivar e escolher cadernos.
- [x] Criar os tres cadernos iniciais apenas no primeiro uso.
- [x] Mover conversas entre cadernos e buscar titulo/mensagens na materia escolhida.
- [x] Salvar objetivo, nivel, assuntos e preferencias pedagogicas de cada caderno.
- [x] Selecionar materia na conversa; adaptar instrucoes da IA ao caderno.
- [x] Escolher entre explicacao completa, dicas progressivas e correcao de tentativa.
- [x] Filtrar e compartilhar materiais entre cadernos sem copia ou autorizacao automatica.

Conclusao: estudo de limites e estudo de inducao ficam em cadernos independentes,
com contexto adequado. Arquivar um caderno preserva suas conversas.

## Etapa 4 — Listas, provas de pratica e simulados

Atividades/tentativas entregues em 11/10/2026: editor manual offline, quatro
formatos, rascunho/reinício, snapshot desde início, correção objetiva, revisão
manual, histórico/comparação e geração/dicas/feedback opcionais com prévia e
fontes explícitas. Validação: 116 testes Python, 15 frontend e dois fluxos Qt.
Consulte docs/ATIVIDADES.md. As propostas não são atividades até revisão/salvar.
Provas/simulados com cronômetro e flashcards seguem pendentes; não há comparação
de domínio, corretor universal, embeddings ou modelo local nesta entrega.

O planejamento abaixo registra também as extensões futuras desta etapa.

Um formulario perguntara materia, assuntos, dificuldade, quantidade de questoes,
formatos, duracao opcional e se o aluno deseja dicas durante a atividade.

Serviço entregue para geração/correção básica; extensão futura referenciando
`cadernos.id`. Criar tabelas versionadas para atividade, questao, tentativa e
resposta, preservando as migracoes existentes. Primeiro entregar lista de
pratica persistente com geracao simulada validada e correcao objetiva; depois
simulado/retomada e rubricas discursivas. Fontes continuam selecionadas
explicitamente. Nao antecipar embeddings ou inferencia local.

Formatos iniciais:

- Multipla escolha, com alternativas A–E e uma resposta correta.
- Verdadeiro/falso, com justificativa opcional.
- Resposta numerica ou expressao matematica curta.
- Discursiva, demonstracao e resolucao passo a passo.
- Atividade mista, combinando os formatos anteriores.

Dois fluxos: **Pratica** permite dicas e feedback durante a resolucao;
**Simulado** apresenta questoes, recolhe respostas e mostra correcao ao finalizar.
O cronometro sera opcional. Tentativas podem ser salvas e retomadas.

- [x] Gerar questoes em estrutura JSON validada, independente da apresentacao.
- [x] Salvar versões, alternativas, gabarito, assunto e tentativas; rubricas avançadas seguem planejadas.
- [ ] Validar numero de alternativas, identificadores, pontuacao e existencia de
  resposta correta. Nao apresentar atividade com estrutura invalida.
- [ ] Separar visualizacao das questoes da exibicao do gabarito.
- [ ] Registrar respostas e permitir finalizar ou retomar uma tentativa.
- [ ] Corrigir alternativas deterministicamente; avaliar respostas numericas e
  equivalencias simbolicas quando houver verificacao local confiavel.
- [ ] Usar IA para feedback discursivo com rubrica e indicar que a avaliacao e
  sugerida, editavel pelo usuario. Nunca tratar essa nota como avaliacao oficial.
- [ ] Mostrar nota, acertos por assunto, justificativas e sugestoes de revisao.

Conclusao: gerar um simulado misto de dez questoes, responder, reiniciar o app,
retomar, finalizar e revisar. Gabarito nao aparece antes da finalizacao no modo
simulado. Questao ambigua ou erro de geracao permite revisar ou substituir.

## Etapa 5 — Qualidade matematica e recursos de estudo

- [ ] Corrigir verificacao de dominio real no resolvedor local, sobretudo sqrt/log.
- [ ] Ampliar calculos locais para limites, derivadas, reta tangente e integrais.
- [ ] Acrescentar verificacoes de logica, conjuntos, combinatoria e inducao quando
  adequadas; explicacoes de provas exigem revisao de hipoteses.
- [ ] Graficos locais para funcoes e comparacao entre curva e reta tangente.
- [ ] Banco de exercicios conhecidos para avaliar resultados dos dois provedores.
- [ ] Resumos por assunto, dicas progressivas e pratica baseada nos erros.

Conclusao: casos de referencia produzem resultados corretos e explicacoes
coerentes; calculo local e sugestao de IA sao identificados na resposta.

## Etapa 6 — Materiais, exportacao e acabamento

- [x] Importar PDFs, imagens, textos, DOCX e links com limites e preview.
- [x] Biblioteca persistente, deduplicacao, metadados, busca e filtros.
- [x] Extrair conteudo localmente, OCR opcional e indice FTS5 por trecho/pagina.
- [x] Selecionar fontes por chat, previa do envio e citacoes com nome/pagina.
- [x] Vinculo de materiais a cadernos reais sem duplicacao.
- [ ] Embeddings locais e busca semantica/hibrida.
- [ ] Exportar conversas e atividades em Markdown e PDF, com opcao de gabarito.
- [ ] Backup/restauracao dos cadernos e historico.
- [ ] Tema claro/escuro, atalhos, acessibilidade e janela adaptavel.
- [ ] Empacotar instalacao para Linux e Windows e atualizar documentacao.

Conclusao: exportacao legivel e restauracao em banco separado preservam dados;
instalacao limpa abre sem caminhos especificos da maquina de desenvolvimento.

## Etapa 7 — IA local e interface unificada

Revisao de 11/10/2026: chat, cadernos, materiais e atividades ja estao entregues.
O novo recorte para Windows/RTX 3060 esta em [docs/IA_LOCAL.md](docs/IA_LOCAL.md).
O piloto e o chat local podem ser desenvolvidos sobre essa base; qualidade
matematica, graficos e exportacao permanecem entregas com criterios proprios.
Comparacao simultanea, difusao e novas plataformas completas ficam posteriores.

### 7.1 — Provedores na mesma conversa

- [ ] Escolher provedor e modelo por conversa; lembrar a escolha ao reabrir.
- [ ] Trocar entre Gemini, OpenAI e IA local mantendo historico e caderno.
- [ ] Manter instrucoes, nivel e objetivos no caderno, independentes do modelo.
- [ ] Registrar qual provedor/modelo respondeu a cada mensagem.
- [ ] Mostrar capacidade, estado de conexao e modo local/online na interface.
- [ ] Usar o mesmo contrato para historico, respostas progressivas, cancelamento,
  limite de contexto e erros; adaptar apenas as particularidades dos provedores.

Conclusao: retomar uma conversa, trocar o modelo e continuar a explicacao com
contexto coerente, sem apagar mensagens nem mudar as preferencias da materia.

### 7.2 — Experimento com modelo local adequado ao computador

O inventario de 10/10/2026 descrevia o notebook de desenvolvimento com i5-13420H,
cerca de 8 GB RAM e RTX 3050 Laptop de 6 GB. O alvo agora informado e outro PC:
Windows, 16 GB RAM e RTX 3060 de 8 ou 12 GB VRAM. Confirmar no PC de casa. O
primeiro artigo usa modelo de 27B em GPU de 16 GB; seu desempenho nao e uma
previsao para nenhum desses computadores.

Comecar com Qwen3.5-4B Q4_K_M; depois comparar Qwen3-8B no perfil 8 GB ou
Qwen3.5-9B no perfil 12 GB, somente apos medir memoria/qualidade. As escolhas
sao candidatas e precisam de revalidacao na data de implementacao.

- [ ] Avaliar Ollama como primeiro runtime; considerar llama.cpp ou LM Studio
  se houver necessidade concreta de desempenho ou compatibilidade.
- [ ] Selecionar um modelo pequeno e quantizado pela memoria e qualidade,
  verificando licenca, tamanho do download e suporte do runtime.
- [ ] Medir memoria RAM/VRAM, tempo ate primeira resposta e velocidade com
  conversas curtas e longas. Limitar contexto para evitar falta de memoria.
- [ ] Testar portugues, Calculo I e Matematica Discreta com exercicios conhecidos.
- [ ] Comparar respostas com gabaritos e verificacoes locais, nao apenas fluidez.
- [ ] Se o desempenho nao for adequado, manter local como opcao experimental e
  Gemini disponivel, sem exigir compra de hardware.

Conclusao: registrar modelo, quantizacao, contexto, resultados e limitacoes;
escolher um candidato somente apos demonstrar utilidade nos exercicios reais.
Nao prometer desempenho de modelos grandes em hardware menor.

### 7.3 — Integracao local utilizavel

- [ ] Conectar ao servidor local e listar modelos ja instalados.
- [ ] Orientar instalacao e download separadamente, mostrando tamanho previsto.
- [ ] Permitir selecionar modelo instalado sem chave de API de nuvem.
- [ ] Conferir disponibilidade do servidor, timeout e falta de memoria com
  mensagens claras; preservar a pergunta quando houver falha.
- [ ] Manter inferencia na maquina no modo local, sem troca automatica para API.
- [ ] Permitir chats e acesso aos cadernos offline apos instalar o modelo.
- [ ] Explicar que nao ha cobranca de API local, mas ha uso de energia,
  armazenamento e processamento do computador.

Conclusao: desconectar a internet e conversar com o modelo local instalado;
reiniciar o servidor e recuperar a conversa sem perder mensagens.

### 7.4 — Materiais locais e verificacao matematica

- [ ] Reutilizar o fluxo de materiais da etapa 6 para consulta com referencias.
- [ ] Se houver busca por embeddings, executar tambem essa etapa localmente no
  modo offline; nao enviar arquivos para servicos externos silenciosamente.
- [ ] Reutilizar verificacoes SymPy da etapa 5 para resultados verificaveis.
- [ ] Indicar limites de avaliacao automatica de demonstracoes e argumentos.

Conclusao: uma pergunta sobre uma apostila local pode citar arquivo e pagina
sem depender de API externa, com teste de extracao e recuperacao do conteudo.

### 7.5 — Comparacao e segunda opiniao (opcionais)

- [ ] Botao explicito para pedir segunda opiniao a outro modelo.
- [ ] Comparacao lado a lado usando o mesmo enunciado e contexto escolhido.
- [ ] Mostrar que cada provedor online recebe uma consulta e pode consumir
  creditos ou cota; nao enviar a todos os modelos por padrao.
- [ ] Permitir pedir critica de uma resolucao e destacar divergencias.
- [ ] Nao considerar concordancia entre modelos como prova de correcao.
- [ ] Avaliar Groq como provedor adicional depois da integracao local principal.

Conclusao: duas respostas ficam identificadas e preservadas; o usuario escolhe
se deseja a consulta adicional. Erro de um provedor nao apaga a outra resposta.

### Referencias e interpretacao

- [Relato de substituicao por IA local](https://www.xda-developers.com/im-not-paying-20-for-chatgpt-claude-or-gemini-because-a-free-local-llm-does-everything-i-need/):
  inspira inferencia offline e autonomia; e uma experiencia pessoal, nao uma
  validacao de qualidade matematica para o CadernoMat.
- [Relato de interface unificada](https://www.xda-developers.com/run-claude-chatgpt-local-llm-through-one-interface/):
  inspira selecao de modelos, instrucoes persistentes e segunda opiniao. O
  CadernoMat mantera seu foco em materias, atividades e acompanhamento.

Os artigos sao referencias de produto. Confirmar documentacao oficial,
compatibilidade, licencas e modelos disponiveis na epoca da implementacao.

## Base tecnica proposta

Manter Python e a interface desktop nesta primeira evolucao. Migrar para outra
interface ou para web somente se limites concretos de renderizacao e interacao
justificarem isso; o armazenamento e os servicos devem permitir essa mudanca.

Camadas:

- Interface: navegacao, chat, configuracao e telas de atividades.
- Servicos: contexto de estudo, geracao de atividades e correcao.
- Provedores: contrato comum para Gemini e OpenAI, erros e capacidades.
- Persistencia: SQLite, repositorios de dados, migracoes e backups.
- Matematica: calculos locais e verificacoes com SymPy.
- Apresentacao: Markdown, formulas, graficos e exportacao.

Entidades principais: Caderno, Conversa, Mensagem, Atividade, Questao, Tentativa,
Resposta e Material. Cada registro tera identificador estavel e datas. Mensagens
registram papel, texto, estado e provedor/modelo utilizado. Questoes e tentativas
terao versoes para que editar uma atividade nao altere uma tentativa ja feita.

As chaves permanecem configuradas por usuario e provedor. Gemini gratuito/pago
e determinado pelo projeto Google; o aplicativo nao ativa faturamento. OpenAI
continua opcional. Nao trocar de provedor automaticamente ao atingir cota.

## Ordem de implementacao e testes

Fundacao, chat, cadernos, materiais e atividades foram entregues. Continuam
provas/simulados (4), qualidade matematica (5), exportacao e acabamento (6).
A revisao de 11/10/2026 detalha o piloto/chat local como uma trilha especifica
sobre a base existente. Seguir L0–L5 de docs/IA_LOCAL.md para suas dependencias,
sem chamar o planejamento de integracao ja implementada.
Evitar construir geracao de provas antes de existir historico persistente.
Nao estabelecer prazos fixos antes de validar o primeiro fluxo de chat.

Testes essenciais: migracoes, isolamento entre chats/cadernos, reinicio do app,
contexto enviado a cada provedor, cancelamento, falha de rede, cota, validacao de
atividades, correcao deterministica e exportacao. Testes automatizados usam
clientes simulados; consultas reais sao verificadas separadamente. Na etapa 7,
incluir testes offline, servidor local indisponivel, contexto por provedor,
memoria limitada e ausencia de envio automatico para nuvem.

Nao sincronizar com nuvem, adicionar multiplos usuarios ou construir plugins
nesta primeira versao. A prioridade e um aplicativo pessoal consistente.


## Entrega parcial — chat persistente (10/10/2026)

Implementados: banco SQLite versionado fora do Git, barra lateral, Novo chat,
titulo automatico, renomeacao, transcricao com formulas, rascunho por conversa e
recuperacao apos reiniciar. A IA recebe ate dez pares completos recentes, com
limite de 16 mil caracteres; pares com erros ficam fora. O historico completo
continua salvo localmente. Resolver local permanece sem contexto de chat.

Validacao: 35 testes automatizados e fluxo de janela com envio simulado, troca,
rascunho e reinicio. Nenhuma consulta real foi necessaria para esta entrega.
Limites: sem busca/exclusao, streaming ou cancelamento. Ao fechar durante uma
consulta, a pergunta salva permanece, mas a resposta em andamento nao e salva.
Cadernos e atividades permanecem nas etapas seguintes; IA local fica por ultimo.


## Entrega parcial — organizacao de chats (10/10/2026)

Busca literal por titulo e mensagens, sem diferenciar maiusculas/minusculas.
Arquivar preserva mensagens e rascunho; Ver arquivados permite restaurar. Chats
arquivados precisam ser restaurados para receber novas mensagens. Exclusao pede
confirmacao e remove as mensagens associadas, preservando outras conversas.
Banco migrado para versao 2 com backup da versao 1 antes da alteracao.
Validacao: 39 testes automatizados e fluxo de janela com cancelamento e
confirmacao da exclusao. Streaming, cancelamento da consulta e repeticao de
envio ainda permanecem pendentes nesta etapa.

## Refinamento — acoes por conversa (10/10/2026)

Implementados menu no hover por chat, fixar/desafixar com persistencia e titulos
longos deslizantes. Acoes globais de renomear/arquivar foram substituidas pelo
menu de cada linha. Migracao de esquema para versao 3 com backup anterior.
Validacao: 40 testes e fluxo de janela de hover, deslocamento e acoes.

## Entrega — biblioteca e RAG textual (10/10/2026)

Implementado o fluxo completo antes da consulta documental: importar arquivos
ou links, guardar uma copia deduplicada fora do Git, extrair/indexar localmente,
visualizar original/texto, editar metadados, buscar/filtrar, reutilizar/desvincular,
excluir e recuperar materiais/selecao apos reiniciar. SQLite v4 com backup v3,
migracao atomica, paginas/trechos FTS5 e limpeza do indice por exclusao.
Processamento isolado com timeout; formatos sem extrator e falhas ficam visiveis.

Depois desse fluxo, Gemini/OpenAI passaram a receber trechos de fontes marcadas
por conversa, com previa e proveniencia. A IA deve citar M1/M2 com nome/pagina,
distinguir conhecimento geral e ignorar instrucoes nos documentos. O aplicativo
verifica IDs das citacoes e mostra quando o modelo nao cita. Resumos genericos
usam amostra inicial sinalizada, sem alegar leitura integral.

Validacao: 61 testes, com OCR real de imagem/PDF digitalizado, extracao de PDF
textual/DOCX, migracao preservando dados e rollback de DDL, deduplicacao, busca,
remoção do indice e fluxo de janela com reinicio/consulta simulada. Uma leitura
real de link publico tambem foi validada. Nao foram feitas chamadas reais a IA
nem consumidos creditos. Dependencias e diff verificados.

Limites e proximos passos: embeddings/busca semantica, cadernos (hoje materia e
metadado livre), leitura visual de formulas/diagramas, mais formatos, exportacao
e backup pela interface. OCR deste PC usa ingles por falta do pacote `por`.
A recuperacao permanece local e independente do provedor, preparando a futura
IA local sem instalar modelos agora. Detalhes em docs/MATERIAIS.md.
## Entrega — atividades e tentativas (11/10/2026)

Estado confirmado: SQLite v5, 88 testes Python e interface React/Qt existente.
Sequência: modelo/migração → editor manual → prática com rascunhos → correção e
histórico → propostas/dicas/feedback com IA → integração → validação/publicação.

Decisões: SQLite v6 com backup v5 e DDL transacional; versões de conteúdo e
snapshots de tentativas imutáveis; organização nullable para preservar dados ao
excluir cadernos/chats. Serviços Python independentes validam exercícios,
respostas e correção; React apenas apresenta DTOs. Nenhuma exclusão de atividade
nesta etapa: arquivamento conserva histórico. Fontes mantêm IDs e nomes sem
duplicar arquivos; associação não autoriza consulta. Tarefas de IA guardam a
prévia exata, propostas e falhas fora do Git; processos interrompidos ficam
recuperáveis, nunca simulam conclusão. Correção local usa escolha, booleano e
decimal finito com tolerância absoluta explícita; discursivas exigem revisão.

Limites: 30 exercícios por lista, 10 por geração, 2–6 alternativas, textos até
8 mil caracteres por enunciado/resposta, até 10 fontes explícitas/6 mil caracteres
recuperados. Sem corretor universal, provas cronometradas ou métricas de domínio.
Riscos: autosave ao fechar, versões antigas, JSON inválido e referências removidas.
Conclusão validada com fluxo manual offline com reinício, nova tentativa, comparação,
edição sem alterar o passado, migração/rollback, falhas simuladas de ambos os
provedores, temas/teclado/1000×650 e publicação sem dados pessoais.


## Validação local da migração v6

O banco real foi migrado com backup v5. As 14 tabelas anteriores tiveram o
mesmo hash de conteúdo antes/depois; integrity_check e foreign_key_check passaram.
Nenhum dado pessoal foi usado nas capturas ou publicado. O atalho existente
continua apontando para iniciar_desktop.sh e a interface compilada atual.

## Em desenvolvimento — L3: cálculos e gráficos locais (11/10/2026)

Sequência: parser limitado → motor isolado/PNG → SQLite v9 e ponte → fluxo manual
no chat com cancelamento, exportação e reinício → propostas JSON e explicação
pelos três provedores → testes matemáticos, migração, Qt e publicação.

Primeiro aceite: quadrática/derivada/mínimo/tangente persistidos; `1/x` e
cancelamento algébrico sem ligação através de buracos. Domínio é calculado a
partir da árvore original. Operações fora do escopo exibem limitação. Integrais
impróprias ficam recusadas nesta entrega; aproximação só sobre intervalo contínuo.
Resultados das ferramentas são registros independentes da narrativa da IA.
Arquivos ficam junto do banco, fora do Git; escrita atômica e processos encerráveis.
Discreta e páginas completas de caderno permanecem nas subetapas seguintes.

## Entrega L3 — cálculos e gráficos locais (11/10/2026)

Entregue o fluxo manual independente de IA: entrada/AST limitada, domínio
original, processamento encerrável, resultados por operação, PNG persistente,
exportação nativa e reinício. SQLite v9 com backup v8/DDL transacional; registros
e artefatos identificados, fora do Git. Depois: proposta JSON revisável, cópia
de parâmetros explícitos, prévia exata e explicação separada pelos três provedores.
Não há execução de conteúdo documental, correção automática de gabaritos nem
fallback online. Windows ainda requer aceite próprio.

Aceites matemáticos, persistência/migração/rollback, frontend/Qt e modelo real
Ollama com rede externa bloqueada; resultados e limites em docs/MATEMATICA_LOCAL.md.
O complemento Discreta está entregue acima. Continuam páginas completas L4 e
ilustrações L5, mais domínios, integrais
impróprias, integração visual com atividades e exportação SVG/PDF.

Validação final L3: 185 testes Python (175 aprovados, 10 do legado ignorados),
24 React, build e cinco fluxos Qt aprovados. Ollama Qwen3.5 4B real com rede
externa bloqueada: proposta ~24 s, explicação ~49 s, pedido ambíguo sem inventar
parâmetros e PNG recuperado após reiniciar. Migração pessoal v8→v9 preservou
os hashes das 25 tabelas anteriores e configurações, com backup/FKs/integridade.
