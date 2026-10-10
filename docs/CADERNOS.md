# Cadernos por matéria

## Começar

Escolha **Geral** ou um caderno na lateral. Os três cadernos iniciais são
Preliminares de Matemática, Cálculo Diferencial e Integral I e Matemática
Discreta. Foram criados uma única vez; renomear ou excluir um deles não provoca
sua recriação ao reiniciar. Chats anteriores à atualização permanecem em Geral.

Clique em **Novo chat** para iniciar uma conversa no caderno escolhido.
Navegar por uma matéria vazia não cria chats. Importar um arquivo/link,
reutilizar um material ou carregar o exemplo pode iniciar um chat quando não
houver uma conversa aberta: são ações explícitas de estudo. Rascunhos são
salvos ao navegar e fechar; o último caderno/chat aberto é recuperado.

Use **+** ao lado de Cadernos para criar outra matéria. **⋯** em cada caderno
abre edição/renomeação, ordenação, arquivamento, restauração e exclusão.
Nomes devem ter até 100 caracteres e ser únicos, inclusive entre arquivados,
sem diferenciar maiúsculas ou acentos. Geral é uma área reservada, não um
caderno editável.

O cabeçalho apresenta o nome completo da matéria e da conversa. Nomes longos
dos cadernos ficam abreviados na lateral; os chats mantêm o deslocamento do
título durante o hover. A busca de chats e a lista de fixados/arquivados são
restritas ao caderno escolhido.

## Mover, arquivar e excluir

No menu de um chat, escolha **Mover para caderno** e selecione uma matéria
ativa ou Geral. A conversa mantém o ID e não é copiada. Mensagens, rascunho,
fixação, arquivamento, anexos, seleção documental e origem dos materiais
permanecem. Ao mover, o aplicativo abre o chat no destino.

Arquivar um caderno não arquiva seus chats individualmente. Eles continuam
acessíveis em leitura por **Cadernos arquivados**. Restaure o caderno antes
de enviar mensagens, iniciar chats ou adicionar fontes. Restaurar o caderno
não restaura chats arquivados individualmente; use também o menu desses chats
quando necessário. Durante uma consulta, navegação e alterações do caderno
aguardam sua conclusão.

Excluir um caderno exige confirmação e remove somente sua organização.
As conversas passam para Geral com suas mensagens intactas. Materiais continuam
na biblioteca, nos chats e em outros cadernos associados. A exclusão de um
chat ou de um documento é uma ação diferente, com as regras do guia de materiais.

## Biblioteca por matéria

Em **Materiais**, use o filtro de caderno ou **Do caderno atual**. O filtro
**Geral (sem caderno)** mostra documentos sem nenhuma associação a cadernos;
**Todos os cadernos** reúne toda a biblioteca, inclusive arquivados.
Os filtros por tipo, metadado de matéria, data e chat continuam disponíveis.

**Editar** permite marcar vários cadernos para um material. Esses vínculos
compartilham o mesmo original, extração e índice. Nome, assunto e etiquetas
também são compartilhados, não propriedades de cada cópia. Importar/reutilizar
um material num chat acrescenta o caderno desse chat. Mover um chat acrescenta
o destino aos materiais anexados e conserva as associações anteriores, pois
eles podem continuar úteis na outra matéria. Ajuste os vínculos em Editar
se desejar retirar uma associação antiga.

Um material pertencente ao caderno não é automaticamente anexado a seus chats
nem autorizado para a IA. **Consultar neste chat** continua sendo uma seleção
independente por conversa. Reutilizar em outro chat começa desmarcado. Remover
o anexo de um chat não remove suas associações aos cadernos.

O campo antigo **matéria** permanece como metadado livre. A migração associa
somente nomes equivalentes aos iniciais, normalizados por acentos, caixa e
espaços, ou aliases explícitos: Preliminares, Cálculo I, Cálculo 1 e Cálculo
Diferencial e Integral 1. Nomes semelhantes ou desconhecidos não são inferidos.
Nenhum título de chat é usado para classificação automática.

