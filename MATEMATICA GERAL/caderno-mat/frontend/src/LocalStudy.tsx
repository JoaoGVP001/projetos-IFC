import { useEffect, useState } from "react";
import { api } from "./bridge";
import { Button, Field } from "./ui";
import type { Mensagem, Orcamento } from "./model";
export type AjustePrevia = {
  id: string;
  acao: string;
  provedor: string;
  modelo: string;
  pergunta: string;
  instrucoes: string;
  fontes: unknown[] | null;
  orcamento: Orcamento | null;
  origem: number;
};
export function ResponseStatus({ m }: { m: Mensagem }) {
  const x = m.metricas;
  return (
    <>
      {x?.qualidade && (
        <div
          className="response-warning"
          role="status"
          data-quality={x.qualidade.estado}
        >
          <strong>{x.qualidade.titulo}</strong>
          <p>{x.qualidade.aviso}</p>
          <small>
            Verificação matemática: {x.qualidade.verificacao_matematica}.
          </small>
          {x.consulta_modelo === false && (
            <p>Processamento local · nenhuma chamada ao modelo.</p>
          )}
          {x.qualidade.rascunho_recusado && (
            <details>
              <summary>
                Rascunho recusado · diagnóstico, não usar como resposta
              </summary>
              <pre className="source-preview">
                {x.qualidade.rascunho_recusado}
              </pre>
              {x.qualidade.rascunho_abreviado && (
                <p>Rascunho abreviado no registro.</p>
              )}
            </details>
          )}
        </div>
      )}
      {m.interrupcao && x?.qualidade?.estado !== "recusada" && (
        <div className="response-warning" role="status">
          <strong>
            Resposta interrompida · {m.interrupcao.motivo?.replaceAll("_", " ")}
          </strong>
          <p>{m.interrupcao.mensagem}</p>
          <small>O conteúdo acima é parcial e precisa de revisão.</small>
        </div>
      )}
      {m.origem_consulta && (
        <p className="muted">
          Parte vinculada à consulta anterior.{" "}
          {m.origem_mensagem && (
            <button
              className="button ghost"
              onClick={() =>
                document
                  .getElementById(`mensagem-${m.origem_mensagem}`)
                  ?.scrollIntoView({ behavior: "smooth", block: "start" })
              }
            >
              Ver resposta de origem
            </button>
          )}
        </p>
      )}
      {x &&
        x.consulta_modelo !== false &&
        Object.keys(x).some(
          (k) => !["qualidade", "consulta_modelo", "motivo"].includes(k),
        ) && (
          <details className="response-metrics">
            <summary>Detalhes da execução</summary>
            <p>
              {x.modelo || m.modelo} · {x.perfil || "perfil anterior"} ·{" "}
              {x.dispositivo?.processador || "dispositivo desconhecido"}
            </p>
            <p>
              {typeof x.segundos === "number"
                ? `${x.segundos.toFixed(1)} s`
                : "Duração indisponível"}{" "}
              · saída {x.tokens_saida ?? "não informada"}/{x.num_predict ?? "?"}{" "}
              tokens ·{" "}
              {typeof x.tokens_s === "number"
                ? `${x.tokens_s.toFixed(1)} tokens/s`
                : "Velocidade indisponível"}
            </p>
            <p>
              Encerramento:{" "}
              {x.done_reason ??
                (x.frame_final
                  ? "motivo não informado"
                  : "frame final não recebido")}
              . Primeiro conteúdo:{" "}
              {typeof x.primeiro_token_s === "number"
                ? `${x.primeiro_token_s.toFixed(1)} s`
                : "não medido"}
              .
            </p>
            <p>
              Carregamento:{" "}
              {x.carga_s == null ? "não medido" : x.carga_s.toFixed(1) + " s"} ·
              entrada:{" "}
              {x.entrada_s == null
                ? "não medida"
                : x.entrada_s.toFixed(1) + " s"}{" "}
              · geração:{" "}
              {x.geracao_s == null
                ? "não medida"
                : x.geracao_s.toFixed(1) + " s"}
              .
            </p>
            {x.memoria && (
              <p>
                RAM disponível mínima:{" "}
                {x.memoria.ram_disponivel_min == null
                  ? "não medida"
                  : (x.memoria.ram_disponivel_min / 2 ** 30).toFixed(1) +
                    " GiB"}{" "}
                · swap máxima observada:{" "}
                {x.memoria.swap_usada_max == null
                  ? "não medida"
                  : (x.memoria.swap_usada_max / 2 ** 30).toFixed(1) + " GiB"}
                . Valores amostrados, não pico exato.
              </p>
            )}
          </details>
        )}
    </>
  );
}
export function Adjustment({
  data,
  onSend,
}: {
  data: AjustePrevia;
  onSend: () => Promise<unknown>;
}) {
  const [busy, setBusy] = useState(false);
  return (
    <>
      <p>
        {data.acao === "curta"
          ? "Repetir de forma curta"
          : "Pedir a próxima parte"}{" "}
        · {data.provedor} · {data.modelo}
      </p>
      <p>
        Sem originais nem histórico completo. Somente os dados exibidos abaixo
        serão consultados.
      </p>
      {data.orcamento && (
        <p>
          Perfil: {data.orcamento.perfil_nome} · saída até{" "}
          {data.orcamento.reserva_saida} tokens · tempo limite{" "}
          {data.orcamento.timeout} s.
        </p>
      )}
      <details open>
        <summary>Dados e contexto enviados</summary>
        <pre className="source-preview">{data.pergunta}</pre>
      </details>
      <details>
        <summary>Instruções e trechos autorizados</summary>
        <pre className="source-preview">
          {data.instrucoes + "\n\n" + JSON.stringify(data.fontes, null, 2)}
        </pre>
      </details>
      <Button
        variant="primary"
        disabled={busy}
        onClick={() => {
          setBusy(true);
          void onSend().finally(() => setBusy(false));
        }}
      >
        Enviar esta parte
      </Button>
    </>
  );
}
export function InductionForm({
  chat,
  done,
  notify,
}: {
  chat: string;
  done: () => void;
  notify: (s: string) => void;
}) {
  const [title, setTitle] = useState("Princípio de indução"),
    [proposition, setProposition] = useState(
      "P(n): soma de 0 até n = n(n+1)/2",
    ),
    [start, setStart] = useState(0),
    [busy, setBusy] = useState(false);
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        setBusy(true);
        void api("inducao_executar", {
          conversa: chat,
          spec: { titulo: title, proposicao: proposition, inicio: start },
        })
          .then(done)
          .catch((e) => {
            notify(e.message);
            setBusy(false);
          });
      }}
    >
      <p>
        Ilustração feita por código local. Não verifica a proposição nem
        substitui sua demonstração.
      </p>
      <Field label="Título da ilustração">
        <input
          aria-label="Título da ilustração"
          value={title}
          maxLength={80}
          onChange={(e) => setTitle(e.target.value)}
        />
      </Field>
      <Field label="Proposição (texto simples)">
        <input
          aria-label="Proposição da ilustração"
          value={proposition}
          maxLength={120}
          onChange={(e) => setProposition(e.target.value)}
        />
      </Field>
      <Field label="Índice inicial">
        <input
          aria-label="Índice inicial"
          type="number"
          min={0}
          max={100}
          step={1}
          value={start}
          onChange={(e) => setStart(Number(e.target.value))}
        />
      </Field>
      <Button variant="primary" type="submit" disabled={busy}>
        Criar ilustração local
      </Button>
    </form>
  );
}
export function InductionCard({
  id,
  notify,
}: {
  id: string;
  notify: (s: string) => void;
}) {
  const [image, setImage] = useState<string | null>(null);
  useEffect(() => {
    let live = true;
    void api<{ imagem: string }>("inducao_obter", { id })
      .then((r) => {
        if (live) setImage(r.imagem);
      })
      .catch((e) => notify(e.message));
    return () => {
      live = false;
    };
  }, [id]);
  return image ? (
    <figure className="induction-figure">
      <img
        src={image}
        alt="Base, hipótese e passo para todo k; ilustração conceitual do princípio de indução"
      />
      <figcaption>
        Ilustração local · sem verificação da demonstração. Use Criar página de
        estudo para salvar/exportar.
      </figcaption>
    </figure>
  ) : null;
}
