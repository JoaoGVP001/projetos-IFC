"use client";

import {
  BarChart3,
  BookOpen,
  Check,
  ChevronRight,
  Clock3,
  Copy,
  Database,
  ExternalLink,
  Home,
  LogOut,
  Plus,
  Search,
  Settings,
  Sparkles,
  Star,
  UserRound,
  X,
} from "lucide-react";
import { type FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import {
  initialKnowledge,
  type KnowledgeItem,
  type KnowledgeSystem,
  type KnowledgeTone,
} from "./knowledge-data";
import {
  buildAiPreview,
  filterKnowledge,
  type AiPreview,
  type SystemFilter,
} from "./workspace-logic";

const quickFilters: SystemFilter[] = ["Todos", "Small Commerce", "ZWeb", "Interno"];

const navItems = [
  { id: "inicio", label: "Início", icon: Home },
  { id: "resultados", label: "Conteúdos", icon: BookOpen },
  { id: "favoritos", label: "Favoritos", icon: Star },
  { id: "metricas", label: "Métricas", icon: BarChart3 },
];

const systemSources: Array<{ system: KnowledgeSystem; label: string; detail: string; color: string }> = [
  { system: "Small Commerce", label: "BDC Small Commerce", detail: "Artigos públicos", color: "#e37443" },
  { system: "ZWeb", label: "BDC ZWeb", detail: "Base de conhecimento", color: "#5f79cc" },
  { system: "Interno", label: "Documentos internos", detail: "Conteúdo revisado", color: "#3d9a78" },
];

function toneForSystem(system: KnowledgeSystem): KnowledgeTone {
  if (system === "Small Commerce") return "small";
  if (system === "ZWeb") return "zweb";
  return "internal";
}

function scrollToSection(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

type KnowledgeCardProps = {
  item: KnowledgeItem;
  favorite: boolean;
  views: number;
  onOpen: (item: KnowledgeItem) => void;
  onToggleFavorite: (item: KnowledgeItem) => void;
};

function KnowledgeCard({
  item,
  favorite,
  views,
  onOpen,
  onToggleFavorite,
}: KnowledgeCardProps) {
  return (
    <article className="content-card flex h-full flex-col" data-content-id={item.id}>
      <div className="flex items-start justify-between gap-3">
        <span className={`system-badge ${item.tone}`}>{item.system}</span>
        <button
          type="button"
          aria-label={favorite ? `Remover ${item.title} dos favoritos` : `Favoritar ${item.title}`}
          aria-pressed={favorite}
          className="rounded-full p-2 text-[#778582] transition hover:bg-[#e9eee7] hover:text-[#17423e] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#82b9aa]"
          onClick={() => onToggleFavorite(item)}
        >
          <Star className={favorite ? "fill-[#d9a727] text-[#d9a727]" : ""} size={18} />
        </button>
      </div>
      <p className="mt-5 text-[11px] font-extrabold uppercase tracking-[0.1em] text-[#71807d]">
        {item.category}
      </p>
      <h3 className="mt-2 text-lg font-black leading-snug tracking-[-0.025em] text-[#163b3b]">
        {item.title}
      </h3>
      <p className="mt-3 line-clamp-3 text-sm leading-6 text-[#65736f]">{item.excerpt}</p>
      <div className="mt-auto flex items-center justify-between gap-3 pt-6">
        <span className="flex items-center gap-1.5 text-xs font-bold text-[#7b8885]">
          <Clock3 size={14} aria-hidden="true" /> {views} acessos
        </span>
        <Button type="button" variant="ghost" size="sm" onClick={() => onOpen(item)}>
          Abrir conteúdo <ChevronRight size={15} aria-hidden="true" />
        </Button>
      </div>
    </article>
  );
}

export function SupportWorkspace() {
  const [items, setItems] = useState<KnowledgeItem[]>(initialKnowledge);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<SystemFilter>("Todos");
  const [showResults, setShowResults] = useState(false);
  const [showAll, setShowAll] = useState(false);
  const [favorites, setFavorites] = useState<Set<string>>(() => new Set());
  const [selected, setSelected] = useState<KnowledgeItem | null>(null);
  const [openCounts, setOpenCounts] = useState<Record<string, number>>({});
  const [aiPreview, setAiPreview] = useState<AiPreview | null>(null);
  const [solutionOpen, setSolutionOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const searchRef = useRef<HTMLInputElement>(null);

  const filteredItems = useMemo(
    () => filterKnowledge(items, query, filter),
    [filter, items, query],
  );
  const recentItems = showAll ? items : items.slice(0, 3);
  const visibleItems = showResults ? filteredItems : recentItems;
  const favoriteItems = items.filter((item) => favorites.has(item.id));

  useEffect(() => {
    if (!toast) return;
    const timeout = window.setTimeout(() => setToast(null), 2600);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setSelected(null);
      setSolutionOpen(false);
      setUserMenuOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, []);

  useEffect(() => {
    document.body.style.overflow = selected || solutionOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [selected, solutionOpen]);

  function notify(message: string) {
    setToast(message);
  }

  function runSearch(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setShowResults(true);
    requestAnimationFrame(() => scrollToSection("resultados"));
  }

  function selectFilter(nextFilter: SystemFilter) {
    setFilter(nextFilter);
    setShowResults(true);
    requestAnimationFrame(() => scrollToSection("resultados"));
  }

  function showEveryItem() {
    setQuery("");
    setFilter("Todos");
    setShowResults(false);
    setShowAll(true);
    requestAnimationFrame(() => scrollToSection("resultados"));
  }

  function openItem(item: KnowledgeItem) {
    setSelected(item);
    setOpenCounts((current) => ({
      ...current,
      [item.id]: (current[item.id] ?? 0) + 1,
    }));
  }

  function toggleFavorite(item: KnowledgeItem) {
    const isFavorite = favorites.has(item.id);
    setFavorites((current) => {
      const next = new Set(current);
      if (next.has(item.id)) next.delete(item.id);
      else next.add(item.id);
      return next;
    });
    notify(isFavorite ? "Conteúdo removido dos favoritos." : "Conteúdo adicionado aos favoritos.");
  }

  function askAi() {
    if (!query.trim()) {
      searchRef.current?.focus();
      notify("Digite uma pergunta antes de consultar a IA.");
      return;
    }
    setAiPreview(buildAiPreview(query, items, filter));
    setShowResults(true);
    requestAnimationFrame(() => scrollToSection("resposta-ia"));
  }

  async function copyProcedure(item: KnowledgeItem) {
    try {
      await navigator.clipboard.writeText(`${item.title}\n\n${item.procedure}`);
      notify("Procedimento copiado para a área de transferência.");
    } catch {
      notify("Não foi possível copiar automaticamente.");
    }
  }

  function createSolution(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const title = String(form.get("title") ?? "").trim();
    const system = String(form.get("system") ?? "Interno") as KnowledgeSystem;
    const procedure = String(form.get("procedure") ?? "").trim();
    if (!title || !procedure) {
      notify("Preencha o título e o procedimento.");
      return;
    }

    const newItem: KnowledgeItem = {
      id: `session-${Date.now()}`,
      system,
      tone: toneForSystem(system),
      title,
      category: "Solução cadastrada · Sessão",
      module: "Atendimento",
      tags: [system, "cadastro", "sessão"],
      views: 0,
      excerpt: procedure,
      procedure,
      sourceLabel: "Cadastro desta sessão",
    };

    setItems((current) => [newItem, ...current]);
    setSolutionOpen(false);
    setSelected(newItem);
    notify("Solução adicionada nesta sessão.");
    event.currentTarget.reset();
  }

  return (
    <main id="inicio" className="min-h-screen bg-[#f3f5f1] text-[#143838]">
      <header className="sticky top-0 z-30 border-b border-[#d7ddd6] bg-[#f8faf6]/95 backdrop-blur">
        <div className="mx-auto flex h-[72px] max-w-[1440px] items-center justify-between gap-5 px-5 lg:px-8">
          <button
            type="button"
            className="flex items-center gap-3 rounded-xl text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#82b9aa]"
            onClick={() => scrollToSection("inicio")}
            aria-label="Voltar ao início"
          >
            <span className="grid size-10 place-items-center rounded-xl bg-[#153e3e] text-[#d7ff75]">
              <Check size={22} strokeWidth={3} aria-hidden="true" />
            </span>
            <span>
              <strong className="block text-lg font-black leading-none tracking-[-0.04em]">ResolveHub</strong>
              <span className="mt-1 block text-[10px] font-extrabold uppercase tracking-[0.14em] text-[#71807d]">
                Central de suporte
              </span>
            </span>
          </button>

          <div className="flex items-center gap-3">
            <Button type="button" className="hidden sm:inline-flex" onClick={() => setSolutionOpen(true)}>
              <Plus size={17} aria-hidden="true" /> Cadastrar solução
            </Button>
            <div className="relative">
              <button
                type="button"
                aria-label="Abrir menu do usuário"
                aria-expanded={userMenuOpen}
                className="grid size-10 place-items-center rounded-full bg-[#d9e9e2] font-black text-[#245b54] outline-none transition hover:bg-[#c7ddd4] focus-visible:ring-2 focus-visible:ring-[#82b9aa]"
                onClick={() => setUserMenuOpen((open) => !open)}
              >
                JP
              </button>
              {userMenuOpen ? (
                <div className="absolute right-0 top-12 w-56 rounded-2xl border border-[#d7ddd6] bg-white p-2 shadow-xl" role="menu">
                  <p className="px-3 py-2 text-xs font-extrabold uppercase tracking-[0.1em] text-[#71807d]">
                    João · Demonstração
                  </p>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold hover:bg-[#edf2eb]"
                    onClick={() => notify("Perfil será conectado ao Auth.js na próxima etapa.")}
                  >
                    <UserRound size={16} /> Meu perfil
                  </button>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold hover:bg-[#edf2eb]"
                    onClick={() => notify("Preferências salvas localmente nesta demonstração.")}
                  >
                    <Settings size={16} /> Preferências
                  </button>
                  <button
                    type="button"
                    className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm font-bold text-[#9a4827] hover:bg-[#fff0e7]"
                    onClick={() => notify("Login ainda não está ativo nesta demonstração.")}
                  >
                    <LogOut size={16} /> Sair
                  </button>
                </div>
              ) : null}
            </div>
          </div>
        </div>

        <nav className="flex gap-1 overflow-x-auto border-t border-[#e2e6e0] px-4 py-2 lg:hidden" aria-label="Navegação móvel">
          {navItems.map(({ id, label, icon: Icon }) => (
            <Button key={id} type="button" variant="ghost" size="sm" onClick={() => scrollToSection(id)}>
              <Icon size={15} aria-hidden="true" /> {label}
            </Button>
          ))}
        </nav>
      </header>

      <div className="mx-auto grid max-w-[1440px] lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="hidden min-h-[calc(100vh-72px)] border-r border-[#d7ddd6] px-5 py-8 lg:block">
          <nav className="space-y-1" aria-label="Navegação principal">
            {navItems.map(({ id, label, icon: Icon }, index) => (
              <button
                key={id}
                type="button"
                className={`nav-item flex w-full items-center gap-3 text-left ${index === 0 ? "nav-item-active" : ""}`}
                onClick={() => scrollToSection(id)}
              >
                <Icon size={18} aria-hidden="true" /> {label}
              </button>
            ))}
          </nav>

          <div className="mt-10 border-t border-[#d7ddd6] pt-7">
            <p className="eyebrow px-2">Fontes conectadas</p>
            <div className="mt-4 space-y-1">
              {systemSources.map((source) => (
                <button
                  key={source.system}
                  type="button"
                  className="flex w-full items-center gap-3 rounded-xl px-2 py-3 text-left transition hover:bg-[#e9eee7] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#82b9aa]"
                  onClick={() => selectFilter(source.system)}
                >
                  <span className="status-dot" style={{ backgroundColor: source.color }} aria-hidden="true" />
                  <span>
                    <strong className="block text-xs font-extrabold">{source.label}</strong>
                    <span className="mt-0.5 block text-[11px] text-[#7a8784]">{source.detail}</span>
                  </span>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <div className="min-w-0 px-5 py-8 sm:px-8 lg:px-12 lg:py-11">
          <section className="overflow-hidden rounded-[30px] bg-[#143e3d] px-6 py-9 text-white shadow-[0_20px_55px_rgba(18,59,59,0.16)] sm:px-9 lg:px-12 lg:py-12">
            <div className="max-w-3xl">
              <p className="text-xs font-black uppercase tracking-[0.15em] text-[#b9d5ca]">Conhecimento confiável</p>
              <h1 className="mt-4 text-3xl font-black leading-[1.08] tracking-[-0.045em] sm:text-4xl lg:text-5xl">
                O que você precisa resolver hoje?
              </h1>
              <p className="mt-4 max-w-2xl text-sm leading-6 text-[#c7d8d1] sm:text-base">
                Pesquise procedimentos, filtre por sistema ou peça uma síntese baseada somente nas fontes cadastradas.
              </p>

              <form className="mt-8 rounded-2xl bg-white p-2 shadow-xl" onSubmit={runSearch} role="search">
                <div className="flex flex-col gap-2 sm:flex-row">
                  <div className="relative min-w-0 flex-1">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-[#68817a]" size={19} aria-hidden="true" />
                    <Input
                      ref={searchRef}
                      value={query}
                      onChange={(event) => setQuery(event.target.value)}
                      className="h-12 bg-white pl-11 text-[#173c3c]"
                      placeholder="Ex.: erro de status da SEFAZ"
                      aria-label="Pesquisar na base de conhecimento"
                    />
                  </div>
                  <Button type="submit" className="h-12 px-6">
                    <Search size={17} aria-hidden="true" /> Pesquisar
                  </Button>
                  <Button type="button" variant="lime" className="h-12 px-6" onClick={askAi}>
                    <Sparkles size={17} aria-hidden="true" /> Perguntar à IA
                  </Button>
                </div>
              </form>

              <div className="mt-5 flex flex-wrap items-center gap-2">
                <span className="mr-1 text-xs font-bold text-[#b9ccc5]">Filtrar:</span>
                {quickFilters.map((quickFilter) => (
                  <button
                    key={quickFilter}
                    type="button"
                    aria-pressed={filter === quickFilter}
                    className={`rounded-full border px-3 py-1.5 text-xs font-extrabold transition ${
                      filter === quickFilter
                        ? "border-[#d7ff75] bg-[#d7ff75] text-[#173c3c]"
                        : "border-[#54706c] text-[#d4e0dc] hover:border-[#8ba59e] hover:bg-[#214b49]"
                    }`}
                    onClick={() => selectFilter(quickFilter)}
                  >
                    {quickFilter}
                  </button>
                ))}
              </div>
            </div>
          </section>

          <section id="metricas" className="scroll-mt-32 py-8">
            <div className="grid grid-cols-2 gap-5 rounded-2xl border border-[#d9dfd8] bg-[#f8faf6] px-5 py-5 sm:grid-cols-4">
              <div className="metric-card"><strong>{items.length}</strong><span>conteúdos demonstrativos</span></div>
              <div className="metric-card"><strong>3</strong><span>fontes organizadas</span></div>
              <div className="metric-card"><strong>{favoriteItems.length}</strong><span>favoritos nesta sessão</span></div>
              <div className="metric-card"><strong>{Object.values(openCounts).reduce((total, value) => total + value, 0)}</strong><span>aberturas nesta sessão</span></div>
            </div>
          </section>

          {aiPreview ? (
            <section id="resposta-ia" className="scroll-mt-32 rounded-3xl border border-[#bfd4ca] bg-[#e7f1ec] p-6 sm:p-8" aria-live="polite">
              <div className="flex items-start gap-4">
                <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-[#153e3e] text-[#d7ff75]">
                  <Sparkles size={20} aria-hidden="true" />
                </span>
                <div className="min-w-0">
                  <p className="eyebrow">Resposta baseada na base</p>
                  <p className="mt-3 text-sm font-semibold leading-7 text-[#294c48]" data-testid="ai-answer">
                    {aiPreview.answer}
                  </p>
                  {aiPreview.sources.length ? (
                    <div className="mt-5 flex flex-wrap gap-2">
                      {aiPreview.sources.map((source) => (
                        <Button key={source.id} type="button" variant="outline" size="sm" onClick={() => openItem(source)}>
                          Fonte: {source.title}
                        </Button>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
            </section>
          ) : null}

          <section id="resultados" className="scroll-mt-32 py-10">
            <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="eyebrow">Base de conhecimento</p>
                <h2 className="mt-2 text-2xl font-black tracking-[-0.035em] sm:text-3xl">
                  {showResults ? `${visibleItems.length} conteúdo(s) encontrado(s)` : "Conteúdos recentes"}
                </h2>
              </div>
              <Button type="button" variant="outline" size="sm" onClick={showEveryItem}>
                Ver todos <ChevronRight size={15} aria-hidden="true" />
              </Button>
            </div>

            {visibleItems.length ? (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {visibleItems.map((item) => (
                  <KnowledgeCard
                    key={item.id}
                    item={item}
                    favorite={favorites.has(item.id)}
                    views={item.views + (openCounts[item.id] ?? 0)}
                    onOpen={openItem}
                    onToggleFavorite={toggleFavorite}
                  />
                ))}
              </div>
            ) : (
              <div className="rounded-3xl border border-dashed border-[#bdc9c1] bg-[#f8faf6] px-6 py-14 text-center">
                <Search className="mx-auto text-[#7b9189]" size={28} aria-hidden="true" />
                <h3 className="mt-4 text-lg font-black">Nenhum conteúdo encontrado</h3>
                <p className="mt-2 text-sm text-[#71807d]">Tente menos palavras ou escolha outro sistema.</p>
                <Button type="button" variant="outline" size="sm" className="mt-5" onClick={showEveryItem}>Limpar busca</Button>
              </div>
            )}
          </section>

          <section id="favoritos" className="scroll-mt-32 border-t border-[#d7ddd6] py-10">
            <div className="mb-6 flex items-center justify-between gap-4">
              <div>
                <p className="eyebrow">Acesso rápido</p>
                <h2 className="mt-2 text-2xl font-black tracking-[-0.035em]">Favoritos</h2>
              </div>
              <Star className="text-[#d9a727]" size={23} aria-hidden="true" />
            </div>
            {favoriteItems.length ? (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {favoriteItems.map((item) => (
                  <KnowledgeCard
                    key={item.id}
                    item={item}
                    favorite
                    views={item.views + (openCounts[item.id] ?? 0)}
                    onOpen={openItem}
                    onToggleFavorite={toggleFavorite}
                  />
                ))}
              </div>
            ) : (
              <button
                type="button"
                className="w-full rounded-3xl border border-dashed border-[#bdc9c1] bg-[#f8faf6] px-6 py-10 text-center transition hover:border-[#8fa79d] hover:bg-[#eef3ec] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#82b9aa]"
                onClick={() => scrollToSection("resultados")}
              >
                <Star className="mx-auto text-[#81908c]" size={25} aria-hidden="true" />
                <strong className="mt-3 block">Você ainda não favoritou conteúdos</strong>
                <span className="mt-1 block text-sm text-[#71807d]">Clique aqui para explorar a base.</span>
              </button>
            )}
          </section>

          <Button type="button" className="fixed bottom-5 right-5 z-20 shadow-lg sm:hidden" onClick={() => setSolutionOpen(true)}>
            <Plus size={17} aria-hidden="true" /> Cadastrar
          </Button>
        </div>
      </div>

      {selected ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-[#0c2525]/55 p-4 backdrop-blur-sm" role="presentation" onMouseDown={(event) => {
          if (event.currentTarget === event.target) setSelected(null);
        }}>
          <section className="max-h-[88vh] w-full max-w-2xl overflow-y-auto rounded-[28px] bg-[#fbfcf9] p-6 shadow-2xl sm:p-8" role="dialog" aria-modal="true" aria-labelledby="content-dialog-title">
            <div className="flex items-start justify-between gap-4">
              <span className={`system-badge ${selected.tone}`}>{selected.system}</span>
              <button type="button" aria-label="Fechar conteúdo" className="rounded-full p-2 text-[#667572] hover:bg-[#e9eee7]" onClick={() => setSelected(null)}>
                <X size={20} aria-hidden="true" />
              </button>
            </div>
            <p className="mt-7 text-xs font-extrabold uppercase tracking-[0.1em] text-[#71807d]">{selected.category}</p>
            <h2 id="content-dialog-title" className="mt-2 text-2xl font-black tracking-[-0.035em] sm:text-3xl">{selected.title}</h2>
            <p className="mt-4 text-sm leading-7 text-[#65736f]">{selected.excerpt}</p>
            <div className="mt-7 rounded-2xl border border-[#d9dfd8] bg-white p-5">
              <p className="eyebrow">Procedimento</p>
              <p className="mt-3 text-sm font-semibold leading-7 text-[#294c48]">{selected.procedure}</p>
            </div>
            <div className="mt-6 flex flex-wrap gap-2">
              <Button type="button" onClick={() => copyProcedure(selected)}>
                <Copy size={16} aria-hidden="true" /> Copiar procedimento
              </Button>
              <Button type="button" variant="outline" onClick={() => toggleFavorite(selected)}>
                <Star size={16} className={favorites.has(selected.id) ? "fill-[#d9a727] text-[#d9a727]" : ""} aria-hidden="true" />
                {favorites.has(selected.id) ? "Remover favorito" : "Favoritar"}
              </Button>
              {selected.sourceUrl ? (
                <Button asChild variant="outline">
                  <a href={selected.sourceUrl} target="_blank" rel="noreferrer">
                    Abrir fonte <ExternalLink size={16} aria-hidden="true" />
                  </a>
                </Button>
              ) : null}
            </div>
            <p className="mt-6 flex items-center gap-2 text-xs font-bold text-[#71807d]">
              <Database size={14} aria-hidden="true" /> Fonte: {selected.sourceLabel}
            </p>
          </section>
        </div>
      ) : null}

      {solutionOpen ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-[#0c2525]/55 p-4 backdrop-blur-sm" role="presentation" onMouseDown={(event) => {
          if (event.currentTarget === event.target) setSolutionOpen(false);
        }}>
          <section className="w-full max-w-xl rounded-[28px] bg-[#fbfcf9] p-6 shadow-2xl sm:p-8" role="dialog" aria-modal="true" aria-labelledby="solution-dialog-title">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="eyebrow">Cadastro rápido</p>
                <h2 id="solution-dialog-title" className="mt-2 text-2xl font-black tracking-[-0.035em]">Nova solução</h2>
              </div>
              <button type="button" aria-label="Fechar cadastro" className="rounded-full p-2 text-[#667572] hover:bg-[#e9eee7]" onClick={() => setSolutionOpen(false)}>
                <X size={20} aria-hidden="true" />
              </button>
            </div>
            <p className="mt-3 text-sm leading-6 text-[#71807d]">Este protótipo mantém o novo conteúdo somente durante a sessão atual.</p>
            <form className="mt-7 space-y-5" onSubmit={createSolution}>
              <label className="block text-sm font-extrabold" htmlFor="solution-title">
                Título
                <Input id="solution-title" name="title" required className="mt-2 border-[#d9dfd8] bg-white" placeholder="Ex.: Como validar uma rejeição fiscal" />
              </label>
              <label className="block text-sm font-extrabold" htmlFor="solution-system">
                Sistema
                <select id="solution-system" name="system" defaultValue="Interno" className="mt-2 h-11 w-full rounded-xl border border-[#d9dfd8] bg-white px-4 outline-none focus:border-[#82b9aa] focus:ring-2 focus:ring-[#82b9aa]/35">
                  <option>Small Commerce</option>
                  <option>ZWeb</option>
                  <option>Interno</option>
                </select>
              </label>
              <label className="block text-sm font-extrabold" htmlFor="solution-procedure">
                Procedimento
                <textarea id="solution-procedure" name="procedure" required rows={5} className="mt-2 w-full resize-y rounded-xl border border-[#d9dfd8] bg-white px-4 py-3 text-sm font-medium outline-none focus:border-[#82b9aa] focus:ring-2 focus:ring-[#82b9aa]/35" placeholder="Descreva os passos seguros para o atendimento." />
              </label>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="outline" onClick={() => setSolutionOpen(false)}>Cancelar</Button>
                <Button type="submit"><Check size={16} aria-hidden="true" /> Salvar solução</Button>
              </div>
            </form>
          </section>
        </div>
      ) : null}

      {toast ? (
        <div className="fixed bottom-5 left-1/2 z-[60] -translate-x-1/2 rounded-xl bg-[#102f2f] px-4 py-3 text-center text-sm font-bold text-white shadow-xl sm:left-auto sm:right-5 sm:translate-x-0" role="status" aria-live="polite">
          {toast}
        </div>
      ) : null}
    </main>
  );
}
