# Piloto de IA local no notebook

Experimento iniciado em **11/10/2026**, como execução inicial de L0 do
[plano de IA local](IA_LOCAL.md). A integração gráfica posterior está em [Ollama integrado](OLLAMA.md).

## Ambiente confirmado

- Ubuntu 26.04.1, Linux x86-64.
- Intel Core i5-13420H; 7,4 GiB de RAM utilizável (classe 8 GB), swap de 4 GiB.
- NVIDIA RTX 3050 Laptop 6 GB, driver 595.91.07, com aceleração CUDA reconhecida.
- Notebook na tomada; navegador e demais aplicativos permaneceram abertos.
- Ollama **0.40.3**, pacote oficial Linux AMD64, checksum SHA-256 conferido com
  o digest da release oficial. Nenhum driver, serviço global ou pacote de sistema
  foi modificado.
- Modelo **qwen3.5:4b-q4_K_M**, cerca de 3,32 GB decimais, digest
  `d8b0f5e9760cd1682034f292d7ef72ec46f432149be0df7574bf2d6e92e38c04`.
- Uma geração simultânea, contexto de 4.096 tokens, saída limitada a 1.536
  tokens e modo direto (`think: false`).

[Release Ollama](https://github.com/ollama/ollama/releases/tag/v0.40.3),
[instalação Linux](https://docs.ollama.com/linux),
[modelo](https://ollama.com/library/qwen3.5:4b-q4_K_M).

## Escopo deste piloto

Executar consultas reais locais, medir velocidade/memória, verificar campos
objetivos com gabaritos independentes e testar extração/FTS/citação de materiais
fictícios usando os serviços existentes. O validador de atividades é executado
sem salvar atividades no banco pessoal. O piloto não lê chaves Gemini/OpenAI
nem modifica a seleção de provedor do aplicativo.

O modelo recebe o enunciado, instruções e tipos do esquema, não os valores do
gabarito. A primeira rodada continha um exemplo de sintaxe igual à derivada
esperada no caso 1; o exemplo foi retirado na revisão. Mesmo com essa pista, a
rodada inicial errou a reta tangente. A avaliação automática cobre as respostas
objetivas e o formato; não certifica todos os passos da explicação nem provas.

As consultas documentais criam um banco temporário e extraem TXT pelo serviço
real. Outro material fica não selecionado e é excluído da recuperação. Há testes
de informação ausente e de instrução maliciosa dentro do documento. Não foram
usadas apostilas pessoais, imagens, PDF digitalizado ou embeddings neste piloto.

## Teste offline verificável

`scripts/benchmark_offline_linux.sh` cria um namespace de rede Linux com somente
loopback, inicia outra instância temporária do runtime e executa o benchmark.
O relatório verifica que o namespace difere do original e que uma conexão
externa não é possível. Esse isolamento abrange o runtime, seus processos
filhos e o cliente; a conexão dos outros aplicativos não é alterada.

Configuração adicional: `OLLAMA_NO_CLOUD=1`, servidor em `127.0.0.1:11434`, sem
proxies/redirecionamentos no cliente. Downloads iniciais ocorreram antes do
isolamento. Ao concluir, o script encerra apenas o servidor temporário criado.
Isso não instala firewall nem altera a rede/driver do sistema.

## Rodadas e limites de interpretação

A baseline passou em **10/14** casos. Usava temperatura zero e esquema com
respostas antes da explicação. Houve erros reais em tangente, inclusão-exclusão
e propriedades de relação; em alguns casos a própria explicação contradisse o
resultado final. A geração de atividade acertou 2+2, mas retornou arrays onde o
contrato exigia campos textuais; foi rejeitada.

O perfil `direto-v2` muda a ordem para explicação curta antes das respostas,
exige o esquema completo da atividade e usa parâmetros de geração do perfil
não deliberativo geral do cartão oficial: temperatura 0,7, top_p 0,8, top_k 20,
presence_penalty 1,5 e repeat_penalty 1,0. Seed 42 registrada; hardware/framework
podem influenciar a reprodutibilidade. [Parâmetros oficiais Qwen](https://huggingface.co/Qwen/Qwen3.5-4B).

A segunda rodada acrescenta quatro casos novos, totalizando 18. Como vários
parâmetros foram ajustados juntos após observar a baseline, uma melhora não
identifica isoladamente sua causa. Esse conjunto pequeno não estima desempenho
geral em matemática nem substitui os 30 casos independentes planejados.
Os relatórios completos permanecem fora do Git. Resultados medidos:

| Medida | Baseline | Perfil direto-v2 |
| --- | --- | --- |
| Critério estrito | 10/14 | 15/18 (11/14 comuns + 4/4 novos) |
| Mediana de geração, modelo carregado | 36,1 tokens/s | 36,2 tokens/s |
| Mediana até primeiro texto, modelo carregado | 0,217 s | 0,225 s |
| Tempo da primeira consulta da rodada | 69,7 s | 13,1 s |
| Pico total de VRAM observado | 3.854 MiB | 3.854 MiB |
| RAM disponível mínima observada | 1.184 MiB | 1.221 MiB |
| Swap total usada máxima | 3.117 MiB | 3.317 MiB |
| Namespace separado/conexão externa bloqueada | Confirmados | Confirmados |

Memória/swap são medições do sistema inteiro, incluindo outros aplicativos.
O primeiro carregamento inicial foi mais lento; o cache de arquivos/kernel já
existia na segunda rodada. Não atribuir a diferença de tempo somente ao prompt.
Logs do runtime confirmaram offload das 33/33 camadas para GPU.

Revisão manual dos três casos rejeitados em v2:

- **calculo-01:** matemática correta, incluindo `y = 2*x - 6`; o campo exigia
  apenas a expressão, e o prefixo `y =` foi rejeitado pelo parser restrito. Isso
  é falha de formato, não erro na tangente nessa rodada.
- **discreta-05:** erro real: afirmou que a falta de simetria impede transitividade.
  A relação `{(1,1),(2,2),(1,2)}` em `{1,2}` é reflexiva e transitiva, não simétrica.
- **material-01:** recuperou corretamente 7 questões/23 minutos e identificou
  M1 pelo nome; faltou o marcador literal `[M1]` pedido pelo contrato de citação.

Não normalizamos silenciosamente esses erros nem os contamos como aprovados.
A geração de atividade em v2 passou pelo validador existente; nada foi criado
no banco pessoal. Um chat real de terminal também respondeu e persistiu uma
consulta fictícia em arquivo separado. As duas rodadas e o smoke de chat fizeram
**33 consultas reais locais**, sem usar APIs Gemini/OpenAI.

Validação de código: **13 testes novos aprovados**, suíte Python completa sem
falhas (**119 aprovados, 10 testes da interface Tk legada ignorados por falta
de Tk**), sintaxe dos launchers e persistência real do chat verificadas. A
interface React não foi alterada; os fluxos Qt não foram repetidos nesta entrega.

## Usar o chat de teste

Neste notebook, o launcher é:

```bash
./iniciar_ia_local.sh
```

O atalho **IA Local - Testes** na área de trabalho abre esse launcher em um
terminal. O atalho original CadernoMat conserva seu comportamento.

Ele inicia o runtime do piloto quando necessário e abre um chat de terminal.
O texto aparece progressivamente. `/sair` encerra o chat; Ctrl+C interrompe uma
consulta. Ele recebe somente texto digitado, sem anexar a biblioteca pessoal.
Conversas concluídas são salvas em arquivos JSON separados do histórico do
CadernoMat. Não há interface gráfica ou retomada automática desses chats ainda.

O runtime descarrega o modelo após cerca de dois minutos sem consultas. A
primeira resposta pode demorar pelo carregamento; perguntas seguintes tendem
a ser mais rápidas. A RAM limitada e os aplicativos abertos influenciam os tempos.

Se outro computador não tiver o runtime/modelo preparados, o launcher não baixa
nada silenciosamente. Instalar o runtime oficial, configurar a pasta e baixar
o candidato é uma etapa separada; clonar o Git não traz esses arquivos. O launcher
e o isolamento deste piloto são Linux; o Windows terá seu fluxo próprio em L0/L1.

## Arquivos locais e reprodução

Neste Linux: `${XDG_DATA_HOME:-~/.local/share}/CadernoMat/ia-local/` contém
runtime, modelos, logs, relatórios e `chats-piloto/`. A pasta fica fora do Git.
O próprio Ollama também cria sua configuração/chave local em `~/.ollama/`.
Não publicar essas pastas, logs ou chats pessoais.

Para repetir o perfil atual, fechar outros testes concorrentes e executar:

```bash
scripts/benchmark_offline_linux.sh --saida /tmp/cadernomat-piloto.json
```

Requisitos: `unshare`, `ip`, `curl`, driver NVIDIA, modelo já instalado e ambiente
Python do CadernoMat. O script exige suporte a namespace de usuário/rede; em
outro Linux isso pode estar desabilitado. Nessa situação, relatar a limitação e
nunca chamar um teste com rede normal de teste isolado.

Testes automatizados do cliente/avaliador usam HTTP simulado e dados fictícios:

```bash
.venv/bin/python -m unittest discover -s tests -p test_piloto_local.py -v
```

## Entrega posterior

O contrato local foi integrado à configuração e ao chat React; consulte
[Ollama integrado](OLLAMA.md). O plano dessa entrega conserva os provedores
online, contexto por conversa, prévia, cancelamento e os serviços de estudo.
Priorizar verificação matemática e consistência de resposta/explicação.
Gráficos, páginas de caderno, embeddings, visão e ComfyUI continuam nas entregas
posteriores. Medir o PC de casa separadamente quando estiver disponível.
