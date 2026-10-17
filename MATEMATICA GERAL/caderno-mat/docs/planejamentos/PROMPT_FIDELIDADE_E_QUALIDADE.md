# Prompt — próxima etapa: organização fiel e qualidade matemática do CadernoMat

Continue o desenvolvimento do CadernoMat **neste notebook Linux**, implementando
uma etapa de organização fiel das páginas de estudo e melhoria da qualidade
matemática. Use a calibração já entregue para orientar o trabalho. Entregue um
fluxo útil, testado e publicado, preservando os dados pessoais.

O objetivo imediato é conseguir criar e organizar páginas com texto, fórmulas e
gráficos existentes sem depender de o modelo pequeno copiá-los corretamente.
Depois, melhorar a assistência da IA, a avaliação e o desempenho por tarefa.

## 1. Estado de partida: confirmar antes de implementar

- Repositório: https://github.com/JoaoGVP001/caderno-mat.
- Checkout atual: `/home/gvp/Projetos/tutor-calculo-1`.
- Referência do código: commit `3a26d2a`; commits posteriores podem conter este
  planejamento. Confira HEAD, branch e mudanças locais, sem sobrescrever nada.
- Pacote Python continua `tutor_calculo`; interface React/TypeScript/Tailwind
  executada pelo pywebview; assets compilados em `tutor_calculo/web`.
- SQLite **v11**; chats, cadernos, biblioteca, RAG textual/híbrido, atividades,
  tentativas, Cálculo/Discreta e páginas PDF/PNG já estão implementados.
- Modelo de chat preparado: `qwen3.5:4b-q4_K_M`, Ollama 0.40.3 na última rodada.
  Embeddings usam outro modelo, `qwen3-embedding:0.6b`.
- Notebook observado: i5-13420H, aproximadamente 8 GB RAM e RTX 3050 Laptop
  de 6 GB. Inferência recente em **CPU**, não GPU.
- Última suíte: 232 testes Python aprovados e dez opcionais ignorados. Aceite
  Qt de páginas confirmou recusa, preservação, proposta válida, PDF/PNG,
  autosave/reinício e temas. Os 35 testes React e oito fluxos Qt anteriores são
  referências históricas; não afirmar que foram todos repetidos na calibração.

Leia primeiro `README.md`, `PLANEJAMENTO.md`, `GUIA_CONTINUIDADE.md` e:

- `docs/CALIBRACAO_IA_LOCAL.md` e `docs/ESTABILIDADE_IA_LOCAL.md`.
- `docs/PAGINAS_ESTUDO.md`, `docs/INTERFACE.md` e `docs/DESIGN.md`.
- `docs/MATEMATICA_LOCAL.md`, `docs/DISCRETA.md` e `docs/ATIVIDADES.md`.
- `docs/MATERIAIS.md`, `docs/BUSCA_SEMANTICA.md` e `docs/OLLAMA.md`.
- `docs/TRANSFERENCIA_PC_CASA.md`: continuidade futura; Windows ainda não foi
  validado e não é o computador desta execução.

Inspecione especialmente `ia.py`, `avaliacao_local.py`, `desempenho.py`,
`recuperacao.py`, `paginas.py`, `paginas_servico.py`, `exportar_paginas.py`,
`provedores/ollama.py`, `frontend/src/Pages.tsx`, `StudyDocument.tsx` e os testes.
Confira instruções aplicáveis do repositório. Registre um plano curto com
critérios verificáveis e comece a implementação, sem encerrar apenas no plano.

## 2. Falhas confirmadas e correções que devem ser conservadas

**Geração de páginas:** o 4B produziu JSON estruturalmente válido, mas alterou
a identidade da soma dos naturais e inventou uma condição `n != -2`, sem apoio
nos dados. JSON válido e encerramento por `stop` não provaram correção matemática.

