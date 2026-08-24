# Política de ingestão de documentos

## Princípio

Arquivos recebidos são dados não confiáveis. Inventariar não significa autorizar extração, publicação, execução ou envio a um provedor de IA.

## Classificações

| Estado | Comportamento inicial |
|---|---|
| `include` | Pode seguir para extração em ambiente isolado, análise de dados sensíveis e revisão editorial. |
| `review` | Exige inspeção humana antes de qualquer extração/publicação. Inclui SQL, YAML e nomes com indícios de dados de cliente. |
| `defer` | Reservado para OCR ou mídia em fase futura; não entra no MVP. |
| `block` | Nunca é extraído automaticamente. Inclui certificados, chaves, bancos, executáveis, scripts de sistema e arquivos compactados aninhados. |
| `skip` | Formato não suportado ou diretório. |

## Controles obrigatórios

- ZIP é lido sem extrair durante o inventário.
- Caminhos absolutos, `..`, links simbólicos e itens acima do limite são bloqueados.
- Certificados, chaves, bancos de dados, executáveis e possíveis senhas nunca entram no Git.
- Arquivos SQL não são executados; entram em revisão obrigatória.
- O conteúdo importável deve passar por detecção de CPF, CNPJ, e-mail, telefone, credenciais e dados de cliente.
- Extração futura deve usar diretório temporário isolado, limite de tamanho/tempo e processo sem privilégios.
- O documento original fica em storage privado; o banco recebe metadados e texto normalizado.
- Conteúdo restrito recebe autorização antes da busca, antes do contexto RAG e antes do download.
- O envio à OpenAI depende da classificação do documento. Conteúdo não autorizado deve usar Ollama local ou permanecer fora da IA.

## Publicação

Uma importação bem-sucedida cria um rascunho. A publicação exige sistema, fonte, categoria, confidencialidade, título e revisão da extração. Itens com alertas de segredo ou dados pessoais não podem ser publicados até o alerta ser resolvido e auditado.

## Visualização e uploads no piloto local

- A visualização do `Help.zip` lê somente o item solicitado e não extrai o pacote inteiro.
- Itens classificados como `block` nunca são entregues pela rota de arquivos.
- SQL, YAML e mídia podem ser consultados apenas no ambiente local para revisão; isso não os publica nem os torna contexto da IA.
- Uploads aceitam somente a lista segura de documentos, imagens e vídeo definida pela aplicação, com limites de quantidade e tamanho.
- Certificados, bancos, executáveis, scripts e arquivos compactados permanecem bloqueados no upload.
- Arquivos enviados ficam em storage privado fora do Git.
- Upload, histórico e leitura privada ficam limitados a `localhost` enquanto autenticação e autorização por documento não estiverem ativas.
