import { useEffect, useState } from "react";
import { Database, Square } from "lucide-react";
import { api } from "./bridge";
import { Button } from "./ui";
import type { StatusSemantica } from "./model";

export function BuscaSemantica({
  revisao,
  occupied,
  run,
  notify,
}: {
  revisao: number;
  occupied: boolean;
  run: (op: string, d?: Record<string, unknown>) => Promise<boolean>;
  notify: (message: string) => void;
}) {
  const [status, setStatus] = useState<StatusSemantica | null>(null);
  const [url, setUrl] = useState("http://127.0.0.1:11434");
  useEffect(() => {
    let live = true;
    api<StatusSemantica>("semantica_status", {})
      .then((s) => {
        if (live) {
          setStatus(s);
          setUrl(s.url);
        }
      })
      .catch((e) => {
        if (live) notify(e.message);
      });
    return () => {
      live = false;
    };
  }, [revisao, notify]);
  const indexing = status?.trabalho?.estado === "executando";
  return (
    <details className="semantic-panel">
      <summary>
        <Database size={17} /> Busca local por significado
        <span>
          {status
            ? `${status.indexados}/${status.total} trechos · ${indexing ? "indexando" : status.habilitada ? "ativada" : "desativada"}`
            : "carregando…"}
        </span>
      </summary>
      <p>
        Indexar gera vetores dos textos extraídos da biblioteca neste
        computador. Isso não seleciona materiais para a IA. Chats e atividades
        continuam usando apenas as fontes que você autorizar.
      </p>
      <p className="muted">
        Modelo: {status?.modelo || "qwen3-embedding:0.6b"} · CPU · lotes de 4.
        Instale o modelo no Ollama antes de indexar. Não há download automático
        nem envio a Gemini/OpenAI para esta busca.
      </p>
      <div className="semantic-actions">
        <label>
          Servidor local de busca
          <input
            aria-label="Servidor local de busca"
            value={url}
            disabled={occupied}
            onChange={(e) => setUrl(e.target.value)}
            maxLength={200}
          />
        </label>
        <Button
          icon={Database}
          disabled={occupied || !status || !status.total}
          onClick={() =>
            void run("semantica_indexar", { confirmado: true, url })
          }
        >
          Indexar / retomar e ativar
        </Button>
        {indexing && (
          <Button icon={Square} onClick={() => void run("semantica_cancelar")}>
            Cancelar indexação
          </Button>
        )}
      </div>
      <label className="filter-checkbox">
        <input
          type="checkbox"
          aria-label="Usar busca híbrida nos chats e no estudo"
          checked={!!status?.habilitada}
          disabled={occupied || !status}
          onChange={(e) =>
            void run("semantica_ativar", { valor: e.target.checked })
          }
        />
        Usar busca híbrida nos chats e no estudo
      </label>
      {status?.trabalho && (
        <p role="status">
          {status.trabalho.estado} · {status.trabalho.feitos}/
          {status.trabalho.total} trechos
          {status.trabalho.erro ? ` · ${status.trabalho.erro}` : ""}
        </p>
      )}
      <p className="muted">
        A preparação incompleta não substitui o índice publicado. Excluir ou
        reprocessar materiais remove seus vetores. Semelhança é uma pista de
        relevância, não uma verificação matemática.
      </p>
    </details>
  );
}