**Fidelidade ainda insuficiente:** uma nova proposta com o contrato real L4
omitiu/reescreveu fórmulas de origem e duplicou escapes LaTeX. Foi recusada pelo
validador. A proteção atual confere presença da notação marcada em `$`, `$$`,
`\(...\)` e `\[...\]`, ignorando espaços/código. Não confere equivalência,
prosa, matemática sem delimitadores ou fórmulas adicionais. Uma origem incorreta
também pode ser copiada fielmente. Não retirar esse controle para fazer o teste passar.

**Precisão pedagógica:** na correção de `(x²-1)/(x-1)`, o núcleo foi correto:
domínio exclui 1, valor em 1 não existe e limite é 2. Porém o título
“Extensão (Domínio)” confundiu conceitos. Algumas explicações de indução ainda
usam redação pouco precisa sobre k arbitrário e ultrapassam a meta suave de
palavras. Verifique o argumento, não apenas palavras-chave.

**Saudação e metadados:** já foram ajustados. A saudação final ficou em
16 palavras/22 tokens/~6,54 s, enquanto antes iniciou aula com 192 tokens.
Assuntos/etiquetas da atividade passaram a vir sem aspas decorativas. Preservar
esses ganhos; saudações com pedido de conteúdo devem continuar sendo perguntas.

**Desempenho:** consultas matemáticas recentes levaram cerca de 36–87 s em CPU,
dependendo da tarefa. Respostas menores reduziram tempo total; não foi comprovada
aceleração do motor. RAM/swap permanecem relevantes. Não culpar React, quantização
ou memória por erros matemáticos sem evidência específica.

**GPU:** no último diagnóstico, kernel 7.0.0-38 sem módulo NVIDIA compatível;
pacote de módulos instalado correspondia a 7.0.0-34. `nvidia-smi` falhou.
Nenhuma correção administrativa foi executada. Reconfira o estado atual.

**Problemas antigos já tratados:** corte em 1024 tokens dentro de Mermaid,
aviso misturado ao Markdown, corpo inteiro vermelho e métricas perdidas.
Perfis, avisos separados, métricas nas falhas, repetição curta e próxima parte
explícitas já existem. Não refazer essas entregas nem reintroduzir os problemas.

## 3. Primeira entrega: organização local que conserve o conteúdo

Implemente uma opção clara de **organizar preservando o conteúdo**, utilizável
sem Ollama, chave ou internet. Reutilize o editor/versionamento/exportação L4.

- Partir de seções selecionadas, mensagem escolhida ou resultados locais já
  autorizados, mantendo a prévia do que será utilizado.
- Copiar texto de origem, fórmulas, condições, citações e imagens existentes;
  não gerar demonstração, gabarito, resumo matemático ou exercício novo nesse modo.
- Preservar a ordem do raciocínio por padrão. Mover fragmentos de uma prova pode
  mudar seu significado mesmo que as fórmulas permaneçam iguais.
- Começar por seções inteiras. Se dividir Markdown por títulos, usar uma análise
  que respeite cercas de código, matemática multilinha, listas e tabelas.
  Não cortar uma equação, hipótese, tabela ou cadeia de demonstração.
- Blocos incompletos/ambíguos devem permanecer íntegros, com indicação para
  edição manual; não fechar LaTeX nem completar conteúdo por adivinhação.
- Reutilizar imagens/recursos congelados, IDs, hashes e versões; não recalcular
  um gráfico ou modificar resultados ao organizar a página.
- Mostrar a página resultante antes de aplicar; aplicação explícita deve
  preservar o original e permitir recuperação pela arquitetura existente.

A fidelidade deve ser verificável por conteúdo/offset/hash, além de testes.
Qualquer transformação de formatação deve ser identificada; não normalizar
silenciosamente o texto matemático. Preserve parágrafos explicativos, pois
condições e quantificadores frequentemente estão fora dos delimitadores LaTeX.

Não criar uma segunda biblioteca/editor ou um novo armazenamento de imagens.
Se algum limite de exportação impedir uma página, informar e permitir divisão
manual; não reduzir legibilidade ou recortar conteúdo para esconder o problema.

## 4. IA organiza por referências, sem reproduzir fórmulas

Depois do fluxo local, ofereça assistência opcional da IA para escolher rótulos
e organizar **blocos existentes por ID**. Evite pedir ao 4B que regenere toda a
resolução em JSON.

