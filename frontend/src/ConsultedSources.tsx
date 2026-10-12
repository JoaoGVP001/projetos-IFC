import { useState } from "react";
import { api } from "./bridge";
import { Button, Loading } from "./ui";

export type StudyOrigin = { mensagem: number; pedido: string };
type Source = {
  referencia: string;
  nome: string;
  texto: string;
  tipo: string;
  pagina?: number | null;
  metodo?: string;
  aviso?: string;
  url?: string;
  unidade: string;
  citada: boolean;
  aviso_atual: string;
  estado_atual: string;
  original_disponivel: boolean;
  hash_enviado?: string;
  envio_exato: boolean;
  origem_titulo?: string;
  proveniencia?: { original: string; extracao: string };
};
type Sources = {
  consulta_modelo?: boolean | null;
  estado?: string;
  mensagem: number;
  pergunta: string;
  fontes: Source[];
  envio_exato: boolean;
  aviso: string;
};
export function ConsultedSources({
  mensagem,
  editable,
  notify,
  onCheck,
}: {
  mensagem: number;
  editable: boolean;
  notify: (s: string) => void;
  onCheck: (tipo: "matematica" | "discreta", origem: StudyOrigin) => void;
}) {
  const [data, setData] = useState<Sources | null>(null),
    [error, setError] = useState("");
  const [images, setImages] = useState<
    Record<string, { imagem?: string; aviso_previa?: string }>
  >({});
  async function load() {
    try {
      setData(await api("consulta_fontes", { mensagem }));
      setError("");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <details
      className="consulted-sources"
      onToggle={(e) => {
        if (e.currentTarget.open) void load();
      }}
    >
      <summary>Conferir fontes e operações</summary>
      <p>
        Explicação da IA · requer revisão. Um trecho citado ou uma conta
        conferida não certifica toda a resposta.
      </p>
      {error ? (
        <p role="alert">{error}</p>
      ) : !data ? (
        <Loading />
      ) : (
        <>
          <p className="notice">{data.aviso}</p>
          {!data.envio_exato && (
            <p role="status">
              Registro legado: não é possível garantir que todos os trechos do
              snapshot foram enviados integralmente.
            </p>
          )}
          {!data.fontes.length && (
            <p>Nenhum trecho documental foi enviado nesta consulta.</p>
          )}
          {data.fontes.map((f) => (
            <section key={f.referencia}>
              <h3>
                [{f.referencia}] {f.nome}
                {f.pagina &&
                (f.tipo === "pdf" ||
                  f.tipo === "pptx" ||
                  f.metodo?.includes("PDF"))
                  ? ` · ${f.unidade} ${f.pagina}`
                  : ""}
              </h3>
              <p>
                {f.citada
                  ? "Referência marcada na resposta"
                  : "Trecho disponibilizado · sem citação na resposta"}{" "}
                · {f.metodo || "Método não registrado"}
              </p>
              {f.origem_titulo && <p>Origem: {f.origem_titulo}</p>}
              {f.aviso && (
                <p className="notice">Limitação da extração: {f.aviso}</p>
              )}
              {f.aviso_atual && <p role="status">{f.aviso_atual}</p>}
              <strong>
                {data.consulta_modelo === false
                  ? "Trecho preparado · não enviado ao modelo"
                  : data.estado && data.estado !== "ok"
                    ? "Trecho preparado no snapshot · envio/conclusão não confirmados"
                    : f.envio_exato
                      ? "Trecho exato enviado"
                      : "Trecho preservado no snapshot"}
              </strong>
              <pre>{f.texto}</pre>
              <details>
                <summary>Identidade e integridade do trecho</summary>
                <pre>
                  {JSON.stringify(
                    {
                      hash_enviado: f.hash_enviado,
                      origem: f.proveniencia,
                      estado_atual: f.estado_atual,
                    },
                    null,
                    2,
                  )}
                </pre>
              </details>
              <div className="form-actions">
                <Button
                  disabled={!f.original_disponivel}
                  onClick={() =>
                    void api("consulta_original", {
                      mensagem,
                      referencia: f.referencia,
                    }).catch((e) => notify(e.message))
                  }
                >
                  {f.url ? "Abrir link atual" : "Abrir arquivo original"}
                </Button>
                {f.original_disponivel &&
                  ["pdf", "imagem"].includes(f.tipo) && (
                    <Button
                      onClick={() =>
                        void api<{ imagem?: string; aviso_previa?: string }>(
                          "consulta_pagina",
                          { mensagem, referencia: f.referencia },
                        )
                          .then((r) =>
                            setImages((s) => ({ ...s, [f.referencia]: r })),
                          )
                          .catch((e) => notify(e.message))
                      }
                    >
                      Ver página do original
                    </Button>
                  )}
              </div>
              <p className="muted">
                O visualizador externo pode exigir selecionar a página
                manualmente.
                {f.url ? " O conteúdo do link atual pode ter mudado." : ""}
              </p>
              {images[f.referencia]?.imagem && (
                <img
                  className="source-original"
                  src={images[f.referencia].imagem}
                  alt={`Original de ${f.nome}, página ${f.pagina || 1}`}
                />
              )}
              {images[f.referencia]?.aviso_previa && (
                <p role="alert">{images[f.referencia].aviso_previa}</p>
              )}
            </section>
          ))}
          <p>
            Escolha uma operação suportada, confira os parâmetros e execute pela
            ferramenta. Demonstrações gerais continuam exigindo revisão.
          </p>
          <div className="form-actions">
            {(["matematica", "discreta"] as const).map((tipo) => (
              <Button
                key={tipo}
                disabled={!editable}
                onClick={() =>
                  onCheck(tipo, { mensagem, pedido: data.pergunta })
                }
              >
                {tipo === "matematica"
                  ? "Conferir operação de Cálculo"
                  : "Conferir operação de Discreta"}
              </Button>
            ))}
          </div>
        </>
      )}
    </details>
  );
}
