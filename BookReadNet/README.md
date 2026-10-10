<div align="center">

<h1>BookReadNet</h1>

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=24&duration=3500&pause=1200&color=E7643B&center=true&vCenter=true&width=700&lines=Sua+biblioteca+digital+pessoal;Leia+HQs%2C+mang%C3%A1s+e+livros;PDF+%7C+CBZ+%7C+CBR+%7C+CB7+%7C+EPUB)](https://github.com/JoaoGVP001/BookReadNet)

### Organize sua coleção. Continue de onde parou. Leia no seu ritmo.

O **BookReadNet** é uma aplicação desktop para cadastrar, organizar e ler
quadrinhos e livros digitais sem sair do próprio sistema.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/Interface-Tkinter-E7643B?style=flat-square)](https://docs.python.org/3/library/tkinter.html)
[![POO](https://img.shields.io/badge/Arquitetura-POO-17232D?style=flat-square)](#conceitos-de-poo)
[![Testes](https://img.shields.io/badge/Testes-20%20aprovados-2E8B57?style=flat-square&logo=pytest&logoColor=white)](#testes)
[![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-D9A441?style=flat-square)](https://github.com/JoaoGVP001/BookReadNet)

[Funcionalidades](#funcionalidades) · [Tecnologias](#tecnologias) · [Instalação](#instalação) · [Arquitetura](#arquitetura) · [Roadmap](ROADMAP.md)

</div>

---

## Sobre o projeto

O BookReadNet nasceu como um sistema acadêmico de biblioteca e evoluiu para um
**gerenciador e leitor pessoal de mídia digital**. A aplicação importa os arquivos
para um acervo local, registra metadados e permite retomar cada leitura exatamente
na página ou no trecho do capítulo em que ela foi interrompida.

O projeto foi desenvolvido para a disciplina de **Programação Orientada a Objetos 1**,
demonstrando conceitos de POO em funcionalidades reais e fáceis de apresentar.

## Funcionalidades

| Recurso | O que o sistema oferece |
| --- | --- |
| **Biblioteca digital** | Cadastro, edição, exclusão, pesquisa e filtros de obras |
| **Acervo visual** | Grade responsiva de cards com capa, favorito e progresso |
| **Capas** | Seleção manual, extração automática, substituição e imagem padrão |
| **Leitor integrado** | Navegação paginada e leitor EPUB com sumário, temas, fonte e espaçamento |
| **Cinco formatos** | Leitura de arquivos PDF, CBZ, CBR, CB7 e EPUB |
| **Progresso** | Página ou capítulo, posição interna, porcentagem e status automáticos |
| **Continuar lendo** | Retoma a obra na última página registrada |
| **Organização** | Categorias, séries, favoritos, autor, editora, idioma e volume |
| **Histórico** | Registro das páginas e obras acessadas recentemente |
| **Persistência** | Acervo e preferências armazenados localmente em JSON |
| **Importação segura** | Cópia dos arquivos e capas para pastas administradas pelo sistema |

## Tecnologias

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-E7643B?style=for-the-badge&logo=python&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-17232D?style=for-the-badge&logo=json&logoColor=white)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-B30B00?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)
<br>
![Pillow](https://img.shields.io/badge/Pillow-D9A441?style=for-the-badge&logo=python&logoColor=white)
![py7zr](https://img.shields.io/badge/py7zr-4F6D7A?style=for-the-badge&logo=7zip&logoColor=white)
![rarfile](https://img.shields.io/badge/rarfile-7B4B94?style=for-the-badge)
![EPUB](https://img.shields.io/badge/EPUB-ZIP%20%2B%20XHTML-E7643B?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

</div>

## Formatos suportados

| Formato | Estrutura | Leitor utilizado |
| :---: | --- | --- |
| **PDF** | Documento paginado | `LeitorPDF` + PyMuPDF |
| **CBZ** | Imagens compactadas em ZIP | `LeitorCBZ` + `zipfile` |
| **CBR** | Imagens compactadas em RAR | `LeitorCBR` + `rarfile` |
| **CB7** | Imagens compactadas em 7-Zip | `LeitorCB7` + `py7zr` |
| **EPUB** | ZIP, OPF, XHTML, imagens e sumário | `LeitorEPUB` + biblioteca padrão |

> [!IMPORTANT]
> A leitura de CBR pode exigir 7-Zip, UnRAR ou bsdtar instalado no Windows.
> PDF, CBZ, CB7 e EPUB funcionam com as dependências Python do projeto.
> EPUBs com capítulos protegidos por DRM são recusados com uma mensagem clara.

## Conceitos de POO

<details open>
<summary><strong>Ver os conceitos aplicados no projeto</strong></summary>

| Conceito | Aplicação no BookReadNet |
| --- | --- |
| **Abstração** | `ObraDigital` e `LeitorArquivo` definem contratos abstratos |
| **Herança** | `HQ`, `Manga` e `LivroDigital` especializam `ObraDigital` |
| **Polimorfismo** | Cada formato implementa sua própria forma de abrir e obter páginas |
| **Encapsulamento** | Atributos privados e propriedades validam o estado dos objetos |
| **Agregação** | `BibliotecaDigital` administra as obras cadastradas |
| **Composição** | O usuário possui seus progressos e registros de histórico |
| **Associação** | Cada progresso é relacionado a uma obra pelo identificador |

</details>

## Arquitetura

<details open>
<summary><strong>Visualizar organização dos módulos</strong></summary>

```text
                         main.py
                            │
                            ▼
                      interface.py
                       Tkinter GUI
                            │
                            ▼
                       servicos.py
                    BibliotecaDigital
                            │
        ┌────────────┬──────┴──────┬──────────────┐
        ▼            ▼             ▼              ▼
   modelos.py    leitor.py      capas.py     persistencia.py
        │            │             │               │
  ObraDigital   LeitorArquivo  ServicoCapas       JSON
   /   |   \    /  |  |  |  \       │
  HQ Manga Livro PDF CBZ CBR CB7 EPUB ▼
                               validacoes.py
```

| Arquivo | Responsabilidade |
| --- | --- |
| `modelos.py` | Entidades, encapsulamento e regras dos objetos |
| `servicos.py` | Regras do acervo, favoritos, filtros e progresso |
| `leitor.py` | Leitura polimórfica de PDF, CBZ, CBR, CB7 e EPUB |
| `capas.py` | Extração, validação, capa padrão e cache de miniaturas |
| `persistencia.py` | Salvamento e carregamento do repositório JSON |
| `validacoes.py` | Validação de arquivos, capas e formatos |
| `interface.py` | Telas e interação do usuário com Tkinter |
| `main.py` | Inicialização da aplicação |

</details>

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Git, caso queira clonar o repositório
- 7-Zip ou UnRAR para maior compatibilidade com CBR

### Clonar e instalar

```bash
git clone https://github.com/JoaoGVP001/BookReadNet.git
cd BookReadNet
python -m pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

No Windows, também é possível executar o atalho:

```bat
run.bat
```

Na primeira execução, o BookReadNet cria automaticamente:

```text
dados/bookreadnet.json
biblioteca/arquivos/
biblioteca/capas/
biblioteca/miniaturas/
```

## Testes

```bash
python -m pytest -v
```

```text
20 passed
```

Os testes validam cadastro, duplicidade, importação, pesquisa, filtros,
favoritos, progresso, histórico, persistência, exclusão, capas automáticas,
capas manuais, miniaturas e os leitores de PDF, CBZ, CB7 e EPUB. Para EPUB,
também são verificados metadados, capa, sumário, XHTML seguro, progresso por
capítulo e bloqueio de conteúdo protegido por DRM.

## Fluxo de uso

```text
Selecionar arquivo
        ↓
Cadastrar metadados
        ↓
Importar para o acervo
        ↓
Abrir no leitor interno
        ↓
Avançar pelas páginas ou capítulos
        ↓
Salvar progresso automaticamente
        ↓
Continuar a leitura depois
```

<details>
<summary><strong>Roteiro rápido para apresentação acadêmica</strong></summary>

1. Apresentar o problema e a proposta do BookReadNet.
2. Importar uma HQ ou um mangá.
3. Importar um EPUB e mostrar metadados, capa, sumário, temas e fonte.
4. Favoritar a obra e abrir o leitor integrado.
5. Avançar algumas páginas e fechar a leitura.
6. Mostrar a obra na seção `Continuar lendo`.
7. Abrir novamente e comprovar a restauração da página.
8. Explicar a hierarquia de obras e a fábrica de leitores.
9. Mostrar o histórico, o JSON e os testes automatizados.

</details>

## Evolução do projeto

O planejamento completo, as fases concluídas e as possíveis melhorias futuras
estão disponíveis no [ROADMAP.md](ROADMAP.md).

---

<div align="center">

### Projeto acadêmico desenvolvido com Python e Programação Orientada a Objetos

[![GitHub](https://img.shields.io/badge/GitHub-JoaoGVP001-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/JoaoGVP001)
[![Repositório](https://img.shields.io/badge/Reposit%C3%B3rio-BookReadNet-E7643B?style=flat-square&logo=github&logoColor=white)](https://github.com/JoaoGVP001/BookReadNet)

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=17&duration=4000&pause=1200&color=D9A441&center=true&vCenter=true&width=650&lines=Organize.+Leia.+Continue.;Uma+biblioteca+digital+constru%C3%ADda+com+POO.)](https://github.com/JoaoGVP001/BookReadNet)

</div>
