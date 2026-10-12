# CadernoMat — resumo completo para continuar no PC de casa

Estado consolidado em **12/10/2026**. Este documento descreve o código entregue,
os dados locais existentes, os limites conhecidos e o primeiro trabalho no
Windows. Os documentos mais antigos registram o estado de suas respectivas
entregas; uma indicação antiga de “próxima etapa” pode já ter sido atendida.

## 1. Identidade e objetivo

O projeto começou como **Tutor de Cálculo I**, com uma interface Tkinter para
resolver e explicar exercícios. Foi ampliado e rebatizado **CadernoMat**:
um aplicativo desktop de estudos de matemática, com conversas, cadernos por
matéria, materiais, atividades e páginas de estudo exportáveis.

O foco inicial é **Preliminares**, **Cálculo Diferencial e Integral I** e
**Matemática Discreta**. Outros cadernos podem ser criados pelo usuário.

- Repositório: <https://github.com/JoaoGVP001/caderno-mat>.
- Branch de trabalho e publicação: `main`.
- Checkout no notebook: `/home/gvp/Projetos/tutor-calculo-1`.
- Nome interno do pacote Python: `tutor_calculo`, mantido para compatibilidade.
- Interface principal: React em uma janela desktop; Tkinter é apenas legado.

O nome antigo da pasta/pacote não indica que ainda seja um programa restrito a
Cálculo I. O destino no Windows pode ser uma pasta chamada `caderno-mat`.

## 2. Visão geral das entregas

| Área | Estado atual |
| --- | --- |
| Conversas persistentes | Entregues, com contexto recente e organização |
| Cadernos por matéria | Entregues, com orientações pedagógicas |
| Interface React e fórmulas | Entregues, com temas claro/escuro e KaTeX |
| Anexos e biblioteca | Entregues, com extração, busca e preservação |
| Atividades e tentativas | Entregues, com versões e correção objetiva limitada |
| Gemini e OpenAI | Integrados, com chave/configuração do próprio usuário |
| L0: piloto local | Executado no notebook com Ollama e modelo real |
| L1: IA local na interface | Entregue, com streaming, cancelamento e recuperação |
| L2: busca semântica/híbrida | Entregue, com embeddings locais e indexação retomável |
| L3: cálculos e gráficos | Entregue para o subconjunto documentado de Cálculo |
| L3: Matemática Discreta | Entregue para conjuntos/relações finitos e lógica proposicional |
| L4: páginas de estudo | Entregue, com versões, PDF e PNG por folha |
| Estabilidade local | Entregue após o diagnóstico da resposta cortada |
| Windows/RTX 3060 | Instalação preparada no código; aceite real ainda pendente |
| L5: visão e ilustrações amplas | Planejada; há somente ilustração conceitual local de indução |
| Instalador/EXE Windows | Ainda não entregue |

### Conversas e cadernos

As conversas podem ser criadas, renomeadas, fixadas, movidas, arquivadas,
restauradas e excluídas com confirmação. O menu aparece no hover e no foco por
teclado. Há pesquisa, títulos abreviados com tooltip, rascunhos persistentes e
recuperação da última navegação. O visual atual não exige o antigo efeito de
deslizamento do título para revelar o nome completo.

Cada caderno reúne chats, materiais, atividades e páginas. É possível editar
objetivo, nível, assuntos e orientações para a IA; arquivar, reordenar e mover
conteúdo. Geral acolhe conteúdo sem matéria. Excluir um caderno conserva os
registros associados, sem transformar essa organização em exclusão de documentos.

O contexto enviado à IA separa orientações do caderno, conversa recente e
trechos documentais. Pertencer ao caderno não autoriza automaticamente uma fonte.

### Interface e apresentação

A interface principal foi migrada de Tkinter para **React + TypeScript + Vite +
Tailwind**, em uma janela **pywebview**. Usa Inter, ícones Lucide, cores e
componentes comuns, lateral recolhível, temas claro/escuro e tamanho mínimo
1000 × 650. Markdown, tabelas, blocos de código e fórmulas são renderizados com
KaTeX; copiar conserva o texto original.

