import { BuscaSemantica } from "./BuscaSemantica";
import { MathTools, MathCard } from "./MathTools";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import {
  Sigma,
  ChartNoAxesCombined,
  ClipboardList,
  BookOpen,
  MessageSquare,
  Plus,
  Search,
  PanelLeftClose,
  PanelLeftOpen,
  Settings,
  Sun,
  Moon,
  Archive,
  Pin,
  Pencil,
  Trash2,
  ArrowUp,
  ArrowDown,
  ArrowRight,
  Paperclip,
  Link,
  FileText,
  Image as ImageIcon,
  Send,
  Copy,
  ExternalLink,
  RotateCcw,
  Library,
  CheckCircle2,
  AlertCircle,
  Eye,
  ChevronLeft,
  ChevronRight,
  Check,
  X,
} from "lucide-react";
import { api } from "./bridge";
import type {
  Caderno,
  Chat,
  Estado,
  Material,
  Filtros,
  ListaMateriais,
  Detalhe,
  Previa,
} from "./model";
import {
  Button,
  Badge,
  Empty,
  Dialog,
  Field,
  Menu,
  Loading,
  copiar,
} from "./ui";
import { Markdown } from "./Markdown";
import { Activities } from "./Activities";
import { ConfigForm, nomeProvedor } from "./ConfigIA";

const preferencias: Record<string, string> = {
  completa: "Explicação completa",
  dicas: "Dicas progressivas",
  correcao: "Correção orientada",
};
const modos = ["Resolver com IA", "Explicar", "Corrigir", "Resolver"];
const bytes = (n: number) =>
  n >= 1048576
    ? `${(n / 1048576).toFixed(1)} MB`
    : `${(n / 1024).toFixed(1)} KB`;
type Modal =
  | { tipo: "caderno"; item?: Caderno }
  | { tipo: "chat"; item: Chat; acao: "renomear" | "mover" }
  | {
      tipo: "confirmar";
      titulo: string;
      descricao: string;
      operacao: string;
      dados: Record<string, unknown>;
    }
  | { tipo: "link" }
  | { tipo: "matematica"; proposta?: string }
  | { tipo: "config" }
  | { tipo: "material"; item: Material }
  | { tipo: "detalhe"; id: string }
  | { tipo: "previa" };

