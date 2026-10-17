# Materiais e memoria documental

Atualização 12/10: fontes de respostas podem ser conferidas pelo snapshot,
com página original e avisos de alteração/remoção. Envios com materiais na
interface usam prévia revalidada; **Consultar materiais** limita a tarefa ao
conteúdo fornecido. [Uso e limitações](ESTUDO_CONFIAVEL.md).

## Usar no aplicativo

1. Abra um chat e use **Anexar arquivos** (clipe) ou **Adicionar link**. A aba **Materiais** tambem
   permite importar. Aguarde o estado Pronto ou Texto parcial.
2. Use **Visualizar** para conferir a extracao. PDF tem previa por pagina;
   imagem tem previa do original. o menu **⋯** permite abrir no aplicativo do
   sistema, ir ao chat de origem, reutilizar, desvincular ou reprocessar.
3. Em **Editar**, organize nome, materia, assunto, etiquetas e cadernos.
   Materia permanece metadado livre; cadernos usam IDs reais e um material
   pode pertencer a varias materias sem duplicar original ou indice.
4. Busque por nome, texto extraido, assunto ou etiquetas. A busca da biblioteca
   e literal, sem distinguir maiusculas ou acentos. Filtre por tipo, materia,
   caderno, data de importacao (UTC) e materiais do chat atual. Ha 30 itens por pagina na interface React.
5. Marque **Consultar neste chat** somente nos materiais que deseja usar.
   Importar ou reutilizar nao ativa envio a IA automaticamente. A selecao e
   independente por conversa e permanece apos reiniciar.
6. Digite a pergunta, confira **Previa do envio** e envie em Resolver com IA,
   Explicar ou Corrigir. Para perguntar sobre um assunto, use palavras que
   aparecem nos materiais no modo textual, ou ative a busca híbrida local por significado.
   Veja [indexação e recuperação semântica](BUSCA_SEMANTICA.md).

A aba reune arquivos e links de todos os chats, inclusive arquivados. Excluir
um chat preserva a biblioteca e o nome de origem; o vinculo direto deixa de
existir. Remover deste chat preserva o material nas outras conversas. Excluir
da biblioteca pede confirmacao e remove original copiado, paginas, trechos,
indice e selecoes. O arquivo de origem do usuario nao e apagado. Respostas
antigas e suas citacoes continuam no historico, mesmo apos excluir o material.

## Formatos e limites

| Formato | Interpretacao local | Limites |
|---|---|---|
| PDF | Texto por pagina; OCR nas paginas sem texto | Ate 500 paginas e 10 paginas de OCR |
| PNG, JPG/JPEG, WebP, BMP, TIFF | Texto via Tesseract; previa da imagem | Ate 40 milhoes de pixels; primeiro quadro |
| TXT, MD, CSV, JSON, LOG, TEX | Leitura textual, sem executar codigo | UTF-8; alternativa Windows-1252 sinalizada |
| DOCX | Parágrafos, tabelas e fórmulas OMML básicas | Sem paginação original, figuras ou objetos embutidos; listas automáticas conservam marcadores, sem reconstruir numeração |
| PPTX | Texto e tabelas por slide, na ordem da apresentação; fórmulas OMML básicas | Até 500 slides; imagens, diagramas, notas e objetos embutidos não interpretados; Abrir original usa o aplicativo do sistema |
| Links HTTP(S) | Copia textual de HTML, texto/JSON ou PDF publico | Ate 2 MiB; sem login ou JavaScript |
| Outros | Armazenamento e abertura manual | Sem interpretacao pela IA |

Cada arquivo aceita ate **20 MiB**; cada extracao conserva ate **1 milhao de
caracteres**. DOCX/PPTX expandidos também têm limite de 20 MiB e 2.000 entradas; entidades XML e slides externos são recusados. PDF com senha exige
copia desbloqueada. Conteudo truncado, paginas sem texto e OCR limitado aparecem
como avisos, nunca como uma extracao completa. Planilhas XLSX, PPT/DOC antigos,
audio, video, ZIP e paginas dinamicas ainda nao tem extratores.

