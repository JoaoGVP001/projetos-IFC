# Sistema de design do CadernoMat

## Identidade e tokens

O espaço de estudo combina papel quente, verde mineral e tipografia discreta.
A marca usa Σ, sem imagens remotas. Inter (400/500/600), ícones Lucide e fontes
KaTeX são compilados localmente. Fontes de sistema são o fallback.

Tokens ficam em `frontend/src/style.css`, com sobrescritas por
`:root[data-theme="escuro"]` e exposição ao Tailwind via `@theme inline`.
Componentes devem usar os tokens e classes compartilhadas, não cores inline.

| Papel | Claro | Escuro |
|---|---|---|
| Fundo | #f8f7f4 | #17201f |
| Superfície | #ffffff | #1d2927 |
| Lateral | #efeee9 | #141d1b |
| Texto principal | #24332f | #e4ece8 |
| Texto secundário | #5c6a63 | #9caea7 |
| Ação/acento | #167665 | #87d9bd |
| Seleção | #e2f0e9 | #253f35 |
| Erro | #a63636 | #f3a8a2 |
| Aviso | #956323 | #e8c68c |
| Borda | #e1e5df | #34423d |

`--space-*` define 4/8/12/16/20/24/32 px; `--radius-*` define pequeno 6,
médio 10, grande 16 e pill. A escala tipográfica (`--type-*`) vai de 11 px
para metadados até 26 px para estados vazios. O corpo usa 14 px e a leitura
das respostas 15 px, com altura de linha 1.85. Dimensões específicas de layout,
bordas e ícones permanecem no mesmo arquivo central.

## Componentes e comportamento

`ui.tsx` concentra Button, Badge, Field, Dialog, Menu, Empty e Loading.
As telas reutilizam esses componentes; abas, cards e notificações usam as
classes centrais. Botão primário representa continuar/salvar/enviar; ações
secundárias usam soft ou ghost; exclusão usa danger e confirmação específica.

Menus usam portal, posição limitada à janela, foco inicial, setas, Home/End e
Escape. Ações da lateral aparecem no hover **e em focus-within**. Títulos são
truncados e acessíveis por tooltip, sem deslocamento automático obrigatório.

Diálogos nativos contêm o foco e aceitam Escape; devolvem foco ao elemento de
origem. Rótulos reais acompanham os campos. Botões só com ícone têm aria-label;
avisos e notificações usam roles alert/status. Estados desabilitados são reais;
processamento usa indicadores sem porcentagens fictícias.

A lateral tem 264 px (240 na janela menor), ou 76 px recolhida. A conversa usa
até 920 px de largura, com histórico rolável separado do compositor. Materiais
usam cards em duas colunas, ou uma em janelas menores. Prévia abre em diálogo
até 880 px e não comprime a largura do chat. O mínimo é 1000 × 650.

Fórmulas em bloco, tabelas e código têm rolagem horizontal própria. Imagens de
prévia respeitam a largura disponível. Textos de documento usam quebra de linha
sem interpretar HTML. Sombras aparecem principalmente em menus e diálogos.
As transições são breves; prefers-reduced-motion remove movimentos não essenciais.

## Exemplos verificados

As capturas usam dados temporários e uma IA simulada, sem documentos pessoais.

![Chat claro](screenshots/chat-claro.png)
![Chat escuro](screenshots/chat-escuro.png)
![Biblioteca clara](screenshots/materiais-claro.png)
![Biblioteca escura](screenshots/materiais-escuro.png)
![Prévia do envio](screenshots/previa-claro.png)

Também há capturas de material, lateral recolhida e janela mínima, geradas pelo
fluxo `pnpm e2e`. Ao alterar tokens ou componentes, confira ambos os temas,
contraste, títulos longos, foco, diálogos e 1000 × 650 antes de publicar.

## Área de atividades

Reutiliza Button/Badge/Field/Menu/Dialog e o Markdown sanitizado. Listagem com
filtros, editor em página rolável, questão central até 860 px, navegação numerada
e resumo com contagens separadas. Resultados/dicas/manuais têm rótulos distintos.
Estados arquivados preservam leitura e explicam restauração. Prévia de IA é
um diálogo com contexto, pedido e trechos separados. Não há métricas fictícias.
Tokens e classes ficam no mesmo style.css; títulos longos quebram, formulários
usam duas colunas e grids tornam-se uma coluna na janela menor.

![Prática clara](screenshots/atividades-pratica-claro.png)
![Prática escura](screenshots/atividades-pratica-escuro.png)
![Histórico](screenshots/atividades-historico-claro.png)

`pnpm e2e:atividades` produz também editor, revisão, prévia e 1000×650 em ambos os
temas, usando conteúdo fictício e API simulada. Ctrl/Tab, labels, foco e diálogos
seguem os componentes existentes; o histórico admite leitura sem liberar edição.

## Cálculos e gráficos

Formulário em diálogo amplo, operações por checkbox e campos necessários
rotulados. Ajuda de IA em details com prévia do destino/dados; ação de calcular
separada da proposta. Cards de PNG no chat, exportação nativa e explicação
identificada. Gráficos mantêm fundo de papel claro para legibilidade/exportação
nos dois temas; os controles usam os tokens existentes. Até 1000×650, o formulário
rola verticalmente sem comprimir campos ou introduzir rolagem horizontal.

![Matemática no tema escuro](screenshots/matematica-minima-escuro.png)

`pnpm e2e:matematica` também captura formulário, gráfico, proposta e explicação
com banco fictício e chamadas online proibidas.
