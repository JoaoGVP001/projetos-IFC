import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "./bridge";
import { Button, Field, Loading, Empty, Badge } from "./ui";
import {
  Plus,
  ArrowUp,
  ArrowDown,
  Trash2,
  FileDown,
  BookOpen,
} from "lucide-react";
import { StudyDocument } from "./StudyDocument";
import type { Page, PageContent, PageJob, PageRender } from "./pages-model";
import type { Estado } from "./model";

function ContentEditor({
  value,
  onChange,
  disabled = false,
}: {
  value: PageContent;
  onChange: (v: PageContent) => void;
  disabled?: boolean;
}) {
  const section = (id: string, change: Record<string, unknown>) =>
    onChange({
      ...value,
      secoes: value.secoes.map((s) => (s.id === id ? { ...s, ...change } : s)),
    });
  return (
    <div className="page-editor">
      <Field label="Título da página">
        <input
          aria-label="Título da página"
          maxLength={180}
          disabled={disabled}
          value={value.titulo}
          onChange={(e) => onChange({ ...value, titulo: e.target.value })}
        />
      </Field>
      <Field label="Assunto">
        <input
          aria-label="Assunto da página"
          maxLength={500}
          disabled={disabled}
          value={value.assunto}
          onChange={(e) => onChange({ ...value, assunto: e.target.value })}
        />
      </Field>
      <Field label="Papel">
        <select
          aria-label="Fundo da página"
          disabled={disabled}
          value={value.fundo}
          onChange={(e) =>
            onChange({
              ...value,
              fundo: e.target.value as PageContent["fundo"],
            })
          }
        >
          <option value="branco">Branco</option>
          <option value="pautado">Pautado</option>
          <option value="quadriculado">Quadriculado</option>
        </select>
      </Field>
      {value.secoes.map((s, i) => (
        <section className="page-section" key={s.id}>
          <div className="page-actions">
            <Badge>
              {s.recurso
                ? "Contém resultado local preservado"
                : s.origem === "ia"
                  ? "Proposta da IA · revise"
                  : "Texto do usuário"}
            </Badge>
            <Button
              icon={ArrowUp}
              aria-label={`Subir seção ${i + 1}`}
              disabled={disabled || i === 0}
              onClick={() => {
                const ss = [...value.secoes];
                [ss[i - 1], ss[i]] = [ss[i], ss[i - 1]];
                onChange({ ...value, secoes: ss });
              }}
            />
            <Button
              icon={ArrowDown}
              aria-label={`Descer seção ${i + 1}`}
              disabled={disabled || i === value.secoes.length - 1}
              onClick={() => {
                const ss = [...value.secoes];
                [ss[i + 1], ss[i]] = [ss[i], ss[i + 1]];
                onChange({ ...value, secoes: ss });
              }}
            />
            <Button
              icon={Trash2}
              aria-label={`Remover seção ${i + 1}`}
              disabled={disabled || value.secoes.length === 1}
              onClick={() =>
                onChange({
                  ...value,
                  secoes: value.secoes.filter((x) => x.id !== s.id),
                })
              }
            />
          </div>
          <Field label={`Título da seção ${i + 1}`}>
            <input
              aria-label={`Título da seção ${i + 1}`}
              maxLength={180}
              value={s.titulo}
              disabled={disabled}
              onChange={(e) => section(s.id, { titulo: e.target.value })}
            />
          </Field>
          <Field
            label={
              s.recurso
                ? `Notas da seção ${i + 1}`
                : `Conteúdo da seção ${i + 1}`
            }
            hint="Markdown e fórmulas $...$ ou $$...$$. Imagens são inseridas pelos resultados locais."
          >
            <textarea
              aria-label={`Conteúdo da seção ${i + 1}`}
              value={s.texto}
              maxLength={15000}
              disabled={disabled}
              onChange={(e) =>
                section(s.id, { texto: e.target.value, origem: "usuario" })
              }
            />
          </Field>
          {s.recurso && (
            <p className="muted">
              O resultado original é mantido na visualização. Suas notas não
              alteram o cálculo.
            </p>
          )}
        </section>
      ))}
      <Button
        icon={Plus}
        disabled={disabled || value.secoes.length >= 40}
        onClick={() =>
          onChange({
            ...value,
            secoes: [
              ...value.secoes,
              {
                id: crypto.randomUUID(),
                titulo: "Nova seção",
                texto: "",
                origem: "usuario",
              },
            ],
          })
        }
      >
        Adicionar seção
      </Button>
    </div>
  );
}
export function Pages({
  state,
  notify,
  seed,
}: {
  state: Estado;
  notify: (s: string) => void;
  seed?: string | null;
}) {
  const book = state.navegacao.caderno_id;
  const [list, setList] = useState<{
    itens: { id: string; titulo: string; assunto: string; versao: number }[];
    total: number;
    pagina: number;
  }>({ itens: [], total: 0, pagina: 0 });
  const [search, setSearch] = useState(""),
    [archive, setArchive] = useState(false),
    [offset, setOffset] = useState(0);
  const [page, setPage] = useState<Page | null>(null),
    [content, setContent] = useState<PageContent | null>(null),
    [status, setStatus] = useState("Tudo salvo"),
    [busy, setBusy] = useState(false),
    [preview, setPreview] = useState(false),
    [history, setHistory] = useState<PageRender | null>(null),
    [version, setVersion] = useState(0),
    [jobs, setJobs] = useState<PageJob[]>([]),
    [sources, setSources] = useState<{
      calculos: { id: string; titulo: string; versao: string }[];
      materiais: { id: string; nome: string; estado: string }[];
    }>({ calculos: [], materiais: [] }),
    [calc, setCalc] = useState(""),
    [chosen, setChosen] = useState<string[]>([]),
    [materials, setMaterials] = useState<string[]>([]),
    [proposal, setProposal] = useState<PageJob | null>(null),
    [proposalContent, setProposalContent] = useState<PageContent | null>(null);
  const draft = useRef<Window["cadernoMatPageDraft"]>(null),
    dirty = useRef(false),
    chain = useRef<Promise<void>>(Promise.resolve()),
    current = useRef<Page | null>(null),
    lastBook = useRef(book);
  current.current = page;
  const refreshList = useCallback(async () => {
    setList(
      await api("paginas", {
        caderno: book,
        busca: search,
        arquivadas: archive,
        pagina: offset,
      }),
    );
  }, [book, search, archive, offset]);
  useEffect(() => {
    const timer = setTimeout(
      () => void refreshList().catch((e) => notify(e.message)),
      180,
    );
    return () => clearTimeout(timer);
  }, [refreshList, state.revisao]);
  const load = async (id: string) => {
    const p = await api<Page>("pagina_obter", { id });
    setPage(p);
    current.current = p;
    setContent(p.rascunho);
    draft.current = { id: p.id, conteudo: p.rascunho, revisao: p.revisao };
    window.cadernoMatPageDraft = draft.current;
    dirty.current = false;
    setStatus("Tudo salvo");
    setHistory(null);
    setVersion(p.versao);
    setChosen([]);
    setMaterials([]);
    setProposal(null);
    setProposalContent(null);
    setPreview(false);
    await api("pagina_navegar", { id });
    setSources(await api("pagina_fontes", { id }));
    setJobs(await api("pagina_jobs", { id }));
  };
  const flush = useCallback(() => {
    const save = async () => {
      while (dirty.current && draft.current) {
        const d = structuredClone(draft.current);
        setStatus("Salvando…");
        const p = await api<Page>("pagina_rascunho", d);
        if (draft.current?.id !== d.id) return;
        draft.current.revisao = p.revisao;
        window.cadernoMatPageDraft = draft.current;
        if (
          JSON.stringify(draft.current.conteudo) === JSON.stringify(d.conteudo)
        ) {
          dirty.current = false;
          setPage(p);
          setStatus("Tudo salvo");
        }
      }
    };
    chain.current = chain.current.catch(() => {}).then(save);
    return chain.current;
  }, []);
  useEffect(() => {
    window.cadernoMatFlushPage = flush;
    return () => {
      window.cadernoMatFlushPage = undefined;
    };
  }, [flush]);
  const safe = async (fn: () => Promise<void>) => {
    setBusy(true);
    try {
      await flush();
      await fn();
    } catch (e) {
      setStatus("Não foi possível concluir");
      notify((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  useEffect(() => {
    if (!page) return;
    const timer = setTimeout(
      () =>
        void flush().catch((e) => {
          setStatus("Falha ao salvar; alterações mantidas na tela");
          notify(e.message);
        }),
      550,
    );
    return () => clearTimeout(timer);
  }, [content, flush]);
  useEffect(() => {
    if (lastBook.current !== book) {
      lastBook.current = book;
      void safe(async () => {
        setPage(null);
        setContent(null);
        draft.current = null;
        window.cadernoMatPageDraft = null;
        await api("pagina_navegar", { id: null });
      });
    }
  }, [book]);
  useEffect(() => {
    const id = seed || state.pagina;
    if (id && !page)
      void safe(async () => {
        const p = await api<Page>("pagina_obter", { id });
        if (p.caderno_id === book) await load(id);
      });
  }, [seed]);
  useEffect(() => {
    if (!page) return;
    let live = true;
    const timer = setInterval(
      () =>
        void api<PageJob[]>("pagina_jobs", { id: page.id })
          .then((js) => {
            if (!live) return;
            setJobs(js);
            setProposal((j) => {
              if (!j) return null;
              const fresh = js.find((x) => x.id === j.id) || j;
              if (
                fresh.estado === "concluida" &&
                fresh.resultado &&
                !proposalContent
              )
                setProposalContent(fresh.resultado);
              return fresh;
            });
          })
          .catch((e) => notify(e.message)),
      700,
    );
    return () => {
      live = false;
      clearInterval(timer);
    };
  }, [page?.id, proposalContent]);
  const change = (v: PageContent) => {
    setContent(v);
    setHistory(null);
    if (draft.current) {
      draft.current.conteudo = v;
      dirty.current = true;
      window.cadernoMatPageDraft = draft.current;
    }
    setStatus("Alterações pendentes");
  };
  const bookArchived = !!state.cadernos.find((b) => b.id === book)?.arquivado;
  const editable = !!page?.editavel && !busy;
  const rendered = useMemo(
    () =>
      history ||
      (page && content
        ? { ...page.render, conteudo: content, versao: "rascunho" }
        : null),
    [history, page?.render, content],
  );
  const exports = jobs.filter((j) => j.tipo === "exportacao");
  return (
    <div className="pages-area">
      <header className="page-actions">
        <div>
          <h1>Páginas de estudo</h1>
          <p className="muted">
            Resoluções editáveis, versões e folhas para impressão.
          </p>
        </div>
        <Button
          icon={Plus}
          disabled={busy || bookArchived}
          onClick={() =>
            void safe(async () => {
              const p = await api<Page>("pagina_criar", { caderno: book });
              await load(p.id);
              await refreshList();
            })
          }
        >
          Nova página
        </Button>
      </header>
      {!page ? (
        <>
          <div className="page-actions">
            <input
              aria-label="Buscar páginas"
              placeholder="Buscar por título, assunto ou texto"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setOffset(0);
              }}
            />
            <label>
              <input
                type="checkbox"
                checked={archive}
                onChange={(e) => {
                  setArchive(e.target.checked);
                  setOffset(0);
                }}
              />{" "}
              Arquivadas
            </label>
          </div>
          {!list.itens.length ? (
            <Empty icon={BookOpen} title="Nenhuma página encontrada">
              Crie uma página ou escolha uma mensagem/resultados do chat.
            </Empty>
          ) : (
            <div className="page-list">
              {list.itens.map((p) => (
                <Button key={p.id} onClick={() => void safe(() => load(p.id))}>
                  <strong>{p.titulo}</strong>
                  <span>
                    {p.assunto} · versão {p.versao || "rascunho"}
                  </span>
                </Button>
              ))}
            </div>
          )}
          {list.total > 30 && (
            <div className="page-actions">
              <Button
                disabled={!list.pagina}
                onClick={() => setOffset((x) => x - 1)}
              >
                Anterior
              </Button>
              <span>{list.pagina + 1}</span>
              <Button
                disabled={(list.pagina + 1) * 30 >= list.total}
                onClick={() => setOffset((x) => x + 1)}
              >
                Próxima
              </Button>
            </div>
          )}
        </>
      ) : (
        <>
          <div className="page-actions">
            <Button
              disabled={busy}
              onClick={() =>
                void safe(async () => {
                  setPage(null);
                  setContent(null);
                  draft.current = null;
                  window.cadernoMatPageDraft = null;
                  await api("pagina_navegar", { id: null });
                  await refreshList();
                })
              }
            >
              Voltar às páginas
            </Button>
            <span role="status">{status}</span>
            <Button
              variant="primary"
              disabled={!editable}
              onClick={() =>
                void safe(async () => {
                  const p = await api<Page>("pagina_salvar", { id: page.id });
                  setPage(p);
                  setVersion(p.versao);
                  notify(
                    "Versão salva. Rascunho e exportações anteriores preservados.",
                  );
                })
              }
            >
              Salvar versão
            </Button>
            <Button onClick={() => setPreview((x) => !x)}>
              {preview ? "Editar página" : "Visualizar folhas"}
            </Button>
            <Button
              disabled={busy || bookArchived}
              onClick={() =>
                void safe(async () => {
                  const p = await api<Page>("pagina_acao", {
                    id: page.id,
                    acao: "arquivar",
                    valor: !page.arquivada,
                  });
                  setPage(p);
                })
              }
            >
              {page.arquivada ? "Restaurar página" : "Arquivar página"}
            </Button>
            <Button
              disabled={busy || bookArchived}
              onClick={() =>
                void safe(async () => {
                  const p = await api<Page>("pagina_acao", {
                    id: page.id,
                    acao: "duplicar",
                  });
                  await load(p.id);
                })
              }
            >
              Duplicar página
            </Button>
          </div>
          <details>
            <summary>Origem da página</summary>
            {page.origens.length ? (
              <ul>
                {(
                  page.origens as {
                    tipo: string;
                    id: string | number;
                    titulo: string;
                    versao?: number;
                    questao?: string;
                  }[]
                ).map((o, i) => (
                  <li key={i}>
                    {o.titulo} · {o.tipo} · registro {String(o.id).slice(0, 8)}
                    {o.versao ? ` · versão ${o.versao}` : ""}
                    {o.questao ? ` · questão ${o.questao}` : ""}
                  </li>
                ))}
              </ul>
            ) : (
              <p>Página criada manualmente neste caderno.</p>
            )}
          </details>
          <details>
            <summary>Versões, exportação e biblioteca</summary>
            <div className="page-actions">
              <select
                aria-label="Versão da página"
                value={version}
                onChange={(e) => setVersion(Number(e.target.value))}
              >
                <option value={0}>Escolha uma versão salva</option>
                {page.versoes.map((v) => (
                  <option value={v.versao} key={v.versao}>
                    Versão {v.versao} ·{" "}
                    {new Date(v.criado.replace(" ", "T") + "Z").toLocaleString(
                      "pt-BR",
                    )}
                  </option>
                ))}
              </select>
              <Button
                disabled={!version || busy}
                onClick={() =>
                  void safe(async () => {
                    setHistory(
                      await api("pagina_versao", {
                        id: page.id,
                        versao: version,
                      }),
                    );
                    setPreview(true);
                  })
                }
              >
                Visualizar versão
              </Button>
              <Button
                disabled={!editable || !version}
                onClick={() =>
                  void safe(async () => {
                    const p = await api<Page>("pagina_acao", {
                      id: page.id,
                      acao: "restaurar_versao",
                      versao: version,
                      revisao: draft.current!.revisao,
                    });
                    await load(p.id);
                  })
                }
              >
                Restaurar no rascunho
              </Button>
              <Button
                icon={FileDown}
                disabled={
                  !version ||
                  busy ||
                  exports.some((j) => j.estado === "executando")
                }
                onClick={() =>
                  void safe(async () => {
                    const j = await api<PageJob>("pagina_exportar", {
                      id: page.id,
                      versao: version,
                      refazer: true,
                    });
                    setJobs((x) => [j, ...x]);
                  })
                }
              >
                Gerar PDF e PNG
              </Button>
              <Button
                icon={BookOpen}
                disabled={!editable || !version}
                onClick={() =>
                  void safe(async () => {
                    await api("pagina_material", {
                      id: page.id,
                      versao: version,
                      revisada: true,
                    });
                    notify(
                      "Versão revisada adicionada à biblioteca como texto com origem preservada. Nenhuma fonte foi selecionada automaticamente.",
                    );
                  })
                }
              >
                Adicionar versão revisada à biblioteca
              </Button>
            </div>
            <p className="muted">
              A exportação usa a versão escolhida. Alterações posteriores do
              rascunho não entram nesses arquivos.
            </p>
            {exports.map((j) => (
              <div className="page-export" key={j.id}>
                <span>
                  Versão {j.versao} · {j.estado}
                  {j.manifesto ? ` · ${j.manifesto.folhas} folhas` : ""}
                </span>
                {j.estado === "executando" ? (
                  <>
                    <Loading>Compondo PDF e imagens localmente…</Loading>
                    <Button
                      onClick={() =>
                        void api("pagina_cancelar", { id: j.id }).catch((e) =>
                          notify(e.message),
                        )
                      }
                    >
                      Cancelar exportação
                    </Button>
                  </>
                ) : j.estado === "concluida" ? (
                  <>
                    <Button
                      onClick={() =>
                        void api("pagina_copiar", { id: j.id, formato: "pdf" })
                          .then(
                            (r: any) =>
                              r.exportado &&
                              notify("PDF salvo no destino escolhido."),
                          )
                          .catch((e) => notify(e.message))
                      }
                    >
                      Salvar PDF no computador
                    </Button>
                    <Button
                      onClick={() =>
                        void api("pagina_copiar", { id: j.id, formato: "png" })
                          .then(
                            (r: any) =>
                              r.exportado &&
                              notify(`${r.arquivos} folhas PNG salvas.`),
                          )
                          .catch((e) => notify(e.message))
                      }
                    >
                      Salvar folhas PNG
                    </Button>
                  </>
                ) : (
                  <p role="alert">{j.erro}</p>
                )}
              </div>
            ))}
          </details>
          {!preview && (
            <>
              <ContentEditor
                value={content!}
                onChange={change}
                disabled={!editable}
              />
              <div className="page-actions">
                <select
                  aria-label="Resultado matemático para inserir"
                  value={calc}
                  onChange={(e) => setCalc(e.target.value)}
                >
                  <option value="">Escolha um resultado deste caderno</option>
                  {sources.calculos.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.titulo} · {c.versao} · {c.id.slice(0, 8)}
                    </option>
                  ))}
                </select>
                <Button
                  disabled={!calc || !editable}
                  onClick={() =>
                    void safe(async () => {
                      const p = await api<Page>("pagina_calculo", {
                        id: page.id,
                        calculo: calc,
                      });
                      await load(p.id);
                    })
                  }
                >
                  Inserir resultado local
                </Button>
              </div>
            </>
          )}
          {preview && rendered && (
            <div className="paper-viewport">
              <StudyDocument data={rendered} />
            </div>
          )}
          {!preview && (
            <details className="page-ai">
              <summary>Organizar com ajuda da IA</summary>
              <p>
                Escolha as seções e os materiais. A prévia mostra o provedor e
                tudo que será enviado. O rascunho muda somente ao aplicar a
                proposta.
              </p>
              {content!.secoes.map((s) => (
                <label key={s.id}>
                  <input
                    type="checkbox"
                    checked={chosen.includes(s.id)}
                    disabled={busy || proposal?.estado === "executando"}
                    onChange={(e) =>
                      setChosen((x) =>
                        e.target.checked
                          ? [...x, s.id]
                          : x.filter((id) => id !== s.id),
                      )
                    }
                  />
                  {s.titulo || "Seção sem título"}
                </label>
              ))}
              {sources.materiais.map((m) => (
                <label key={m.id}>
                  <input
                    type="checkbox"
                    checked={materials.includes(m.id)}
                    disabled={busy || proposal?.estado === "executando"}
                    onChange={(e) =>
                      setMaterials((x) =>
                        e.target.checked
                          ? [...x, m.id]
                          : x.filter((id) => id !== m.id),
                      )
                    }
                  />
                  {m.nome} · {m.estado}
                </label>
              ))}
              <Button
                disabled={
                  !chosen.length ||
                  !editable ||
                  proposal?.estado === "executando"
                }
                onClick={() =>
                  void safe(async () => {
                    setProposalContent(null);
                    setProposal(
                      await api("pagina_previa", {
                        id: page.id,
                        secoes: chosen,
                        materiais: materials,
                      }),
                    );
                  })
                }
              >
                Preparar proposta de página
              </Button>
              {proposal?.previa && (
                <>
                  <strong>{String(proposal.previa.destino)}</strong>
                  <details>
                    <summary>Dados e instruções que serão enviados</summary>
                    <pre>
                      {proposal.previa.preparada.instrucoes +
                        "\n\n" +
                        proposal.previa.preparada.pergunta}
                    </pre>
                  </details>
                </>
              )}
              {proposal?.estado === "previa" && (
                <Button
                  disabled={!editable}
                  onClick={() =>
                    void safe(async () => {
                      setProposal(
                        await api("pagina_consultar", { id: proposal.id }),
                      );
                    })
                  }
                >
                  Pedir organização à IA
                </Button>
              )}
              {proposal?.estado === "executando" && (
                <>
                  <Loading>Aguardando o provedor escolhido…</Loading>
                  <Button
                    onClick={() =>
                      void api("pagina_cancelar", { id: proposal.id }).catch(
                        (e) => notify(e.message),
                      )
                    }
                  >
                    Cancelar proposta
                  </Button>
                </>
              )}
              {proposal?.erro && <p role="alert">{proposal.erro}</p>}
              {proposalContent && proposal?.estado === "concluida" && (
                <>
                  <h2>Proposta editável · revise antes de aplicar</h2>
                  <ContentEditor
                    value={proposalContent}
                    onChange={setProposalContent}
                  />
                  <Button
                    disabled={!editable}
                    onClick={() =>
                      void safe(async () => {
                        const p = await api<Page>("pagina_aceitar", {
                          id: page.id,
                          trabalho: proposal.id,
                          conteudo: proposalContent,
                        });
                        await load(p.id);
                        notify(
                          "Proposta aplicada ao rascunho. Revise e salve uma versão.",
                        );
                      })
                    }
                  >
                    Aplicar proposta ao rascunho
                  </Button>
                </>
              )}
            </details>
          )}
        </>
      )}
    </div>
  );
}
