import { useCallback, useEffect, useRef, useState } from "react";
import {
  Plus,
  ClipboardList,
  ArrowLeft,
  Pencil,
  Archive,
  Copy,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Eye,
  Lightbulb,
  Sparkles,
  Search,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { api } from "./bridge";
import { Button, Badge, Dialog, Field, Menu, Empty, Loading } from "./ui";
import { Markdown } from "./Markdown";
import type { Estado, ListaMateriais } from "./model";
import type {
  Atividade,
  Conteudo,
  Exercicio,
  Formato,
  Tentativa,
  Historico,
  Job,
  StudyDraft,
} from "./activities-model";
import {
  formatos,
  dificuldades,
  novaQuestao,
  novoConteudo,
  respondida,
} from "./activities-model";

type Seed = {
  origem_chat?: string;
  materiais?: string[];
  assunto?: string;
  nonce: number;
};
type Props = {
  state: Estado;
  notify: (s: string) => void;
  seed?: Seed | null;
  onChat: () => Promise<void>;
};
const data = (v: string | null) =>
  v ? new Date(v.replace(" ", "T") + "Z").toLocaleString("pt-BR") : "—";
const esperado = (q: Exercicio) =>
  q.formato === "vf"
    ? q.resposta === true
      ? "Verdadeiro"
      : q.resposta === false
        ? "Falso"
        : "Sem gabarito"
    : q.formato === "escolha"
      ? q.alternativas.find((a) => a.id === q.resposta)?.texto || "Sem gabarito"
      : String(q.resposta || "Sem gabarito");
const rotulos: Record<string, string> = {
  correta: "Correta",
  incorreta: "Revisar",
  sem_resposta: "Em branco",
  sem_gabarito: "Sem gabarito",
  revisao_necessaria: "Revisão necessária",
};

export function Activities({ state, notify, seed, onChat }: Props) {
  const [list, setList] = useState<{
    itens: Atividade[];
    total: number;
    pagina: number;
  }>({ itens: [], total: 0, pagina: 0 });
  const [filters, setFilters] = useState({
    busca: "",
    formato: "",
    dificuldade: "",
    situacao: "ativas",
    pagina: 0,
  });
  const [activity, setActivity] = useState<Atividade | null>(null),
    [attempt, setAttempt] = useState<Tentativa | null>(null),
    [history, setHistory] = useState<Historico[]>([]);
  const [editor, setEditor] = useState<{
    a?: Atividade;
    content: Conteudo;
    materiais: string[];
    origem_chat?: string;
    proposta?: string;
    caderno?: string | null;
  } | null>(null);
  const [gen, setGen] = useState<{ tipo: string; materiais: string[] } | null>(
      null,
    ),
    [job, setJob] = useState<Job | null>(null),
    [jobs, setJobs] = useState<Job[]>([]);
  const [moving, setMoving] = useState<Atividade | null>(null),
    [destination, setDestination] = useState(""),
    [comparison, setComparison] = useState<Tentativa[] | null>(null),
    [selected, setSelected] = useState<string[]>([]);
  const [working, setWorking] = useState(false),
    [ready, setReady] = useState(false);
  const book = state.navegacao.caderno_id;
  const bookArchived = !!state.cadernos.find((c) => c.id === book)?.arquivado;
  const origin = useRef<{
    origem_chat?: string;
    materiais: string[];
    assunto?: string;
    caderno?: string | null;
  }>({
    materiais: [],
  });
  const attemptRef = useRef(attempt);
  attemptRef.current = attempt;
  const safe = useCallback(
    async <T,>(fn: () => Promise<T>): Promise<T | undefined> => {
      setWorking(true);
      try {
        return await fn();
      } catch (e) {
        notify((e as Error).message);
      } finally {
        setWorking(false);
      }
    },
    [notify],
  );
  const refresh = useCallback(async () => {
    const [ls, js] = await Promise.all([
      api<typeof list>("atividades", { ...filters, caderno: book }),
      api<Job[]>("estudo_jobs"),
    ]);
    setList(ls);
    setJobs(js);
  }, [filters, book]);
  const nav = async (a: Atividade | null, t: Tentativa | null) => {
    await api("estudo_navegar", {
      area: "atividades",
      atividade: a?.id || null,
      tentativa: t?.id || null,
    });
    setActivity(a);
    setAttempt(t);
    setSelected([]);
    if (a)
      setHistory(await api<Historico[]>("tentativas", { atividade: a.id }));
  };
  const flush = async () => {
    await window.cadernoMatFlushStudy?.();
  };
  useEffect(() => {
    const timer = setTimeout(() => {
      refresh().catch((e) => notify(e.message));
    }, 180);
    return () => clearTimeout(timer);
  }, [refresh, notify, state.revisao]);
  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const n = (await api<Estado>("estado")).estudo;
        if (n?.atividade) {
          const a = await api<Atividade>("atividade_obter", {
            id: n.atividade,
          });
          const t = n.tentativa
            ? await api<Tentativa>("tentativa_obter", { id: n.tentativa })
            : null;
          if (live && a.caderno_id === book) {
            setActivity(a);
            setAttempt(t);
            setHistory(
              await api<Historico[]>("tentativas", { atividade: a.id }),
            );
          }
        }
      } catch (e) {
        notify((e as Error).message);
      } finally {
        if (live) setReady(true);
      }
    })();
    return () => {
      live = false;
    };
  }, []);
  const previousBook = useRef(book);
  useEffect(() => {
    if (previousBook.current !== book) {
      previousBook.current = book;
      void safe(async () => {
        await flush();
        setEditor(null);
        setGen(null);
        await nav(null, null);
        setFilters((f) => ({ ...f, pagina: 0 }));
      });
    }
  }, [book]);
  useEffect(() => {
    if (seed) {
      origin.current = {
        origem_chat: seed.origem_chat,
        materiais: seed.materiais || [],
      };
      setAttempt(null);
      setActivity(null);
      const content = novoConteudo();
      content.assuntos = seed.assunto || "";
      setEditor({ content, ...origin.current });
    }
  }, [seed?.nonce]);
  useEffect(() => {
    if (!job || job.estado !== "executando") return;
    const timer = setInterval(() => {
      api<Job>("estudo_job", { id: job.id })
        .then((j) => {
          setJob(j);
          if (j.estado !== "executando" && attemptRef.current)
            api<Tentativa>("tentativa_obter", { id: attemptRef.current.id })
              .then(setAttempt)
              .catch((e) => notify(e.message));
        })
        .catch((e) => notify(e.message));
    }, 500);
    return () => clearInterval(timer);
  }, [job?.id, job?.estado, notify]);
  useEffect(() => {
    let live = true;
    const current = attemptRef.current;
    if (current)
      (async () => {
        try {
          await window.cadernoMatFlushStudy?.();
          const updated = await api<Tentativa>("tentativa_obter", {
            id: current.id,
          });
          if (live && attemptRef.current?.id === current.id)
            setAttempt(updated);
        } catch (e) {
          notify((e as Error).message);
        }
      })();
    return () => {
      live = false;
    };
  }, [state.revisao, notify]);
  const open = async (a: Atividade, t?: string) => {
    await flush();
    const detail = await api<Atividade>("atividade_obter", { id: a.id });
    await nav(
      detail,
      t ? await api<Tentativa>("tentativa_obter", { id: t }) : null,
    );
  };
  const start = async (nova = false) => {
    if (!activity) return;
    await flush();
    const t = await api<Tentativa>("tentativa_iniciar", {
      atividade: activity.id,
      nova,
    });
    await nav(activity, t);
  };
  const act = async (a: Atividade, acao: string, extras = {}) => {
    const updated = await api<Atividade>("atividade_acao", {
      id: a.id,
      acao,
      ...extras,
    });
    await refresh();
    if (activity?.id === a.id)
      await nav(updated.caderno_id === book ? updated : null, null);
  };
  const generate = (tipo = "geracao") => setGen({ tipo, materiais: [] });
  if (!ready)
    return (
      <div className="activities-view">
        <Loading />
      </div>
    );
  return (
    <section className="activities-view" aria-label="Atividades de estudo">
      {editor ? (
        <ActivityEditor
          key={editor.proposta || editor.a?.id || seed?.nonce || "nova"}
          initial={editor}
          state={state}
          notify={notify}
          busy={working || state.ocupado}
          onGenerate={(mats, assunto, caderno) => {
            origin.current = {
              ...origin.current,
              materiais: mats,
              assunto,
              caderno,
            };
            setGen({ tipo: "geracao", materiais: mats });
          }}
          onClose={() => {
            if (
              window.confirm(
                "Descartar as alterações ainda não salvas do editor?",
              )
            )
              setEditor(null);
          }}
          onSave={async (content, caderno, mats) => {
            await safe(async () => {
              const a = await api<Atividade>("atividade_salvar", {
                id: editor.a?.id,
                versao: editor.a?.versao,
                conteudo: content,
                caderno,
                materiais: mats,
                origem_chat: editor.origem_chat,
                proposta: editor.proposta,
              });
              setEditor(null);
              await nav(a.caderno_id === book ? a : null, null);
              await refresh();
              notify(
                `Atividade salva em ${state.cadernos.find((c) => c.id === a.caderno_id)?.nome || "Geral"}. O histórico anterior foi preservado.`,
              );
            });
          }}
        />
      ) : attempt && activity ? (
        <Practice
          key={attempt.id}
          attempt={attempt}
          onUpdate={setAttempt}
          notify={notify}
          busy={working || state.ocupado}
          onBack={() =>
            void safe(async () => {
              await flush();
              await nav(activity, null);
            })
          }
          onAI={generate}
          onChat={() =>
            void safe(async () => {
              await flush();
              await api("exercicio_chat", {
                id: attempt.id,
                exercicio:
                  attempt.snapshot.conteudo.exercicios[attempt.posicao].id,
              });
              await onChat();
            })
          }
        />
      ) : activity ? (
        <>
          <div className="activity-heading">
            <Button
              variant="ghost"
              icon={ArrowLeft}
              onClick={() => void safe(() => nav(null, null))}
            >
              Todas as atividades
            </Button>
            <div className="activity-actions">
              <Button
                icon={Pencil}
                disabled={
                  !!activity.arquivada ||
                  activity.caderno_arquivado ||
                  state.ocupado
                }
                onClick={() =>
                  setEditor({
                    a: activity,
                    content: structuredClone(activity.conteudo),
                    materiais: activity.fontes
                      .filter((f) => f.disponivel)
                      .map((f) => f.id),
                  })
                }
              >
                Editar atividade
              </Button>
              <Menu
                label="Ações da atividade"
                disabled={state.ocupado || activity.caderno_arquivado}
                items={[
                  {
                    label: "Duplicar atividade",
                    icon: Copy,
                    action: () => void safe(() => act(activity, "duplicar")),
                  },
                  {
                    label: "Mover atividade",
                    icon: ArrowRight,
                    action: () => {
                      setMoving(activity);
                      setDestination(activity.caderno_id || "");
                    },
                  },
                  {
                    label: activity.arquivada
                      ? "Restaurar atividade"
                      : "Arquivar atividade",
                    icon: Archive,
                    action: () =>
                      void safe(() =>
                        act(activity, "arquivar", {
                          valor: !activity.arquivada,
                        }),
                      ),
                  },
                ]}
              />
            </div>
          </div>
          <article className="activity-intro">
            <div className="eyebrow">PRÁTICA · VERSÃO {activity.versao}</div>
            <h2>{activity.conteudo.titulo}</h2>
            <Markdown texto={activity.conteudo.descricao} />
            <p>
              {activity.conteudo.objetivo ||
                "Pratique e registre suas respostas."}
            </p>
            <div className="activity-tags">
              <Badge>{activity.conteudo.exercicios.length} exercícios</Badge>
              <Badge>{dificuldades[activity.conteudo.dificuldade]}</Badge>
              <Badge>
                {activity.origem === "ia"
                  ? `Proposta ${activity.proveniencia.provedor} revisada`
                  : "Criação manual"}
              </Badge>
            </div>
            {(!!activity.arquivada || activity.caderno_arquivado) && (
              <p role="status" className="activity-warning">
                Restaure a atividade e seu caderno para editar ou continuar. As
                tentativas permanecem disponíveis para leitura.
              </p>
            )}
            <div className="activity-actions">
              <Button
                variant="primary"
                icon={BookOpen}
                disabled={
                  !!activity.arquivada ||
                  activity.caderno_arquivado ||
                  state.ocupado ||
                  working
                }
                onClick={() => void safe(() => start())}
              >
                Começar ou continuar
              </Button>
              <Button
                disabled={
                  !!activity.arquivada ||
                  activity.caderno_arquivado ||
                  state.ocupado ||
                  working
                }
                onClick={() => void safe(() => start(true))}
              >
                Nova tentativa
              </Button>
            </div>
            {activity.origem_titulo && (
              <p className="muted">
                Origem: {activity.origem_titulo}
                {!activity.origem_disponivel ? " · conversa removida" : ""}
              </p>
            )}
            <Sources fontes={activity.fontes} />
          </article>
          <div className="activity-heading">
            <h3>Histórico de tentativas</h3>
            <Button
              disabled={selected.length !== 2}
              onClick={() =>
                void safe(async () => {
                  const r = await api<{
                    mesma_versao: boolean;
                    tentativas: Tentativa[];
                  }>("tentativas_comparar", { ids: selected });
                  setComparison(r.tentativas);
                })
              }
            >
              Comparar duas tentativas
            </Button>
          </div>
          <p className="muted">
            Marque duas tentativas. Resultados objetivos não incluem questões
            discursivas.
          </p>
          <div className="attempt-history">
            {history.length ? (
              history.map((h) => (
                <div className="attempt-row" key={h.id}>
                  <input
                    type="checkbox"
                    aria-label={`Comparar tentativa ${h.id}`}
                    checked={selected.includes(h.id)}
                    onChange={(e) =>
                      setSelected((prev) =>
                        e.target.checked
                          ? [...prev.slice(-1), h.id]
                          : prev.filter((i) => i !== h.id),
                      )
                    }
                  />
                  <div>
                    <strong>{data(h.inicio)}</strong>
                    <small>
                      Versão {h.versao} ·{" "}
                      {h.estado === "andamento" ? "Em andamento" : "Finalizada"}{" "}
                      · {h.resumo.respondidas}/{h.resumo.total} respondidas
                    </small>
                    <small>
                      {h.estado === "finalizada"
                        ? `${h.resumo.acertos} acertos · ${h.resumo.erros} erros · ${h.resumo.nao_avaliadas} não avaliadas`
                        : "Resultado disponível ao finalizar"}{" "}
                      · {h.resumo.dicas} dicas · {h.resumo.solucoes} soluções
                    </small>
                  </div>
                  <Button onClick={() => void safe(() => open(activity, h.id))}>
                    {h.estado === "andamento" ? "Retomar" : "Ver tentativa"}
                  </Button>
                </div>
              ))
            ) : (
              <p className="muted">Você ainda não iniciou uma tentativa.</p>
            )}
          </div>
        </>
      ) : (
        <>
          <div className="activity-heading">
            <div>
              <h2>Pratique no seu ritmo</h2>
              <p className="muted">
                Listas e tentativas salvas neste computador.
              </p>
            </div>
            <div className="activity-actions">
              <Button
                icon={Sparkles}
                disabled={bookArchived || state.ocupado}
                onClick={() => generate()}
              >
                Gerar com IA
              </Button>
              <Button
                variant="primary"
                icon={Plus}
                disabled={bookArchived || state.ocupado}
                onClick={() => {
                  origin.current = { materiais: [] };
                  setEditor({ content: novoConteudo(), materiais: [] });
                }}
              >
                Criar atividade
              </Button>
            </div>
          </div>
          {bookArchived && (
            <p className="activity-warning">
              Caderno arquivado. Você pode ler as atividades e tentativas;
              restaure para continuar.
            </p>
          )}
          <div className="activity-filters">
            <Field label="Buscar atividades">
              <input
                placeholder="Título, assunto ou etiquetas"
                value={filters.busca}
                maxLength={300}
                onChange={(e) =>
                  setFilters({ ...filters, busca: e.target.value, pagina: 0 })
                }
              />
            </Field>
            <Field label="Formato">
              <select
                value={filters.formato}
                onChange={(e) =>
                  setFilters({ ...filters, formato: e.target.value, pagina: 0 })
                }
              >
                <option value="">Todos</option>
                {Object.entries(formatos).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Dificuldade">
              <select
                value={filters.dificuldade}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    dificuldade: e.target.value,
                    pagina: 0,
                  })
                }
              >
                <option value="">Todas</option>
                {Object.entries(dificuldades).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Situação">
              <select
                value={filters.situacao}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    situacao: e.target.value,
                    pagina: 0,
                  })
                }
              >
                {Object.entries({
                  ativas: "Ativas",
                  arquivadas: "Arquivadas",
                  andamento: "Com tentativa em andamento",
                  finalizadas: "Com tentativa finalizada",
                }).map(([k, v]) => (
                  <option key={k} value={k}>
                    {v}
                  </option>
                ))}
              </select>
            </Field>
          </div>
          {list.total ? (
            <>
              <div className="activity-grid">
                {list.itens.map((a) => (
                  <article className="activity-card" key={a.id}>
                    <div className="activity-tags">
                      <Badge>{dificuldades[a.conteudo.dificuldade]}</Badge>
                      <span className="muted">v{a.versao}</span>
                    </div>
                    <h3>{a.conteudo.titulo}</h3>
                    <p>
                      {a.conteudo.objetivo ||
                        a.conteudo.assuntos ||
                        "Atividade de estudo"}
                    </p>
                    <small>
                      {a.quantidade} exercícios · {a.tentativas} tentativas
                    </small>
                    <div className="activity-actions">
                      <Button onClick={() => void safe(() => open(a))}>
                        Abrir atividade
                      </Button>
                      {a.em_andamento && (
                        <Button
                          variant="ghost"
                          onClick={() =>
                            void safe(() => open(a, a.em_andamento!))
                          }
                        >
                          Retomar
                        </Button>
                      )}
                    </div>
                  </article>
                ))}
              </div>
              <div className="activity-actions">
                <Button
                  aria-label="Página anterior de atividades"
                  disabled={!list.pagina}
                  onClick={() =>
                    setFilters({ ...filters, pagina: list.pagina - 1 })
                  }
                >
                  <ChevronLeft size={18} />
                </Button>
                <span>
                  {list.total} atividades · Página {list.pagina + 1}
                </span>
                <Button
                  aria-label="Próxima página de atividades"
                  disabled={(list.pagina + 1) * 30 >= list.total}
                  onClick={() =>
                    setFilters({ ...filters, pagina: list.pagina + 1 })
                  }
                >
                  <ChevronRight size={18} />
                </Button>
              </div>
            </>
          ) : (
            <Empty
              icon={ClipboardList}
              title="Seu próximo exercício começa aqui"
            >
              Crie uma atividade manual sem internet, ou gere uma proposta com
              sua API.
            </Empty>
          )}
        </>
      )}
      {!editor && jobs.length > 0 && !attempt && (
        <details className="activity-jobs">
          <summary>Consultas e propostas de IA ({jobs.length})</summary>
          {jobs.map((j) => (
            <div className="attempt-row" key={j.id}>
              <div>
                <strong>
                  {j.tipo === "geracao"
                    ? "Geração"
                    : j.tipo === "dica"
                      ? "Dica"
                      : "Feedback"}
                </strong>
                <small>
                  {data(j.criado)} · {j.estado} · {j.previa.provedor}
                </small>
              </div>
              <Button onClick={() => setJob(j)}>Abrir consulta</Button>
            </div>
          ))}
        </details>
      )}
      {moving && (
        <Dialog title="Mover atividade" onClose={() => setMoving(null)}>
          <Field label="Caderno de destino">
            <select
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
            >
              <option value="">Geral</option>
              {state.cadernos
                .filter((c) => !c.arquivado)
                .map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nome}
                  </option>
                ))}
            </select>
          </Field>
          <div className="dialog-actions">
            <Button
              variant="primary"
              onClick={() =>
                void safe(async () => {
                  await act(moving, "mover", { destino: destination || null });
                  setMoving(null);
                })
              }
            >
              Mover
            </Button>
          </div>
        </Dialog>
      )}
      {gen && (
        <GenerationForm
          tipo={gen.tipo}
          origin={origin.current}
          state={state}
          attempt={attempt}
          onClose={() => setGen(null)}
          onPreview={(d) =>
            void safe(async () => {
              await flush();
              const j = await api<Job>("estudo_previa", d);
              setGen(null);
              setJob(j);
            })
          }
        />
      )}
      {job && (
        <Dialog
          title={
            job.tipo === "geracao"
              ? "Proposta de atividade com IA"
              : job.tipo === "dica"
                ? "Dica progressiva com IA"
                : "Feedback pedagógico com IA"
          }
          subtitle="Consulta opcional ao provedor escolhido. Confira os dados antes de enviar."
          wide
          onClose={() => setJob(null)}
        >
          <JobPreview job={job} />
          {job.estado === "executando" ? (
            <Loading>
              Consultando {job.previa.provedor}… Pode continuar escrevendo sua
              resposta.
            </Loading>
          ) : ["erro", "cancelada", "incompleta"].includes(job.estado) ? (
            <p role="alert" className="activity-warning">
              {job.erro}
            </p>
          ) : job.estado === "concluida" &&
            job.resultado &&
            job.tipo !== "geracao" ? (
            <Markdown texto={(job.resultado as { texto: string }).texto} />
          ) : null}
          <div className="dialog-actions">
            {job.estado === "executando" && job.previa.local && (
              <Button
                onClick={() =>
                  void safe(async () => {
                    await api("ia_cancelar", { id: job.id });
                  })
                }
              >
                Cancelar consulta local
              </Button>
            )}
            {job.estado === "concluida" && job.tipo === "geracao" ? (
              <Button
                variant="primary"
                onClick={() => {
                  setEditor({
                    content: structuredClone(job.resultado as Conteudo),
                    materiais: job.previa.materiais.map((m) => m.id),
                    origem_chat: job.previa.origem_chat || undefined,
                    proposta: job.id,
                    caderno: job.previa.caderno,
                  });
                  setAttempt(null);
                  setActivity(null);
                  setJob(null);
                }}
              >
                Revisar proposta no editor
              </Button>
            ) : job.estado !== "executando" && job.estado !== "concluida" ? (
              <Button
                variant="primary"
                disabled={state.ocupado || working}
                onClick={() =>
                  void safe(async () =>
                    setJob(await api<Job>("estudo_consultar", { id: job.id })),
                  )
                }
              >
                {job.previa.local
                  ? "Confirmar consulta local"
                  : "Confirmar consulta à API"}
              </Button>
            ) : null}
            <Button onClick={() => setJob(null)}>Fechar</Button>
          </div>
        </Dialog>
      )}
      {comparison && (
        <Dialog
          title="Comparar tentativas"
          subtitle={
            comparison[0].versao === comparison[1].versao
              ? "Mesma versão: compare os resultados objetivos e o uso de ajuda."
              : "Versões diferentes: os exercícios podem ter mudado. Não compare como se fossem a mesma lista."
          }
          wide
          onClose={() => setComparison(null)}
        >
          <div className="comparison-grid">
            {comparison.map((t) => (
              <article className="activity-card" key={t.id}>
                <h3>Versão {t.versao}</h3>
                <p>
                  {data(t.inicio)} ·{" "}
                  {t.estado === "finalizada" ? "Finalizada" : "Em andamento"}
                </p>
                <Summary t={t} />
                {t.snapshot.conteudo.exercicios.map((q) => (
                  <div key={q.id}>
                    <Markdown texto={q.enunciado} />
                    <p>
                      Resposta:{" "}
                      {String(t.respostas[q.id]?.resposta ?? "Em branco")}
                    </p>
                  </div>
                ))}
              </article>
            ))}
          </div>
        </Dialog>
      )}
    </section>
  );
}