Assets e fontes são locais e compilados em `tutor_calculo/web`. Abrir o programa
não exige Node, servidor Vite nem conexão a um CDN. Alterar o frontend exige
recompilar esses assets. O modo Tkinter anterior continua opcional, separado.

### Anexos, links e biblioteca

A aba Materiais reúne arquivos e links, com origem, estado de processamento,
nome, tipo, tamanho, assunto, etiquetas e associações a cadernos. Oferece busca,
filtros, paginação, consulta do texto/original, reprocessamento, reutilização,
desvinculação e exclusão com atualização de índices.

Formatos atualmente interpretados:

- PDF textual; PDFs digitalizados e imagens por OCR opcional.
- TXT, Markdown, CSV, JSON, LOG e TEX.
- DOCX e PPTX: texto, tabelas e parte das fórmulas Office/OMML, com referências
  de página ou slide quando disponíveis.
- Links públicos HTML, texto e PDF, com conteúdo extraído para consulta.

Há limite de **20 MiB por arquivo**, **500 páginas de PDF/slides** e **10 páginas
de OCR**. OCR depende de Tesseract e dos idiomas instalados. Outros formatos
podem ser armazenados, mas são identificados como não interpretados. A extração
de Office é parcial: figuras, diagramas, objetos embutidos e fórmulas fora do
subconjunto suportado precisam de conferência no original.

Arquivos iguais são deduplicados por SHA-256. As fontes usadas pela IA são
selecionadas explicitamente e aparecem na prévia do envio. A consulta atual
envia texto recuperado; não envia o PDF/imagem original como anexo multimodal.

### Memória documental e RAG

O fluxo implementado é:

```text
Arquivo/link → extração por página/slide → trechos → FTS5
                                          ↓
                              embeddings locais opcionais
                                          ↓
Pergunta + fontes selecionadas → busca híbrida → trechos com origem
                                          ↓
                      prévia → provedor escolhido → resposta
```

O índice textual usa SQLite FTS5. A busca por significado usa
**Qwen3-Embedding 0.6B**, pela API local do Ollama. A comparação por cosseno e a
fusão de rankings RRF acontecem no Python. Indexação é explícita, incremental,
cancelável e retomável; hash, extrator, modelo/digest e dimensão são conferidos.
Remover ou alterar material invalida os vetores correspondentes.

As consultas de chat recuperam exclusivamente trechos dos materiais autorizados.
Falha na busca semântica deixa a busca textual disponível com aviso. Os trechos
conservam arquivo/link, página ou slide. Similaridade não comprova a correção de
uma resposta, e uma citação da IA ainda pode precisar de conferência.

**Não houve treinamento ou fine-tuning de uma rede neural própria.** Os modelos
continuam com os pesos originais; o aplicativo recupera informação local para
incluí-la no contexto. Histórico salvo também não significa que todo chat antigo
entre em todas as perguntas: o envio tem um orçamento limitado e fontes explícitas.

### Atividades e tentativas

Há listas manuais offline e propostas de atividades por IA, com respostas
abertas, múltipla escolha, verdadeiro/falso e números com tolerância absoluta.
Propostas exigem revisão e salvamento antes de se tornarem atividades.

Tentativas preservam respostas, posição e versão da atividade; podem ser
retomadas após reiniciar e comparadas no histórico. Editar uma atividade cria
outra versão sem alterar tentativas antigas. Dicas, feedback e revelação de
soluções são registrados. Respostas objetivas têm correção determinística no
escopo suportado; discursivas dependem de revisão manual/feedback pedagógico.

Não há corretor universal de demonstrações nem notas automáticas da IA para
respostas abertas. Provas cronometradas, simulados completos, flashcards e
indicadores de domínio do conteúdo permanecem planejados.

### Provedores de IA

O usuário escolhe **Ollama**, **Gemini** ou **OpenAI**, como padrão ou por conversa.
Há herança da configuração e prévia do destino/modelo/dados. Falhas não causam
troca automática para uma API online. Chaves dos provedores online são pessoais,
configuradas no aplicativo e armazenadas no `.env` local ignorado pelo Git.

