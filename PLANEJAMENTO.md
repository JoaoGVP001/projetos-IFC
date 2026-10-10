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
validacao. Ainda nao existem chats persistentes, cadernos, memoria de conversa,
provas, simulados ou acompanhamento de desempenho.

Esta atualizacao muda a identidade e registra o plano. As funcionalidades abaixo
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
- [ ] Criar SQLite local com migracoes e backup antes de mudancas de esquema.
- [ ] Padronizar componentes, cores, espacamento, fontes e mensagens em portugues.
- [ ] Definir pasta de dados do usuario separada do checkout Git, usando o diretorio
  de dados da plataforma. Manter chaves fora do banco e do Git.

Conclusao: dados persistem apos reiniciar; falha de migracao preserva o banco
anterior; configuracao dos provedores existentes continua funcionando.

## Etapa 2 — Chat com historico (primeira entrega utilizavel)

- [ ] Barra lateral, Novo chat, lista de conversas e conversa central.
- [ ] Salvar mensagens, titulo, datas, estado de envio, materia e provedor.
- [ ] Renomear, buscar e excluir conversas com confirmacao e alternativa de arquivo.
- [ ] Enviar historico relevante ao Gemini e a OpenAI, com limite de contexto.
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
- [ ] Avaliar Groq e Ollama local apenas depois do fluxo principal estabilizar.

Conclusao: exportacao legivel e restauracao em banco separado preservam dados;
instalacao limpa abre sem caminhos especificos da maquina de desenvolvimento.

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

Comecar pelas etapas 1 e 2. Depois implementar cadernos e so entao atividades.
Evitar construir geracao de provas antes de existir historico persistente.
Nao estabelecer prazos fixos antes de validar o primeiro fluxo de chat.

Testes essenciais: migracoes, isolamento entre chats/cadernos, reinicio do app,
contexto enviado a cada provedor, cancelamento, falha de rede, cota, validacao de
atividades, correcao deterministica e exportacao. Testes automatizados usam
clientes simulados; consultas reais sao verificadas separadamente.

Nao sincronizar com nuvem, adicionar multiplos usuarios ou construir plugins
nesta primeira versao. A prioridade e um aplicativo pessoal consistente.