function Sources({ fontes }: { fontes: Atividade["fontes"] }) {
  return fontes.length > 0 ? (
    <div className="activity-sources">
      <small>
        Materiais de origem (usar em uma consulta exige nova seleção explícita)
      </small>
      {fontes.map((f) => (
        <span key={f.id}>
          {f.nome}
          {f.disponivel === false ? " · fonte indisponível" : ""}
        </span>
      ))}
    </div>
  ) : null;
}
function Summary({ t }: { t: Tentativa }) {
  return (
    <div className="practice-summary">
      <div>
        <strong>
          {t.resumo.respondidas}/{t.resumo.total}
        </strong>
        <small>Respondidas</small>
      </div>
      {t.estado === "finalizada" && (
        <>
          <div>
            <strong>{t.resumo.objetivas}</strong>
            <small>Corrigidas objetivamente</small>
          </div>
          <div>
            <strong>
              {t.resumo.acertos} / {t.resumo.erros}
            </strong>
            <small>Acertos / erros</small>
          </div>
          <div>
            <strong>{t.resumo.nao_avaliadas}</strong>
            <small>Não avaliadas</small>
          </div>
        </>
      )}
      <p>
        {t.resumo.dicas} dicas · {t.resumo.solucoes} soluções reveladas.
        Feedback de IA e revisão manual ficam separados da correção objetiva.
      </p>
    </div>
  );
}