export default function App() {
  const [state, setState] = useState<Estado | null>(null),
    [erro, setErro] = useState(""),
    [toast, setToast] = useState(""),
    [view, setView] = useState<"chat" | "materiais" | "atividades">("chat"),
    [busca, setBusca] = useState(""),
    [archBooks, setArchBooks] = useState(false),
    [modal, setModal] = useState<Modal | null>(null),
    [working, setWorking] = useState(false),
    [draft, setDraft] = useState(""),
    [modo, setModo] = useState("Resolver com IA");
  const [studySeed, setStudySeed] = useState<{
    origem_chat?: string;
    materiais?: string[];
    assunto?: string;
    nonce: number;
  } | null>(null);
  const firstView = useRef(true);
  const pendingSend = useRef<{
    id: string;
    texto: string;
    modo: string;
    requisicao: string;
  } | null>(null);
  const stateRef = useRef(state),
    draftRef = useRef<{ id: string; texto: string } | null>(null),
    dirty = useRef(false),
    busyRef = useRef(false),
    searchRef = useRef(""),
    scroller = useRef<HTMLDivElement>(null);
  stateRef.current = state;
  searchRef.current = busca;
  const notify = useCallback((m: string) => {
    setToast(m);
  }, []);
  useEffect(() => {
    if (toast) {
      const t = setTimeout(() => setToast(""), 6000);
      return () => clearTimeout(t);
    }
  }, [toast]);
  const apply = useCallback((s: Estado, force = false) => {
    const cid = s.conversa?.id || null;
    const troca = draftRef.current?.id !== cid;
    stateRef.current = s;
    setState(s);
    if (firstView.current) {
      firstView.current = false;
      setView(s.estudo?.area || "chat");
    }
    if (force || troca || !dirty.current) {
      const texto = s.conversa?.rascunho || "";
      setDraft(texto);
      draftRef.current = cid ? { id: cid, texto } : null;
      dirty.current = false;
      window.cadernoMatDraft = draftRef.current;
    }
    document.documentElement.dataset.theme = s.preferencias.tema;
  }, []);
  const refresh = useCallback(
    async (force = false) => {
      const s = await api<Estado>("estado", { busca: searchRef.current });
      apply(s, force);
      setErro("");
    },
    [apply],
  );
  useEffect(() => {
    let live = true;
    const update = () => {
      if (live && !busyRef.current)
        refresh().catch((e) => {
          if (live) setErro(e.message);
        });
    };
    update();
    const t = setInterval(update, 1000);
    return () => {
      live = false;
      clearInterval(t);
    };
  }, [refresh]);
  useEffect(() => {
    const t = setTimeout(() => refresh().catch((e) => notify(e.message)), 250);
    return () => clearTimeout(t);
  }, [busca, refresh, notify]);
  const flush = useCallback(async () => {
    await window.cadernoMatFlushStudy?.();
    const d = draftRef.current;
    if (d && dirty.current) {
      await api("rascunho", d);
      if (draftRef.current?.id === d.id && draftRef.current.texto === d.texto)
        dirty.current = false;
    }
  }, []);
  useEffect(() => {
    const t = setTimeout(() => {
      flush().catch((e) => notify(e.message));
    }, 250);
    return () => clearTimeout(t);
  }, [draft, flush, notify]);
  useEffect(() => {
    window.cadernoMatDraft = draftRef.current;
  }, [draft, state?.conversa?.id]);
  useEffect(() => {
    scroller.current?.scrollTo({
      top: scroller.current.scrollHeight,
      behavior: "smooth",
    });
  }, [
    state?.mensagens.length,
    state?.conversa?.id,
    state?.tarefas.find((t) => t.estado === "executando")?.parcial,
  ]);
  const run = useCallback(
    async (op: string, dados: Record<string, unknown> = {}, close = false) => {
      setWorking(true);
      busyRef.current = true;
      try {
        await flush();
        const res = await api<any>(op, dados);
        if (res?.navegacao) apply(res, true);
        else if (res?.estado?.navegacao) {
          apply(res.estado, true);
          if (res.avisos?.length) notify(res.avisos.join(" "));
        } else await refresh();
        if (close) setModal(null);
        return true;
      } catch (e) {
        notify((e as Error).message);
        return false;
      } finally {
        busyRef.current = false;
        setWorking(false);
      }
    },
    [apply, flush, notify, refresh],
  );
  const currentBook = state?.cadernos.find(
    (c) => c.id === state.navegacao.caderno_id,
  );
  const editable =
    !!state?.conversa && !state.conversa.arquivada && !currentBook?.arquivado;
  const occupied = !!state?.ocupado || working;
  const activeTask = state?.tarefas.find(
    (t) => t.estado === "executando" && t.conversa === state.conversa?.id,
  );
  const navigate = async (
    caderno: string | null,
    conversa?: string,
    arquivadas = false,
  ) => {
    if (await run("navegar", { caderno, conversa, arquivadas })) {
      setBusca("");
      const area = view === "atividades" && !conversa ? "atividades" : "chat";
      await api("estudo_navegar", { area, atividade: null, tentativa: null });
      setView(area);
    }
  };
  const newChat = async () => {
    const ok = await run("chat_criar", {
      caderno: stateRef.current?.navegacao.caderno_id || null,
    });
    if (ok) {
      await api("estudo_navegar", { area: "chat" });
      setView("chat");
      setBusca("");
    }
    return ok;
  };
  const switchView = async (area: "chat" | "materiais" | "atividades") => {
    try {
      await flush();
      await api("estudo_navegar", {
        area,
      });
      setStudySeed(null);
      setView(area);
    } catch (e) {
      notify((e as Error).message);
    }
  };
  const createFrom = async (seed: {
    origem_chat?: string;
    materiais?: string[];
    assunto?: string;
  }) => {
    await switchView("atividades");
    setStudySeed({ ...seed, nonce: Date.now() });
  };
  const confirm = (
    titulo: string,
    descricao: string,
    operacao: string,
    dados: Record<string, unknown>,
  ) => setModal({ tipo: "confirmar", titulo, descricao, operacao, dados });
  const chatItems = (chat: Chat) => [
    {
      label: "Renomear",
      icon: Pencil,
      action: () => setModal({ tipo: "chat", acao: "renomear", item: chat }),
    },
    {
      label: chat.fixada ? "Desafixar" : "Fixar no topo",
      icon: Pin,
      action: () =>
        void run("chat_acao", {
          id: chat.id,
          acao: "fixar",
          valor: !chat.fixada,
        }),
    },
    {
      label: "Mover para caderno",
      icon: ArrowRight,
      action: () => setModal({ tipo: "chat", acao: "mover", item: chat }),
    },
    {
      label: chat.arquivada ? "Restaurar" : "Arquivar",
      icon: Archive,
      action: () =>
        void run("chat_acao", {
          id: chat.id,
          acao: "arquivar",
          valor: !chat.arquivada,
        }),
    },
    {
      label: "Excluir chat",
      icon: Trash2,
      danger: true,
      action: () =>
        confirm(
          "Excluir conversa?",
          `“${chat.titulo}” e suas mensagens serão removidas. Os materiais permanecem na biblioteca.`,
          "chat_acao",
          { id: chat.id, acao: "excluir" },
        ),
    },
    {
      label: "Criar atividade deste chat",
      icon: ClipboardList,
      action: () => void createFrom({ origem_chat: chat.id }),
    },
  ];
  const bookItems = (book: Caderno) => [
    {
      label: "Editar caderno",
      icon: Pencil,
      action: () => setModal({ tipo: "caderno", item: book }),
    },
    {
      label: "Mover para cima",
      icon: ArrowUp,
      action: () =>
        void run("caderno_acao", { id: book.id, acao: "ordenar", passo: -1 }),
    },
    {
      label: "Mover para baixo",
      icon: ArrowDown,
      action: () =>
        void run("caderno_acao", { id: book.id, acao: "ordenar", passo: 1 }),
    },
    {
      label: book.arquivado ? "Restaurar caderno" : "Arquivar caderno",
      icon: Archive,
      action: () =>
        void run("caderno_acao", {
          id: book.id,
          acao: "arquivar",
          valor: !book.arquivado,
        }),
    },
    {
      label: "Excluir caderno",
      icon: Trash2,
      danger: true,
      action: () =>
        confirm(
          "Excluir organização do caderno?",
          `“${book.nome}” será removido. Chats e atividades passam para Geral; mensagens, tentativas e documentos são preservados.`,
          "caderno_acao",
          { id: book.id, acao: "excluir" },
        ),
    },
  ];
  const materialItems = (m: Material) => [
    {
      label: "Criar atividade deste material",
      icon: ClipboardList,
      action: () => void createFrom({ materiais: [m.id], assunto: m.assunto }),
    },
    {
      label: "Editar material",
      icon: Pencil,
      action: () => setModal({ tipo: "material", item: m }),
    },
    {
      label: "Abrir original / link",
      icon: ExternalLink,
      action: () => void run("abrir_original", { id: m.id }),
    },
    ...(m.origem_id
      ? [
          {
            label: "Ir ao chat de origem",
            icon: MessageSquare,
            action: () => void navigate(null, m.origem_id!),
          },
        ]
      : []),
    {
      label: "Adicionar ao chat",
      icon: Plus,
      action: () => void run("material_acao", { id: m.id, acao: "reutilizar" }),
    },
    ...(m.anexado
      ? [
          {
            label: "Remover deste chat",
            icon: X,
            action: () =>
              void run("material_acao", { id: m.id, acao: "desvincular" }),
          },
        ]
      : []),
    {
      label: "Reprocessar",
      icon: RotateCcw,
      action: () =>
        void run("material_acao", { id: m.id, acao: "reprocessar" }),
    },
    {
      label: "Excluir da biblioteca",
      icon: Trash2,
      danger: true,
      action: () =>
        confirm(
          "Excluir material?",
          `“${m.nome}” será removido da biblioteca e dos índices. Seu arquivo de origem e as mensagens antigas são preservados.`,
          "material_acao",
          { id: m.id, acao: "excluir" },
        ),
    },
  ];
  const changeDraft = (texto: string) => {
    setDraft(texto);
    dirty.current = true;
    draftRef.current = stateRef.current?.conversa
      ? { id: stateRef.current.conversa.id, texto }
      : null;
    window.cadernoMatDraft = draftRef.current;
  };
  const send = async () => {
    if (!editable || occupied || !draft.trim()) return;
    setWorking(true);
    busyRef.current = true;
    try {
      await flush();
      const cid = state!.conversa!.id;
      if (
        !pendingSend.current ||
        pendingSend.current.id !== cid ||
        pendingSend.current.texto !== draft ||
        pendingSend.current.modo !== modo
      )
        pendingSend.current = {
          id: cid,
          texto: draft,
          modo,
          requisicao: crypto.randomUUID(),
        };
      await api("enviar", pendingSend.current);
      pendingSend.current = null;
      changeDraft("");
      dirty.current = false;
      await refresh(true);
    } catch (e) {
      notify((e as Error).message);
    } finally {
      busyRef.current = false;
      setWorking(false);
    }
  };
  const example = async () => {
    if (occupied) return;
    if (!stateRef.current?.conversa && !(await newChat())) return;
    const text = await api<string>("exemplo");
    setModo("Resolver");
    changeDraft(text);
  };
  const prefs = async (p: Estado["preferencias"]) => {
    if (state) {
      setState({ ...state, preferencias: p });
      document.documentElement.dataset.theme = p.tema;
      await api("preferencias", p).catch((e) => notify(e.message));
    }
  };
  const copy = async (text: string) => {
    try {
      await copiar(text);
      notify("Copiado para a área de transferência.");
    } catch (e) {
      notify((e as Error).message);
    }
  };
  const collapsed = state?.preferencias.recolhida || false;
  if (!state)
    return (
      <div className="boot">
        <div className="brand-mark">
          <Sigma />
        </div>
        <h1>CadernoMat</h1>
        {erro ? (
          <>
            <p role="alert">{erro}</p>
            <Button onClick={() => refresh().catch((e) => setErro(e.message))}>
              Tentar novamente
            </Button>
          </>
        ) : (
          <Loading>Preparando seu espaço de estudo…</Loading>
        )}
      </div>
    );
  return (
    <div className={`app ${collapsed ? "collapsed" : ""}`}>
      <aside className="sidebar" aria-label="Navegação de estudos">
        <div className="brand">
          <div className="brand-mark">
            <Sigma size={24} />
          </div>
          {!collapsed && (
            <div>
              <strong>CadernoMat</strong>
              <small>Seu espaço de matemática</small>
            </div>
          )}
          <Button
            variant="ghost"
            className="collapse-button"
            aria-label={
              collapsed ? "Expandir barra lateral" : "Recolher barra lateral"
            }
            onClick={() =>
              prefs({ ...state.preferencias, recolhida: !collapsed })
            }
          >
            {collapsed ? (
              <PanelLeftOpen size={18} />
            ) : (
              <PanelLeftClose size={18} />
            )}
          </Button>
        </div>
        <Button
          variant="primary"
          icon={Plus}
          className="new-chat"
          aria-label="Novo chat"
          disabled={occupied || !!currentBook?.arquivado}
          onClick={newChat}
        >
          {!collapsed && "Novo chat"}
        </Button>
        <Button
          variant={view === "materiais" ? "soft" : "ghost"}
          icon={Library}
          className="library-nav"
          aria-label="Abrir materiais"
          onClick={() => void switchView("materiais")}
        >
          {!collapsed && (
            <>
              Materiais<span className="nav-caption">Biblioteca</span>
            </>
          )}
        </Button>
        <Button
          variant={view === "atividades" ? "soft" : "ghost"}
          icon={ClipboardList}
          className="library-nav"
          aria-label="Abrir atividades"
          onClick={() => void switchView("atividades")}
        >
          {!collapsed && (
            <>
              Atividades<span className="nav-caption">Praticar</span>
            </>
          )}
        </Button>
        {!collapsed ? (
          <>
            <div className="section-title">
              <span>Cadernos</span>
              <Button
                variant="ghost"
                aria-label="Criar caderno"
                disabled={occupied}
                onClick={() => setModal({ tipo: "caderno" })}
              >
                <Plus size={16} />
              </Button>
            </div>
            <nav className="books">
              <button
                className={`book-row ${!currentBook ? "active" : ""}`}
                onClick={() => navigate(null)}
                disabled={occupied}
              >
                <BookOpen size={17} />
                <span>Geral</span>
              </button>
              {state.cadernos
                .filter((c) => !!c.arquivado === archBooks)
                .map((c) => (
                  <div
                    className={`book-line group ${currentBook?.id === c.id ? "active" : ""}`}
                    key={c.id}
                  >
                    <button
                      className="book-row"
                      title={c.nome}
                      onClick={() => navigate(c.id)}
                      disabled={occupied}
                    >
                      <BookOpen size={17} />
                      <span>{c.nome}</span>
                    </button>
                    <Menu
                      label={`Ações do caderno ${c.nome}`}
                      items={bookItems(c)}
                      disabled={occupied}
                    />
                  </div>
                ))}
            </nav>
            <button
              className="archive-toggle"
              onClick={() => setArchBooks(!archBooks)}
            >
              <Archive size={14} />
              {archBooks ? "Ver cadernos ativos" : "Cadernos arquivados"}
            </button>
            <div className="section-title conversations-title">
              <span>Conversas</span>
              <button
                className={state.navegacao.arquivados ? "selected" : ""}
                title={
                  state.navegacao.arquivados
                    ? "Ver chats ativos"
                    : "Ver chats arquivados"
                }
                aria-label={
                  state.navegacao.arquivados
                    ? "Ver chats ativos"
                    : "Ver chats arquivados"
                }
                onClick={() =>
                  navigate(
                    state.navegacao.caderno_id,
                    undefined,
                    !state.navegacao.arquivados,
                  )
                }
                disabled={occupied}
              >
                <Archive size={15} />
              </button>
            </div>
            <div className="search sidebar-search">
              <Search size={15} />
              <input
                aria-label="Buscar conversas"
                placeholder="Buscar conversa…"
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
              />
            </div>
            <div className="chats">
              {state.conversas.length ? (
                state.conversas.map((chat) => (
                  <div
                    className={`chat-row group ${chat.id === state.conversa?.id && view === "chat" ? "active" : ""}`}
                    key={chat.id}
                  >
                    <button
                      title={chat.titulo}
                      disabled={occupied}
                      onClick={() => navigate(chat.caderno_id, chat.id)}
                    >
                      {chat.fixada ? (
                        <Pin size={15} />
                      ) : (
                        <MessageSquare size={15} />
                      )}
                      <span>{chat.titulo}</span>
                    </button>
                    <Menu
                      label={`Ações da conversa ${chat.titulo}`}
                      items={chatItems(chat)}
                      disabled={occupied}
                    />
                  </div>
                ))
              ) : (
                <p className="sidebar-empty">
                  {busca
                    ? "Nenhum resultado."
                    : "Nenhuma conversa nesta lista."}
                </p>
              )}
            </div>
          </>
        ) : (
          <div className="collapsed-books">
            <Button
              variant="ghost"
              icon={BookOpen}
              aria-label="Mostrar cadernos"
              onClick={() => prefs({ ...state.preferencias, recolhida: false })}
            />
            <Button
              variant="ghost"
              icon={MessageSquare}
              aria-label="Mostrar chat"
              onClick={() => void switchView("chat")}
            />
          </div>
        )}
        <div className="sidebar-footer">
          <Button
            variant="ghost"
            icon={Settings}
            aria-label="Configurações de IA"
            disabled={occupied}
            onClick={() => setModal({ tipo: "config" })}
          >
            {!collapsed && "Configurações de IA"}
          </Button>
          <div className="sidebar-bottom">
            {!collapsed && (
              <span>
                <i className="local-dot" />
                Dados neste computador
              </span>
            )}
            <Button
              variant="ghost"
              aria-label={
                state.preferencias.tema === "claro"
                  ? "Usar tema escuro"
                  : "Usar tema claro"
              }
              onClick={() =>
                prefs({
                  ...state.preferencias,
                  tema:
                    state.preferencias.tema === "claro" ? "escuro" : "claro",
                })
              }
            >
              {state.preferencias.tema === "claro" ? (
                <Moon size={17} />
              ) : (
                <Sun size={17} />
              )}
            </Button>
          </div>
        </div>
      </aside>
      <main className="workspace">
        <header className="topbar">
          <div className="breadcrumb">
            <span className="breadcrumb-icon">
              {view === "chat" ? (
                <BookOpen size={19} />
              ) : view === "atividades" ? (
                <ClipboardList size={19} />
              ) : (
                <Library size={19} />
              )}
            </span>
            <div>
              <small title={currentBook?.nome || "Geral"}>
                {view !== "materiais"
                  ? currentBook?.nome || "Geral"
                  : "Sua biblioteca"}
              </small>
              <h1 title={state.conversa?.titulo}>
                {view === "chat"
                  ? state.conversa?.titulo || "Um novo espaço para aprender"
                  : view === "atividades"
                    ? "Atividades"
                    : "Materiais"}
              </h1>
            </div>
          </div>
          <div className="topbar-actions">
            {!!currentBook?.arquivado && (
              <Badge kind="warning">Caderno arquivado</Badge>
            )}
            {!!state.conversa?.arquivada && view === "chat" && (
              <Badge>Chat arquivado</Badge>
            )}
            <button
              className="provider-pill"
              disabled={occupied}
              onClick={() => setModal({ tipo: "config" })}
            >
              <i
                className={
                  state.config.provedores[state.config.provedor].configurada
                    ? "local-dot"
                    : "unconfigured-dot"
                }
              />
              <span>
                {nomeProvedor(state.config.provedor)}
                <small>
                  {state.config.modelo ||
                    state.config.provedores[state.config.provedor].modelo}
                </small>
              </span>
            </button>
            {view === "chat" && state.conversa && (
              <Menu
                label="Ações do chat aberto"
                items={chatItems(state.conversa)}
                disabled={occupied}
              />
            )}
          </div>
        </header>
        {erro && (
          <div role="alert" className="connection-error">
            {erro}
          </div>
        )}
        {view === "chat" ? (
          <div className="chat-view">
            <div
              ref={scroller}
              className="messages"
              aria-label="Histórico da conversa"
            >
              {!state.mensagens.length ? (
                <Empty
                  icon={Sigma}
                  title={
                    state.conversa
                      ? "O que vamos explorar hoje?"
                      : `Vamos estudar ${currentBook?.nome || "matemática"}?`
                  }
                  action={
                    !state.conversa ? (
                      <Button
                        variant="primary"
                        icon={Plus}
                        onClick={newChat}
                        disabled={occupied || !!currentBook?.arquivado}
                      >
                        Iniciar conversa
                      </Button>
                    ) : (
                      <div className="suggestions">
                        <Button
                          variant="soft"
                          disabled={occupied || !editable}
                          onClick={() =>
                            changeDraft(
                              "Explique este assunto com um exemplo e depois me faça uma pergunta.",
                            )
                          }
                        >
                          Entender um conceito
                        </Button>
                        <Button
                          variant="soft"
                          disabled={occupied || !editable}
                          onClick={() => {
                            setModo("Corrigir");
                            changeDraft(
                              "Quero revisar minha resolução. Enunciado:\n\nMinha tentativa:\n",
                            );
                          }}
                        >
                          Revisar minha tentativa
                        </Button>
                        <Button
                          variant="soft"
                          onClick={example}
                          disabled={occupied || !editable}
                        >
                          Carregar exemplo local
                        </Button>
                      </div>
                    )
                  }
                >
                  {currentBook?.arquivado
                    ? "Este caderno está arquivado. Restaure-o para continuar."
                    : state.conversa
                      ? "Traga uma dúvida, um exercício ou um material. Vamos construir o raciocínio passo a passo."
                      : "Crie um chat para começar. Seus materiais e conversas ficam organizados por matéria."}
                </Empty>
              ) : (
                <div className="message-list">
                  {state.mensagens.map((m) => (
                    <article
                      key={m.id}
                      className={`message message-${m.papel} ${m.estado !== "ok" ? "message-error" : ""}`}
                    >
                      <div className="message-label">
                        <span className={`avatar ${m.papel}`}>
                          {m.papel === "user" ? (
                            <span>V</span>
                          ) : (
                            <Sigma size={17} />
                          )}
                        </span>
                        <strong>
                          {m.papel === "user" ? "Você" : "CadernoMat"}
                        </strong>
                        {m.estado !== "ok" && (
                          <Badge kind="warning">
                            {m.estado === "cancelada"
                              ? "Cancelada · texto parcial"
                              : m.estado === "incompleta"
                                ? "Resposta incompleta"
                                : "Não concluído"}
                          </Badge>
                        )}
                        {m.papel === "assistant" && m.provedor && (
                          <span className="message-provider" title={m.modelo}>
                            {nomeProvedor(m.provedor)} · {m.modelo}
                          </span>
                        )}
                      </div>
                      <div className="message-content">
                        <Markdown texto={m.texto} onError={notify} />
                        {(state.calculos || [])
                          .filter(
                            (j) =>
                              j.tipo === "proposta" &&
                              j.estado === "concluida" &&
                              j.mensagem_id === m.id,
                          )
                          .map((j) => (
                            <Button
                              key={j.id}
                              disabled={!editable || occupied}
                              onClick={() =>
                                setModal({ tipo: "matematica", proposta: j.id })
                              }
                            >
                              Revisar proposta da IA
                            </Button>
                          ))}
                        {(state.calculos || [])
                          .filter(
                            (j) =>
                              j.tipo === "calculo" &&
                              j.estado === "concluida" &&
                              j.mensagem_id === m.id,
                          )
                          .map((j) => (
                            <MathCard
                              key={j.id}
                              id={j.id}
                              chat={state.conversa!.id}
                              notify={notify}
                            />
                          ))}
                      </div>
                      <button
                        className="copy-message"
                        aria-label={`Copiar ${m.papel === "assistant" ? "resposta" : "mensagem"} ${m.id}`}
                        onClick={() => copy(m.texto)}
                      >
                        <Copy size={14} />
                        <span>Copiar</span>
                      </button>
                      {m.estado !== "ok" && m.consulta_id && (
                        <Button
                          variant="ghost"
                          icon={RotateCcw}
                          disabled={occupied || !editable}
                          onClick={() =>
                            void run("ia_repetir", {
                              id: m.consulta_id,
                              requisicao: crypto.randomUUID(),
                            })
                          }
                        >
                          Repetir consulta
                        </Button>
                      )}
                    </article>
                  ))}
                  {activeTask && (
                    <article
                      className="message message-assistant streaming-message"
                      aria-label="Resposta em geração"
                    >
                      <div className="message-label">
                        <span className="avatar assistant">
                          <Sigma size={17} />
                        </span>
                        <strong>CadernoMat</strong>
                        <Badge kind="warning">Em geração · texto parcial</Badge>
                        {activeTask.cancelavel && (
                          <Button
                            variant="ghost"
                            disabled={activeTask.cancelando}
                            onClick={() =>
                              void run("ia_cancelar", { id: activeTask.id })
                            }
                          >
                            {activeTask.cancelando
                              ? "Interrompendo…"
                              : "Cancelar resposta"}
                          </Button>
                        )}
                      </div>
                      {activeTask.parcial ? (
                        <Markdown texto={activeTask.parcial} onError={notify} />
                      ) : (
                        <Loading>
                          Carregando modelo e construindo a resposta…
                        </Loading>
                      )}
                    </article>
                  )}
                </div>
              )}
            </div>
            <div className="composer-region">
              {state.tarefas
                .filter(
                  (t) =>
                    t.tipo === "matematica" &&
                    t.estado === "executando" &&
                    t.conversa === state.conversa?.id,
                )
                .map((t) => (
                  <div className="math-progress" key={t.id} role="status">
                    <Loading>Processando ferramenta matemática…</Loading>
                    <Button
                      disabled={t.cancelando}
                      onClick={() => void run("math_cancelar", { id: t.id })}
                    >
                      {t.cancelando ? "Interrompendo…" : "Cancelar operação"}
                    </Button>
                  </div>
                ))}
              {state.anexos.length > 0 && (
                <div className="attachment-strip">
                  {state.anexos.map((m) => (
                    <div className="attachment-chip" key={m.id}>
                      <button
                        title={`Visualizar ${m.nome}`}
                        onClick={() => setModal({ tipo: "detalhe", id: m.id })}
                      >
                        <FileText size={15} />
                        <span>{m.nome}</span>
                      </button>
                      <label title="Selecionar explicitamente como fonte neste chat">
                        <input
                          aria-label={`Consultar ${m.nome}`}
                          type="checkbox"
                          checked={m.selecionado}
                          disabled={
                            occupied ||
                            !editable ||
                            !["pronto", "parcial"].includes(m.estado)
                          }
                          onChange={(e) =>
                            void run("material_acao", {
                              id: m.id,
                              acao: "selecionar",
                              valor: e.target.checked,
                            })
                          }
                        />
                        <span>IA</span>
                      </label>
                      <button
                        aria-label={`Remover anexo ${m.nome}`}
                        disabled={occupied}
                        onClick={() =>
                          void run("material_acao", {
                            id: m.id,
                            acao: "desvincular",
                          })
                        }
                      >
                        <X size={13} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
              <div
                className={`composer ${!editable ? "composer-disabled" : ""}`}
              >
                <textarea
                  aria-label="Mensagem"
                  placeholder={
                    editable
                      ? "Escreva sua dúvida ou cole um exercício…"
                      : "Escolha Novo chat para iniciar uma conversa…"
                  }
                  value={draft}
                  disabled={!editable || working}
                  onChange={(e) => changeDraft(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                      e.preventDefault();
                      void send();
                    }
                  }}
                  maxLength={30000}
                />
                <div className="composer-tools">
                  <div className="composer-left">
                    <Button
                      variant="ghost"
                      icon={ChartNoAxesCombined}
                      aria-label="Cálculos e gráficos"
                      title="Cálculos e gráficos locais"
                      disabled={!editable || occupied}
                      onClick={() => setModal({ tipo: "matematica" })}
                    />
                    <Button
                      variant="ghost"
                      icon={Paperclip}
                      aria-label="Anexar arquivos"
                      disabled={
                        occupied ||
                        !!currentBook?.arquivado ||
                        !!state.conversa?.arquivada
                      }
                      onClick={() => void run("importar")}
                    />
                    <Button
                      variant="ghost"
                      icon={Link}
                      aria-label="Adicionar link"
                      disabled={
                        occupied ||
                        !!currentBook?.arquivado ||
                        !!state.conversa?.arquivada
                      }
                      onClick={() => setModal({ tipo: "link" })}
                    />
                    <select
                      aria-label="Modo de estudo"
                      value={modo}
                      onChange={(e) => setModo(e.target.value)}
                    >
                      {modos.map((m) => (
                        <option key={m}>{m}</option>
                      ))}
                    </select>
                    <Button
                      className="preview-button"
                      variant="ghost"
                      icon={Eye}
                      aria-label="Prévia do envio"
                      onClick={() => setModal({ tipo: "previa" })}
                    >
                      Prévia
                    </Button>
                  </div>
                  <Button
                    variant="primary"
                    icon={Send}
                    aria-label="Enviar mensagem"
                    disabled={!editable || occupied || !draft.trim()}
                    onClick={send}
                  >
                    {state.ocupado ? "Consultando" : "Enviar"}
                  </Button>
                </div>
              </div>
              <div className="composer-caption">
                <span>
                  {state.anexos.filter((m) => m.selecionado).length}{" "}
                  {state.anexos.filter((m) => m.selecionado).length === 1
                    ? "fonte selecionada"
                    : "fontes selecionadas"}{" "}
                  ·{" "}
                  {currentBook
                    ? preferencias[currentBook.preferencia]
                    : "Explicação padrão"}
                </span>
                <span>Ctrl + Enter para enviar</span>
              </div>
              <div className="chat-bottom-actions">
                <button
                  onClick={() =>
                    copy(
                      state.mensagens
                        .map(
                          (m) =>
                            `${m.papel === "user" ? "## Você" : "## CadernoMat"}\n${m.texto}`,
                        )
                        .join("\n\n---\n\n"),
                    )
                  }
                  disabled={!state.mensagens.length}
                >
                  Copiar conversa
                </button>
                <button
                  onClick={() => changeDraft("")}
                  disabled={!editable || occupied}
                >
                  Limpar entrada
                </button>
                <button
                  onClick={example}
                  disabled={
                    occupied ||
                    !!currentBook?.arquivado ||
                    !!state.conversa?.arquivada
                  }
                >
                  Exemplo local
                </button>
              </div>
            </div>
          </div>
        ) : view === "atividades" ? (
          <Activities
            state={state}
            notify={notify}
            seed={studySeed}
            onChat={async () => {
              await refresh(true);
              setStudySeed(null);
              setView("chat");
            }}
          />
        ) : (
          <Materiais
            state={state}
            occupied={occupied}
            run={run}
            notify={notify}
            open={(m) => setModal(m)}
            items={materialItems}
          />
        )}
      </main>
      {toast && (
        <div className="toast" role="status">
          <AlertCircle size={17} />
          <span>{toast}</span>
          <button aria-label="Fechar aviso" onClick={() => setToast("")}>
            <X size={16} />
          </button>
        </div>
      )}
      {modal && (
        <Dialog
          title={
            modal.tipo === "caderno"
              ? modal.item
                ? "Editar caderno"
                : "Criar caderno"
              : modal.tipo === "chat"
                ? modal.acao === "mover"
                  ? "Mover conversa"
                  : "Renomear conversa"
                : modal.tipo === "confirmar"
                  ? modal.titulo
                  : modal.tipo === "link"
                    ? "Adicionar link de estudo"
                    : modal.tipo === "config"
                      ? "Seu instrutor de IA"
                      : modal.tipo === "material"
                        ? "Organizar material"
                        : modal.tipo === "detalhe"
                          ? "Visualizar material"
                          : modal.tipo === "matematica"
                            ? "Cálculos e gráficos locais"
                            : "Prévia do envio"
          }
          subtitle={
            modal.tipo === "config"
              ? "Escolha IA local ou online e onde aplicar a configuração."
              : undefined
          }
          wide={["detalhe", "previa", "matematica"].includes(modal.tipo)}
          onClose={() => setModal(null)}
        >
          {modal.tipo === "matematica" && state.conversa && (
            <MathTools
              chat={state.conversa.id}
              proposta={modal.proposta}
              notify={notify}
              onStarted={() => {
                setModal(null);
                void refresh();
              }}
            />
          )}
          {modal.tipo === "caderno" && (
            <CadernoForm
              item={modal.item}
              save={(d) => run("caderno_salvar", d, true)}
              busy={working}
            />
          )}
          {modal.tipo === "chat" && (
            <ChatForm
              item={modal.item}
              acao={modal.acao}
              books={state.cadernos}
              save={(d) => run("chat_acao", d, true)}
              busy={working}
            />
          )}
          {modal.tipo === "confirmar" && (
            <>
              <p className="confirmation-text">{modal.descricao}</p>
              <div className="form-actions">
                <Button onClick={() => setModal(null)}>Cancelar</Button>
                <Button
                  variant="danger"
                  disabled={working}
                  icon={Trash2}
                  onClick={() =>
                    void run(
                      modal.operacao,
                      { ...modal.dados, confirmado: true },
                      true,
                    )
                  }
                >
                  Confirmar exclusão
                </Button>
              </div>
            </>
          )}
          {modal.tipo === "link" && (
            <LinkForm
              save={(url) => run("link", { url }, true)}
              busy={working}
            />
          )}
          {modal.tipo === "config" && (
            <ConfigForm
              chat={!!state.conversa && editable}
              config={state.config}
              save={(d) => run("configurar", d, true)}
              busy={working}
              notify={notify}
            />
          )}
          {modal.tipo === "material" && (
            <MaterialForm
              item={modal.item}
              books={state.cadernos}
              save={(d) => run("material_salvar", d, true)}
              busy={working}
            />
          )}
          {modal.tipo === "detalhe" && (
            <Preview id={modal.id} notify={notify} />
          )}
          {modal.tipo === "previa" && (
            <SendPreview
              id={state.conversa?.id || null}
              texto={draft}
              modo={modo}
              notify={notify}
            />
          )}
        </Dialog>
      )}
    </div>
  );
}

function CadernoForm({
  item,
  save,
  busy,
}: {
  item?: Caderno;
  save: (d: Record<string, unknown>) => Promise<boolean>;
  busy: boolean;
}) {
  const [form, setForm] = useState({
    nome: item?.nome || "",
    descricao: item?.descricao || "",
    objetivo: item?.objetivo || "",
    nivel: item?.nivel || "",
    assuntos: item?.assuntos || "",
    orientacao: item?.orientacao || "",
    preferencia: item?.preferencia || "completa",
  });
  const change = (k: string, v: string) => setForm({ ...form, [k]: v });
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void save({ id: item?.id || null, ...form });
      }}
    >
      <Field label="Nome do caderno">
        <input
          autoFocus
          required
          maxLength={100}
          value={form.nome}
          onChange={(e) => change("nome", e.target.value)}
          placeholder="Ex.: Álgebra Linear"
        />
      </Field>
      <Field label="Descrição">
        <textarea
          value={form.descricao}
          maxLength={1000}
          onChange={(e) => change("descricao", e.target.value)}
          rows={2}
        />
      </Field>
      <div className="form-grid">
        <Field label="Objetivo de estudo">
          <textarea
            rows={2}
            value={form.objetivo}
            maxLength={1000}
            onChange={(e) => change("objetivo", e.target.value)}
          />
        </Field>
        <Field label="Nível do estudante">
          <input
            value={form.nivel}
            maxLength={200}
            onChange={(e) => change("nivel", e.target.value)}
            placeholder="Ex.: Graduação, iniciante"
          />
        </Field>
      </div>
      <Field label="Assuntos principais">
        <textarea
          rows={2}
          value={form.assuntos}
          maxLength={1500}
          onChange={(e) => change("assuntos", e.target.value)}
        />
      </Field>
      <Field label="Preferência de explicação">
        <select
          value={form.preferencia}
          onChange={(e) => change("preferencia", e.target.value)}
        >
          {Object.entries(preferencias).map(([k, v]) => (
            <option value={k} key={k}>
              {v}
            </option>
          ))}
        </select>
      </Field>
      <Field
        label="Orientações pedagógicas"
        hint="Esses dados serão enviados ao provedor quando você consultar a IA neste caderno."
      >
        <textarea
          rows={2}
          value={form.orientacao}
          maxLength={1000}
          onChange={(e) => change("orientacao", e.target.value)}
        />
      </Field>
      <div className="form-actions">
        <Button type="submit" variant="primary" disabled={busy} icon={Check}>
          Salvar caderno
        </Button>
      </div>
    </form>
  );
}
function ChatForm({
  item,
  acao,
  books,
  save,
  busy,
}: {
  item: Chat;
  acao: "renomear" | "mover";
  books: Caderno[];
  save: (d: Record<string, unknown>) => Promise<boolean>;
  busy: boolean;
}) {
  const [value, setValue] = useState(
    acao === "renomear" ? item.titulo : item.caderno_id || "geral",
  );
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void save({
          id: item.id,
          acao,
          ...(acao === "renomear"
            ? { titulo: value }
            : { destino: value === "geral" ? null : value }),
        });
      }}
    >
      <Field
        label={
          acao === "renomear" ? "Título da conversa" : "Caderno de destino"
        }
      >
        {acao === "renomear" ? (
          <input
            autoFocus
            required
            maxLength={100}
            value={value}
            onChange={(e) => setValue(e.target.value)}
          />
        ) : (
          <select value={value} onChange={(e) => setValue(e.target.value)}>
            <option value="geral">Geral</option>
            {books
              .filter((c) => !c.arquivado)
              .map((c) => (
                <option key={c.id} value={c.id}>
                  {c.nome}
                </option>
              ))}
          </select>
        )}
      </Field>
      {acao === "mover" && (
        <p className="hint">
          Mensagens, rascunho e fontes selecionadas serão preservados. Os
          materiais também serão associados ao destino.
        </p>
      )}
      <div className="form-actions">
        <Button type="submit" variant="primary" disabled={busy}>
          {acao === "mover" ? "Mover conversa" : "Salvar título"}
        </Button>
      </div>
    </form>
  );
}
function LinkForm({
  save,
  busy,
}: {
  save: (url: string) => Promise<boolean>;
  busy: boolean;
}) {
  const [url, setUrl] = useState("");
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void save(url);
      }}
    >
      <Field
        label="Link público"
        hint="Páginas sem login. Será guardada uma cópia textual para consulta."
      >
        <input
          type="url"
          autoFocus
          required
          maxLength={2000}
          placeholder="https://…"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
      </Field>
      <div className="form-actions">
        <Button variant="primary" type="submit" disabled={busy} icon={Link}>
          Adicionar link
        </Button>
      </div>
    </form>
  );
}
function MaterialForm({
  item,
  books,
  save,
  busy,
}: {
  item: Material;
  books: Caderno[];
  save: (d: Record<string, unknown>) => Promise<boolean>;
  busy: boolean;
}) {
  const [form, setForm] = useState({
    nome: item.nome,
    materia: item.materia,
    assunto: item.assunto,
    etiquetas: item.etiquetas,
    cadernos: item.cadernos,
  });
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void save({ id: item.id, ...form });
      }}
    >
      {[
        ["nome", "Nome", 240],
        ["assunto", "Assunto", 200],
        ["etiquetas", "Etiquetas", 500],
        ["materia", "Matéria (metadado livre)", 100],
      ].map(([k, label, max]) => (
        <Field label={String(label)} key={String(k)}>
          <input
            required={k === "nome"}
            value={form[k as "nome" | "assunto" | "etiquetas" | "materia"]}
            maxLength={Number(max)}
            onChange={(e) => setForm({ ...form, [k]: e.target.value })}
          />
        </Field>
      ))}
      <fieldset className="book-associations">
        <legend>Cadernos associados</legend>
        <p className="hint">
          Compartilhar entre cadernos não duplica o arquivo nem autoriza envio à
          IA.
        </p>
        {books.map((c) => (
          <label key={c.id}>
            <input
              type="checkbox"
              checked={form.cadernos.includes(c.id)}
              onChange={(e) =>
                setForm({
                  ...form,
                  cadernos: e.target.checked
                    ? [...form.cadernos, c.id]
                    : form.cadernos.filter((id) => id !== c.id),
                })
              }
            />
            <span>
              {c.nome}
              {c.arquivado ? " (arquivado)" : ""}
            </span>
          </label>
        ))}
      </fieldset>
      <div className="form-actions">
        <Button type="submit" variant="primary" disabled={busy}>
          Salvar material
        </Button>
      </div>
    </form>
  );
}
function Materiais({
  state,
  occupied,
  run,
  notify,
  open,
  items,
}: {
  state: Estado;
  occupied: boolean;
  run: (op: string, d?: Record<string, unknown>) => Promise<boolean>;
  notify: (s: string) => void;
  open: (m: Modal) => void;
  items: (m: Material) => any[];
}) {
  const [filters, setFilters] = useState<Filtros>({
      busca: "",
      tipo: "",
      materia: "",
      dias: 0,
      caderno: "todos",
      so_chat: false,
      modo: "texto",
      pagina: 0,
    }),
    [list, setList] = useState<ListaMateriais | null>(null),
    [loading, setLoading] = useState(false);
  useEffect(() => {
    let live = true;
    const t = setTimeout(() => {
      setLoading(true);
      api<ListaMateriais>("materiais", { ...filters })
        .then((r) => {
          if (live) setList(r);
        })
        .catch((e) => notify(e.message))
        .finally(() => {
          if (live) setLoading(false);
        });
    }, 200);
    return () => {
      live = false;
      clearTimeout(t);
    };
  }, [filters, state.revisao, notify]);
  const filter = (k: keyof Filtros, v: any) =>
    setFilters({ ...filters, [k]: v, pagina: 0 });
  const editable =
    !!state.conversa &&
    !state.conversa.arquivada &&
    !state.cadernos.find((c) => c.id === state.navegacao.caderno_id)?.arquivado;
  return (
    <section className="materials-view">
      <div className="materials-heading">
        <div>
          <h2>Conhecimento, bem organizado.</h2>
          <p>Seus arquivos e links, disponíveis em cada etapa do estudo.</p>
        </div>
        <div className="flex gap-2">
          <Button
            icon={Link}
            disabled={occupied}
            onClick={() => open({ tipo: "link" })}
          >
            Adicionar link
          </Button>
          <Button
            icon={Plus}
            variant="primary"
            disabled={occupied}
            onClick={() => void run("importar")}
          >
            Arquivos
          </Button>
        </div>
      </div>
      <BuscaSemantica
        revisao={state.revisao}
        occupied={occupied}
        run={run}
        notify={notify}
      />
      <div className="search material-search">
        <Search size={19} />
        <input
          aria-label="Buscar materiais"
          value={filters.busca}
          placeholder="Buscar nome, conteúdo extraído, assunto ou etiquetas…"
          onChange={(e) => filter("busca", e.target.value)}
        />
      </div>
      <div className="filters">
        <select
          aria-label="Modo de busca nos materiais"
          value={filters.modo}
          onChange={(e) => filter("modo", e.target.value)}
        >
          <option value="texto">Palavra / nome</option>
          <option value="hibrida">Palavra e significado local</option>
        </select>
        <select
          aria-label="Filtrar por caderno"
          value={filters.caderno || "geral"}
          onChange={(e) =>
            filter(
              "caderno",
              e.target.value === "geral" ? null : e.target.value,
            )
          }
        >
          <option value="todos">Todos os cadernos</option>
          <option value="geral">Geral (sem caderno)</option>
          {state.cadernos.map((c) => (
            <option value={c.id} key={c.id}>
              {c.nome}
              {c.arquivado ? " (arquivado)" : ""}
            </option>
          ))}
        </select>
        <select
          aria-label="Filtrar por tipo"
          value={filters.tipo}
          onChange={(e) => filter("tipo", e.target.value)}
        >
          {Object.entries({
            "": "Todos os tipos",
            pdf: "PDF",
            imagem: "Imagens",
            texto: "Texto",
            docx: "DOCX",
            pptx: "PowerPoint (PPTX)",
            link: "Links",
            arquivo: "Outros",
          }).map(([k, v]) => (
            <option key={k} value={k}>
              {v}
            </option>
          ))}
        </select>
        <select
          aria-label="Filtrar por data"
          value={filters.dias}
          onChange={(e) => filter("dias", Number(e.target.value))}
        >
          {[0, 7, 30, 90].map((n) => (
            <option key={n} value={n}>
              {n ? `Últimos ${n} dias` : "Qualquer data"}
            </option>
          ))}
        </select>
        <select
          aria-label="Filtrar por matéria legada"
          value={filters.materia}
          onChange={(e) => filter("materia", e.target.value)}
        >
          <option value="">Todas as matérias</option>
          {list?.materias.map((m) => (
            <option key={m}>{m}</option>
          ))}
        </select>
        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={filters.so_chat}
            onChange={(e) => filter("so_chat", e.target.checked)}
          />
          Deste chat
        </label>
      </div>
      <div className="materials-summary">
        <span>
          {list?.total || 0} {list?.total === 1 ? "material" : "materiais"}
          {loading ? " · buscando…" : ""}
        </span>
        <button onClick={() => filter("caderno", state.navegacao.caderno_id)}>
          Do caderno atual
        </button>
      </div>
      {list?.recuperacao?.metodo && (
        <p className="semantic-notice" role="status">
          {list.recuperacao.metodo}
          {list.recuperacao.aviso ? ` · ${list.recuperacao.aviso}` : ""}
        </p>
      )}
      <div className="material-scroll">
        {list?.itens.length ? (
          <div className="material-grid">
            {list.itens.map((m) => (
              <article className="material-card" key={m.id}>
                <div className="material-card-top">
                  <div className={`file-icon ${m.tipo}`}>
                    {m.tipo === "imagem" ? (
                      <ImageIcon size={24} />
                    ) : m.tipo === "link" ? (
                      <Link size={24} />
                    ) : (
                      <FileText size={24} />
                    )}
                  </div>
                  <Menu
                    label={`Ações do material ${m.nome}`}
                    items={items(m)}
                    disabled={occupied}
                  />
                </div>
                <button
                  className="material-title"
                  title={m.nome}
                  onClick={() => open({ tipo: "detalhe", id: m.id })}
                >
                  {m.nome}
                </button>
                <p className="material-meta">
                  {m.tipo.toUpperCase()} · {bytes(m.tamanho)} ·{" "}
                  {m.criado.slice(0, 10)}
                </p>
                <Badge
                  kind={
                    m.estado === "erro"
                      ? "error"
                      : m.estado === "parcial"
                        ? "warning"
                        : m.estado === "pronto"
                          ? "success"
                          : "neutral"
                  }
                >
                  {m.estado_rotulo}
                </Badge>
                {m.aviso && (
                  <p className="material-warning" title={m.aviso}>
                    {m.aviso}
                  </p>
                )}
                {m.ocorrencias?.map((hit, i) => (
                  <p className="semantic-hit" key={i}>
                    <strong>
                      {hit.selecao}
                      {m.tipo === "pptx"
                        ? ` · slide ${hit.pagina}`
                        : m.tipo === "pdf" || m.metodo.includes("PDF")
                          ? ` · página ${hit.pagina}`
                          : ""}
                    </strong>
                    <br />
                    {hit.texto.slice(0, 280)}
                    {hit.texto.length > 280 ? "…" : ""}
                  </p>
                ))}
                <div className="material-subjects">
                  {m.cadernos.length ? (
                    m.cadernos.map((id) => (
                      <span key={id}>
                        {state.cadernos.find((c) => c.id === id)?.nome}
                      </span>
                    ))
                  ) : (
                    <span>Geral</span>
                  )}
                  {m.assunto && <span>{m.assunto}</span>}
                </div>
                <p className="material-origin" title={m.origem_titulo}>
                  Origem: {m.origem_titulo || "Chat removido"}
                </p>
                <div className="material-card-footer">
                  <Button
                    variant="ghost"
                    icon={Eye}
                    onClick={() => open({ tipo: "detalhe", id: m.id })}
                  >
                    Visualizar
                  </Button>
                  <label>
                    <input
                      type="checkbox"
                      aria-label={`Consultar ${m.nome} neste chat`}
                      checked={m.selecionado}
                      disabled={
                        occupied ||
                        !editable ||
                        !["pronto", "parcial"].includes(m.estado)
                      }
                      onChange={(e) =>
                        void run("material_acao", {
                          id: m.id,
                          acao: "selecionar",
                          valor: e.target.checked,
                        })
                      }
                    />
                    <span>Consultar neste chat</span>
                  </label>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <Empty
            icon={Library}
            title={
              filters.busca
                ? "Nenhum material encontrado"
                : "Sua biblioteca começa aqui"
            }
          >
            Adicione um PDF, imagem, texto ou link. Depois escolha
            explicitamente quais fontes a IA pode consultar.
          </Empty>
        )}
      </div>
      <div className="material-pagination">
        <span>
          Página {(list?.pagina || 0) + 1} · {list?.total || 0}{" "}
          {list?.total === 1 ? "material" : "materiais"}
        </span>
        <Button
          icon={ChevronLeft}
          disabled={!list?.pagina}
          onClick={() =>
            setFilters({ ...filters, pagina: Math.max(0, filters.pagina - 1) })
          }
        >
          Anterior
        </Button>
        <Button
          icon={ChevronRight}
          disabled={!list || (list.pagina + 1) * 30 >= list.total}
          onClick={() => setFilters({ ...filters, pagina: filters.pagina + 1 })}
        >
          Próxima
        </Button>
      </div>
    </section>
  );
}
function Preview({ id, notify }: { id: string; notify: (s: string) => void }) {
  const [detail, setDetail] = useState<Detalhe | null>(null),
    [page, setPage] = useState(1),
    [tab, setTab] = useState("texto"),
    [error, setError] = useState("");
  useEffect(() => {
    let live = true;
    api<Detalhe>("material_detalhe", { id, pagina: page })
      .then((r) => {
        if (live) {
          setDetail(r);
          setError("");
        }
      })
      .catch((e) => {
        if (live) setError(e.message);
      });
    return () => {
      live = false;
    };
  }, [id, page]);
  if (error) return <p role="alert">{error}</p>;
  if (!detail) return <Loading />;
  return (
    <>
      <div className="preview-heading">
        <div>
          <h3>{detail.material.nome}</h3>
          <p>
            {detail.material.estado_rotulo} ·{" "}
            {detail.material.metodo || "Sem extração"}
          </p>
        </div>
        <Button
          icon={ExternalLink}
          onClick={() =>
            void api("abrir_original", { id }).catch((e) => notify(e.message))
          }
        >
          Abrir original
        </Button>
      </div>
      {detail.material.aviso && (
        <div className="notice">{detail.material.aviso}</div>
      )}
      <div className="preview-controls">
        <div className="tabs">
          <button
            className={tab === "texto" ? "active" : ""}
            onClick={() => setTab("texto")}
          >
            Texto extraído
          </button>
          {["pdf", "imagem"].includes(detail.material.tipo) && (
            <button
              className={tab === "original" ? "active" : ""}
              onClick={() => setTab("original")}
            >
              Prévia original
            </button>
          )}
        </div>
        <select
          aria-label="Página do material"
          value={page}
          onChange={(e) => setPage(Number(e.target.value))}
        >
          {(detail.paginas.length ? detail.paginas : [1]).map((p) => (
            <option value={p} key={p}>
              {detail.material.tipo === "pptx"
                ? `Slide ${p}`
                : detail.material.tipo === "pdf"
                  ? `Página ${p}`
                  : `Trecho ${p}`}
            </option>
          ))}
        </select>
      </div>
      {tab === "texto" ? (
        <pre className="document-text">
          {detail.texto ||
            "Sem texto interpretável. A IA não receberá conteúdo inventado."}
        </pre>
      ) : detail.imagem ? (
        <div className="document-image">
          <img
            src={detail.imagem}
            alt={`Prévia de ${detail.material.nome}, página ${page}`}
          />
        </div>
      ) : (
        <p className="hint">{detail.aviso_previa || "Prévia indisponível."}</p>
      )}
    </>
  );
}
function SendPreview({
  id,
  texto,
  modo,
  notify,
}: {
  id: string | null;
  texto: string;
  modo: string;
  notify: (s: string) => void;
}) {
  const [p, setP] = useState<Previa | null>(null),
    [error, setError] = useState("");
  useEffect(() => {
    api<Previa>("previa", { id, texto, modo })
      .then(setP)
      .catch((e) => setError(e.message));
  }, [id, texto, modo]);
  if (error) return <p role="alert">{error}</p>;
  if (!p) return <Loading />;
  return (
    <div className="send-preview">
      <div className="notice">
        <CheckCircle2 size={18} />
        <span>
          Consulta a <strong>{nomeProvedor(p.provedor)}</strong> · {p.modelo}.{" "}
          {p.destino}. Originais binários ficam neste computador.
        </span>
      </div>
      {p.orcamento && (
        <section className="local-budget">
          <h3>Orçamento do modelo local</h3>
          <p>
            Entrada estimada: {p.orcamento.entrada_estimada} · saída reservada:{" "}
            {p.orcamento.reserva_saida} · margem: {p.orcamento.margem} ·
            contexto: {p.orcamento.contexto} tokens.
          </p>
          <p className="hint">
            {p.orcamento.metodo}. Pares omitidos: {p.orcamento.pares_omitidos};
            trechos omitidos: {p.orcamento.trechos_omitidos}; abreviados:{" "}
            {p.orcamento.trechos_abreviados}. Abaixo estão os dados que serão
            usados.
          </p>
        </section>
      )}
      <h3>Configurações do caderno</h3>
      <pre>{p.pedagogia || "Geral: instruções padrão de estudo."}</pre>
      <h3>Mensagem</h3>
      <pre>{p.mensagem || "(vazia)"}</pre>
      {p.instrucoes && (
        <details>
          <summary>Instruções desta consulta</summary>
          <pre>{p.instrucoes}</pre>
        </details>
      )}
      <h3>Histórico desta conversa</h3>
      {p.historico.length ? (
        p.historico.map((m, i) => (
          <section key={i}>
            <Badge>{m.role === "user" ? "Você" : "CadernoMat"}</Badge>
            <pre>{m.content}</pre>
          </section>
        ))
      ) : (
        <p className="hint">Nenhum par completo recente.</p>
      )}
      <h3>Trechos documentais selecionados</h3>
      {p.recuperacao?.metodo && (
        <p role="status">
          Recuperação: {p.recuperacao.metodo}. {p.recuperacao.aviso}
        </p>
      )}
      {p.fontes?.length ? (
        p.fontes.map((f) => (
          <section key={f.referencia}>
            <strong>
              [{f.referencia}] {f.nome}
              {f.tipo === "pptx"
                ? ` · slide ${f.pagina}`
                : f.tipo === "pdf"
                  ? ` · página ${f.pagina}`
                  : ""}
            </strong>
            {f.aviso && <p className="notice">Extração parcial: {f.aviso}</p>}
            <pre>{f.texto}</pre>
          </section>
        ))
      ) : (
        <p className="hint">
          {p.fontes
            ? "Nenhum trecho relevante recuperado. O modelo será informado."
            : "Nenhum material selecionado para consulta."}
        </p>
      )}
      <p className="hint">
        Inclui também instruções gerais de estudo e de uso seguro das fontes.
        Desmarcar um material não apaga informações de mensagens antigas.
        Resolver pode executar o cálculo local sem enviar estes dados.
      </p>
    </div>
  );
}
