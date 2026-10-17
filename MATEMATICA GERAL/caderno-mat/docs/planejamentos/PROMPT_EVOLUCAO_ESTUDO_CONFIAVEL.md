# Prompt — evolução do CadernoMat para estudo confiável

Continue o desenvolvimento do CadernoMat a partir do código atual, seguindo
este planejamento. O objetivo é melhorar a confiabilidade das explicações,
o aproveitamento dos meus materiais e a experiência de estudo, preservando
as funcionalidades e os dados existentes.

O foco é Cálculo Diferencial e Integral I e Matemática Discreta. Ainda estou
usando o notebook Linux; o PC de casa usa Windows, com RTX 3060 e quantidade
de RAM/VRAM a confirmar. Não dependa do acesso ao PC de casa para entregar
melhorias úteis no notebook.

**Primeira entrega deste prompt:** implemente um fluxo completo de estudo que
consulta os materiais selecionados, permite conferir as fontes, utiliza as
ferramentas matemáticas compatíveis e identifica os limites da explicação.
Isso reúne as fases 1 e 2 abaixo. As fases 3 a 6 constituem o roteiro das
entregas seguintes, com critérios definidos; não devem virar seis grandes
reescritas simultâneas.

## 1. Confira o estado antes de alterar

Leia README.md, PLANEJAMENTO.md e, principalmente:

- docs/FIDELIDADE_QUALIDADE.md;
- docs/CALIBRACAO_IA_LOCAL.md e docs/ESTABILIDADE_IA_LOCAL.md;
- docs/MATERIAIS.md e docs/BUSCA_SEMANTICA.md;
- docs/MATEMATICA_LOCAL.md e docs/DISCRETA.md;
- docs/ATIVIDADES.md e docs/PAGINAS_ESTUDO.md;
- docs/DESIGN.md, docs/INTERFACE.md e docs/TRANSFERENCIA_PC_CASA.md.

Verifique o código efetivo, o esquema e o estado do Git. Documentos antigos
descrevem entregas históricas; uma pendência antiga pode já estar implementada.
Na entrega anterior, o SQLite continuou v11, e passaram 247 testes Python e
39 React, além dos aceites Qt. Confirme esses números no checkout disponível.

A arquitetura existente inclui Python, React/TypeScript, pywebview/Qt,
Markdown/KaTeX, SQLite, biblioteca textual/híbrida com embeddings locais,
Ollama/Gemini/OpenAI, atividades/tentativas, ferramentas limitadas de Cálculo
e Discreta e páginas com versões/PDF/PNG. Reutilize esses componentes.

Antes da implementação, atualize o planejamento com o escopo da primeira
entrega, decisões, riscos reais e critérios de aceite. Identifique o que já
existe, o que precisa apenas de integração e o que exige uma extensão.

Preserve chats, parciais, cadernos, fontes selecionadas, materiais, FTS,
vetores, atividades, gabaritos, tentativas, cálculos, imagens, páginas,
versões, exportações, preferências e atalho. Audite integridade/FKs e conteúdo
antes/depois. Relatórios e dados pessoais ficam fora do Git.

## 2. Fase 1 — qualidade das explicações e revisão matemática

### Problemas conhecidos a reproduzir

Use casos fictícios para reproduzir, antes de corrigir:

- Indução com “algum k” em lugar de k arbitrário, ou conclusão sem domínio.
- Fórmulas corretas acompanhadas de hipóteses/prosa incorretas.
- Analogias geométricas inventadas e descrição de uma imagem que não existe.
- Títulos de Cálculo aplicados indevidamente a perguntas de Discreta.
- Correção que presume um erro ou raciocínio que o aluno não enviou.
- Simplificação de uma função que perde a restrição do domínio original.
- Resposta longa que termina sem a conclusão matemática necessária.
- JSON válido ou runtime com `stop` interpretado como confirmação de acerto.