function SourcePicker({
  ids,
  onChange,
  onNames,
  consulta = true,
}: {
  ids: string[];
  onChange: (ids: string[]) => void;
  onNames?: (names: Record<string, string>) => void;
  consulta?: boolean;
}) {
  const [search, setSearch] = useState(""),
    [page, setPage] = useState(0),
    [list, setList] = useState<ListaMateriais | null>(null),
    [error, setError] = useState("");
  const namesCallback = useRef(onNames);
  namesCallback.current = onNames;
  useEffect(() => {
    let live = true;
    const timer = setTimeout(
      () =>
        api<ListaMateriais>("materiais", {
          busca: search,
          pagina: page,
          caderno: "todos",
        })
          .then((r) => {
            if (live) {
              setList(r);
              namesCallback.current?.(
                Object.fromEntries(r.itens.map((m) => [m.id, m.nome])),
              );
              setError("");
            }
          })
          .catch((e) => {
            if (live) setError(e.message);
          }),
      150,
    );
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [search, page]);
  return (
    <fieldset className="source-picker">
      <legend>
        {consulta
          ? "Fontes autorizadas para esta consulta"
          : "Materiais de origem da atividade"}
      </legend>
      <p className="muted">
        {consulta
          ? "Seleção explícita, até 10 materiais. Associação ao caderno não envia documentos. Apenas trechos de texto serão enviados."
          : "Vincular materiais não envia documentos à IA. Em cada consulta, selecione novamente as fontes. Até 10 materiais."}
      </p>
      <input
        aria-label="Buscar fontes"
        placeholder="Buscar material"
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setPage(0);
        }}
      />
      {error && <p role="alert">{error}</p>}
      <div className="source-list">
        {list?.itens.map((m) => (
          <label key={m.id}>
            <input
              type="checkbox"
              disabled={
                !ids.includes(m.id) &&
                ((consulta && !["pronto", "parcial"].includes(m.estado)) ||
                  ids.length >= 10)
              }
              checked={ids.includes(m.id)}
              onChange={(e) =>
                onChange(
                  e.target.checked
                    ? [...ids, m.id]
                    : ids.filter((i) => i !== m.id),
                )
              }
            />
            <span>
              {m.nome}
              <small>{m.estado_rotulo}</small>
            </span>
          </label>
        ))}
      </div>
      <div className="activity-actions">
        <small>{ids.length} selecionados</small>
        <Button disabled={!page} onClick={() => setPage((p) => p - 1)}>
          Anterior
        </Button>
        <Button
          disabled={!list || (page + 1) * 30 >= list.total}
          onClick={() => setPage((p) => p + 1)}
        >
          Próxima
        </Button>
      </div>
    </fieldset>
  );
}

