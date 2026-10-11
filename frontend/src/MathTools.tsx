import { useEffect, useState } from "react";
import { ChartNoAxesCombined, Download, Sparkles } from "lucide-react";
import { api } from "./bridge";
import { Button, Field, Badge, Loading } from "./ui";

export type MathSpec = {
  expressao: string;
  inicio: string;
  fim: string;
  ponto: string;
  operacoes: string[];
};
export type MathJob = {
  id: string;
  tipo: string;
  estado: string;
  mensagem_id: number | null;
  erro: string;
  spec?: MathSpec;
  resultado?: MathSpec;
  previa?: {
    destino: string;
    aviso: string;
    preparada: { pergunta: string; instrucoes: string; orcamento?: unknown };
  };
  imagem?: string | null;
  aviso_artefato?: string;
};
const operations: Record<string, string> = {
  derivada: "Derivada",
  valor: "Valor no ponto",
  tangente: "Reta tangente",
  criticos: "Pontos críticos e extremos",
  integral: "Integral definida (saldo)",
  area: "Área geométrica",
};

export function MathTools({
  chat,
  onStarted,
  notify,
  proposta,
}: {
  proposta?: string;
  chat: string;
  onStarted: () => void;
  notify: (s: string) => void;
}) {
  const [spec, setSpec] = useState<MathSpec>({
    expressao: "",
    inicio: "",
    fim: "",
    ponto: "",
    operacoes: ["grafico"],
  });
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (proposta)
      api<MathJob>("math_obter", { id: proposta })
        .then((j) => {
          if (j.tipo === "proposta" && j.estado === "concluida" && j.resultado)
            setSpec(j.resultado);
        })
        .catch((e) => notify(e.message));
  }, [proposta, notify]);
  const change = (field: keyof MathSpec, value: string) =>
    setSpec((s) => ({ ...s, [field]: value }));
  async function start() {
    setBusy(true);
    try {
      await api("math_executar", { conversa: chat, spec });
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
        Cálculos neste computador, sem IA ou internet. O gráfico e os resultados
        ficam salvos no chat.
      </p>
      <MathAI
        chat={chat}
        tipo="proposta"
        notify={notify}
        onResult={(r) => setSpec(r)}
      />
      <form
        onSubmit={(e) => {
          e.preventDefault();
          void start();
        }}
      >
        <Field
          label="Função f(x)"
          hint="Use x, +, -, *, /, potências inteiras e sin, cos, tan, sqrt, log, exp, abs. Trigonometria em radianos."
        >
          <input
            aria-label="Função f(x)"
            required
            maxLength={300}
            value={spec.expressao}
            onChange={(e) => change("expressao", e.target.value)}
            placeholder="x^2 - 4*x + 3"
          />
        </Field>
        <div className="math-grid">
          <Field label="Início do intervalo">
            <input
              aria-label="Início do intervalo"
              required
              maxLength={80}
              value={spec.inicio}
              onChange={(e) => change("inicio", e.target.value)}
              placeholder="-2"
            />
          </Field>
          <Field label="Fim do intervalo">
            <input
              aria-label="Fim do intervalo"
              required
              maxLength={80}
              value={spec.fim}
              onChange={(e) => change("fim", e.target.value)}
              placeholder="6"
            />
          </Field>
        </div>
        <fieldset className="math-operations">
          <legend>Além do gráfico</legend>
          {Object.entries(operations).map(([op, name]) => (
            <label key={op}>
              <input
                type="checkbox"
                checked={spec.operacoes.includes(op)}
                onChange={(e) =>
                  setSpec((s) => ({
                    ...s,
                    operacoes: e.target.checked
                      ? [...s.operacoes, op]
                      : s.operacoes.filter((v) => v !== op),
                  }))
                }
              />
              {name}
            </label>
          ))}
        </fieldset>
        {spec.operacoes.some((o) => ["valor", "tangente"].includes(o)) && (
          <Field label="Ponto x" hint="Necessário para valor e tangente.">
            <input
              aria-label="Ponto x"
              required
              maxLength={80}
              value={spec.ponto}
              onChange={(e) => change("ponto", e.target.value)}
              placeholder="3"
            />
          </Field>
        )}
        <p className="muted">
          Extremos: polinômios até grau 4. Integrais próprias em intervalo
          contínuo. Até 25 segundos por execução.
        </p>
        <div className="form-actions">
          <Button
            onClick={() =>
              setSpec({
                expressao: "x^2 - 4*x + 3",
                inicio: "-2",
                fim: "6",
                ponto: "3",
                operacoes: ["grafico", "derivada", "criticos", "tangente"],
              })
            }
          >
            Exemplo da parábola
          </Button>
          <Button
            type="submit"
            variant="primary"
            icon={ChartNoAxesCombined}
            disabled={busy}
          >
            {busy ? "Iniciando…" : "Calcular e salvar no chat"}
          </Button>
        </div>
      </form>
    </section>
  );
}

