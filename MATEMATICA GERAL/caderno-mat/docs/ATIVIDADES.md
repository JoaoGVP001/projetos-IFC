# Atividades e tentativas

## Fluxo de estudo

Escolha Geral ou um caderno e abra **Atividades**. **Criar atividade** funciona
sem internet: preencha título, objetivo e os exercícios. Adicione questões,
escolha o formato, registre gabaritos quando aplicável e confira a prévia
Markdown/KaTeX antes de salvar. Cada questão e alternativa tem um ID estável.
Busca por título, descrição, assunto e etiquetas é literal e ignora maiúsculas;
filtros separam formato, dificuldade e atividades ativas/arquivadas ou com
uma tentativa em andamento/finalizada. Listas têm paginação de 30 itens.

**Começar ou continuar** retoma a última tentativa em andamento, mesmo de uma
versão anterior. **Nova tentativa** cria outro registro com respostas vazias na
versão atual. Respostas são salvas após 300 ms, antes de trocar de questão/área
e ao fechar normalmente a janela. A posição e a área abertas também persistem.
O gabarito permanece oculto até finalizar ou usar **Revelar solução**, ação
registrada no histórico. Finalizar questões em branco pede confirmação.

O histórico permite retomar, ler resultados e comparar duas tentativas. Versões
diferentes têm aviso: as questões podem ter mudado. Não há métricas de domínio,
nota global, cronômetro ou comparação que misture discursivas com acertos locais.

## Formatos e correção

| Formato | Gabarito e resultado |
|---|---|
| Aberta | Texto opcional. Sem gabarito ou revisão necessária; revisão manual e feedback de IA são separados. |
| Múltipla escolha | 2–6 alternativas distintas, uma correta por ID. Comparação local determinística. |
| Verdadeiro/falso | Booleano explícito; falso é uma resposta, não questão vazia. Comparação local. |
| Numérica | Decimal finito (vírgula/ponto ou notação científica), sem expressões/unidades. Acerto se diferença absoluta ≤ tolerância registrada; zero exige igualdade. |

Números não nulos são limitados em módulo a 1e-100…1e100; zero é permitido.
Correção usa Decimal com precisão suficiente para esses limites, sem floats.
Uma expressão como `1/2`, número inválido ou resposta aberta não vira nota zero.
Questões em branco ficam sem resposta, fora dos erros objetivos.

O resumo separa respondidas, corrigidas objetivamente, acertos, erros e não
avaliadas, além de dicas e soluções reveladas. Revisão manual permite observação,
resposta adequada ou precisa revisar, sem alterar o resultado objetivo.
Enunciados, alternativas, respostas esperadas e explicações usam Markdown e
fórmulas. Histórico também conserva a resposta que cada feedback de IA avaliou;
se ela mudou durante a consulta, aparece um aviso.

## Versões e preservação

SQLite v6 acrescenta atividades, versões, tentativas, consultas de IA e navegação
de estudo. A migração cria `historico.sqlite3.v5.backup` antes da alteração e
executa o DDL em transação. Bancos v1–v4 mantêm suas migrações/backs intermediários.
Nenhum conteúdo anterior é reclassificado ou eliminado pela migração v6.

Atividade tem UUID, metadados, caderno nullable, origem manual/IA, fonte/chat de
origem e versão. Editar exige a versão vista no editor; uma gravação concorrente
é recusada. Cada edição cria uma versão. O snapshot da tentativa é fixado **ao
iniciar**, preservando também tentativas ainda em andamento, e nunca substituído.
Finalizar novamente retorna a tentativa já finalizada, sem duplicar registros.
Respostas finalizadas não podem ser reescritas; revisões/feedback são anotações
separadas. A posição de leitura pode mudar sem alterar respostas ou o snapshot.

Não há exclusão definitiva de atividade na interface: arquive/restaure e preserve
o histórico. Duplicar cria outra atividade sem copiar tentativas ou arquivos.
Mover altera apenas organização. Excluir um caderno transfere atividades para
Geral por FK SET NULL; excluir o chat original conserva atividade e tentativas.
Arquivos referenciados mantêm IDs/nomes históricos; quando removidos, ficam
indisponíveis. Arquivar caderno/atividade preserva leitura, mas exige restauração
para responder, revisar ou editar. Bancos/arquivos/consultas permanecem na pasta
de dados do usuário, fora do Git, junto à biblioteca existente.

## IA opcional e fontes

**Gerar com IA** solicita caderno, assunto, objetivo, dificuldade, quantidade e
formatos. Também pode ser iniciado no editor com os materiais de origem.
**Conferir dados enviados** grava uma prévia local com provedor/modelo,
configurações pedagógicas, solicitação, instruções da tarefa e trechos documentais
separados. Só **Confirmar consulta à API** faz a chamada. Usa Gemini ou OpenAI
configurado, sem fallback entre serviços, sem histórico de outros chats e sem
originais binários. Credenciais não fazem parte da prévia ou do SQLite.

