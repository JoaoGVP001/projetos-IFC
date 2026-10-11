# CadernoMat

Um espaço desktop para estudar matemática: chats, cadernos por matéria e uma
biblioteca de materiais que você pode consultar com Gemini ou OpenAI. Foco
inicial em Preliminares, Cálculo Diferencial e Integral I e Matemática Discreta.

A interface usa **React + TypeScript + Tailwind**, executada localmente pelo
**pywebview**. Python continua responsável por SQLite, matemática, extração,
OCR e recuperação textual. Markdown e fórmulas são apresentados com KaTeX.

![Conversa no tema claro](docs/screenshots/chat-claro.png)

## Abrir no computador atual

Feche a versão anterior e abra **CadernoMat** pelo atalho da área de trabalho.
O mesmo atalho abre a interface nova. Também funciona:

```bash
./iniciar_desktop.sh
```

O pacote interno continua `tutor_calculo` para preservar os comandos. Os arquivos
da interface já estão compilados em `tutor_calculo/web`: **não é necessário Node,
Vite ou servidor de desenvolvimento para usar o aplicativo**.

## Instalação

Python 3.12+ e um ambiente virtual. No Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./iniciar_desktop.sh
```

Neste Ubuntu, a janela usa Qt/PySide6 e Qt WebEngine. Esses pacotes estão nas
dependências; a sessão gráfica e as bibliotecas do sistema continuam necessárias.
A instalação atual foi validada com Python 3.14, PySide6 6.12 e pywebview 6.2.
Veja [instalação e arquitetura](docs/INTERFACE.md) para diagnóstico.

No Windows, instale Python 3.12+ e o runtime Microsoft Edge WebView2:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\iniciar_desktop.ps1
```

A execução em Windows ainda precisa de validação nessa plataforma. O menu de
terminal permanece: `python -m tutor_calculo.app` no ambiente preparado.

Durante a transição, a interface anterior pode ser aberta separadamente:

```bash
.venv/bin/python -m pip install -r requirements-legado.txt
./iniciar_desktop.sh --legado
```

Esse modo requer Tkinter. A interface nova não importa Tkinter ou Matplotlib.

## Usar os chats e cadernos

- Escolha **Geral** ou um caderno na lateral e clique em **Novo chat**.
  Visitar uma matéria vazia não cria conversas.
- Escreva sua dúvida e envie pelo botão ou **Ctrl + Enter**. Os modos são
  Resolver, Resolver com IA, Explicar e Corrigir.
- O menu **⋯** aparece ao passar o mouse e ao focar com teclado. Permite
  renomear, fixar, mover, arquivar, restaurar e excluir com confirmação.
  Títulos longos são abreviados; o tooltip mostra o título inteiro.
- **+** em Cadernos cria uma matéria. O menu do caderno permite editar,
  reordenar e configurar objetivo, nível, assuntos e preferência pedagógica.
  Excluir um caderno conserva chats e materiais, movendo os chats para Geral.
- Use o botão de tema e recolha a lateral quando quiser mais espaço de leitura.
  Tema, última conversa e rascunhos ficam salvos neste computador.

Mensagens distinguem aluno e assistente; aceitam listas, títulos, tabelas,
citações, blocos de código e matemática com `$`, `$$`, `\(...\)` e `\[...\]`.
Fórmulas largas e tabelas podem rolar horizontalmente. Fórmulas inválidas têm
alternativa textual. **Copiar** preserva o Markdown/LaTeX original.

Os três cadernos iniciais são criados apenas na migração original. A mudança
visual mantém SQLite **v5**, IDs, mensagens, rascunhos, arquivos, índices e
seleções existentes. Veja [Cadernos](docs/CADERNOS.md).

## IA e cálculo local

Em **Configurações de IA**, escolha Gemini ou OpenAI, informe o modelo e sua
própria chave no campo protegido. Cada provedor mantém configurações separadas;
chave vazia reutiliza a anterior. Salvar não testa acesso nem faz consultas.
A chave permanece no `.env` local, ignorado pelo Git; ela não é devolvida ao
React, armazenada no navegador ou incluída na interface compilada.