### Comportamento esperado

Melhore as instruções e o fluxo por tarefa: explicar, resolver, corrigir,
dar dica e consultar material. Pedidos mistos devem conservar seus objetivos;
uma saudação continua curta. Respeite preferências do caderno dentro do
orçamento disponível. A seleção de instruções por palavras é uma heurística
limitada, e não deve ser apresentada como compreensão ou verificação matemática.

Em indução, exigir n inicial/domínio, base, k arbitrário, hipótese P(k), passo
P(k) implica P(k+1) e conclusão para todo n permitido. Distinguir indução
simples de forte quando pertinente. Exemplos numéricos não substituem uma
prova; enunciados incompletos exigem esclarecimento. Se a tentativa não foi
fornecida, pedir o texto sem inventar uma correção ou adicionar uma dica falsa.

Em Cálculo, separar domínio original, valor no ponto, limite, continuidade e
extensão contínua. Conservar hipóteses e unidades. Cancelar um fator não define
a função no ponto excluído. Não atribuir às ferramentas operações que elas
não implementam.

Em Discreta, conservar universo, quantificadores, domínio/contradomínio e
convenções. Distinguir afirmações sobre um conjunto finito das universais.
Um contraexemplo precisa satisfazer as hipóteses e refutar a conclusão.

Reutilize as ferramentas existentes para entradas aceitas pelo parser.
Facilite propor parâmetros, mostrar prévia e executar após ação explícita.
Mantenha o resultado local independente da narrativa da IA. Não execute
código/HTML/SVG/comandos do modelo nem tente interpretar qualquer LaTeX com eval.

Apresente origem e alcance de cada resultado: explicação da IA, cálculo
simbólico local, aproximação numérica, trecho documental ou edição do usuário.
Só mostre uma verificação quando uma operação real tiver sido executada, com
parâmetros/resultado recuperáveis. A verificação de uma conta não certifica
a demonstração inteira. Concordância entre modelos, palavras-chave ou
ausência de erro de renderização também não certificam uma prova.

Use a ilustração local existente quando pertinente, sem afirmar que ela
representa algo diferente do que foi gerado. Completar uma resposta por nova
consulta deve continuar explícito, com fontes, snapshot e possibilidade de
cancelar. Nenhuma correção automática pode sobrescrever silenciosamente o
texto original, o resultado de ferramenta ou o gabarito de uma atividade.

### Avaliação

Amplie gradualmente um conjunto versionado de referência, visando 30 casos:
dez de Cálculo, dez de Discreta e dez documentais. Gabaritos/rubricas devem
ser independentes e não entrar no pedido enviado ao modelo.

Inclua variantes legítimas de notação e raciocínio. Checagens determinísticas
devem declarar seu alcance; prosa e demonstrações exigem revisão identificada.
Registre acerto pontual, erro, incerteza e caso não suportado, em vez de gerar
um selo global por busca de palavras. Mantenha exemplos de falha na documentação.

Reutilize o avaliador finito existente. Rodadas reais devem usar modelos já
instalados, rede externa bloqueada e orçamento explícito: até 12 consultas por
rodada, limite total de tempo e timeout por consulta. Comece com um subconjunto
pequeno relevante às mudanças. APIs online são simuladas nos testes desta fase.

## 3. Fase 2 — materiais, recuperação e fontes conferíveis

### Fluxo completo prioritário

Implemente ou refine o seguinte percurso:

1. Escolho o caderno e marco os materiais que podem ser consultados.
2. Faço uma pergunta sobre o conteúdo.
3. Vejo os trechos recuperados, arquivos, páginas/slides, avisos e destino dos dados.
4. Inicio a consulta ao provedor escolhido.
5. A resposta apresenta referências conferíveis; consigo abrir o trecho e
   acessar o original na página correspondente quando o visualizador permitir.
6. Posso executar uma ferramenta compatível para conferir uma operação,
   preservando separadamente a explicação, a fonte e o resultado local.