Ollama permite conversa local real, streaming, cancelamento, repetição
idempotente, snapshots, recuperação de respostas interrompidas e diagnóstico
de modelos/CPU/GPU. Gemini/OpenAI conservam o fluxo atual sem streaming e sem
cancelamento equivalente ao local. Propostas JSON são validadas, mas essa
validação estrutural não certifica os gabaritos.

O modelo de chat preparado no notebook é **`qwen3.5:4b-q4_K_M`**, com Ollama
0.40.3. Embeddings usam outro modelo: **`qwen3-embedding:0.6b`**. O programa não
baixa modelos automaticamente nem assume que instalar o CadernoMat instala o
runtime. O piloto de terminal `iniciar_ia_local.sh` continua separado da interface.

### Ferramentas verificáveis de Cálculo

Funcionam localmente, sem perguntar ao modelo: expressões restritas em uma
variável real, gráfico, substituição, derivada, tangente, extremos de polinômios
até grau 4 e integrais próprias/área no escopo documentado. A matemática usa
SymPy; os gráficos usam Matplotlib em processo separado e cancelável.

O domínio original é preservado: cancelar uma divisão não apaga um buraco.
Polos, raízes, logs e cúspides recebem tratamento específico. Tangente exige
derivada bilateral finita; integrais impróprias continuam fora do suporte.
Resultados distinguem cálculo simbólico, aproximação numérica e não verificado.

A IA pode propor campos para revisão e explicar resultados, mas não muda o
resultado calculado. Expressões não são executadas com `eval`/`exec`. PNGs,
parâmetros, resultados e origem persistem após reiniciar.

### Ferramentas verificáveis de Matemática Discreta

Incluem operações de conjuntos finitos, cardinalidade, complemento com universo
explícito, produto cartesiano, relações, domínio/imagem, inversa/composição,
reflexividade, irreflexividade, simetria, antissimetria e transitividade com
contraexemplos. Lógica proposicional oferece tabelas-verdade, classificação e
equivalência com até seis variáveis/64 linhas.

O usuário confere os dados interpretados antes de executar. Diagramas pequenos
são produzidos localmente e exportados em PNG. Resultados podem ser vinculados
a atividade/questão/tentativa; comparar com gabarito não sobrescreve notas e
respeita a proteção da solução. Verificar casos finitos não demonstra afirmações
sobre todos os naturais nem prova indução matemática.

### Páginas de estudo e exportação — L4

Há editor de páginas por caderno, com seções Markdown/KaTeX, busca, arquivo,
duplicação, rascunho/autosave e versões independentes. Páginas podem começar
manualmente ou a partir de chat, questão e resultado local. Imagens de resultados
são copiadas e congeladas por hash; versões anteriores continuam preservadas.

A IA propõe organização de seções/fontes selecionadas, com prévia e aplicação
explícita. Exportação local usa um worker Qt para **PDF A4 com texto selecionável**
e **um PNG por folha**, com fundo branco, pautado ou quadriculado e repetição de
cabeçalhos de tabelas. Exporta uma versão salva, separada do rascunho.

Falhas/cancelamentos não publicam uma exportação concluída. Blocos/fórmulas
inválidos ou grandes demais são recusados, sem cortar conteúdo silenciosamente.
Uma versão revisada pode ser adicionada explicitamente à biblioteca como
Markdown, conservando proveniência e sem seleção/indexação automática.

## 3. Última atualização: resposta cortada e desempenho

O problema observado na explicação de indução foi investigado pelos registros
da consulta, não apenas pela captura de tela. A resposta chegou exatamente ao
teto de **1024 tokens**: cerca de **164 segundos** no total, corte dentro de
Mermaid e aviso misturado ao texto. Não foi confirmado estouro de RAM ou timeout
como causa desse corte. Naquela pergunta não havia trechos documentais enviados.

Também foi identificado que o runtime estava usando **CPU**: o módulo NVIDIA
instalado correspondia a outro kernel do notebook. Havia pressão de RAM/swap.
A correção administrativa do driver/kernel não foi feita; esse problema Linux
não deve ser reproduzido como instrução de instalação no Windows.