Fórmulas OMML básicas conservam frações, potências, índices, raízes e
delimitadores em LaTeX textual. Sobrescritos/subscritos de runs do Word/PowerPoint
também são preservados, evitando transformar `2^n` em `2n`. Estruturas
matemáticas desconhecidas recebem um marcador de equação não interpretada.
Office sempre aparece como **Texto parcial**, mesmo com todos os parágrafos
lidos: a extração não certifica as fórmulas nem interpreta figuras. O texto de
PDF também precisa de conferência de símbolos e fórmulas no original.
Nenhuma macro, objeto embutido ou link interno é executado durante a leitura.

## Materiais do Classroom

Arquivos baixados do Classroom podem ser importados como quaisquer anexos locais.
Associe-os ao caderno da disciplina e preencha assunto/etiquetas para busca.
O hash do arquivo evita duplicar o original quando ele é anexado novamente.
O endereço do arquivo de origem pode ser preservado como referência do material;
isso não dá ao aplicativo acesso à conta Google nem sincroniza futuras publicações.
O download inicial exige acesso autorizado ao Classroom/Drive.

Para consultar todos os materiais de uma disciplina, reúna-os em um chat de
estudo e marque **Consultar neste chat**. A recuperação continua limitada aos
materiais selecionados e cita páginas de PDF e números de slides de PPTX.
Um caderno novo ou chat novo não herda automaticamente a seleção documental.
Para simulados, selecione os materiais também na geração da atividade.
Arquivos pessoais, livros, índices e relatórios de importação permanecem no
diretório de dados do aplicativo, fora do Git; publicar o código não os publica.

OCR e opcional. Instale Tesseract no sistema (no Ubuntu, `tesseract-ocr` e
`tesseract-ocr-por`; no Windows, inclua o executavel no PATH). O aplicativo
prefere `por`, usa `eng` ou outro idioma instalado como alternativa e informa
isso. Neste PC ha apenas `eng`: acentos e formulas podem ser reconhecidos
incorretamente. **OCR nao interpreta graficos, diagramas ou notacao matematica
como um modelo visual.** Confira o texto antes de pedir a resolucao.

A extracao roda em um processo separado, com limite total de 150 segundos,
sem travar a janela. OCR tem timeout de 25 segundos por pagina; leitura de links
usa timeout de conexao de 10 segundos e orcamento de leitura de 30 segundos.
Links validam destino e redirecionamentos e recusam IPs privados/locais, portas
fora de HTTP(S) e usuario/senha na URL. Scripts e estilos nao entram no texto.
Se a extracao falhar, o material continua visivel e pode ser reprocessado.
Ao reiniciar, itens interrompidos sao sinalizados para reprocessamento. Fechar
a janela pode deixar o processamento atual terminando em segundo plano; itens
na fila sao cancelados e ficam recuperaveis.

## O que e enviado a IA

Gemini e OpenAI recebem a mensagem, preferencias pedagogicas do caderno atual,
instrucoes de estudo/uso das fontes,
historico recente da conversa (ate dez pares completos/16 mil caracteres),
**ate seis trechos relevantes**, limitados a 6 mil caracteres de texto, e sua
proveniencia (nome, URL e pagina aplicavel). Arquivos originais, imagens e PDFs
binarios **nao sao enviados**. Historico pode conter informacoes de documentos
usados em consultas anteriores; desmarcar ou excluir um material nao apaga
essas mensagens. A previa mostra caderno, historico e trechos antes da consulta.
Pertencer ao caderno nunca autoriza consulta documental automaticamente.

Os trechos usam referencias M1, M2 etc, numeradas por consulta. As instrucoes
pedem citacoes junto das afirmacoes; o app acrescenta nome/pagina/slide das fontes
citadas. Se o modelo omitir citacoes, mostra a lista de trechos disponibilizados
com esse aviso. Referencias numeradas inexistentes sao marcadas como
indisponiveis. Isso verifica a existencia da fonte, nao prova automaticamente
que uma afirmacao esteja correta: confira o documento original.

