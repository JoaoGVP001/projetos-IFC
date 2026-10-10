# CadernoMat — planejamento de produto e desenvolvimento

Atualizado em 10/10/2026.

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
confirmou uma resposta real do Gemini. Os 31 testes atuais passaram na ultima
validacao. Agora existem chats persistentes, barra lateral, renomeacao, rascunhos e
contexto recente enviado a Gemini/OpenAI. Cadernos, provas, simulados e
acompanhamento de desempenho ainda estao planejados.

Este planejamento inclui a evolucao principal e uma etapa final de IA local e
interface com multiplos modelos, inspirada nos artigos analisados. As funcionalidades abaixo
serao implementadas em entregas separadas, com criterios verificaveis.

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
- Materiais: resumos e, em uma etapa posterior, arquivos enviados pelo usuario.

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

- [ ] Criar, editar, ordenar, arquivar e escolher cadernos.
- [ ] Criar os tres cadernos iniciais apenas no primeiro uso.
- [ ] Mover conversas entre cadernos e buscar por materia ou assunto.
- [ ] Salvar objetivo, nivel, assuntos e preferencias pedagogicas de cada caderno.
- [ ] Selecionar materia na conversa; adaptar instrucoes da IA ao caderno.
- [ ] Escolher entre explicacao completa, dicas progressivas e correcao de tentativa.

Conclusao: estudo de limites e estudo de inducao ficam em cadernos independentes,
com contexto adequado. Arquivar um caderno preserva suas conversas.

## Etapa 4 — Listas, provas de pratica e simulados

Um formulario perguntara materia, assuntos, dificuldade, quantidade de questoes,
formatos, duracao opcional e se o aluno deseja dicas durante a atividade.

Formatos iniciais:

- Multipla escolha, com alternativas A–E e uma resposta correta.
- Verdadeiro/falso, com justificativa opcional.
- Resposta numerica ou expressao matematica curta.
- Discursiva, demonstracao e resolucao passo a passo.
- Atividade mista, combinando os formatos anteriores.

Dois fluxos: **Pratica** permite dicas e feedback durante a resolucao;
**Simulado** apresenta questoes, recolhe respostas e mostra correcao ao finalizar.
O cronometro sera opcional. Tentativas podem ser salvas e retomadas.

- [ ] Gerar questoes em estrutura JSON validada, independente da apresentacao.
- [ ] Salvar versao das questoes, alternativas, gabarito, rubrica e assunto.
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

- [ ] Importar PDFs, imagens e notas com limites de tamanho e preview.
- [ ] Extrair conteudo e indicar arquivo/pagina ao usar material na resposta.
- [ ] Exportar conversas e atividades em Markdown e PDF, com opcao de gabarito.
- [ ] Backup/restauracao dos cadernos e historico.
- [ ] Tema claro/escuro, atalhos, acessibilidade e janela adaptavel.
- [ ] Empacotar instalacao para Linux e Windows e atualizar documentacao.

Conclusao: exportacao legivel e restauracao em banco separado preservam dados;
instalacao limpa abre sem caminhos especificos da maquina de desenvolvimento.

## Etapa 7 — IA local e interface unificada (apos as etapas 1–6)

Esta etapa sera implementada por ultimo. Nao antecipar instalacao de modelos,
comparacao simultanea ou novas integracoes enquanto chat, cadernos, atividades,
qualidade matematica, materiais e exportacao nao estiverem funcionando.
Preparar interfaces extensivas nas etapas anteriores nao significa implementar
estes recursos antes da sua vez.

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

O inventario de 10/10/2026 identificou i5-13420H, cerca de 8 GB de RAM e RTX
3050 Laptop de 6 GB. O primeiro artigo usa um modelo de 27 bilhoes de parametros
em uma GPU de 16 GB; seus resultados nao devem ser prometidos neste computador.
Verificar recursos disponiveis novamente antes dos testes.

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

Seguir a ordem 1 → 2 → 3 → 4 → 5 → 6 → 7. Comecar pelas etapas 1 e 2.
Depois implementar cadernos e so entao atividades. A etapa de IA local e
interface unificada vem apenas depois das entregas principais.
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