A atualização implementou:

- Perfis Rápido, Estudo e Completo, com orçamento de entrada/saída por tarefa.
- Avisos separados do Markdown, preservando o conteúdo parcial sem pintar toda
  a mensagem como erro.
- Métricas persistidas também em falhas: tokens, tempos, encerramento,
  parâmetros, dispositivo observado e memória quando mensurável.
- **Repetir curto** e **Próxima parte** com prévia, envio explícito, fontes
  revalidadas, relação à resposta de origem e configuração por chamada.
- Coordenação de operações pesadas; busca FTS continua disponível com aviso
  quando a busca híbrida não puder usar o runtime ocupado.
- Instruções para priorizar um exemplo terminado e não prometer diagramas ou
  imagens que o aplicativo não produziu.
- Botão **Ilustração de indução**, com diagrama Matplotlib local de base,
  hipótese e passo. É uma ilustração conceitual, não uma prova verificada;
  pode ser incorporada às páginas/PDF/PNG.

| Perfil local | Teto narrativo | Tempo sugerido |
| --- | --- | --- |
| Rápido no notebook | 640 tokens | 180 s |
| Estudo | 1024 tokens | 240 s |
| Completo | 1536 tokens; exige contexto 4096 | 360 s |

Configurações anteriores continuam preservadas. O tempo pode ser ajustado e é
mostrado na prévia; JSON de atividades/páginas mantém uma reserva própria.
Contexto local atualmente aceita **2048 ou 4096**, sem expansão automática por
haver mais RAM. A estimativa do orçamento não é um tokenizer exato.

No aceite real offline em CPU, foram observadas respostas terminadas em
**82,57 s/404 tokens**, **95,36 s/452 tokens**, **46,27 s/237 tokens** e confirmação
final de **98,73 s/488 tokens**. O ganho foi conseguir respostas menores e
terminadas. A velocidade por token não aumentou: aproximadamente 5,8 tokens/s
na confirmação contra 6,7 na referência; carga/cache/prompt diferiram, sem
comparação controlada do motor. A redação matemática do modelo ainda exige revisão.

Medição de RAM/RSS/swap foi implementada pelo `/proc` no Linux. No Windows esses
campos atualmente podem ficar desconhecidos; informação CPU/GPU da API do
Ollama continua distinta dessa medição. Confirmar GPU significa observar o
modelo realmente carregado no dispositivo, não só encontrar uma RTX no PC.

Detalhes: [Estabilidade da IA local](ESTABILIDADE_IA_LOCAL.md).

## 4. Arquitetura e arquivos para o próximo desenvolvedor

**Continuação no notebook após este resumo:** a calibração por tarefa está em
[CALIBRACAO_IA_LOCAL.md](CALIBRACAO_IA_LOCAL.md). Inclui avaliador privado com
limites, saudações curtas e proteção de presença da notação original em novas
propostas de página. O 4B produziu JSON matematicamente incorreto e ainda falhou
no contrato de fidelidade; a recusa preserva os dados. Foram doze respostas
reais CPU/offline e 232 testes Python aprovados/dez opcionais ignorados. Mantém
SQLite v11 e não altera o plano de transferência Windows.

```text
React/TypeScript → ponte de operações permitidas → serviço Python
                                                  ├─ SQLite/arquivos locais
                                                  ├─ extração + FTS/embeddings
                                                  ├─ atividades/tentativas
                                                  ├─ Ollama/Gemini/OpenAI
                                                  └─ workers de matemática/PDF
```

