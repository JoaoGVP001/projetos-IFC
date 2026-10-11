import { useEffect, useRef, useState } from "react";
import { api } from "./bridge";
import { Button, Field, Badge, Loading } from "./ui";
import { MathAI } from "./MathTools";
import { Markdown } from "./Markdown";
import { Download } from "lucide-react";

export type DiscreteSpec = {
  tipo: "conjuntos" | "relacoes" | "logica";
  sobre: boolean;
  A: string;
  B: string;
  U: string;
  R: string;
  S: string;
  C: string;
  expressao: string;
  comparar: string;
  origens?: unknown[];
};
export type DiscreteContext = {
  atividade: string;
  atividade_versao: number;
  questao: string;
  tentativa?: string;
};
type DiscreteJob = {
  id: string;
  estado: string;
  erro: string;
  tipo: string;
  imagem?: string;
  aviso_artefato?: string;
  resumo?: string;
  tentativa_id?: string;
  conferencia?: { estado: string; campo: string; aviso: string };
  resultado?: DiscreteSpec & {
    resultados?: Record<string, unknown>;
    png_disponivel?: boolean;
  };
  spec?: DiscreteSpec;
};
const blank = (tipo: DiscreteSpec["tipo"] = "conjuntos"): DiscreteSpec => ({
  tipo,
  sobre: true,
  A: "",
  B: "",
  U: "",
  R: "",
  S: "",
  C: "",
  expressao: "",
  comparar: "",
});
const examples: Record<DiscreteSpec["tipo"], DiscreteSpec> = {
  conjuntos: { ...blank(), A: "{1,2,3}", B: "{2,3,4}", U: "{1,2,3,4,5}" },
  relacoes: { ...blank("relacoes"), A: "{1,2,3}", R: "{(1,2),(2,3)}" },
  logica: { ...blank("logica"), expressao: "p -> q", comparar: "~p | q" },
};
const labels: Record<string, string> = {
  A: "Conjunto A",
  B: "Conjunto B",
  U: "Universo U (opcional)",
  R: "Relação R",
  S: "Relação S (opcional)",
  C: "Conjunto C",
  expressao: "Expressão lógica",
  comparar: "Comparar expressão (opcional)",
};
export function DiscreteTools({
  chat,
  notify,
  onStarted,
  proposta,
  context,
  enunciado,
}: {
  chat: string;
  notify: (s: string) => void;
  onStarted: () => void;
  proposta?: string;
  context?: DiscreteContext;
  enunciado?: string;
}) {
  const revision = useRef(0);
  const [proposalId, setProposalId] = useState<string | undefined>(proposta);
  const [spec, setSpec] = useState<DiscreteSpec>(blank()),
    [preview, setPreview] = useState<Record<string, unknown> | null>(null),
    [busy, setBusy] = useState(false),
    [job, setJob] = useState<DiscreteJob | null>(null),
    [sources, setSources] = useState<
      { id: string; nome: string; estado: string; selecionado: boolean }[]
    >([]);
  const apply = (s: DiscreteSpec) => {
    revision.current++;
    const t = blank(s.tipo);
    for (const k of Object.keys(t) as (keyof DiscreteSpec)[])
      Object.assign(t, { [k]: s[k] });
    setSpec(t);
    setPreview(null);
  };
  useEffect(() => {
    if (proposta)
      void api<DiscreteJob>("discreta_obter", { id: proposta })
        .then((j) => {
          if (j.tipo === "proposta" && j.resultado) apply(j.resultado);
        })
        .catch((e) => notify(e.message));
  }, [proposta]);
  useEffect(() => {
    void api<typeof sources>("discreta_materiais", { conversa: chat })
      .then(setSources)
      .catch((e) => notify(e.message));
  }, [chat]);
  useEffect(() => {
    if (job?.estado !== "executando") return;
    const timer = setInterval(
      () =>
        void api<DiscreteJob>("discreta_obter", { id: job.id })
          .then(setJob)
          .catch((e) => notify(e.message)),
      500,
    );
    return () => clearInterval(timer);
  }, [job?.id, job?.estado]);
  const change = (key: string, value: unknown) => {
    revision.current++;
    setSpec((s) => ({ ...s, [key]: value }));
    setPreview(null);
  };
  const fields =
    spec.tipo === "conjuntos"
      ? ["A", "B", "U"]
      : spec.tipo === "logica"
        ? ["expressao", "comparar"]
        : [
            "A",
            ...(!spec.sobre ? ["B"] : []),
            "R",
            "S",
            ...(!spec.sobre && spec.S ? ["C"] : []),
          ];
  const missing = (
    spec.tipo === "conjuntos"
      ? ["A", "B"]
      : spec.tipo === "logica"
        ? ["expressao"]
        : [
            "A",
            "R",
            ...(!spec.sobre ? ["B"] : []),
            ...(!spec.sobre && spec.S ? ["C"] : []),
          ]
  ).filter((k) => !spec[k as keyof DiscreteSpec]);
  async function inspect() {
    setBusy(true);
    const current = revision.current;
    try {
      const result = await api<Record<string, unknown>>("discreta_validar", {
        spec,
      });
      if (revision.current === current) setPreview(result);
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function start() {
    setBusy(true);
    try {
      const r = await api<{ id: string }>("discreta_executar", {
        conversa: chat,
        spec,
        ...context,
        proposta: proposalId,
      });
      setJob({ id: r.id, estado: "executando", erro: "", tipo: "calculo" });
      onStarted();
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="math-tools">
      <p className="muted">
        Operações exatas em conjuntos finitos e lógica, neste computador.
        Confira os dados antes de calcular. Indução e conjuntos infinitos exigem
        outro tratamento.
      </p>
      {enunciado && (
        <details>
          <summary>Questão vinculada</summary>
          <pre>{enunciado}</pre>
        </details>
      )}
      <MathAI<DiscreteSpec>
        prefix="discreta"
        chat={chat}
        tipo="proposta"
        notify={notify}
        onResult={(s, id) => {
          apply(s);
          setProposalId(id);
        }}
        hint="Rotule os dados: A={...}; R={(a,b)}; expressao=p -> q. Selecione abaixo as fontes que deseja consultar. Dados ausentes ficam em branco."
        placeholder={"Verifique R={(1,2),(2,3)} sobre A={1,2,3}."}
      />
      <details>
        <summary>
          Materiais para a proposta da IA (
          {sources.filter((x) => x.selecionado).length} selecionados)
        </summary>
        <p>
          Seleção salva neste chat. Os trechos e avisos serão exibidos na
          prévia; originais não são enviados.
        </p>
        {sources.map((m) => (
          <label className="math-check" key={m.id}>
            <input
              type="checkbox"
              checked={m.selecionado}
              disabled={
                busy ||
                (!["pronto", "parcial"].includes(m.estado) && !m.selecionado)
              }
              onChange={(e) => {
                const valor = e.target.checked;
                void api("discreta_fonte", { conversa: chat, id: m.id, valor })
                  .then(() =>
                    setSources((s) =>
                      s.map((x) =>
                        x.id === m.id ? { ...x, selecionado: valor } : x,
                      ),
                    ),
                  )
                  .catch((e) => notify(e.message));
              }}
            />
            {m.nome}
          </label>
        ))}
        {!sources.length && (
          <p>Nenhum material associado a este caderno/chat.</p>
        )}
      </details>
      {proposalId && missing.length > 0 && (
        <p role="alert" className="notice">
          Dados ausentes ou ambíguos na proposta:{" "}
          {missing.map((k) => labels[k]).join(", ")}. Preencha e confira antes
          de calcular.
        </p>
      )}
      <Field label="Ferramenta de Discreta">
        <select
          aria-label="Ferramenta de Discreta"
          value={spec.tipo}
          disabled={busy || job?.estado === "executando"}
          onChange={(e) => {
            apply(blank(e.target.value as DiscreteSpec["tipo"]));
          }}
        >
          <option value="conjuntos">Conjuntos finitos</option>
          <option value="relacoes">Relações finitas</option>
          <option value="logica">Lógica proposicional</option>
        </select>
      </Field>
      {spec.tipo === "relacoes" && (
        <label className="math-check">
          <input
            type="checkbox"
            checked={spec.sobre}
            disabled={busy || job?.estado === "executando"}
            onChange={(e) => change("sobre", e.target.checked)}
          />
          Relação sobre A (origem e destino A)
        </label>
      )}
      {fields.map((k) => (
        <Field
          key={k}
          label={labels[k]}
          hint={
            k === "R" || k === "S"
              ? "Use {(1,2),(2,3)}. Composição: primeiro R, depois S."
              : k === "expressao"
                ? "Use letras, ¬/~, ∧/&, ∨/|, →/->, ↔/<-> e parênteses. Até seis variáveis."
                : 'Use chaves, por exemplo {1,2,"a"}. {} representa vazio.'
          }
        >
          <input
            aria-label={labels[k]}
            maxLength={k === "expressao" || k === "comparar" ? 300 : 6000}
            disabled={busy || job?.estado === "executando"}
            value={String(spec[k as keyof DiscreteSpec])}
            onChange={(e) => change(k, e.target.value)}
          />
        </Field>
      ))}
      <Button
        disabled={busy || job?.estado === "executando"}
        onClick={() => {
          apply(examples[spec.tipo]);
        }}
      >
        Carregar exemplo de Discreta
      </Button>
      <Button
        disabled={busy || job?.estado === "executando"}
        onClick={() => void inspect()}
      >
        Conferir dados interpretados
      </Button>
      {preview && (
        <div className="notice">
          <strong>Dados que serão calculados</strong>
          <pre>{JSON.stringify(preview, null, 2)}</pre>
          <Button
            variant="primary"
            disabled={busy || job?.estado === "executando"}
            onClick={() => void start()}
          >
            Calcular e salvar Discreta
          </Button>
        </div>
      )}
      {job?.estado === "executando" && (
        <>
          <Loading>Calculando localmente…</Loading>
          <Button
            onClick={() =>
              void api("discreta_cancelar", { id: job.id }).catch((e) =>
                notify(e.message),
              )
            }
          >
            Cancelar cálculo de Discreta
          </Button>
        </>
      )}
      {job?.erro && <p role="alert">{job.erro}</p>}
      {job?.estado === "concluida" && (
        <>
          <p role="status">
            Resultado salvo no chat
            {context ? " e vinculado à questão/tentativa" : ""}.
          </p>
          <DiscreteCard id={job.id} chat={chat} notify={notify} />
        </>
      )}
    </section>
  );
}
export function DiscreteCard({
  id,
  chat,
  notify,
}: {
  id: string;
  chat: string;
  notify: (s: string) => void;
}) {
  const [job, setJob] = useState<DiscreteJob | null>(null),
    [field, setField] = useState("");
  useEffect(() => {
    void api<DiscreteJob>("discreta_obter", { id })
      .then(setJob)
      .catch((e) => notify(e.message));
  }, [id]);
  const results = job?.resultado?.resultados || {};
  const values = Object.entries(results)
    .filter(([, v]) => typeof v === "boolean" || typeof v === "number")
    .map(([k]) => k);
  if (Array.isArray(results.propriedades))
    for (const p of results.propriedades as { propriedade: string }[])
      values.push(p.propriedade);
  return (
    <section
      className="math-artifact"
      aria-label="Resultado de Matemática Discreta"
    >
      <Badge>Operações locais · dados finitos · {id.slice(0, 8)}</Badge>
      {job?.resumo && (
        <details>
          <summary>Resultados, definições e contraexemplos</summary>
          <Markdown texto={job.resumo} onError={notify} />
        </details>
      )}
      {!job ? (
        <Loading />
      ) : job.imagem ? (
        <img
          src={job.imagem}
          alt="Diagrama dos conjuntos ou pares informados; resultados e contraexemplos na mensagem."
        />
      ) : job.aviso_artefato ? (
        <p role="alert">{job.aviso_artefato}</p>
      ) : (
        <p>
          Tabela/resultados registrados em texto; diagrama não aplicável ou
          acima do limite visual.
        </p>
      )}
      <Button
        icon={Download}
        disabled={!job?.imagem}
        onClick={() =>
          void api<{ exportado: boolean }>("discreta_exportar", { id })
            .then((r) => {
              if (r.exportado) notify("Diagrama exportado em PNG.");
            })
            .catch((e) => notify(e.message))
        }
      >
        Exportar diagrama PNG
      </Button>
      <MathAI
        prefix="discreta"
        chat={chat}
        tipo="explicacao"
        origem={id}
        notify={notify}
      />
      {job?.tentativa_id && values.length > 0 && (
        <details>
          <summary>Conferir com solução registrada</summary>
          <p>
            Requer solução revelada ou tentativa finalizada. Escolha qual
            resultado corresponde à questão; o gabarito e a nota permanecem
            registrados.
          </p>
          <select
            aria-label="Resultado para conferir"
            value={field}
            onChange={(e) => setField(e.target.value)}
          >
            <option value="">Escolha um resultado</option>
            {values.map((k) => (
              <option key={k}>{k}</option>
            ))}
          </select>
          <Button
            disabled={!field}
            onClick={() =>
              void api<{ estado: string; campo: string; aviso: string }>(
                "discreta_conferir",
                { id, campo: field },
              )
                .then((r) => setJob((j) => (j ? { ...j, conferencia: r } : j)))
                .catch((e) => notify(e.message))
            }
          >
            Comparar resultado local
          </Button>
          {job.conferencia?.estado && (
            <p role="status">
              {job.conferencia.estado}: {job.conferencia.aviso}
            </p>
          )}
        </details>
      )}
    </section>
  );
}