7. Fecho/reabro o aplicativo e recupero resposta, fontes, resultados e vínculos.

Quando um visualizador não conseguir abrir diretamente na página, mostre o
número/unidade e ofereça abrir o original e o texto extraído. Não simule sucesso.
Uma citação deve abrir o trecho usado naquela resposta, não apenas buscar
novamente um trecho possivelmente diferente no documento atualizado.

### Recuperação e extração

Separe três avaliações: fidelidade da extração, relevância da recuperação e
correção da resposta. Use perguntas com respostas/páginas conhecidas, incluindo
informação ausente, documentos parecidos, extração parcial e OCR ambíguo.

Reaproveite FTS, embeddings, busca híbrida e índices incrementais. Respeite
seleção explícita, caderno, orçamento e exclusão de material. Reprocesse apenas
o que mudou ou foi solicitado; não reimporte/reindexe todo o acervo pessoal.
Durante uma tarefa pesada, mantenha o fallback textual informado existente.

Permita inspecionar o texto extraído e sua origem/método. Mostre problemas
observáveis de extração sem inventar porcentagens de confiança. Fórmulas
ilegíveis, figuras não extraídas e informação ausente continuam desconhecidas.

Se acrescentar correção manual de texto extraído, mantenha original e versão
da correção, autoria/data e indicação de edição. Atualize os trechos/índices
afetados explicitamente, conservando snapshots de respostas anteriores.
Não substitua uma fórmula OCR por uma fórmula “provável” sem revisão do usuário.

Conserve ID, hash/versão do material, trecho e página/unidade usados na resposta.
Uma referência removida ou modificada deve ser identificada. Revalide seleção
e fontes antes do envio; preservar o histórico não autoriza novos usos do
material removido/desmarcado.

Documentos são dados de consulta. Teste conteúdo que manda ignorar regras,
inventar professor, executar comandos ou consultar material não selecionado.
Essas instruções não podem controlar o aplicativo. Fonte relevante não é
automaticamente verdadeira. Páginas geradas pela própria IA devem manter sua
origem, evitando confirmação circular de conteúdo produzido pelo CadernoMat.

O sistema continua sendo RAG, sem treinamento de uma rede neural própria.
Avaliações pessoais, se necessárias, ficam locais e usam apenas materiais
já autorizados. Repositório, screenshots e fixtures recebem dados fictícios.

## 4. Fase 3 — páginas, organização e apresentação

Preserve organização fiel, contrato por IDs, rótulos catalogados, hashes,
ordem obrigatória, recursos congelados, prévia e checkpoint recuperável.
Nova explicação por IA continua uma modalidade identificada e revisável.

Como evolução, permitir separar uma seção por títulos Markdown apenas quando
as fronteiras forem inequívocas. Conservar caracteres, offsets, fórmulas,
condições, citações, recursos e ordem. Respeitar cercas, matemática multilinha,
matrizes, tabelas, listas e grupos de demonstração indivisíveis. Conteúdo
incompleto permanece intacto para edição manual. Testar recomposição exata.

Acrescentar zoom na prévia, navegação por folha e orientação paisagem quando
útil para tabelas/gráficos. Melhorar quebras e manter título com o início do
conteúdo. Recusar blocos que não caibam, com orientação de ajuste; não recortar
conteúdo ou reduzir tudo até ficar ilegível.

Conservar o mesmo documento entre rascunho, versão, prévia, PDF e PNG. Repetir
cabeçalhos de tabelas quando necessário. Separar serialização JSON de LaTeX;
não substituir barras globalmente, pois matrizes/alinhamentos usam quebras
legítimas. Sintaxe renderizável não significa matemática correta.

Seguir o design existente, com temas, teclado, avisos acessíveis e janela mínima
1000 × 650. Não criar outro editor/biblioteca ou trocar de framework nesta fase.