| Arquivo/área | Responsabilidade |
| --- | --- |
| `frontend/src/App.tsx`, `model.ts` | Composição da interface, navegação e DTOs |
| `ConfigIA.tsx`, `LocalStudy.tsx` | Configuração, métricas, partes e ilustração |
| `Activities.tsx`, `StudyDocument.tsx` | Atividades e composição das páginas |
| `tutor_calculo/desktop.py`, `ponte.py` | Janela desktop e acesso restrito ao backend |
| `servico.py` | Coordenação, conexões por operação, tarefas e snapshots |
| `armazenamento.py`, `cadernos.py` | Histórico, migrações e organização |
| `materiais.py`, `extracao.py`, `links.py` | Biblioteca, importação e texto extraído |
| `semantica.py`, `recuperacao.py` | Índice semântico, busca híbrida e contexto |
| `atividades.py`, `tentativas.py`, `correcao.py`, `estudo.py` | Prática e propostas |
| `ia.py`, `preferencias_ia.py`, `provedores/` | Configuração e contratos de IA |
| `desempenho.py`, `continuacao.py` | Perfis, métricas e consultas em partes |
| `calculos.py`, `ferramentas_matematicas.py` | Execução matemática e artefatos |
| `discreta.py`, `discreta_servico.py` | Motor finito de Discreta e integração |
| `inducao.py`, `inducao_servico.py` | Ilustração conceitual local limitada |
| `paginas.py`, `paginas_servico.py`, `exportar_paginas.py` | Versões, recursos e exportação |
| `tutor_calculo/web` | Interface compilada distribuída com o código |
| `tests/`, `frontend/tests/` | Testes Python e fluxos de janela real |

SQLite está em **v11**. Migrações têm backups e preservam IDs/dados; a entrega
de estabilidade não mudou o esquema. As 33 tabelas da auditoria incluem tabelas
internas do FTS, não 33 funcionalidades independentes.

O navegador não deve acessar SQL, arquivos arbitrários, runtime ou chaves.
Documentos são dados de consulta, nunca instruções autorizadas para executar
shell. A IA não altera gabaritos, cálculos e versões por conta própria. Não
confundir “JSON válido”, “fonte encontrada” e “resposta matematicamente correta”.

## 5. Dados pessoais: o que levar do notebook

**Clonar o GitHub leva o código; seus chats e materiais precisam de transferência
separada.** Eles não foram publicados no repositório.

