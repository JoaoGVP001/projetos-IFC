# Interface desktop React

## Responsabilidades e execução

```text
React + TypeScript → bridge.ts → Ponte.request → Aplicacao
                                                ├─ Historico / Cadernos / Biblioteca / Atividades / Tentativas (SQLite v8)
                                                ├─ processamento documental em subprocesso
                                                ├─ ia.py → Gemini / OpenAI / provedores.ollama
                                                └─ app.py → matemática local / fallback IA
```

`frontend/src/App.tsx` coordena navegação, formulários e estado da apresentação.
`ui.tsx` fornece os componentes; `Markdown.tsx` trata respostas.
`model.ts` define os DTOs e `bridge.ts` serializa requisições assíncronas.
Não existe SQL ou chamada a um provedor nos componentes React.

`tutor_calculo/servico.py` concentra a coordenação antes presente na janela Tk.
Cada operação abre e fecha `Historico` na thread onde executa. O RLock serializa
mutação e criação de snapshots; **check_same_thread não é desativado**.
Tarefas recebem histórico, contexto pedagógico e fontes da conversa escolhida.
A persistência do resultado usa uma conexão nova na thread de conclusão.

IA usa um executor; a extração/OCR continua em processo isolado com limite de
150 segundos. O estado expõe tarefas e revisão; a interface consulta o estado
a cada segundo, sem fazer chamadas extras à API. Não há progresso percentual
inventado. Enquanto a IA está ocupada, operações de organização ficam bloqueadas,
mas rascunhos podem ser escritos para a próxima pergunta.

`desktop.py` carrega `tutor_calculo/web/index.html` usando o servidor local
interno do pywebview, sem Vite. Ao fechar, adia o encerramento para uma thread
que lê e salva o último rascunho e então destrói a janela; avaliar JavaScript
dentro do callback síncrono do Qt bloquearia a thread gráfica.

## Contrato da ponte

L2 acrescenta `semantica_status`, `semantica_indexar`, `semantica_cancelar` e
`semantica_ativar`. `materiais` aceita `modo=texto|hibrida` mantendo os filtros.
Prévia de chat/estudo recebe `recuperacao` (estratégia e aviso); cards podem ter
`ocorrencias` (texto/página/estratégia). O React não vê blobs, hashes ou caminhos.
[Contrato e persistência da busca](BUSCA_SEMANTICA.md).

Existe uma única função pública: `request(operacao, dados)`.
Respostas: `{ok: true, data: ...}` ou `{ok: false, error: "mensagem"}`.
Erros inesperados recebem texto genérico, sem stacktrace, caminhos ou credenciais.

| Operações | Efeito |
|---|---|
| estado, navegar | Snapshot de cadernos/chat/rascunho/mensagens/anexos; navegação persistente |
| chat_criar, chat_acao, rascunho | Criar, renomear/fixar/mover/arquivar/excluir e salvar texto |
| caderno_salvar, caderno_acao | CRUD, ordem e arquivo independente dos chats |
| importar, link | Seletor nativo limitado; importação de URL HTTP(S) validada |
| materiais, material_detalhe | Busca, filtros, 30 por página, texto e imagem de prévia |
| material_acao, material_salvar | Seleção/reuso/desvincular/reprocessar/excluir e metadados |
| previa, enviar | Snapshot visível e tarefa de cálculo/IA |
| configurar, preferencias | Configurações no Python e preferências locais |
| ollama_diagnostico, ollama_iniciar | Metadados em loopback e iniciar somente runtime previamente preparado |
| ia_cancelar, ia_repetir | Cancelamento local e repetição idempotente de snapshot autorizado |
| abrir_original, abrir_link, exemplo | Abrir material registrado/URL validada e exemplo estático |

Validação exige tipos, limites de texto, ações e provedores permitidos. Exclusões
exigem `confirmado: true`. Não existe acesso SQL, shell ou leitura de caminhos
arbitrários. Importar só aceita `{}`: o Python recebe os caminhos do seletor
nativo. Abrir original resolve um ID de material; extensões executáveis são
bloqueadas, e comandos do sistema usam argumentos sem shell.

Estado da configuração contém provedor/modelo/escopo e, para Ollama, URL de
loopback, contexto e timeout. O diagnóstico distingue configuração de runtime
disponível e expõe metadados permitidos. A chave digitada atravessa a ponte somente para salvar no Python;
ela nunca volta. Nenhuma chave entra em localStorage ou sessionStorage.

## Conteúdo não confiável

React escapa texto. Markdown usa react-markdown sem HTML bruto, remark-gfm e
remark-math. rehype-sanitize atua **antes** do KaTeX; KaTeX usa `trust: false`.
Links são interceptados e encaminhados à operação HTTP(S) da ponte, sem substituir
a página do aplicativo. A CSP impede frames, objetos, formulários e recursos
remotos. Fórmulas e fontes são locais. Texto de documento é apresentado como
texto literal, jamais HTML; instruções documentais continuam como dados não
confiáveis na construção do prompt Python.

A prévia entrega uma imagem PNG limitada, não um caminho de arquivo. O original
é aberto externamente apenas por ação explícita. São mantidas as proteções de
extração, limites, URLs públicas e proveniência descritas em MATERIAIS.md.

## Dados e transição

A migração visual manteve v5; a entrega de atividades acrescenta v6 com backup
v5 e migração transacional. A integração local acrescenta v7 com backup v6,
preferências por chat e consultas persistidas. L2 acrescenta v8 com backup v7
e índice semântico local publicado atomicamente. Consulte [Ollama](OLLAMA.md) e
ATIVIDADES.md para tabelas e invariantes. Permanecem os IDs, registros, relações FTS5,
arquivos e seleção documental. `interface.json` no diretório de dados conserva
tema/lateral, com substituição atômica e permissão 0600 no Linux. O cache WebView
fica nesse mesmo diretório, fora do Git. Não contém chaves de configuração.