Sem correspondencia, o provedor recebe aviso de que nao ha trechos relevantes
e nao deve inventar o conteudo dos materiais. Pedidos genericos de resumo,
analise ou atividades podem receber uma **amostra inicial**, identificada como
amostra, que nao representa todo o documento. Nenhuma extracao vazia vira
texto inventado. O modelo pode explicar pelo conhecimento geral, distinguindo
isso da consulta documental. Conteudo dos documentos nunca controla o app;
nao ha execucao de instrucoes, ferramentas ou codigo provenientes deles.

Consultar usa as cotas e politicas do provedor escolhido. Armazenar, pesquisar,
extrair e visualizar localmente nao usa chave nem creditos de API.

## Armazenamento e arquitetura

Todos os dados ficam ao lado de `historico.sqlite3`, no diretorio de dados
CadernoMat da plataforma descrito no README. `materiais/` guarda uma copia por
SHA-256. Importar o mesmo conteudo em outro chat reutiliza o registro/original;
o nome e os metadados sao compartilhados na biblioteca. Links sao deduplicados
pela URL normalizada (sem fragmento), e sua copia textual persiste offline.
Reprocessar um link atualiza essa copia e substitui o indice atomicamente.

SQLite **v4** acrescentou materiais, vinculos por chat, paginas e trechos com
indice **FTS5**, necessario na instalacao de SQLite. Os triggers removem o indice
junto dos trechos. A migracao tem transacao explicita e backup v3 antes de
alterar bancos existentes. Chats, rascunhos, fixacoes e chaves sao preservados.
Banco usa WAL para leitura enquanto o worker grava. Banco/backups tem permissao
0600 e pasta de materiais 0700 no Linux/macOS; permissoes Windows dependem do
perfil do usuario. Dados pessoais nao entram em commits.

SQLite **v5** acrescenta cadernos e associacoes muitos-para-muitos, com backup v4.
Novos anexos herdam a materia do chat por ID, sem marcar consulta. Dados legados
so recebem associacoes por correspondencia inequívoca. Veja
[Cadernos](CADERNOS.md) para filtros, compartilhamento e movimentacao de chats.

Para backup manual, feche o app, aguarde o worker terminar e copie **toda a
pasta de dados** (banco, auxiliares WAL se existirem e materiais). Backups antigos
nao sao apagados automaticamente ao excluir um material; podem conter historico
anterior. Backup/restauracao pela interface permanece no planejamento.

Modulos:

- `armazenamento.py`: migracao/historico.
- `materiais.py`: armazenamento, metadados, indexacao e contrato de recuperacao.
- `extracao.py`: extratores locais, paginas e OCR.
- `links.py`: leitura limitada de sites publicos.
- `processamento.py`: worker isolado.
- `biblioteca_ui.py`: biblioteca e visualizacao.
- `ia.py`: adaptacao do contexto documental aos provedores existentes.

A base atual é **RAG textual/híbrido**, sem treinar uma rede neural. O contrato
conserva trechos, IDs, páginas e referências, independente de Gemini/OpenAI/Ollama.
[Embeddings locais](BUSCA_SEMANTICA.md) acrescentam busca por significado, cache
versionado e indexação incremental na migração v8. Visão e relações gráficas entre
materiais ainda são futuras. A extração/OCR e seus limites permanecem iguais.

## Páginas revisadas do CadernoMat

Uma versão salva de página pode entrar na biblioteca por ação explícita.
A cópia é Markdown textual, associada ao caderno e deduplicada por página/versão;
permanece desmarcada para consultas e não dispara embeddings. Identificação de
origem acompanha cada trecho na recuperação textual/híbrida, evitando usar texto
gerado como confirmação independente. Diagramas ficam na página/PDF/PNG e não
são interpretados por essa cópia textual. [Uso e limites](PAGINAS_ESTUDO.md).