Origem padrão Linux: `/home/gvp/.local/share/CadernoMat/`.
Destino padrão Windows: `%LOCALAPPDATA%\CadernoMat\`.

| Item | Conteúdo e necessidade |
| --- | --- |
| `historico.sqlite3` | Essencial: chats, cadernos, atividades, tentativas, texto extraído, índices e páginas |
| `materiais/` | Essencial: originais deduplicados |
| `calculos/` | Essencial para imagens/resultados já salvos |
| `paginas/` | Essencial para recursos congelados e exportações internas |
| `ia.json`, `interface.json` | Preferências locais; revisar endpoint/modelos no novo PC |
| Backups `historico.sqlite3.*backup` | Recomendado conservar para recuperação |
| `planejamentos/`, `exemplos/`, `importacoes/` e relatórios | Material auxiliar privado; conservar conforme necessidade |
| `webview/` | Cache da janela; pode ser recriado |
| `ia-local/` | Pesos, executáveis Linux e relatórios do piloto; tratar separadamente |
| `.env` no checkout | Chaves online; reconfigurar pelo aplicativo no Windows, sem Git |

A pasta completa ocupa aproximadamente **5,9 GB** neste levantamento; cerca de
**5,8 GB** são `ia-local/`. Não é necessário copiar executáveis Linux para usar
Ollama no Windows. O runtime nativo deve ser instalado separadamente. Reutilizar
pesos exige conferir manifests e digest; usar a mesma tag baixada novamente não
garante que os pesos sejam idênticos aos do piloto.

Inventário conferido no último aceite: **seis materiais**, **317 páginas de texto
extraído**, **678 trechos** e **678 vetores**, além de três conversas, nove mensagens
e dois rascunhos de páginas de estudo. As 317 páginas são da extração dos materiais,
não 317 páginas de caderno produzidas. O inventário representa aquele momento;
uso posterior pode alterá-lo. Funcionalidades de atividades existem mesmo quando
o banco pessoal ainda não contém listas/tentativas criadas.

Os seis materiais importados do Classroom estão no acervo privado de Matemática
Discreta. Isso não confirma todos os anexos já publicados pela professora nem
constitui sincronização contínua com o Classroom.

Procedimento de transferência:

1. Fechar o CadernoMat e aguardar o encerramento de suas tarefas. Fazer uma cópia
   da pasta de dados antes de mover qualquer coisa; conservar a origem.
2. Copiar banco, materiais, cálculos, páginas e preferências juntos. Não copiar
   apenas o SQLite, pois as imagens/originais estão fora dele. Uma cópia de banco
   em uso exige a API de backup SQLite; não retirar apenas um arquivo enquanto
   houver escrita/WAL ativo.
3. No Windows, preparar o código/ambiente. Testar primeiro com dados fictícios
   ou com uma cópia isolada do acervo, usando `--banco`.
4. Com o aplicativo fechado, restaurar os dados em `%LOCALAPPDATA%\CadernoMat\`.
   Se houver dados no destino, guardá-los antes; não mesclar dois bancos à mão.
5. Abrir e conferir integridade, contagens, originais, imagens, páginas e busca.
   Comparar com o backup e registrar qualquer incompatibilidade antes de corrigir.
6. Reconfigurar chaves online pela interface, se forem necessárias. Revisar
   Ollama e o modelo de embeddings. Digest diferente exige reindexação explícita;
   não apagar documentos para reconstruir vetores.

Originais e artefatos usam nomes relativos à raiz de dados, e o vetor possui
formato portátil. A transferência Windows ainda precisa desse aceite real;
o banco não deve ser considerado migrado só porque a janela abriu.

Esta entrega documenta o procedimento; não cria sincronização, exportador de
backup, pacote de transferência ou envio dos dados pessoais a outro computador.

## 6. Preparar o Windows e abrir o programa

Você informou anteriormente Windows, 16 GB de RAM e RTX 3060 de 8 ou 12 GB de
VRAM. Como agora mencionou mais RAM, **confirmar a quantidade atual**, CPU, VRAM,
driver e espaço de disco é o primeiro diagnóstico. Não escolher modelo maior
nem aumentar contexto só com base no nome da placa.

### Código e ambiente Python

Em uma pasta de projetos, com Git e Python 3.12+ disponíveis:

```powershell
git clone https://github.com/JoaoGVP001/caderno-mat.git
cd caderno-mat
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\iniciar_desktop.ps1
```

O launcher Windows existe e usa a `.venv` dessa pasta. A janela requer Microsoft
Edge WebView2. A exportação PDF usa **PySide6/Qt WebEngine e PDFium**, mesmo quando
a janela principal usa WebView2; essas dependências constam em `requirements.txt`.
Não remover PySide6 supondo que seja exclusivo do Linux.

Não copiar a `.venv` Linux, `node_modules` ou executáveis do piloto para o Windows.
Criar ambientes nativos e reinstalar dependências. O atalho da área de trabalho
foi feito para o notebook Linux; um atalho Windows deverá ser criado após o
primeiro aceite. Não há EXE/instalador Windows nesta entrega.

Para desenvolver o frontend, o projeto declara **Node >=24** e
**pnpm 11.25.0** no `package.json`:

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm test
pnpm build
cd ..
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Node/pnpm são ferramentas de desenvolvimento, não requisito para abrir o build
já publicado. Os scripts e2e atuais foram executados no Qt/Linux e precisam de
adaptação/validação no Windows; os scripts offline com `unshare` são Linux.

### Ollama nativo e modelos

Instalar o aplicativo oficial para Windows. Ele executa em segundo plano e
expõe API local em `localhost:11434`, com suporte NVIDIA; disponibilidade da
GPU deve ser conferida durante inferência. [Documentação oficial Windows](https://docs.ollama.com/windows).

Com o runtime instalado, o download explícito dos modelos de referência é:

```powershell
ollama pull qwen3.5:4b-q4_K_M
ollama pull qwen3-embedding:0.6b
ollama list
```

Referências oficiais: [modelo de chat](https://ollama.com/library/qwen3.5:4b-q4_K_M)
e [modelo de embeddings](https://ollama.com/library/qwen3-embedding:0.6b).
Downloads exigem rede/disco; depois, consultas locais podem funcionar offline.
Registrar a versão do runtime e os digests dos pesos para comparação.

No CadernoMat: selecionar Ollama, URL `http://127.0.0.1:11434`, modelo de chat,
perfil/contexto e **Testar conexão e listar modelos**. Começar comparando o mesmo
4B usado no notebook, observando dispositivo/latência. Aumentar modelo/contexto
vem depois da medição; contexto acima de 4096 exigirá mudança no aplicativo.