Projete um contrato mínimo, por exemplo uma lista de `bloco_id` e rótulo de seção.
Os IDs precisam vir de uma lista autorizada no snapshot. O backend monta o
documento com os originais; texto matemático/imagens não retornam do modelo.

- Rejeitar IDs inexistentes, duplicados, referências cruzadas não autorizadas,
  exclusão de blocos obrigatórios e parâmetros fora dos limites.
- Definir ordem obrigatória/grupos indivisíveis para raciocínios que não podem
  ser rearranjados; não confiar na IA para descobrir todas as dependências.
- Usar rótulos neutros/catalogados quando suficiente. Um título novo também
  pode introduzir uma afirmação falsa: não liberar equações/condições inventadas
  no título como caminho para contornar a preservação.
- Enviar somente os dados necessários à tarefa, conforme orçamento, seleção e
  destino mostrados na prévia. Se dados essenciais não couberem, pedir seleção
  menor; não descartá-los silenciosamente.
- Revalidar seleção, revisões, fontes removidas, modelo/provedor e hashes antes
  de enviar/aplicar. Não iniciar consulta ou aplicação automática após reiniciar.
- Distinguir texto original, organização sugerida pela IA, resultados de
  ferramentas e edições do usuário. Origem IA anterior continua sendo IA; copiar
  uma resposta não a converte em resultado matemático verificado.

Se mantiver a modalidade atual de **nova explicação por IA**, separá-la
claramente da organização fiel. Ela continua proposta revisável, com fontes,
aviso de limitações e aplicação explícita. Não inserir afirmações novas em uma
página apresentada como mera reorganização do original.

Não substituir uma proposta falha por uma “corrigida” sem explicar a origem.
Falha mantém rascunho/versões e oferece opções reais: organizar localmente,
editar manualmente ou preparar outra consulta por ação do usuário.

## 5. Fórmulas, JSON e apresentação