## 5. Fase 4 — banco de questões, simulados e revisão

Reutilize atividades, versões e tentativas para um banco de questões por
caderno/assunto, com busca, filtros, origem e dificuldade declarada.
Referencie a versão da questão usada; editar o banco não muda tentativas antigas.

Permita montar simulados por seleção manual ou geração de proposta revisável.
Respeite formatos/limites suportados. Para material documental, conserve
referências; revise gabaritos e explicações antes de publicar a atividade.

Acrescente tempo de prova com regras explícitas: início, pausas permitidas,
prazo, comportamento ao fechar e reabrir e finalização. O backend controla
estado e snapshots; não dependa apenas de um contador JavaScript. Autosave
deve preservar respostas após interrupção. Este é um recurso de estudo,
sem alegar controles de uma plataforma de fiscalização de provas.

Gabarito oculto continua protegido no backend, inclusive em dicas, exportação
e páginas derivadas. A correção objetiva conserva tolerâncias/convenções.
Questões abertas mantêm revisão manual e feedback de IA separados da nota.

Crie histórico dos erros por assunto, com acesso à questão, tentativa e
revisão. Distinguir erro objetivo, não respondido e revisão pendente. Acertar
uma alternativa não comprova domínio; ver a solução não equivale a errar.
Permitir refazer questões e organizar revisões, sem inventar índices de
aprendizagem ou classificar o aluno a partir de evidência insuficiente.

## 6. Fase 5 — backup, restauração e distribuição

Acrescente exportação/restauração pela interface de um pacote com banco,
materiais, recursos, imagens, versões, configurações não secretas e manifesto
de hashes/versão. Chaves ficam fora do pacote por padrão; não apagar ou modificar
as credenciais existentes ao produzir o backup.

Obtenha um snapshot consistente do SQLite e dos arquivos, coordenando tarefas
ativas. Não copie apenas o banco aberto ignorando WAL ou operações pendentes.
Inclua limites e valide o pacote em área temporária: hashes, integridade,
relações, caminhos, arquivos obrigatórios e compatibilidade de versão.
Impeça extração fora do destino, links simbólicos e expansão descontrolada.

Mostre o conteúdo antes de aplicar a restauração e preserve um backup do estado
atual. Falhas devem permitir rollback, sem mesclar bancos arbitrariamente nem
sobrescrever silenciosamente os dados. Teste restauração com dados fictícios e
conserve os registros pessoais durante o desenvolvimento.

Depois, faça aceite nativo Windows: ambientes/dependências próprios, interface,
Ollama, dados, ferramentas, OCR quando instalado e exportação PDF/PNG.
Não copie executáveis ou ambientes virtuais Linux para o Windows. Crie atalho
e, após esse aceite, instalador/EXE com versão e atualização que conserve dados.
Planeje licença/distribuição das dependências e requisitos do runtime/modelos.
Sem acesso ao Windows, documente o que foi preparado e o que falta testar.

## 7. Fase 6 — desempenho, GPU e interpretação de imagens

Meça RAM/swap, uso observado de GPU/VRAM, carga, tempo até primeiro conteúdo,
entrada/geração, tokens e motivo de término. Compare o mesmo pedido/modelo/digest,
tarefa, perfil e contexto. Separe carga fria e estado observado; não atribua um
ganho ao modelo com base em uma resposta mais curta ou amostra insuficiente.

Mantenha perfis para o notebook e o PC de casa. Confirme CPU, RAM, VRAM e runtime
antes de escolher modelos maiores. Compare candidatos com o conjunto de referência,
incluindo correção e português, em vez de escolher só pelo tamanho ou velocidade.
Use documentação oficial atual quando for selecionar/instalar runtime ou modelo.

