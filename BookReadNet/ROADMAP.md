<div align="center">

# BookReadNet - Roadmap de Evolução

### Da biblioteca digital funcional para uma experiência completa de leitura

![Concluído](https://img.shields.io/badge/Versão_atual-Concluída-2E8B57?style=flat-square)
![Versão 2.2](https://img.shields.io/badge/Versão_2.2-EPUB-2E8B57?style=flat-square)
![Próxima versão](https://img.shields.io/badge/Próxima_versão-Leitor_avançado-E7643B?style=flat-square)

</div>

---

## Visão geral

O BookReadNet já possui cadastro de obras, acervo visual e leitura de PDF, CBZ,
CBR, CB7 e EPUB, além de progresso, favoritos, histórico e persistência JSON.
As próximas etapas se concentram na experiência avançada para HQs e mangás.

| Versão | Objetivo principal | Prioridade | Situação |
| --- | --- | :---: | :---: |
| **Atual** | Biblioteca digital e leitores PDF/CBZ/CBR/CB7 | A | Concluída |
| **2.1** | Capas e acervo visual em cards | A | Concluída |
| **2.2** | Suporte a EPUB | A | Concluída |
| **2.3** | Melhorias no leitor de HQs e mangás | B | Próxima |
| **2.4** | Novos formatos e importação em lote | B | Futura |
| **3.0** | SQLite, backup e estatísticas | C | Futura |

---

<details>
<summary><strong>Versão atual - base já concluída</strong></summary>

### Domínio e POO

- [x] Classe abstrata `ObraDigital`
- [x] Especializações `HQ`, `Manga` e `LivroDigital`
- [x] Encapsulamento com propriedades e validações
- [x] Abstração e polimorfismo na arquitetura dos leitores
- [x] Progresso, histórico, favoritos, categorias e séries

### Arquivos e leitura

- [x] Importação de PDF, CBZ, CBR e CB7
- [x] Leitor interno com próxima página, página anterior e zoom
- [x] Continuação automática da última página
- [x] Ordenação natural das imagens em arquivos compactados

### Interface e dados

- [x] Cadastro, edição, exclusão, busca e filtros
- [x] Tela `Continuar lendo`
- [x] Tela de favoritos e histórico
- [x] Persistência local em JSON
- [x] Seleção manual de uma imagem de capa durante o cadastro
- [x] Cópia da capa para `biblioteca/capas`

</details>

---

<details>
<summary><strong>Versão 2.1 - capas e acervo visual em cards - concluída</strong></summary>

### Objetivo

Fazer o acervo parecer uma biblioteca de mídia: cada obra deve aparecer com sua
capa, título, autor, tipo, progresso e ações principais.

### 1. Exibição das capas

- [x] Substituir a tabela atual por uma grade de cards
- [x] Exibir a capa de cada obra no acervo principal
- [x] Exibir capas em `Continuar lendo` e `Favoritos`
- [x] Exibir título, autor, formato e progresso abaixo da capa
- [x] Destacar obras favoritas com um ícone discreto
- [x] Mostrar uma capa padrão quando a obra não possuir imagem
- [x] Adaptar o número de cards ao tamanho da janela

### 2. Cadastro e edição de capas

- [x] Permitir selecionar uma capa durante o cadastro
- [x] Mostrar uma prévia da capa antes de salvar
- [x] Permitir adicionar uma capa depois que a obra já foi cadastrada
- [x] Permitir substituir ou remover a capa atual
- [x] Validar extensão e integridade da imagem
- [x] Aceitar JPG, JPEG, PNG e WEBP como capa
- [x] Recortar ou ajustar a miniatura sem deformar a proporção original

### 3. Extração automática

- [x] Extrair a primeira página como capa de PDF
- [x] Extrair a primeira imagem como capa de CBZ
- [x] Extrair a primeira imagem como capa de CBR
- [x] Extrair a primeira imagem como capa de CB7
- [x] Permitir que o usuário escolha entre capa automática, manual ou sem capa
- [x] Salvar miniaturas em cache para evitar reabrir arquivos grandes

### 4. Tela de detalhes

- [x] Criar uma tela ou janela de detalhes da obra
- [x] Exibir capa em tamanho maior
- [x] Mostrar título, autor, série, volume, categoria, formato e status
- [x] Mostrar barra visual de progresso
- [x] Disponibilizar `Ler`, `Favoritar`, `Editar` e `Excluir`
- [x] Abrir os detalhes ao dar duplo clique em um card

### Classes e módulos sugeridos

```text
ServicoCapas
├── validar_capa()
├── copiar_capa()
├── extrair_capa()
├── gerar_miniatura()
└── obter_capa_padrao()

GradeObras
├── exibir_capa()
├── exibir_progresso()
└── abrir_detalhes()
```

### Critérios de conclusão

- Toda obra aparece com capa própria ou imagem padrão
- O usuário consegue escolher, trocar e remover uma capa
- Obras sem capa podem gerar uma miniatura a partir da primeira página
- A grade continua funcionando ao redimensionar a janela
- Capas grandes não deixam a navegação lenta

</details>

---

<details open>
<summary><strong>Versão 2.2 - suporte a EPUB - concluída</strong></summary>

### Objetivo

Adicionar livros EPUB ao acervo e permitir sua leitura dentro do BookReadNet,
respeitando capítulos, ordem de leitura, imagens, capa e progresso.

### 1. Domínio e validação

- [x] Adicionar `.epub` aos formatos aceitos
- [x] Validar se o arquivo é um contêiner EPUB válido
- [x] Criar `LeitorEPUB` como especialização de `LeitorArquivo`
- [x] Registrar `LeitorEPUB` na `FabricaLeitores`
- [x] Diferenciar EPUB de layout fluido e EPUB de layout fixo
- [x] Tratar arquivos protegidos por DRM com mensagem clara de incompatibilidade

### 2. Estrutura do arquivo

- [x] Abrir o contêiner ZIP do EPUB
- [x] Localizar `META-INF/container.xml`
- [x] Ler o arquivo OPF e seu manifesto
- [x] Seguir a ordem de leitura definida pelo `spine`
- [x] Carregar título, autor, editora, idioma, ISBN e descrição
- [x] Localizar a capa oficial nos metadados
- [x] Ler o sumário e a divisão por capítulos

### 3. Renderização

- [x] Definir a estratégia para exibir XHTML com componentes seguros do Tkinter
- [x] Criar um modo inicial com texto, títulos e imagens essenciais
- [x] Respeitar quebra de parágrafo, negrito, itálico e alinhamento básico
- [x] Permitir alterar tamanho da fonte e espaçamento
- [x] Implementar tema claro, sépia e escuro para textos
- [x] Bloquear scripts e recursos externos por segurança
- [x] Exibir conteúdo visual de EPUB de layout fixo quando baseado em imagens compatíveis

### 4. Navegação e progresso

- [x] Exibir sumário navegável
- [x] Permitir avançar e voltar entre capítulos
- [x] Salvar capítulo e posição interna, não apenas número de página
- [x] Adaptar `ProgressoLeitura` para diferentes tipos de posição
- [x] Calcular porcentagem aproximada com base no conteúdo percorrido
- [x] Retomar exatamente no capítulo e trecho salvos
- [x] Registrar EPUB no histórico de leitura

### 5. Estratégia de dependências escolhida

```text
zipfile / XML  estrutura, OPF, manifesto, spine e metadados
HTMLParser     processamento controlado do XHTML
Tkinter        exibição segura de texto, estilos básicos e imagens
Pillow         imagens e capa, já utilizada pelo projeto
```

A implementação usa a biblioteca padrão do Python e o Pillow já existente. Essa
escolha mantém a instalação simples no Windows e evita executar scripts do EPUB.

### Critérios de conclusão

- [x] EPUB pode ser importado, validado e exibido no acervo
- [x] Capa e metadados são preenchidos automaticamente quando disponíveis
- [x] Sumário e capítulos funcionam dentro do leitor
- [x] Preferências de fonte, espaçamento e tema podem ser alteradas
- [x] Progresso é salvo e restaurado corretamente
- [x] Arquivos inválidos ou protegidos apresentam mensagens compreensíveis

</details>

---

<details>
<summary><strong>Versão 2.3 - experiência avançada para HQs e mangás</strong></summary>

### Navegação

- [ ] Modo tela cheia
- [ ] Campo para ir diretamente a uma página
- [ ] Barra ou miniaturas para navegar entre páginas
- [ ] Atalhos configuráveis de teclado
- [ ] Rolagem contínua vertical
- [ ] Pré-carregamento da página seguinte

### Modos de leitura

- [ ] Página única
- [ ] Página dupla
- [ ] Sentido ocidental: esquerda para direita
- [ ] Sentido de mangá: direita para esquerda
- [ ] Ajustar à largura, altura ou janela
- [ ] Rotação de página
- [ ] Zoom com roda do mouse

### Desempenho

- [ ] Cache limitado das páginas mais próximas
- [ ] Carregamento em segundo plano sem travar a interface
- [ ] Liberação automática de imagens fora do cache
- [ ] Indicador de carregamento para arquivos grandes
- [ ] Testes com obras de centenas de páginas

</details>

---

<details>
<summary><strong>Versão 2.4 - novos formatos e importação</strong></summary>

### Formatos adicionais

- [ ] Imagens avulsas: JPG, JPEG, PNG e WEBP
- [ ] Leitura de uma pasta ordenada de imagens
- [ ] CBT, com páginas compactadas em TAR
- [ ] Avaliar DJVU para documentos digitalizados
- [ ] Manter MOBI e AZW3 apenas como possibilidade futura

### Importação e organização

- [ ] Importar vários arquivos de uma vez
- [ ] Importar uma pasta completa
- [ ] Arrastar e soltar arquivos na janela
- [ ] Detectar duplicidade por hash do arquivo
- [ ] Sugerir título e volume a partir do nome do arquivo
- [ ] Gerar capas e metadados em segundo plano
- [ ] Exibir relatório dos arquivos importados ou rejeitados

</details>

---

<details>
<summary><strong>Versão 2.5 - organização e experiência pessoal</strong></summary>

- [ ] Notas pessoais por obra
- [ ] Avaliação de uma a cinco estrelas
- [ ] Tags personalizadas
- [ ] Ordenação por título, autor, data, progresso e avaliação
- [ ] Filtros combinados e filtros salvos
- [ ] Agrupamento visual por série e volume
- [ ] Tela de obras lidas recentemente
- [ ] Estatísticas simples de leitura
- [ ] Exportação da lista do acervo em JSON ou CSV
- [ ] Temas claro, escuro e sépia para a aplicação
- [ ] Configurações persistentes do usuário

</details>

---

<details>
<summary><strong>Versão 3.0 - persistência, backup e estabilidade</strong></summary>

### Dados

- [ ] Migrar o repositório JSON para SQLite
- [ ] Criar migração automática dos dados existentes
- [ ] Separar tabelas de obras, séries, progresso, histórico e tags
- [ ] Implementar backup manual e automático
- [ ] Permitir restaurar um backup
- [ ] Verificar arquivos ausentes ou movidos
- [ ] Permitir relocalizar uma obra sem perder seus dados

### Qualidade

- [x] Ampliar os testes unitários para EPUB
- [ ] Criar testes de integração para importação e persistência
- [ ] Testar arquivos corrompidos, vazios e protegidos por senha
- [ ] Testar caminhos com acentos e nomes longos no Windows
- [ ] Adicionar logs locais para diagnóstico
- [ ] Criar tratamento global de erros da interface
- [ ] Preparar uma versão executável para Windows

</details>

---

## Ordem recomendada de implementação

```text
FASE 1 - Capas
Campo existente → prévia → troca → capa padrão → extração automática
                              ↓
FASE 2 - Acervo visual
Cards → grade responsiva → detalhes → continuar lendo com capas
                              ↓
FASE 3 - EPUB básico
Validação → metadados → capa → capítulos → renderização
                              ↓
FASE 4 - Progresso EPUB
Posição no capítulo → porcentagem → continuar lendo
                              ↓
FASE 5 - Leitor avançado
Página dupla → sentido mangá → tela cheia → cache
                              ↓
FASE 6 - Expansão
Imagens/pastas → CBT → importação em lote → SQLite
```

## Próximo incremento recomendado

O próximo desenvolvimento deve iniciar a **Versão 2.3**:

1. Criar os modos de página única e página dupla.
2. Adicionar o sentido de leitura ocidental e de mangá.
3. Implementar tela cheia, rolagem contínua e navegação direta.
4. Melhorar zoom, ajuste à janela e rotação.
5. Adicionar cache limitado e pré-carregamento em segundo plano.
6. Testar obras extensas sem travar a interface.

## Fluxo futuro planejado

```text
Adicionar obra
      ↓
Selecionar PDF / CBZ / CBR / CB7 / EPUB
      ↓
Ler metadados e localizar uma capa
      ↓
Usar capa automática ou escolher outra
      ↓
Exibir a obra em um card no acervo
      ↓
Abrir detalhes ou iniciar leitura
      ↓
Salvar página, capítulo ou posição
      ↓
Continuar posteriormente
```