- Tratar serialização JSON e conteúdo LaTeX como camadas distintas.
- Reproduzir casos de escapes duplicados sem converter globalmente `\\` em
  `\`: quebras de linha em matrizes/ambientes podem usar barras legitimamente.
- No modo fiel, copiar o original localmente resolve a dependência de escape
  gerado pela IA; testar ida/volta Python → JSON → React → KaTeX → PDF/PNG.
- Validar sintaxe de apresentação pelo renderizador existente, conservando
  texto original e erro acessível. Sintaxe válida não é matemática correta.
- Conservar fórmulas inline/bloco, frações, índices, matrizes, desigualdades,
  delimitadores, Unicode, tabelas e cercas de código com aparências semelhantes.
- Exibir origem e motivo da recusa com linguagem precisa. Uma notação diferente
  pode ser equivalente: não rotular toda recusa literal como erro matemático.
- Rascunhos, cópia, versões e PDF devem conservar os mesmos dados de origem.

Não usar `eval`, código/SVG/HTML arbitrário do modelo, imagens remotas ou comandos
contidos nos documentos. Aproveite sanitização e recursos locais existentes.

## 6. Qualidade das explicações e uso das ferramentas

Melhore por tarefa com rubricas e casos de regressão, evitando um prompt global
que transforme saudações ou perguntas de Discreta em aulas de Cálculo.

Para Cálculo, distinguir domínio original, valor no ponto, limite, continuidade
e extensão contínua. Cancelar fator não preenche buraco; respeitar hipóteses,
unidades quando informadas e limites das operações implementadas.

Para indução, exigir domínio/n inicial, caso base, k arbitrário, hipótese,
implicação P(k) ⇒ P(k+1) e conclusão universal. Testes numéricos finitos não
substituem prova. Se faltar a tentativa do aluno, solicitar a informação, sem
inventar qual erro ele cometeu.

Nas ferramentas existentes, distinguir cálculo simbólico, aproximação e não
verificado. Reusar SymPy/Discreta quando a entrada estiver no parser suportado,
com confirmação já prevista; a explicação da IA não muda resultado/gabarito.
Não tentar converter qualquer texto/LaTeX em expressão executável.

Revisão de demonstrações continua limitada. Concordância de dois modelos,
palavras-chave, JSON válido, presença de fórmulas ou checagem finita não são
certificação. Feedback pedagógico não deve atribuir raciocínio que não foi escrito.

Metas de palavras são orientação: não truncar uma prova correta para atingir
uma contagem. Priorizar um núcleo completo; conteúdo extra pode vir por próxima
parte explícita, conservando fontes, snapshots, idempotência e orçamento.

## 7. Desempenho e GPU em trilhas separadas

Meça antes de otimizar: tempo até primeiro conteúdo, carga/entrada/geração,
tokens, parâmetros, RAM/swap e dispositivo observado. Comparações devem manter
pedido, tarefa, modelo/digest, contexto e perfil identificados; separar carga
fria e estado observado. Não publicar p95/ganho percentual sem amostra adequada.

Use o avaliador existente com chamadas/tempo finitos e casos fictícios. Atualize
seu caso de página para testar organização por referências, preservando também
os exemplos negativos anteriores. Primeiro use pesos já instalados.

Se comparar outro modelo, verificar documentação primária, tamanho, licença,
capacidades, compatibilidade e memória. Download deve ser uma ação explícita;
não instalar/trocar modelo silenciosamente nem assumir que menor será mais correto.
Alterações de sampling, cache, threads e thinking precisam de uma hipótese e
comparação de qualidade. Não habilitar thinking custoso como solução automática.

Diagnostique NVIDIA somente em leitura: kernel, módulos, driver, PCI e estado
do runtime. Detectar placa não comprova inferência na GPU. Caso haja correção
administrativa necessária, apresente procedimento concreto, impacto, risco,
backup/recuperação e necessidade de reinício **antes** de executá-la; aguarde
autorização explícita para essa trilha. Não bloquear o trabalho seguro em CPU.

Não executar swapoff, limpar caches globais, matar processos do usuário,
desativar sandbox ou modificar Secure Boot sem uma decisão separada. Conservar
coordenação das operações pesadas e fallback FTS informado. A organização local
deve funcionar rapidamente sem esperar que o driver seja corrigido.

## 8. Materiais, RAG e limites do conteúdo

Preservar os seis materiais pessoais/índices existentes, sem reimportação,
reindexação completa automática ou publicação de conteúdo do Classroom.

Separar três avaliações: qualidade da extração, recuperação do trecho correto
e correção da resposta. Um trecho relevante não garante a conclusão do modelo.
Ampliar um pequeno conjunto de perguntas com respostas/páginas conhecidas,
incluindo informação ausente, fonte parcial, fórmula com OCR duvidoso e documentos
com instruções maliciosas. Dados pessoais somente em avaliação local autorizada;
fixtures públicos devem ser fictícios.

Manter seleção explícita e citação de arquivo/página/slide. Desmarcar/remover
material invalida usos futuros, sem apagar o passado da conversa. Figura não
extraída deve continuar desconhecida; não imaginar seu conteúdo.

Este sistema usa RAG/embeddings, não treinamento de uma rede neural própria.
Visão multimodal, sincronização Classroom e leitura geral de diagramas ficam
para uma etapa posterior, após fidelidade/qualidade; não simulá-las com texto.

## 9. Preservação, compatibilidade e arquitetura

Preservar chats, parciais, cadernos, materiais, vetores, fontes selecionadas,
atividades, gabaritos, tentativas, cálculos, imagens, páginas, versões, exportações,
preferências e o atalho Linux. Não substituir React/pywebview nem renomear o
pacote interno nesta etapa.

Guardar relatórios, originais, pesos, índices e chaves fora de Git. Usar arquivos
atômicos, limites de entrada/saída/tempo e processos encerráveis. Documentos são
dados de consulta e não podem controlar o aplicativo.

Preferir snapshots/JSON versionados existentes quando suficiente. Se novo
esquema for necessário, justificar e fazer backup, migração transacional e
testes de rollback; preservar IDs e leituras de propostas/versões antigas.

Ollama, Gemini e OpenAI continuam escolhas explícitas; nenhuma falha provoca
fallback online. Testar provedores pagos com simulações e não usar uma chave
real para esta etapa. Biblioteca/copiar/exportar/organizar localmente continuam
funcionando offline. Não declarar Windows validado por existir um `.ps1`.

## 10. Testes e critérios de aceite

Testes devem cobrir, com variantes matemáticas legítimas:

1. Organização local sem modelo/API; conservação de texto, ordem, fórmulas,
   condições em prosa, citações e recursos/hash.
2. Cercas, tabelas, fórmulas multilinha, blocos incompletos e fronteiras de corte;
   nenhum conteúdo omitido/corrigido silenciosamente.
3. Contrato por referências: IDs desconhecidos/duplicados, fonte removida,
   revisão alterada, bloco obrigatório ausente, grupo fora de ordem e limites.
4. Casos negativos de identidade alterada, n!=−2 inventado, escapes LaTeX
   duplicados, fórmula correta acompanhada de prosa falsa e origem incorreta.
5. Fidelidade diferente de correção: um texto original errado permanece errado;
   nenhum selo global é produzido por copiar ou renderizar.
6. Domínio/valor/limite/extensão e indução sem hipótese; não aprovar por keywords.
7. Saudações curtas versus “Olá, explique indução”, pedidos mistos e caderno
   configurado para explicação completa.
8. JSON de atividade, gabarito pontual e solução protegida; os contratos não
   podem receber orçamento insuficiente ou revelar gabarito antes da hora.
9. Timeout, cancelamento, erro, checkpoint e reinício; métricas conhecidas
   preservadas e ausências nulas, sem retry infinito.
10. Dados antigos, versões e resultados preservados; hash/integridade/FKs,
    migração/rollback se houver alteração real do esquema.

Aceite na janela Qt: criar página de uma resposta, organizar localmente,
visualizar fórmulas/imagem, salvar versão, exportar PDF/PNG, reiniciar e recuperar.
Depois testar proposta por IDs, recusa visível, aplicação explícita e preservação.
Conferir temas/1000×650 e acessibilidade dos avisos. Inspecionar visualmente as
folhas afetadas, sem aceitar PDF que apenas tenha o cabeçalho correto.

Execute regressões apropriadas: Python, React se alterado, build se alterar
frontend, e2e de páginas/estabilidade e outros fluxos afetados. Rodadas reais
devem ser pequenas, offline e limitadas; publicar também falhas/limitações.

Critério principal: a página da soma dos naturais conserva identidade, n inicial,
texto e recursos sem o modelo redigitá-los. Quando a IA falha, a organização
local continua útil e os dados originais ficam intactos. A conclusão do runtime
é registrada separadamente da revisão matemática.

## 11. Ordem de execução e entrega

1. Confirmar estado, ler documentação, preservar dados e atualizar planejamento.
2. Reproduzir os casos de falha com fixtures, sem consultas pagas.
3. Entregar primeiro organização local fiel, prévia, versões e PDF/PNG.
4. Implementar assistência opcional por IDs/contrato limitado, com preservação.
5. Refinar explicações/rubricas e investigar LaTeX sem reparos indiscriminados.
6. Atualizar calibração e executar o subconjunto real justificável em CPU.
7. Avaliar extração/RAG e registrar pendências; diagnosticar GPU separadamente.
8. Executar testes, inspecionar artefatos, atualizar documentação e publicar.

Entregue código funcional, documentação, testes, interface compilada quando
necessário e alterações no GitHub. Exemplos/capturas públicos devem ser fictícios.
Informe o que mudou, por quê, testes/medições, dados preservados, falhas restantes
e próximos passos. Não chamar essa etapa de solução de todos os erros da IA.

Depois desta entrega, manter como backlog: comparação de modelos/hardware,
aceite Windows e instalador/atalho, provas/simulados cronometrados, qualidade de
RAG com materiais reais, melhorias de zoom/orientação/paginação e L5 de visão.
Priorizar conforme evidências; não começar todas essas trilhas simultaneamente.