A disponibilidade, cotas e cobrança dependem do projeto e modelo configurados.
Consulte [Google AI Studio](https://aistudio.google.com/api-keys),
[condições do Gemini](https://ai.google.dev/gemini-api/docs/pricing) e
[plataforma OpenAI](https://platform.openai.com/api-keys).
Não há troca automática entre provedores depois de falhas.

**Prévia do envio** mostra provedor, modelo e três partes separadas:
configurações do caderno, histórico recente da conversa atual e trechos dos
materiais explicitamente selecionados. Até dez pares completos recentes são
usados, limitados a 16 mil caracteres; erros ficam fora do contexto.

**Resolver** analisa localmente continuidade de funções por partes no formato
suportado; outros enunciados podem usar a API. **Exemplo local** preenche:

```text
f(x) = {
sen(x)/x, se x diferente de 0
0, se x = 0
}
em x = 0
```

Os limites laterais são 1, mas `f(0)=0`, então a função não é contínua em 0.
O analisador aceita operações aritméticas e sen, cos, tan, exp, log e sqrt;
as condições devem comparar x com o ponto indicado. Para dúvidas abertas,
use Resolver com IA, Explicar ou Corrigir.

Consultas e processamento documental acontecem em segundo plano. Falhas
preservam a pergunta e o histórico. Ainda não há streaming ou cancelamento;
ao fechar, uma tarefa já iniciada pode levar alguns segundos para terminar e
salvar a resposta. Alterações de organização ficam bloqueadas durante a consulta.

## Materiais e memória documental

Anexe pelo clipe ou adicione um link. **Materiais** reúne os arquivos e links,
com busca por nome, conteúdo, assunto e etiquetas, filtros e paginação de 30
itens. É possível visualizar texto/original, editar, associar a vários cadernos,
reutilizar, desvincular, reprocessar e excluir com atualização do índice.

Formatos interpretados: PDF textual; PDF digitalizado/imagens com OCR opcional;
TXT, MD, CSV, JSON, LOG, TEX; DOCX; links públicos HTML/texto/PDF. Outros formatos
podem ser guardados, mas são identificados como não interpretados. Limite de
20 MiB por arquivo, 80 páginas de PDF e 10 páginas de OCR. OCR exige Tesseract;
a disponibilidade de idioma é informada pela extração.

Importar ou pertencer a um caderno **não seleciona fontes para a IA**. Marque
**Consultar neste chat**, confira a prévia e pergunte em um modo de IA. A busca
recupera trechos por palavras; os originais binários ficam no computador.
Citações indicam referência e página quando disponível. Desmarcar um material
não apaga informações de respostas antigas do histórico.

Arquivos iguais usam uma cópia local, deduplicada por SHA-256. Dados ficam fora
do Git, no diretório CadernoMat do usuário:

- Linux: `~/.local/share/CadernoMat/` ou `$XDG_DATA_HOME/CadernoMat/`.
- Windows: `%LOCALAPPDATA%/CadernoMat/`.
- macOS: `~/Library/Application Support/CadernoMat/`.

Inclui banco, originais, índices, preferências visuais e cache da WebView.
Chats e materiais salvos podem ser acessados offline. Consultas online e
importação de links exigem conexão. Veja [Materiais](docs/MATERIAIS.md).

## Desenvolver, compilar e testar

Para alterar a interface, use Node 24 e pnpm 11:

```bash
cd frontend
pnpm install --frozen-lockfile
pnpm test
pnpm build
cd ..
./iniciar_desktop.sh --debug
```

`pnpm build` verifica TypeScript e substitui os assets de `tutor_calculo/web`.
O preview `pnpm dev` serve para desenvolvimento visual; a ponte Python só está
disponível dentro do pywebview. Recompile e reinicie a janela para testar o fluxo
integrado. Não abra duas instâncias no mesmo banco ao mesmo tempo.

Testes de Python e fluxo real de desktop:

```bash
.venv/bin/python -m unittest discover -s tests -v
cd frontend
pnpm e2e
```

A entrega foi validada com **88 testes Python**, **9 testes de interface** e um
fluxo completo na janela Qt, incluindo reinício, dois temas, tamanho mínimo e
teclado. Testes usam bancos temporários e IA simulada; não consomem créditos.
Os testes da interface anterior são opcionais sem Tkinter/display.

[Arquitetura e contrato](docs/INTERFACE.md) · [Sistema de design](docs/DESIGN.md) ·
[Continuidade](GUIA_CONTINUIDADE.md) · [Planejamento](PLANEJAMENTO.md).

Próxima etapa: atividades e tentativas por caderno. Provas, simulados, embeddings,
busca semântica, novos provedores e IA local permanecem planejados.