Selecione até 10 fontes explicitamente a cada consulta. Vincular materiais ao
caderno/atividade/chat não autoriza envio nesta área. Recuperação textual usa
até 6 trechos, 6.000 caracteres e 2 trechos por página. A geração pode usar uma
amostra inicial identificada quando não há correspondência textual; falta de
conteúdo em alguma fonte gera aviso. OCR pode conter erros matemáticos.
Documentos são dados de consulta, nunca instruções de execução.

Geração retorna JSON validado pelo Python: formatos, IDs, alternativas, gabaritos,
limites e referências às páginas realmente disponibilizadas. Texto/JSON inválido,
quantidade divergente e citações inventadas ficam como falha recuperável, sem
criar atividade. A validação estrutural **não comprova correção matemática**.
A proposta é editável e só vira atividade após **Salvar atividade**. Provedor,
modelo, pedido e fontes de geração permanecem como proveniência.

Dicas pedem um próximo passo sem enviar o gabarito; feedback inclui enunciado,
resposta do estudante e gabarito registrado, quando existe. Ambos aceitam fontes
explícitas, prévia e confirmação. Feedback é orientação de IA sem nota ou
verificação definitiva. Pode discutir a solução; use dicas para não antecipá-la.
Falha de API não corrige questões nem altera resultados locais. As últimas 20
consultas/propostas ficam acessíveis na área Atividades; resultados persistem.
Uma consulta interrompida é marcada como erro na próxima abertura e pode ser
repetida. Repetir uma consulta concluída não faz nova chamada.

Use **Criar atividade deste chat/material** no menu correspondente para iniciar
um editor com proveniência, sem duplicar documentos. **Pedir ajuda em novo chat**
prepara um rascunho em uma conversa nova com apenas o exercício escolhido, suas
alternativas e a resposta dessa tentativa. Não envia automaticamente; não inclui
gabarito nem outras questões/conversas.

## Arquitetura e limites

`atividades.py`: validação, organização, versões, migração e navegação.
`tentativas.py`: snapshots, rascunhos, finalização, revisão e histórico.
`correcao.py`: respostas válidas e correção/resumo determinísticos.
`estudo.py`: contratos, recuperação por IDs explícitos, prévias e jobs persistidos.
`Aplicacao` serializa mutações e cria SQLite na thread de cada operação. Workers
recebem a prévia congelada, fazem a consulta fora do lock e persistem feedback e
estado do job na mesma transação. Propostas nunca são gravadas como atividade
pelo worker. O React usa DTOs em `activities-model.ts`, sem SQL ou chamadas API
de provedor. A ponte continua limitada a operações nomeadas e argumentos.

Limites: 30 exercícios/atividade, 10/geração, 2–6 alternativas, 10 referências
por exercício, título 180, descrição 3.000, objetivo 1.500, assuntos/etiquetas 500,
enunciado/resposta/explicação 8.000 e alternativa 2.000 caracteres. Propostas
limitadas a 120.000 caracteres, feedback a 20.000. Editores manuais ainda não
salvos não têm rascunho automático; tentativas e propostas de IA têm persistência.
Encerramento abrupto pode perder os últimos 300 ms; fechamento normal salva o
último campo. A integração [Ollama](OLLAMA.md) permite cancelar consultas locais,
gerar 1–3 questões com esquema JSON e usar dicas/feedback sem chave. O chat local
tem streaming; uma proposta JSON parcial não vira atividade. Não há avaliação
universal de provas.

## Validação

116 testes Python (28 novos de estudo), 15 testes frontend (6 novos de prática)
e dois fluxos Qt reais com bancos temporários/IA simulada. Incluem migração com
backup e rollback, índices/seleções preservados, formatos/tolerância, isolamento,
rascunho/reinício, versão antiga imutável, finalização idempotente, arquivo,
fontes explícitas/indisponíveis, JSON inválido, falha de API e ambos os provedores.
A interface valida 4 formatos, nova tentativa/comparação, edição, revisão,
prévia/geração/dica/feedback, ajuda em chat, temas e 1000×650.

```bash
.venv/bin/python -m unittest discover -s tests -q
cd frontend
pnpm test
pnpm build
pnpm e2e
pnpm e2e:atividades
```

As capturas em `docs/screenshots/atividades-*.png` usam dados fictícios. A execução
do usuário continua pelo atalho CadernoMat, com assets compilados localmente.
Provas/simulados cronometrados, flashcards e embeddings permanecem para
outras entregas. Próxima etapa: provas/simulados usando estas versões e tentativas,
com regras explícitas de conclusão, tempo e apresentação dos resultados.

## Páginas de estudo

Na tentativa, **Criar página da questão** copia o enunciado do snapshot vigente.
**Criar página com solução** só está disponível depois de revelar/finalizar,
com proteção também no backend. A página identifica atividade, versão, questão
e tentativa, sem alterar gabaritos, respostas ou notas.
[Editor, versões e exportação](PAGINAS_ESTUDO.md).