## O que a IA recebe

Cada caderno guarda descrição, objetivo, nível, assuntos e orientações de
estudo. Escolha também uma preferência:

- **Explicação completa:** conceito, etapas, resultado e verificação.
- **Dicas progressivas:** uma dica por vez; solução completa quando pedida
  explicitamente pelo aluno.
- **Correção orientada de uma tentativa:** primeiro erro e orientação para
  continuar; pede a tentativa quando faltar.

Essas preferências complementam Resolver com IA, Explicar e Corrigir.
São instruções ao modelo, e a resposta gerada ainda pode exigir revisão.
Geral usa as instruções gerais do aplicativo, sem configurações extras.

O serviço envia três partes separadas: configurações do caderno atual,
histórico recente somente da conversa aberta e trechos dos documentos
explicitamente selecionados. Não consulta automaticamente chats vizinhos.
**Prévia do envio** mostra as três partes e o provedor/modelo. Dados pessoais
incluídos nas configurações também serão enviados ao provedor online.
Originais binários continuam no PC; documentos permanecem dados de consulta,
não instruções para controlar o aplicativo.

O contexto é construído uma única vez em `ia.py` para Gemini e OpenAI. Na
OpenAI, usa o parâmetro `instructions` da
[Responses API](https://developers.openai.com/api/reference/python/resources/responses/methods/create).
Resolver conserva o cálculo local; apenas sua alternativa de consulta à API
recebe o caderno e o histórico. Não há mudança automática de provedor.

## Persistência e arquitetura

SQLite **v5** adiciona `cadernos`, `conversas.caderno_id`, a relação
`materiais_cadernos` e a navegação persistente. Os dados permanecem no diretório
local indicado no README, fora do Git. Antes de migrar bancos existentes,
o aplicativo cria `historico.sqlite3.v4.backup` por meio do backup do SQLite.
DDL, dados iniciais, aliases e versão são alterados em transação explícita.
Uma falha reverte a migração e mantém a versão anterior; o backup também
permanece disponível. Reabrir a versão nova não repete a migração nem os seeds.

As chaves estrangeiras removem apenas associações ao excluir cadernos:
chats recebem `NULL`; mensagens, anexos, seleções, arquivos e índices ficam
intactos. O processamento documental mantém seu contrato e IDs. Para backup
completo, feche o aplicativo, aguarde os processos de extração e copie toda
a pasta de dados, incluindo `materiais/` e auxiliares do SQLite existentes.
O backup de migração é somente do banco e não substitui essa cópia completa.

Responsabilidades:

- `cadernos.py`: migração, CRUD, ordenação, vínculos e contexto pedagógico.
- `cadernos_ui.py`: lateral, editor e formulário para mover chats.
- `armazenamento.py`: histórico e filtro por caderno.
- `materiais.py`: associações e busca, sem multiplicar originais/índices.
- `ia.py`: composição do contexto e adaptação aos provedores.

Atividades futuras podem referenciar o mesmo ID estável de caderno. O próximo
passo é modelar atividades/questões/tentativas versionadas, validar formatos
JSON e entregar prática e simulado com gabarito separado. Múltipla escolha,
verdadeiro/falso, questões discursivas e correção estão no planejamento.
Nenhuma tabela de atividades, embedding ou modelo local foi instalado nesta etapa.

## Validação

Os testes usam bancos temporários e clientes simulados. Cobrem criação única,
CRUD, ordenação, arquivo independente, migração v4 e rollback, dados legados,
movimentação por ID, deduplicação, seleção por chat e contexto nos dois
provedores. O fluxo de janela cria caderno, inicia conversa, importa material,
confere a prévia, consulta IA simulada, move e reinicia recuperando os dados.
Também verifica rascunhos, cadernos vazios e controles na janela mínima.
Nenhum teste consome créditos de API.