export function MathCard({
  id,
  chat,
  notify,
}: {
  id: string;
  chat: string;
  notify: (s: string) => void;
}) {
  const [job, setJob] = useState<MathJob | null>(null);
  useEffect(() => {
    let live = true;
    api<MathJob>("math_obter", { id })
      .then((j) => {
        if (live) setJob(j);
      })
      .catch((e) => notify(e.message));
    return () => {
      live = false;
    };
  }, [id, notify]);
  return (
    <section
      className="math-artifact"
      aria-label="Gráfico calculado localmente"
    >
      <Badge>Gráfico por amostragem numérica · {id.slice(0, 8)}</Badge>
      {!job ? (
        <Loading>Carregando gráfico salvo…</Loading>
      ) : job.imagem ? (
        <img
          src={job.imagem}
          alt="Gráfico da função e da reta tangente, quando solicitada. Domínio e resultados na mensagem acima."
        />
      ) : (
        <p role="alert">{job.aviso_artefato || "Gráfico indisponível."}</p>
      )}
      <MathAI chat={chat} tipo="explicacao" origem={id} notify={notify} />
      <Button
        icon={Download}
        disabled={!job?.imagem}
        onClick={() =>
          void api<{ exportado: boolean }>("math_exportar", { id })
            .then((r) => {
              if (r.exportado) notify("Gráfico exportado em PNG.");
            })
            .catch((e) => notify(e.message))
        }
      >
        Exportar PNG
      </Button>
    </section>
  );
}

function MathAI({
  chat,
  tipo,
  origem,
  notify,
  onResult,
}: {
  chat: string;
  tipo: "proposta" | "explicacao";
  origem?: string;
  notify: (s: string) => void;
  onResult?: (s: MathSpec) => void;
}) {
  const [pedido, setPedido] = useState("");
  const [job, setJob] = useState<MathJob | null>(null);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (job?.estado !== "executando") return;
    let live = true;
    const timer = setInterval(
      () =>
        void api<MathJob>("math_obter", { id: job.id })
          .then((r) => {
            if (!live) return;
            setJob(r);
            if (r.estado === "concluida" && tipo === "proposta" && r.resultado)
              onResult?.(r.resultado);
          })
          .catch((e) => {
            if (live) notify(e.message);
          }),
      1000,
    );
    return () => {
      live = false;
      clearInterval(timer);
    };
  }, [job?.id, job?.estado, tipo]);
  async function preview() {
    setBusy(true);
    try {
      setJob(
        await api<MathJob>("math_previa", {
          conversa: chat,
          tipo,
          pedido,
          origem,
        }),
      );
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function consult() {
    setBusy(true);
    try {
      setJob(await api<MathJob>("math_consultar", { id: job!.id }));
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const active = job?.estado === "executando";
  return (
    <details className="math-ai">
      <summary>
        {tipo === "proposta"
          ? "Preencher os campos com ajuda da IA"
          : "Explicar resultados com IA"}
      </summary>
      {tipo === "proposta" && (
        <Field
          label="Pedido para IA"
          hint="Inclua a função, o intervalo e o ponto desejados. Confira os parâmetros da proposta antes de calcular."
        >
          <textarea
            aria-label="Pedido para IA"
            value={pedido}
            maxLength={1500}
            disabled={active}
            onChange={(e) => {
              setPedido(e.target.value);
              setJob(null);
            }}
            placeholder="Trace f(x)=x^2-4*x+3 no intervalo [-2,6] e a tangente em x=3."
          />
        </Field>
      )}
      <Button
        icon={Sparkles}
        disabled={busy || active || (tipo === "proposta" && !pedido.trim())}
        onClick={() => void preview()}
      >
        {tipo === "proposta"
          ? "Preparar proposta da IA"
          : "Preparar explicação da IA"}
      </Button>
      {job?.previa && (
        <div className="math-ai-preview">
          <strong>{job.previa.destino}</strong>
          <p>{job.previa.aviso}</p>
          <details>
            <summary>Dados e instruções que serão enviados</summary>
            <pre>
              {job.previa.preparada.instrucoes +
                "\n\n" +
                job.previa.preparada.pergunta}
            </pre>
          </details>
          {job.estado === "previa" && (
            <Button
              variant="primary"
              disabled={busy}
              onClick={() => void consult()}
            >
              {tipo === "proposta"
                ? "Pedir proposta à IA"
                : "Pedir explicação à IA"}
            </Button>
          )}
        </div>
      )}
      {active && <Loading>Aguardando o provedor escolhido…</Loading>}
      {active && (
        <Button
          onClick={() =>
            void api("math_cancelar", { id: job!.id }).catch((e) =>
              notify(e.message),
            )
          }
        >
          Cancelar consulta
        </Button>
      )}
      {job?.erro && <p role="alert">{job.erro}</p>}
      {job?.estado === "concluida" && (
        <p role="status">
          {tipo === "proposta"
            ? "Proposta aplicada aos campos abaixo. Revise e preencha os parâmetros ausentes; nenhum cálculo foi executado."
            : "Explicação salva no chat. Os resultados locais permanecem separados."}
        </p>
      )}
    </details>
  );
}