`desktop_legado.py` conserva a janela anterior; os componentes Tk auxiliares
continuam somente para `--legado` e testes históricos. Dependências opcionais
estão em requirements-legado.txt. Não execute ambas as janelas simultaneamente
sobre o mesmo banco: a recuperação de processamento é feita na inicialização.

## Instalação e desenvolvimento

Linux usa `pywebview[pyside6]`: Qt, PySide6 e WebEngine são instalados pelo pip.
A sessão gráfica precisa das bibliotecas usuais Qt/X11/Wayland. No Ubuntu desta
entrega não foi necessário instalar bibliotecas de sistema adicionais. Se outra
máquina apresentar erro de plugin xcb, confira a documentação e os diagnósticos
do Qt, incluindo a dependência libxcb-cursor. Não desative o sandbox WebEngine
para contornar erros.

Windows usa pywebview e o runtime WebView2; a rota de inicialização foi preparada,
mas não executada nesta entrega. macOS depende da integração Cocoa do pywebview
e também não foi validado.

Use Node 24 e pnpm 11 para editar, `pnpm install --frozen-lockfile`, `pnpm test`
e `pnpm build` em frontend. Versione o lockfile e os arquivos compilados; não
versione node_modules. A compilação preserva também as licenças dos pacotes
e fontes em THIRD_PARTY_NOTICES.txt. O override KaTeX em pnpm-workspace.yaml
mantém as dependências indiretas na versão corrigida, conforme a
[configuração atual do pnpm](https://pnpm.io/settings). `./iniciar_desktop.sh --debug` habilita as ferramentas da
WebView. Para dados de teste isolados, acrescente `--banco /tmp/exemplo.sqlite3`.
O Vite em navegador não possui a ponte; a validação integrada usa o build local.

## Validação

Python: 116 testes, incluindo 12 de serviço/ponte e 28 de atividades/tentativas,
concorrência, snapshots,
falhas, importação, índice, movimentação e persistência. Os testes legados são
adaptados para desktop_legado. Frontend: 15 testes de prática, sanitização, matemática,
contrato assíncrono, menu por teclado e diálogo.

`pnpm e2e` inicia Qt real com banco/arquivo temporários e Gemini simulado. O teste
usa CDP via WebSocket nativo, pois Qt não implementa os contextos de navegador
exigidos pelo Playwright. Inclui criar caderno/chat, seletor nativo simulado,
extração real, seleção, prévia, resposta, mover, fixar/renomear/arquivar/restaurar,
temas, teclado, fechamento e reinício. Capturas em docs/screenshots contêm
somente dados sintéticos. Exige Linux gráfico, Qt e ambiente Python preparado.
`CADERNOMAT_PYTHON` permite escolher outro executável para esse teste.

## Limites e próxima etapa

Streaming/cancelamento local e indexação cancelável foram entregues em L1/L2.
Atualização automática, virtualização de históricos longos e instalador seguem pendentes. A tarefa já iniciada pode terminar e salvar
após a janela fechar. OCR depende do Tesseract. A consulta documental continua
textual na migração original. Ollama e busca híbrida foram acrescentados depois,
conforme docs/OLLAMA.md e docs/BUSCA_SEMANTICA.md.
Atividades/tentativas foram entregues com este padrão; a próxima etapa são provas/simulados.

Referências oficiais consultadas:
[pywebview instalação](https://pywebview.flowrl.com/guide/installation.html),
[ponte](https://pywebview.flowrl.com/guide/interdomain.html),
[segurança](https://pywebview.flowrl.com/guide/security.html),
[Tailwind/Vite](https://tailwindcss.com/docs/installation/using-vite) e
[react-markdown](https://github.com/remarkjs/react-markdown).

## Contratos de estudo (v6)

| Operações | Efeito |
|---|---|
| atividades, atividade_obter | Busca/filtros/paginação por caderno, detalhe do editor |
| atividade_salvar, atividade_acao | Validar/gravar nova versão; duplicar/mover/arquivar/restaurar |
| estudo_navegar | Persistir área, atividade e tentativa; IDs são verificados |
| tentativa_iniciar, tentativa_obter | Retomar/criar snapshot e obter DTO com gabarito oculto até revelar/finalizar |
| tentativa_salvar, tentativa_navegar | Salvar resposta em andamento; posição de leitura também funciona em arquivo/histórico |
| tentativa_revelar, tentativa_finalizar | Registrar solução usada e corrigir localmente; finalização idempotente |
| tentativa_revisar, tentativas, tentativas_comparar | Revisão manual separada, histórico/comparação da mesma atividade |
| estudo_previa, estudo_consultar, estudo_job, estudo_jobs | Prévia exata, confirmação, tarefa e propostas persistidas; últimas 20 consultas |
| exercicio_chat | Criar novo chat/rascunho com contexto mínimo, sem envio automático |

Frontend usa `window.cadernoMatStudyDraft` e um flush assíncrono ao navegar; o
callback desktop salva o último campo independentemente do rascunho do chat.
Snapshots/validação ficam em Python. Jobs interrompidos são recuperados como
falha; o resultado de feedback e a conclusão são persistidos na mesma transação.
Não entram credenciais ou caminhos arbitrários nos DTOs. Veja [Atividades](ATIVIDADES.md).