O botão interno de iniciar runtime foi preparado para o piloto Linux. Na nova
máquina, iniciar Ollama pelo aplicativo nativo; não copiar `runtime-path.txt`
apontando para um executável Linux. Sem runtime/modelo local, biblioteca, páginas
e ferramentas manuais continuam disponíveis; a conversa local depende do serviço.

## 7. Validação realizada

- Última suíte: **218 testes Python aprovados** e dez opcionais Tk ignorados.
- **35 testes React** aprovados e compilação TypeScript/Vite concluída.
- **Oito fluxos reais Qt/Linux**: desktop, atividades, Ollama, semântica,
  Cálculo, Discreta, páginas e estabilidade, com persistência/reinício.
- Ollama real em ambiente com rede externa bloqueada; geração, propostas,
  recuperação e benchmarks locais. Gemini/OpenAI foram simulados nesses
  testes de regressão, sem consumo de créditos.
- Exportações reais e inspeção visual das folhas/PNGs; a etapa L4 conferiu
  catorze folhas e a estabilidade acrescentou a ilustração em PDF.
- Auditoria da estabilidade: hashes iguais nas **33 tabelas** e nos **nove
  arquivos/configurações** conferidos, integridade/FKs aprovadas, SQLite v11.

Esses resultados comprovam os casos exercitados no notebook, não qualidade
universal do modelo nem compatibilidade Windows já validada. A última entrega
preservou o banco pessoal, sem nova migração de esquema.

## 8. Próxima sequência no PC de casa

1. **Aceite Windows com dados fictícios:** preparar Python/WebView2/Qt/Ollama,
   abrir a interface, verificar diálogos de arquivo, temas, teclado e fechamento.
2. **GPU e benchmark de referência:** medir o mesmo 4B com prompts registrados,
   contexto/perfil fixos, casos frios/quentes e uso observado de GPU/VRAM.
3. **Transferência de dados:** validar uma cópia do acervo, sem tocar na única
   cópia pessoal; conferir FTS, arquivos, vetores, chats e páginas.
4. **Qualidade matemática/RAG:** avaliar com os slides reais de Discreta,
   perguntas com resposta conhecida, referências e demonstrações. Separar
   recuperação correta de resposta correta. Ampliar testes de indução.
5. **Modelos/perfis para o hardware real:** comparar candidatos com o 4B,
   tempo total, memória e acertos. Não há modelo maior escolhido/instalado.
   O candidato `qwen3:1.7b` documentado para o notebook não foi benchmarkado.
6. **Distribuição:** criar atalho Windows, depois instalador/EXE e atualização
   preservando os dados. Isso depende do aceite nativo anterior.
7. **Evolução de produto:** provas/simulados, visualização com zoom/orientação,
   melhoria de paginação de blocos grandes e avaliação de aprendizado.
8. **L5:** visão para figuras/PDFs, interpretação visual com fonte/página e
   ilustrações opcionais. A tag do modelo poder aceitar imagens não significa
   que o aplicativo já envie/interprete imagens dessa maneira.

Mais RAM/VRAM pode permitir modelos/contextos maiores e reduzir pressão de
memória. Não garante acerto matemático. Manter as ferramentas locais e os
resultados verificáveis separados da narrativa da IA continua central.

## 9. Documentos e marcos de código

Começar por este resumo e pelos documentos atuais:

- [README](../README.md): instalação e uso.
- [Guia de continuidade](../GUIA_CONTINUIDADE.md): entregas e contratos históricos.
- [Planejamento](../PLANEJAMENTO.md): produto e trilha L0–L5.
- [Interface](INTERFACE.md) e [Design](DESIGN.md): arquitetura visual.
- [Materiais](MATERIAIS.md), [Cadernos](CADERNOS.md), [Atividades](ATIVIDADES.md).
- [Ollama](OLLAMA.md), [Piloto](PILOTO_LOCAL.md), [Busca híbrida](BUSCA_SEMANTICA.md).
- [Cálculo](MATEMATICA_LOCAL.md), [Discreta](DISCRETA.md), [Páginas](PAGINAS_ESTUDO.md).
- [Estabilidade](ESTABILIDADE_IA_LOCAL.md): causa do corte, contratos e medições.
- [Calibração](CALIBRACAO_IA_LOCAL.md): avaliação por tarefa e relatórios privados.

Marcos no Git:

| Commit | Entrega |
| --- | --- |
| `91cda13` | Anexos, biblioteca e consulta documental |
| `53f9738` | Cadernos integrados |
| `281fdd7` | Interface React desktop |
| `215a2c7` | Atividades e tentativas |
| `51d0026` | Piloto Ollama no notebook |
| `c173d1d` | Ollama na interface |
| `c74fbe7` | Busca híbrida local |
| `769919c` | Cálculos/gráficos |
| `1c7a188` | Materiais Office e fórmulas |
| `3f3fb3c` | Ferramentas de Discreta |
| `c885c59` | Páginas de estudo/PDF/PNG |
| Commit que inclui este documento | Estabilidade local e preparação da continuidade |

Diagnóstico/prompt detalhado original e relatórios pessoais ficam no notebook,
em `CadernoMat/planejamentos/` e `CadernoMat/ia-local/relatorios/`, fora do Git.
Este resumo e a documentação técnica publicada permitem continuar sem depender
do histórico desta conversa.

## 10. Prompt para iniciar o trabalho no PC de casa

```text
Continue o CadernoMat no meu PC Windows. Leia primeiro README.md,
docs/TRANSFERENCIA_PC_CASA.md, GUIA_CONTINUIDADE.md e
docs/ESTABILIDADE_IA_LOCAL.md. Preserve a arquitetura React/pywebview/Python,
SQLite v11, cadernos, chats, materiais, atividades, tentativas, RAG e páginas.

A primeira entrega é validar a execução nativa no Windows e o uso real da GPU,
não adicionar funcionalidades novas ou trocar o modelo às cegas.

1. Confira branch/commit, alterações locais, Python, WebView2, Qt, Ollama,
   CPU/RAM/VRAM/driver e disco. Crie ambientes nativos; não reutilize executáveis
   ou .venv Linux. Não exponha .env nem dados pessoais nos logs.
2. Abra o programa em banco fictício separado. Teste chat/configuração/streaming,
   cancelamento/partes, materiais, reinício, atividades, Cálculo, Discreta,
   ilustração e páginas PDF/PNG. Corrija incompatibilidades sem desativar
   controles de arquivos, fontes, prompts e resultados.
3. Use Ollama nativo em loopback. Confira o modelo realmente carregado em GPU;
   detectar a placa não basta. Não tente aplicar a correção de kernel Linux.
   Proponha qualquer mudança administrativa necessária com diagnóstico concreto.
4. Compare o 4B de referência com contexto/perfil fixos, prompts de indução,
   lógica e Cálculo, casos frios/quentes, tempos/tokens/memória e respostas
   conhecidas. Registre versões/digests e falhas, sem inventar aceleração ou
   correção. Não baixar modelos adicionais nem aumentar contexto sem plano.
5. Se o acervo estiver disponível, valide primeiro uma cópia isolada: contagens,
   integridade/FKs, originais, FTS, vetores, versões e imagens. Faça backup antes
   de restaurar em LOCALAPPDATA. Não publicar documentos, chaves ou SQLite.
6. Entregue o aceite Windows documentado, testes relevantes, atalho para abrir
   no desktop e alterações publicadas. Informe diferenças do Linux e pendências.

Depois desse aceite, proponha comparação de modelos/perfis para o hardware real,
qualidade de RAG e matemática, distribuição e L5. Não refaça as etapas já entregues.
```
