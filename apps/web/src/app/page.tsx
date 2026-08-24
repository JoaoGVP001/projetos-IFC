import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const quickFilters = ["Todos", "Small Commerce", "ZWeb", "Interno"];

const recentContent = [
  {
    system: "Small Commerce",
    tone: "small",
    title: "Reforma tributária: primeiros passos",
    category: "Fiscal · Configurações",
    views: "128 acessos",
  },
  {
    system: "ZWeb",
    tone: "zweb",
    title: "Ativação da API para boletos Sicoob",
    category: "Financeiro · Integrações",
    views: "94 acessos",
  },
  {
    system: "Interno",
    tone: "internal",
    title: "Certificado não comunica: diagnóstico seguro",
    category: "Procedimentos · Certificado",
    views: "76 acessos",
  },
];

const metrics = [
  { value: "1.248", label: "conteúdos catalogados" },
  { value: "86%", label: "buscas com resultado" },
  { value: "4,7/5", label: "qualidade das soluções" },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[#f3f5f1] text-[#102a2b]">
      <header className="border-b border-[#dce2da] bg-[#f8faf6]/95 px-5 py-4 backdrop-blur md:px-9">
        <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-xl bg-[#123b3b] text-sm font-black tracking-tight text-[#d7ff75]">
              RH
            </div>
            <div>
              <p className="text-base font-black tracking-[-0.02em]">ResolveHub</p>
              <p className="text-xs font-medium text-[#607271]">Central inteligente de suporte</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-bold">João</p>
              <p className="text-xs text-[#738280]">Atendente</p>
            </div>
            <div className="grid size-10 place-items-center rounded-full border border-[#cdd7cf] bg-white text-sm font-extrabold">
              JP
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1440px] lg:grid-cols-[230px_1fr]">
        <aside className="hidden min-h-[calc(100vh-73px)] border-r border-[#dce2da] bg-[#f8faf6] p-5 lg:block">
          <nav aria-label="Navegação principal" className="space-y-1 text-sm font-semibold">
            <a className="nav-item nav-item-active" href="#inicio">Início</a>
            <a className="nav-item" href="#pesquisar">Pesquisar</a>
            <a className="nav-item" href="#recentes">Recentes</a>
            <a className="nav-item" href="#favoritos">Favoritos</a>
            <a className="nav-item" href="#metricas">Métricas</a>
          </nav>

          <div className="mt-9 border-t border-[#dce2da] pt-5">
            <p className="mb-3 px-3 text-[11px] font-black uppercase tracking-[0.14em] text-[#7c8987]">
              Fontes
            </p>
            <div className="space-y-3 px-3 text-sm">
              <p className="flex items-center justify-between"><span>Small Commerce</span><span className="status-dot bg-[#ff9c68]" /></p>
              <p className="flex items-center justify-between"><span>ZWeb</span><span className="status-dot bg-[#6a8fff]" /></p>
              <p className="flex items-center justify-between"><span>Conteúdo interno</span><span className="status-dot bg-[#2f9f86]" /></p>
            </div>
          </div>

          <div className="mt-10 rounded-2xl bg-[#123b3b] p-4 text-white">
            <p className="text-xs font-bold uppercase tracking-[0.12em] text-[#b9ccc6]">Base em evolução</p>
            <p className="mt-2 text-sm leading-5">Encontrou uma solução nova durante o atendimento?</p>
            <Button className="mt-4 w-full text-xs font-black" variant="lime">
              Cadastrar solução
            </Button>
          </div>
        </aside>

        <section id="inicio" className="min-w-0 px-5 py-8 md:px-9 md:py-10 lg:px-12">
          <div className="mx-auto max-w-6xl">
            <div className="grid gap-8 xl:grid-cols-[1fr_320px] xl:items-end">
              <div>
                <div className="flex flex-wrap items-center gap-3">
                  <p className="eyebrow">Conhecimento certo, na hora do atendimento</p>
                  <span className="rounded-full border border-[#cbd8cd] bg-[#e8eee4] px-2.5 py-1 text-[10px] font-black uppercase tracking-[0.08em] text-[#60716e]">
                    Prévia com dados demonstrativos
                  </span>
                </div>
                <h1 className="mt-3 max-w-3xl text-4xl font-black leading-[1.05] tracking-[-0.045em] text-[#102f30] md:text-6xl">
                  Como podemos resolver hoje?
                </h1>
                <p className="mt-4 max-w-2xl text-base leading-7 text-[#5c706e] md:text-lg">
                  Pesquise procedimentos, erros e manuais ou peça uma resposta fundamentada nas fontes cadastradas.
                </p>
              </div>

              <div id="metricas" className="grid grid-cols-3 gap-2 xl:grid-cols-1">
                {metrics.map((metric) => (
                  <div key={metric.label} className="metric-card">
                    <strong>{metric.value}</strong>
                    <span>{metric.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <form id="pesquisar" className="mt-9 rounded-[26px] border border-[#d5ddd5] bg-white p-3 shadow-[0_18px_60px_rgba(20,55,53,0.08)]">
              <label className="sr-only" htmlFor="support-search">Pesquisar na central de suporte</label>
              <div className="flex flex-col gap-3 md:flex-row">
                <Input
                  id="support-search"
                  name="q"
                  className="min-h-14 flex-1 rounded-2xl px-5 text-base"
                  placeholder="Digite um erro, módulo ou dúvida do cliente..."
                  type="search"
                />
                <Button className="font-black" size="lg" type="submit">
                  Pesquisar
                </Button>
                <Button className="font-black" size="lg" type="button" variant="lime">
                  Perguntar à IA
                </Button>
              </div>

              <div className="flex flex-wrap items-center gap-2 px-1 pb-1 pt-4">
                <span className="mr-1 text-xs font-bold text-[#6f7f7c]">Filtrar por:</span>
                {quickFilters.map((filter, index) => (
                  <button key={filter} className={index === 0 ? "filter-pill filter-pill-active" : "filter-pill"} type="button">
                    {filter}
                  </button>
                ))}
              </div>
            </form>

            <div id="recentes" className="mt-12">
              <div className="flex items-end justify-between gap-5">
                <div>
                  <p className="eyebrow">Acesso rápido</p>
                  <h2 className="mt-2 text-2xl font-black tracking-[-0.03em] md:text-3xl">Mais úteis nesta semana</h2>
                </div>
                <a className="hidden text-sm font-black text-[#176455] hover:underline sm:block" href="#todos">Ver todos</a>
              </div>

              <div className="mt-5 grid gap-4 md:grid-cols-3">
                {recentContent.map((item) => (
                  <article key={item.title} className="content-card">
                    <div className="flex items-center justify-between gap-3">
                      <span className={`system-badge ${item.tone}`}>{item.system}</span>
                      <span className="text-xs font-semibold text-[#84918e]">{item.views}</span>
                    </div>
                    <h3 className="mt-6 text-lg font-black leading-6 tracking-[-0.02em]">{item.title}</h3>
                    <p className="mt-2 text-sm text-[#6d7d7a]">{item.category}</p>
                    <a className="mt-7 inline-flex text-sm font-black text-[#176455] hover:underline" href="#abrir">
                      Abrir conteúdo →
                    </a>
                  </article>
                ))}
              </div>
            </div>

            <div className="mt-8 grid gap-4 md:grid-cols-[1.2fr_0.8fr]">
              <section className="rounded-[26px] bg-[#123b3b] p-6 text-white md:p-8">
                <p className="text-xs font-black uppercase tracking-[0.14em] text-[#a9c4bc]">Resposta com fontes</p>
                <h2 className="mt-3 text-2xl font-black tracking-[-0.03em]">A IA responde apenas com o que está cadastrado.</h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-[#c9d9d4]">
                  Cada orientação mostra os documentos consultados. Quando a evidência não for suficiente, o ResolveHub informa que não encontrou uma resposta segura.
                </p>
              </section>

              <section id="favoritos" className="rounded-[26px] border border-[#d6ddd6] bg-[#e8eddf] p-6 md:p-8">
                <p className="text-xs font-black uppercase tracking-[0.14em] text-[#687773]">Continuidade</p>
                <h2 className="mt-3 text-2xl font-black tracking-[-0.03em]">Retome de onde parou.</h2>
                <p className="mt-3 text-sm leading-6 text-[#5f706d]">Histórico recente e favoritos pessoais ficam a um clique durante o atendimento.</p>
              </section>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