Não execute downloads de pesos, instalação de drivers, mudanças de kernel,
reinício, swapoff, limpeza de caches ou encerramento de processos do usuário
automaticamente. Se uma dessas ações for necessária, prepare diagnóstico,
ação concreta, impacto e recuperação antes de solicitar a autorização específica.
CPU e organização local devem continuar utilizáveis sem essas mudanças.

Para visão futura, distinguir extração de texto/OCR, interpretação de imagem
por modelo multimodal e geração de ilustração. Uma capacidade não implica as
outras. Permitir selecionar página/imagem, conferir resolução/limites, destino
dos dados e corrigir a transcrição antes de resolver símbolos ambíguos.

Reutilize gráficos/diagramas determinísticos para resultados matemáticos.
Ilustrações artísticas são apoio visual, sem função de verificar contas.
Se futuramente houver um gerador de imagens, integre como serviço opcional
com origem, limites e persistência, mantendo a compatibilidade dos provedores.

## 8. Confiabilidade, testes e critérios de aceite

Use armazenamento privado, escrita atômica, limites e tarefas canceláveis.
Prefira snapshots/JSON existentes quando suficientes. Nova migração exige
justificativa, backup, transação, compatibilidade e teste de rollback.
Preserve modelos/provedores escolhidos; falha local não causa fallback online.

Na primeira entrega, os testes relevantes devem cobrir:

1. Indução com base ausente, k específico, passo incompleto e conclusão sem domínio.
2. Fórmula correta com prosa falsa, contraexemplo inválido e tentativa não enviada.
3. Domínio/valor/limite/extensão, pedidos mistos e saudações.
4. Extração correta/parcial, fórmula OCR ambígua e figura não interpretada.
5. Recuperação da página esperada, fonte ausente, material removido/desmarcado
   e revisão do documento após preparar a consulta.
6. Citação existente que não sustenta a afirmação: não aprovar só pelo ID.
7. Documento com instruções maliciosas e conteúdo da própria IA como fonte.
8. Parser/ferramenta fora do escopo, aproximação e narrativa que discorda do resultado.
9. Contexto 2048/4096, orçamento adequado para JSON, resposta parcial,
   cancelamento/timeout, idempotência e recuperação após reiniciar.
10. Integridade/FKs, hashes e preservação de registros/configurações antigos.

Faça o aceite real Qt com dados fictícios: marcar materiais, perguntar, conferir
prévia, receber resposta simulada/consulta local finita, abrir fontes, executar
uma ferramenta compatível, criar página fiel, salvar/exportar e recuperar após
reiniciar. Conferir temas, teclado e janela mínima; inspecionar as folhas PDF/PNG
afetadas. Provedores online devem ter testes simulados, sem consumir créditos.

Nas fases seguintes, acrescentar aceites específicos: segmentação/recomposição
exata, zoom/paisagem, gabarito protegido, cronômetro/reinício, restauração válida/
inválida e Windows quando houver acesso real. Rode regressões apropriadas,
compile o frontend alterado e não repita testes sem mudança/falha que justifique.

## 9. Ordem e entrega

1. Auditar estado/dados e atualizar planejamento.
2. Reproduzir falhas e estabelecer casos/rubricas independentes.
3. Melhorar o fluxo de fontes e limites de extração/recuperação.
4. Integrar revisão por tarefa e ferramentas compatíveis com prévias explícitas.
5. Entregar o percurso completo de estudo e recuperação após reiniciar.
6. Executar testes e pequeno subconjunto real offline, registrando também falhas.
7. Atualizar documentação e publicar código, testes e interface compilada no GitHub.
8. Manter as fases 3 a 6 como próximos incrementos conforme seus critérios.

Ao concluir a primeira entrega, explique o que funciona, o que foi conferido
por ferramentas, o que exige revisão, medições comparáveis, dados preservados
e pendências. Liste os arquivos alterados e como abrir/usá-los pelo atalho.
Não declare todos os erros da IA resolvidos, nem Windows/GPU/visão validados
quando tiver feito somente preparação ou simulação.