function ActivityEditor({
  initial,
  state,
  notify,
  busy,
  onClose,
  onSave,
  onGenerate,
}: {
  initial: {
    a?: Atividade;
    content: Conteudo;
    materiais: string[];
    proposta?: string;
    caderno?: string | null;
  };
  state: Estado;
  notify: (s: string) => void;
  busy: boolean;
  onClose: () => void;
  onSave: (c: Conteudo, b: string | null, m: string[]) => Promise<void>;
  onGenerate: (m: string[], assunto: string, caderno: string | null) => void;
}) {
  const [content, setContent] = useState(initial.content),
    [book, setBook] = useState(
      initial.a
        ? initial.a.caderno_id || ""
        : initial.caderno !== undefined
          ? initial.caderno || ""
          : state.navegacao.caderno_id || "",
    ),
    [mats, setMats] = useState(initial.materiais),
    [index, setIndex] = useState(0),
    [preview, setPreview] = useState(false);
  const [names, setNames] = useState<Record<string, string>>({});
  const q = content.exercicios[index];
  const patch = (d: Partial<Exercicio>) =>
    setContent((c) => ({
      ...c,
      exercicios: c.exercicios.map((v, i) =>
        i === index ? { ...v, ...d } : v,
      ),
    }));
  const changeFormat = (f: Formato) =>
    patch({
      formato: f,
      resposta: f === "vf" ? true : "",
      tolerancia: "0",
      alternativas:
        f === "escolha"
          ? [
              { id: crypto.randomUUID(), texto: "" },
              { id: crypto.randomUUID(), texto: "" },
            ]
          : [],
    });
  return (
    <form
      className="activity-editor"
      onSubmit={(e) => {
        e.preventDefault();
        void onSave(content, book || null, mats);
      }}
    >
      <div className="activity-heading">
        <div>
          <div className="eyebrow">
            {initial.proposta
              ? "PROPOSTA DE IA · CONFIRA O GABARITO"
              : "CRIAÇÃO MANUAL · FUNCIONA OFFLINE"}
          </div>
          <h2>{initial.a ? "Editar atividade" : "Criar atividade"}</h2>
        </div>
        <div className="activity-actions">
          <Button
            icon={Sparkles}
            disabled={busy}
            onClick={() => onGenerate(mats, content.assuntos, book || null)}
          >
            Gerar proposta com IA
          </Button>
          <Button onClick={onClose}>Cancelar edição</Button>
          <Button type="submit" variant="primary" disabled={busy}>
            Salvar atividade
          </Button>
        </div>
      </div>
      <p className="muted">
        Até 30 exercícios, 2–6 alternativas. Enunciados/respostas até 8.000
        caracteres. Ao editar, as tentativas anteriores continuam na versão
        original.
      </p>
      <div className="editor-grid">
        <Field label="Título da atividade">
          <input
            required
            maxLength={180}
            value={content.titulo}
            onChange={(e) => setContent({ ...content, titulo: e.target.value })}
          />
        </Field>
        <Field label="Caderno da atividade">
          <select value={book} onChange={(e) => setBook(e.target.value)}>
            <option value="">Geral</option>
            {state.cadernos
              .filter((c) => !c.arquivado)
              .map((c) => (
                <option key={c.id} value={c.id}>
                  {c.nome}
                </option>
              ))}
          </select>
        </Field>
        <Field label="Assuntos">
          <input
            maxLength={500}
            value={content.assuntos}
            onChange={(e) =>
              setContent({ ...content, assuntos: e.target.value })
            }
          />
        </Field>
        <Field label="Etiquetas">
          <input
            maxLength={500}
            value={content.etiquetas}
            onChange={(e) =>
              setContent({ ...content, etiquetas: e.target.value })
            }
          />
        </Field>
        <Field label="Dificuldade da atividade">
          <select
            value={content.dificuldade}
            onChange={(e) =>
              setContent({ ...content, dificuldade: e.target.value })
            }
          >
            {Object.entries(dificuldades).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Objetivo de aprendizagem">
          <input
            maxLength={1500}
            value={content.objetivo}
            onChange={(e) =>
              setContent({ ...content, objetivo: e.target.value })
            }
          />
        </Field>
      </div>
      <Field label="Descrição">
        <textarea
          rows={2}
          maxLength={3000}
          value={content.descricao}
          onChange={(e) =>
            setContent({ ...content, descricao: e.target.value })
          }
        />
      </Field>
      <div className="exercise-editor">
        <div className="activity-heading">
          <h3>
            Exercício {index + 1} de {content.exercicios.length}
          </h3>
          <div className="activity-actions">
            <Button
              disabled={content.exercicios.length >= 30}
              icon={Plus}
              onClick={() => {
                setContent({
                  ...content,
                  exercicios: [...content.exercicios, novaQuestao()],
                });
                setIndex(content.exercicios.length);
              }}
            >
              Adicionar exercício
            </Button>
            <Button
              variant="danger"
              disabled={content.exercicios.length <= 1}
              onClick={() => {
                if (
                  window.confirm(
                    "Remover este exercício do editor? As tentativas existentes não mudam.",
                  )
                ) {
                  setContent({
                    ...content,
                    exercicios: content.exercicios.filter(
                      (_, i) => i !== index,
                    ),
                  });
                  setIndex(Math.max(0, index - 1));
                }
              }}
            >
              Remover exercício
            </Button>
          </div>
        </div>
        <nav className="question-tabs" aria-label="Exercícios do editor">
          {content.exercicios.map((v, i) => (
            <button
              type="button"
              key={v.id}
              aria-current={index === i ? "step" : undefined}
              onClick={() => setIndex(i)}
            >
              {i + 1}
            </button>
          ))}
        </nav>
        <div className="editor-grid">
          <Field label="Formato do exercício">
            <select
              value={q.formato}
              onChange={(e) => changeFormat(e.target.value as Formato)}
            >
              {Object.entries(formatos).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Dificuldade do exercício">
            <select
              value={q.dificuldade}
              onChange={(e) => patch({ dificuldade: e.target.value })}
            >
              {Object.entries(dificuldades).map(([k, v]) => (
                <option key={k} value={k}>
                  {v}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <Field label="Assunto do exercício">
          <input
            maxLength={500}
            value={q.assunto}
            onChange={(e) => patch({ assunto: e.target.value })}
          />
        </Field>
        <Field label="Enunciado" hint="Markdown e fórmulas: $x^2$, $$f'(x)$$.">
          <textarea
            rows={5}
            required
            maxLength={8000}
            value={q.enunciado}
            onChange={(e) => patch({ enunciado: e.target.value })}
          />
        </Field>
        {q.formato === "escolha" ? (
          <fieldset className="alternatives-editor">
            <legend>Alternativas · marque uma correta</legend>
            {q.alternativas.map((a, i) => (
              <div className="alternative-editor" key={a.id}>
                <input
                  type="radio"
                  name="gabarito"
                  aria-label={`Alternativa ${i + 1} correta`}
                  checked={q.resposta === a.id}
                  onChange={() => patch({ resposta: a.id })}
                />
                <Field label={`Alternativa ${i + 1}`}>
                  <textarea
                    rows={2}
                    required
                    maxLength={2000}
                    value={a.texto}
                    onChange={(e) =>
                      patch({
                        alternativas: q.alternativas.map((v) =>
                          v.id === a.id ? { ...v, texto: e.target.value } : v,
                        ),
                      })
                    }
                  />
                </Field>
                <Button
                  disabled={q.alternativas.length <= 2}
                  onClick={() =>
                    patch({
                      alternativas: q.alternativas.filter((v) => v.id !== a.id),
                      resposta: q.resposta === a.id ? "" : q.resposta,
                    })
                  }
                  aria-label={`Remover alternativa ${i + 1}`}
                >
                  ×
                </Button>
              </div>
            ))}
            <Button
              disabled={q.alternativas.length >= 6}
              onClick={() =>
                patch({
                  alternativas: [
                    ...q.alternativas,
                    { id: crypto.randomUUID(), texto: "" },
                  ],
                })
              }
            >
              Adicionar alternativa
            </Button>
          </fieldset>
        ) : q.formato === "vf" ? (
          <Field label="Gabarito">
            <select
              value={String(q.resposta)}
              onChange={(e) => patch({ resposta: e.target.value === "true" })}
            >
              <option value="true">Verdadeiro</option>
              <option value="false">Falso</option>
            </select>
          </Field>
        ) : (
          <Field
            label={
              q.formato === "numerica"
                ? "Resposta numérica esperada"
                : "Resposta esperada (opcional)"
            }
            hint={
              q.formato === "aberta"
                ? "Sem gabarito: revisão manual ou feedback de IA."
                : ""
            }
          >
            <textarea
              rows={q.formato === "numerica" ? 1 : 3}
              maxLength={8000}
              required={q.formato === "numerica"}
              value={String(q.resposta || "")}
              onChange={(e) => patch({ resposta: e.target.value })}
            />
          </Field>
        )}
        {q.formato === "numerica" && (
          <Field
            label="Tolerância absoluta"
            hint="Acerto quando |resposta − gabarito| ≤ tolerância. Zero exige igualdade decimal. Sem expressões ou unidades."
          >
            <input
              required
              value={q.tolerancia || "0"}
              onChange={(e) => patch({ tolerancia: e.target.value })}
            />
          </Field>
        )}
        <Field label="Explicação da solução (opcional)">
          <textarea
            rows={3}
            maxLength={8000}
            value={q.explicacao || ""}
            onChange={(e) => patch({ explicacao: e.target.value })}
          />
        </Field>
        <fieldset className="source-picker">
          <legend>Referências deste exercício</legend>
          <p className="muted">
            IDs preservam o vínculo, inclusive quando um material é removido.
            Não envia fontes automaticamente.
          </p>
          {q.referencias.map((ref, i) => (
            <div className="editor-grid" key={i}>
              <Field label={`Fonte da referência ${i + 1}`}>
                <select
                  value={ref.material_id}
                  onChange={(e) =>
                    patch({
                      referencias: q.referencias.map((r, j) =>
                        j === i ? { ...r, material_id: e.target.value } : r,
                      ),
                    })
                  }
                >
                  {Array.from(
                    new Set([
                      ...mats,
                      ...q.referencias.map((r) => r.material_id),
                    ]),
                  ).map((id) => (
                    <option key={id} value={id}>
                      {names[id] ||
                        initial.a?.fontes.find((f) => f.id === id)?.nome ||
                        id}
                      {!mats.includes(id)
                        ? " · fonte indisponível/não selecionada"
                        : ""}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label={`Página da referência ${i + 1} (opcional)`}>
                <input
                  type="number"
                  min={1}
                  max={100000}
                  value={ref.pagina || ""}
                  onChange={(e) =>
                    patch({
                      referencias: q.referencias.map((r, j) =>
                        j === i
                          ? {
                              ...r,
                              pagina: e.target.value
                                ? Number(e.target.value)
                                : null,
                            }
                          : r,
                      ),
                    })
                  }
                />
              </Field>
              <Button
                aria-label={`Remover referência ${i + 1}`}
                onClick={() =>
                  patch({
                    referencias: q.referencias.filter((_, j) => j !== i),
                  })
                }
              >
                Remover referência
              </Button>
            </div>
          ))}
          <Button
            disabled={!mats.length || q.referencias.length >= 10}
            onClick={() =>
              patch({
                referencias: [
                  ...q.referencias,
                  { material_id: mats[0], pagina: null },
                ],
              })
            }
          >
            Adicionar referência
          </Button>
        </fieldset>
        <Button icon={Eye} onClick={() => setPreview(!preview)}>
          {preview ? "Ocultar prévia" : "Ver prévia do exercício"}
        </Button>
        {preview && (
          <article className="exercise-preview">
            <Markdown texto={q.enunciado} />
            {q.alternativas.map((a) => (
              <Markdown key={a.id} texto={a.texto} />
            ))}
            <p>Gabarito:</p>
            <Markdown texto={esperado(q)} />
            <Markdown texto={q.explicacao || ""} />
          </article>
        )}
      </div>
      <SourcePicker
        consulta={false}
        onNames={(n) => setNames((prev) => ({ ...prev, ...n }))}
        ids={mats}
        onChange={(ids) => {
          setMats(ids);
          if (ids.length < mats.length)
            notify("Confira as referências dos exercícios antes de salvar.");
        }}
      />
      <div className="dialog-actions">
        <Button type="submit" variant="primary" disabled={busy}>
          Salvar atividade
        </Button>
      </div>
    </form>
  );
}

export function Practice({
  attempt: t,
  onUpdate,
  notify,
  busy,
  onBack,
  onAI,
  onChat,
}: {
  attempt: Tentativa;
  onUpdate: (t: Tentativa) => void;
  notify: (s: string) => void;
  busy: boolean;
  onBack: () => void;
  onAI: (tipo: string) => void;
  onChat: () => void;
}) {
  const [values, setValues] = useState<Record<string, string | boolean | null>>(
      () =>
        Object.fromEntries(
          Object.entries(t.respostas).map(([id, r]) => [
            id,
            r.resposta ?? null,
          ]),
        ),
    ),
    [status, setStatus] = useState("Tudo salvo"),
    [confirmFinish, setConfirmFinish] = useState(false),
    [saving, setSaving] = useState(false);
  const pending = useRef<StudyDraft | null>(null),
    dirty = useRef(false);
  const q = t.snapshot.conteudo.exercicios[t.posicao],
    final = t.estado === "finalizada",
    editable = t.editavel && !final;
  const flush = useCallback(async () => {
    const d = pending.current;
    if (!d || !dirty.current) return;
    try {
      setStatus("Salvando…");
      const updated = await api<Tentativa>("tentativa_salvar", d);
      if (JSON.stringify(pending.current) === JSON.stringify(d)) {
        dirty.current = false;
        setStatus("Tudo salvo");
        onUpdate(updated);
      }
    } catch (e) {
      setStatus("Falha ao salvar — tente novamente");
      notify((e as Error).message);
      throw e;
    }
  }, [onUpdate, notify]);
  useEffect(() => {
    window.cadernoMatFlushStudy = flush;
    return () => {
      delete window.cadernoMatFlushStudy;
      window.cadernoMatStudyDraft = null;
    };
  }, [flush]);
  useEffect(() => {
    if (!dirty.current) return;
    const timer = setTimeout(() => {
      flush().catch(() => {});
    }, 300);
    return () => clearTimeout(timer);
  }, [values, flush]);
  const change = (v: string | boolean | null) => {
    setValues((prev) => ({ ...prev, [q.id]: v }));
    pending.current = {
      id: t.id,
      exercicio: q.id,
      resposta: v,
      posicao: t.posicao,
    };
    window.cadernoMatStudyDraft = pending.current;
    dirty.current = true;
    setStatus("Alteração não salva");
  };
  const perform = async (fn: () => Promise<void>) => {
    setSaving(true);
    try {
      await flush();
      await fn();
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setSaving(false);
    }
  };
  const move = (posicao: number) =>
    void perform(async () => {
      onUpdate(
        await api<Tentativa>("tentativa_navegar", { id: t.id, posicao }),
      );
      pending.current = null;
      window.cadernoMatStudyDraft = null;
    });
  const finish = (confirmed = false) =>
    void perform(async () => {
      if (!confirmed) {
        const blanks = t.snapshot.conteudo.exercicios.filter(
          (q) => !respondida(values[q.id]),
        ).length;
        if (blanks) {
          setConfirmFinish(true);
          return;
        }
      }
      onUpdate(
        await api<Tentativa>("tentativa_finalizar", {
          id: t.id,
          confirmado: confirmed,
        }),
      );
      setConfirmFinish(false);
      pending.current = null;
      window.cadernoMatStudyDraft = null;
      dirty.current = false;
    });
  const r = t.respostas[q.id] || {},
    correction = t.resultado[q.id];
  return (
    <div className="practice">
      <div className="activity-heading">
        <Button variant="ghost" icon={ArrowLeft} onClick={onBack}>
          Histórico da atividade
        </Button>
        <Badge>
          {final ? "Tentativa finalizada" : "Em andamento"} · v{t.versao}
        </Badge>
      </div>
      <div className="practice-title">
        <small>
          {t.snapshot.caderno} · {data(t.inicio)}
        </small>
        <h2>{t.snapshot.conteudo.titulo}</h2>
        <p>{t.snapshot.conteudo.objetivo}</p>
      </div>
      {t.versao !== t.versao_atual && (
        <p className="activity-warning">
          A atividade está na versão {t.versao_atual}. Esta tentativa preserva
          os exercícios da versão {t.versao}.
        </p>
      )}
      {!t.editavel && (
        <p className="activity-warning">
          Restaure a atividade e seu caderno para continuar. Leitura do
          histórico preservada.
        </p>
      )}
      {final ? (
        <Summary t={t} />
      ) : (
        <div className="practice-progress">
          <span>
            Exercício {t.posicao + 1} de {t.snapshot.conteudo.exercicios.length}
          </span>
          <progress value={t.resumo.respondidas} max={t.resumo.total} />
          <small role="status">{status}</small>
        </div>
      )}
      <nav className="question-tabs" aria-label="Navegar exercícios">
        {t.snapshot.conteudo.exercicios.map((v, i) => (
          <button
            type="button"
            key={v.id}
            aria-label={`Ir para exercício ${i + 1}`}
            aria-current={t.posicao === i ? "step" : undefined}
            className={respondida(values[v.id]) ? "answered" : ""}
            disabled={saving}
            onClick={() => move(i)}
          >
            {i + 1}
            {respondida(values[v.id]) && <CheckCircle2 size={12} />}
          </button>
        ))}
      </nav>
      <article className="practice-question">
        <div className="activity-tags">
          <Badge>{formatos[q.formato]}</Badge>
          <small>{q.assunto}</small>
          {correction && (
            <Badge
              kind={
                correction.estado === "correta"
                  ? "success"
                  : correction.estado === "incorreta"
                    ? "warning"
                    : "neutral"
              }
            >
              {rotulos[correction.estado]}
            </Badge>
          )}
        </div>
        <Markdown texto={q.enunciado} />
        {q.formato === "escolha" || q.formato === "vf" ? (
          <fieldset className="practice-answers">
            <legend>Sua resposta</legend>
            {(q.formato === "vf"
              ? [
                  { id: true, texto: "Verdadeiro" },
                  { id: false, texto: "Falso" },
                ]
              : q.alternativas
            ).map((a, i) => (
              <label
                className={values[q.id] === a.id ? "chosen" : ""}
                key={String(a.id)}
              >
                <input
                  type="radio"
                  name={`resposta-${q.id}`}
                  disabled={!editable}
                  checked={values[q.id] === a.id}
                  onChange={() => change(a.id)}
                />
                <span className="answer-letter">
                  {q.formato === "escolha" ? String.fromCharCode(65 + i) : ""}
                </span>
                <Markdown texto={a.texto} />
              </label>
            ))}
          </fieldset>
        ) : (
          <Field
            label="Sua resposta"
            hint={
              q.formato === "numerica"
                ? `Use decimal ou notação científica, sem unidades. Tolerância absoluta: ${q.tolerancia}.`
                : "Explique seu raciocínio. Markdown e fórmulas são aceitos."
            }
          >
            <textarea
              rows={q.formato === "numerica" ? 2 : 6}
              maxLength={8000}
              readOnly={!editable}
              value={String(values[q.id] ?? "")}
              onChange={(e) => change(e.target.value)}
            />
          </Field>
        )}
        {editable && respondida(values[q.id]) && (
          <Button variant="ghost" onClick={() => change(null)}>
            Limpar resposta
          </Button>
        )}
        {q.referencias.length > 0 && (
          <div className="activity-sources">
            {q.referencias.map((ref, i) => {
              const f = t.snapshot.fontes.find((f) => f.id === ref.material_id);
              return (
                <small key={i}>
                  Fonte: {f?.nome || ref.material_id}
                  {ref.pagina ? ` · página ${ref.pagina}` : ""}
                  {f?.disponivel === false ? " · indisponível" : ""}
                </small>
              );
            })}
          </div>
        )}
        <div className="practice-tools">
          <Button
            icon={Lightbulb}
            disabled={!editable || busy || saving}
            onClick={() => onAI("dica")}
          >
            Pedir dica com IA
          </Button>
          <Button
            icon={Eye}
            disabled={
              !editable || r.revelada || saving || !q.solucao_disponivel
            }
            onClick={() =>
              void perform(async () =>
                onUpdate(
                  await api<Tentativa>("tentativa_revelar", {
                    id: t.id,
                    exercicio: q.id,
                  }),
                ),
              )
            }
          >
            Revelar solução
          </Button>
          <Button
            icon={Sparkles}
            disabled={
              !t.editavel || busy || saving || !respondida(values[q.id])
            }
            onClick={() => onAI("feedback")}
          >
            Feedback com IA
          </Button>
          <Button disabled={!t.editavel || busy || saving} onClick={onChat}>
            Pedir ajuda em novo chat
          </Button>
        </div>
        {(final || r.revelada) && (
          <section className="practice-solution">
            <h3>
              Solução registrada{" "}
              {r.revelada && !final ? "· revelação registrada" : ""}
            </h3>
            <Markdown texto={esperado(q)} />
            <Markdown texto={q.explicacao || ""} />
            {correction && <p className="muted">{correction.justificativa}</p>}
          </section>
        )}
        {r.dicas?.map((f, i) => (
          <div className="practice-feedback" key={`d${i}`}>
            <Badge>
              Dica {i + 1} · {f.provedor} / {f.modelo}
            </Badge>
            <Markdown texto={f.texto} />
          </div>
        ))}
        {r.feedbacks?.map((f, i) => (
          <div className="practice-feedback" key={`f${i}`}>
            <Badge>
              Feedback de IA · {f.provedor} / {f.modelo}
            </Badge>
            <p className="muted">
              Orientação pedagógica, sem nota ou verificação definitiva.
              Resposta avaliada: {String(f.resposta_avaliada ?? "Em branco")}
            </p>
            {f.resposta_avaliada !== values[q.id] && (
              <p className="activity-warning">
                Este feedback avaliou uma resposta anterior.
              </p>
            )}
            <Markdown texto={f.texto} />
          </div>
        ))}
        {r.revisao && (
          <div className="practice-feedback">
            <Badge>Revisão manual · {r.revisao.avaliacao}</Badge>
            <Markdown texto={r.revisao.texto} />
          </div>
        )}
        {final &&
          t.editavel &&
          correction &&
          !["correta", "incorreta"].includes(correction.estado) && (
            <ManualReview
              key={q.id}
              t={t}
              q={q}
              onSave={(d) =>
                void perform(async () =>
                  onUpdate(await api<Tentativa>("tentativa_revisar", d)),
                )
              }
            />
          )}
      </article>
      <footer className="practice-footer">
        <div className="activity-actions">
          <Button
            icon={ChevronLeft}
            disabled={t.posicao === 0 || saving}
            onClick={() => move(t.posicao - 1)}
          >
            Exercício anterior
          </Button>
          <Button
            disabled={
              t.posicao >= t.snapshot.conteudo.exercicios.length - 1 || saving
            }
            onClick={() => move(t.posicao + 1)}
          >
            Próximo exercício <ChevronRight size={17} />
          </Button>
        </div>
        {!final && (
          <Button
            variant="primary"
            disabled={!t.editavel || saving || busy}
            onClick={() => finish()}
          >
            Finalizar tentativa
          </Button>
        )}
        {!final && status.startsWith("Falha") && (
          <Button onClick={() => void perform(async () => {})}>
            Tentar salvar novamente
          </Button>
        )}
      </footer>
      {confirmFinish && (
        <Dialog
          title="Finalizar com questões em branco?"
          onClose={() => setConfirmFinish(false)}
        >
          <p>
            {
              t.snapshot.conteudo.exercicios.filter(
                (q) => !respondida(values[q.id]),
              ).length
            }{" "}
            questão(ões) sem resposta. Ficarão como não avaliadas e não serão
            contadas como erros. Suas respostas serão preservadas.
          </p>
          <div className="dialog-actions">
            <Button onClick={() => setConfirmFinish(false)}>
              Continuar respondendo
            </Button>
            <Button
              variant="primary"
              disabled={saving}
              onClick={() => finish(true)}
            >
              Finalizar mesmo assim
            </Button>
          </div>
        </Dialog>
      )}
    </div>
  );
}
function ManualReview({
  t,
  q,
  onSave,
}: {
  t: Tentativa;
  q: Exercicio;
  onSave: (d: Record<string, unknown>) => void;
}) {
  const [note, setNote] = useState(t.respostas[q.id]?.revisao?.texto || ""),
    [evaluation, setEvaluation] = useState("observacao");
  return (
    <div className="manual-review">
      <h3>Revisão manual</h3>
      <Field label="Avaliação manual">
        <select
          value={evaluation}
          onChange={(e) => setEvaluation(e.target.value)}
        >
          <option value="observacao">Somente observação</option>
          <option value="adequada">Resposta adequada</option>
          <option value="revisar">Precisa revisar</option>
        </select>
      </Field>
      <Field label="Observação manual">
        <textarea
          rows={3}
          maxLength={8000}
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
      </Field>
      <Button
        disabled={!note.trim()}
        onClick={() =>
          onSave({
            id: t.id,
            exercicio: q.id,
            texto: note,
            avaliacao: evaluation,
          })
        }
      >
        Salvar revisão manual
      </Button>
    </div>
  );
}
function GenerationForm({
  tipo,
  origin,
  state,
  attempt,
  onClose,
  onPreview,
}: {
  tipo: string;
  origin: {
    materiais: string[];
    origem_chat?: string;
    assunto?: string;
    caderno?: string | null;
  };
  state: Estado;
  attempt: Tentativa | null;
  onClose: () => void;
  onPreview: (d: Record<string, unknown>) => void;
}) {
  const [subject, setSubject] = useState(origin.assunto || ""),
    [objective, setObjective] = useState(""),
    [count, setCount] = useState(3),
    [dif, setDif] = useState("basica"),
    [forms, setForms] = useState<string[]>(["aberta"]),
    [mats, setMats] = useState(tipo === "geracao" ? origin.materiais : []),
    [book, setBook] = useState(
      origin.caderno !== undefined
        ? origin.caderno || ""
        : state.navegacao.caderno_id || "",
    );
  return (
    <Dialog
      title={
        tipo === "geracao"
          ? "Gerar proposta de atividade"
          : tipo === "dica"
            ? "Pedir uma dica"
            : "Pedir feedback"
      }
      wide
      onClose={onClose}
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onPreview(
            tipo === "geracao"
              ? {
                  tipo,
                  caderno: book || null,
                  assunto: subject,
                  objetivo: objective,
                  quantidade: count,
                  dificuldade: dif,
                  formatos: forms,
                  materiais: mats,
                  origem_chat: origin.origem_chat,
                }
              : {
                  tipo,
                  tentativa: attempt?.id,
                  exercicio:
                    attempt?.snapshot.conteudo.exercicios[attempt.posicao].id,
                  materiais: mats,
                },
          );
        }}
      >
        {tipo === "geracao" ? (
          <>
            <div className="editor-grid">
              <Field label="Caderno da geração">
                <select value={book} onChange={(e) => setBook(e.target.value)}>
                  <option value="">Geral</option>
                  {state.cadernos
                    .filter((c) => !c.arquivado)
                    .map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.nome}
                      </option>
                    ))}
                </select>
              </Field>
              <Field label="Assunto para gerar">
                <input
                  required
                  maxLength={500}
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                />
              </Field>
              <Field
                label={
                  state.config.provedor === "ollama"
                    ? "Quantidade de exercícios (1–3)"
                    : "Quantidade de exercícios (1–10)"
                }
              >
                <input
                  type="number"
                  min={1}
                  max={state.config.provedor === "ollama" ? 3 : 10}
                  required
                  value={count}
                  onChange={(e) => setCount(Number(e.target.value))}
                />
              </Field>
              <Field label="Dificuldade da geração">
                <select value={dif} onChange={(e) => setDif(e.target.value)}>
                  {Object.entries(dificuldades).map(([k, v]) => (
                    <option key={k} value={k}>
                      {v}
                    </option>
                  ))}
                </select>
              </Field>
            </div>
            <Field label="Objetivo da geração">
              <textarea
                rows={2}
                maxLength={1500}
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
              />
            </Field>
            <fieldset className="generation-formats">
              <legend>Formatos desejados</legend>
              {Object.entries(formatos).map(([k, v]) => (
                <label key={k}>
                  <input
                    type="checkbox"
                    checked={forms.includes(k)}
                    onChange={(e) =>
                      setForms(
                        e.target.checked
                          ? [...forms, k]
                          : forms.filter((f) => f !== k),
                      )
                    }
                  />
                  {v}
                </label>
              ))}
            </fieldset>
          </>
        ) : (
          <p className="muted">
            A consulta inclui apenas este exercício e sua resposta. Feedback
            pode discutir o gabarito; dicas solicitam o próximo passo sem
            solução completa. A IA pode errar.
          </p>
        )}
        <SourcePicker ids={mats} onChange={setMats} />
        <div className="dialog-actions">
          <Button
            type="submit"
            variant="primary"
            disabled={tipo === "geracao" && !forms.length}
          >
            Conferir dados enviados
          </Button>
        </div>
      </form>
    </Dialog>
  );
}
function JobPreview({ job }: { job: Job }) {
  const p = job.previa;
  return (
    <div className="job-preview">
      <div className="activity-tags">
        <Badge>{p.provedor}</Badge>
        <Badge>{p.modelo}</Badge>
        <Badge>{job.estado}</Badge>
      </div>
      <p className="muted">
        Nenhum arquivo original, outro chat ou chave entra nos dados abaixo. A
        confirmação usa exatamente esta prévia.{" "}
        {p.local
          ? "Processamento somente no Ollama deste computador, sem fallback online."
          : "A API pode ter cotas ou cobrança conforme sua conta."}
      </p>
      {p.aviso && (
        <p role="status" className="activity-warning">
          {p.aviso}
        </p>
      )}
      {p.orcamento && (
        <p className="hint">
          Contexto local: {p.orcamento.contexto} tokens; entrada estimada:{" "}
          {p.orcamento.entrada_estimada}; reserva de saída:{" "}
          {p.orcamento.reserva_saida}; margem: {p.orcamento.margem}.{" "}
          {p.orcamento.metodo}. Trechos omitidos: {p.orcamento.trechos_omitidos}
          , abreviados: {p.orcamento.trechos_abreviados}.
        </p>
      )}
      <details open>
        <summary>Contexto pedagógico</summary>
        <pre>
          {p.pedagogia || "Geral, sem configuração adicional de caderno."}
        </pre>
      </details>
      <details open>
        <summary>Solicitação</summary>
        <pre>{JSON.stringify(p.pedido, null, 2)}</pre>
        <details>
          <summary>Instruções da tarefa</summary>
          <pre>{p.tarefa}</pre>
        </details>
      </details>
      <details open>
        <summary>Trechos documentais autorizados ({p.fontes.length})</summary>
        {p.recuperacao?.metodo && (
          <p role="status">
            Recuperação: {p.recuperacao.metodo}. {p.recuperacao.aviso}
          </p>
        )}
        {p.fontes.map((f) => (
          <article key={f.referencia}>
            <strong>
              {f.referencia} · {f.nome}
              {f.pagina ? ` · página ${f.pagina}` : ""}
            </strong>
            <small>{f.selecao}</small>
            <pre>{f.texto}</pre>
          </article>
        ))}
        {!p.fontes.length && (
          <p>
            Sem texto documental. A IA usará conhecimento geral e o enunciado.
          </p>
        )}
      </details>
      {job.estado === "concluida" && job.tipo === "geracao" && (
        <p className="activity-warning">
          A proposta foi validada estruturalmente. Confira enunciados e
          gabaritos no editor: isso não comprova a correção matemática da IA.
          Nada foi salvo como atividade ainda.
        </p>
      )}
    </div>
  );
}
