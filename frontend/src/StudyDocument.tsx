import { useEffect, useRef, useState } from "react";
import { Markdown, normalizarMatematica } from "./Markdown";
import { api } from "./bridge";
import katex from "katex";
import type { PageRender } from "./pages-model";

const origins = {
  usuario: "Texto do usuário",
  ia: "Explicação da IA · revise",
  ferramenta: "Resultado da ferramenta local · escopo limitado",
};
export function validateNotation(text: string) {
  const prose = normalizarMatematica(text)
    .replace(/(`{3,}[\s\S]*?`{3,}|~{3,}[\s\S]*?~{3,}|`+[^`\n]*`+)/g, "")
    .replace(/\\\$/g, "");
  if (
    (prose.match(/\$\$/g) || []).length % 2 ||
    (prose.replace(/\$\$[\s\S]*?\$\$/g, "").match(/\$/g) || []).length % 2
  )
    throw Error(
      "Delimitadores de fórmula incompletos. Use $...$ ou $$...$$, e \\$ para valores monetários.",
    );
}
export async function readyDocument(root: HTMLElement) {
  await new Promise<void>((r) => setTimeout(r, 50));
  await document.fonts.ready;
  await Promise.all(
    Array.from(root.querySelectorAll("img")).map(async (img) => {
      if (img.complete && img.naturalWidth) return;
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(
          () => reject(Error("Imagem indisponível; exportação interrompida.")),
          10000,
        );
        img.onload = () => {
          clearTimeout(timeout);
          img.naturalWidth ? resolve() : reject(Error("Imagem inválida."));
        };
        img.onerror = () => {
          clearTimeout(timeout);
          reject(Error("Imagem indisponível; exportação interrompida."));
        };
      });
    }),
  );
  for (const annotation of Array.from(
    root.querySelectorAll('annotation[encoding="application/x-tex"]'),
  )) {
    try {
      katex.renderToString(annotation.textContent || "", {
        throwOnError: true,
        trust: false,
        strict: "ignore",
      });
    } catch {
      throw Error("Há fórmula inválida. Corrija-a antes de exportar.");
    }
  }
  if (root.querySelector(".katex-error"))
    throw Error("Há fórmula inválida. Corrija-a antes de exportar.");
}
// Somente nós já sanitizados pelo Markdown/KaTeX são clonados; não há HTML recebido pela ponte.
export function paginate(
  source: HTMLElement,
  target: HTMLElement,
  data: PageRender,
) {
  target.replaceChildren();
  let body!: HTMLElement;
  let sheets: HTMLElement[] = [];
  let warnings: string[] = [];
  function newSheet() {
    if (sheets.length >= 20)
      throw Error(
        "O documento excede vinte folhas. Divida a página de estudo.",
      );
    const sheet = document.createElement("article");
    sheet.className = "study-sheet paper-" + data.conteudo.fundo;
    const header = document.createElement("header");
    header.textContent =
      (data.materia || "CadernoMat") + " · " + data.conteudo.titulo;
    sheet.append(header);
    body = document.createElement("div");
    body.className = "study-sheet-body";
    sheet.append(body);
    const footer = document.createElement("footer");
    sheet.append(footer);
    target.append(sheet);
    sheets.push(sheet);
  }
  newSheet();
  const over = () => body.scrollHeight > body.clientHeight + 1;
  function append(node: HTMLElement) {
    body.append(node);
    // Uma fórmula larga pode reduzir até 20%, sem reduzir o documento inteiro.
    for (const math of Array.from(
      node.querySelectorAll<HTMLElement>(".katex"),
    )) {
      const natural = Math.max(
        math.scrollWidth,
        math.getBoundingClientRect().width,
        ...Array.from(
          math.querySelectorAll<HTMLElement>(".katex-base,.base"),
        ).map((x) => x.getBoundingClientRect().width),
      );
      const ratio = body.clientWidth / natural;
      if (ratio < 0.8)
        throw Error(
          "Fórmula muito larga para A4. Divida-a usando alinhamento ou etapas menores.",
        );
      if (ratio < 0.99) {
        math.style.fontSize =
          parseFloat(getComputedStyle(math).fontSize) * ratio + "px";
        warnings.push(
          "Uma fórmula foi ajustada para caber na largura da folha.",
        );
      }
    }
    if (node.scrollWidth > body.clientWidth + 2)
      throw Error(
        "Elemento muito largo para A4. Divida a tabela, fórmula ou linha de código.",
      );
    if (over() && body.children.length > 1) {
      node.remove();
      newSheet();
      body.append(node);
    }
    if (over())
      throw Error(
        "Um bloco não cabe na folha. Divida o parágrafo, lista ou equação em blocos menores.",
      );
  }
  function table(original: HTMLTableElement) {
    const rows = Array.from(original.tBodies).flatMap((b) =>
      Array.from(b.rows),
    );
    let current!: HTMLTableElement;
    const create = () => {
      current = original.cloneNode(false) as HTMLTableElement;
      if (original.tHead) current.append(original.tHead.cloneNode(true));
      current.append(document.createElement("tbody"));
      body.append(current);
    };
    create();
    for (const row of rows) {
      const copy = row.cloneNode(true) as HTMLTableRowElement;
      current.tBodies[0].append(copy);
      if (current.scrollWidth > body.clientWidth + 2)
        throw Error(
          "Tabela muito larga para A4. Reduza a quantidade de colunas.",
        );
      if (over()) {
        copy.remove();
        if (!current.tBodies[0].rows.length) current.remove();
        newSheet();
        create();
        current.tBodies[0].append(copy);
        if (over()) throw Error("Uma linha da tabela não cabe em uma folha.");
      }
    }
  }
  const blocks = Array.from(source.children) as HTMLElement[];
  for (let i = 0; i < blocks.length; i++) {
    const original = blocks[i];
    if (original.matches("table")) {
      table(original as HTMLTableElement);
      continue;
    }
    if (original.matches("ul,ol") && original.children.length > 1) {
      let number = Number(original.getAttribute("start") || 1);
      for (const li of Array.from(original.children)) {
        const list = original.cloneNode(false) as HTMLElement;
        if (list.tagName === "OL") list.setAttribute("start", String(number++));
        list.append(li.cloneNode(true));
        append(list);
      }
      continue;
    }
    // Mantém títulos com o início do próximo bloco.
    if (
      /^H[1-6]$/.test(original.tagName) &&
      body.children.length &&
      body.clientHeight -
        (body.lastElementChild instanceof HTMLElement
          ? body.lastElementChild.offsetTop +
            body.lastElementChild.offsetHeight +
            parseFloat(
              getComputedStyle(body.lastElementChild).marginBottom || "0",
            )
          : 0) <
        110
    )
      newSheet();
    append(original.cloneNode(true) as HTMLElement);
  }
  sheets.forEach(
    (sheet, i) =>
      (sheet.querySelector("footer")!.textContent =
        "CadernoMat · versão " +
        data.versao +
        " · " +
        (i + 1) +
        " / " +
        sheets.length),
  );
  return {
    folhas: sheets.length,
    avisos: Array.from(new Set([...(data.avisos || []), ...warnings])),
  };
}
export function StudyDocument({
  data,
  onReady,
}: {
  data: PageRender;
  onReady?: (s: {
    ok: boolean;
    folhas?: number;
    erro?: string;
    avisos?: string[];
  }) => void;
}) {
  const source = useRef<HTMLDivElement>(null),
    target = useRef<HTMLDivElement>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let live = true;
    setError("");
    (async () => {
      try {
        for (const section of data.conteudo.secoes)
          validateNotation(section.texto);
        for (const resource of Object.values(data.recursos))
          validateNotation(resource.resumo);
        await readyDocument(source.current!);
        if (!live) return;
        // Flatten Markdown containers while preserving safe rendered blocks.
        const flat = document.createElement("div");
        for (const section of Array.from(source.current!.children)) {
          for (const child of Array.from(section.children)) {
            if (child.classList.contains("markdown")) {
              for (const item of Array.from(child.children)) {
                if (item.classList.contains("table-scroll")) {
                  flat.append(item.firstElementChild!.cloneNode(true));
                } else flat.append(item.cloneNode(true));
              }
            } else flat.append(child.cloneNode(true));
          }
        }
        const result = paginate(flat, target.current!, data);
        onReady?.({ ok: true, ...result });
      } catch (e) {
        if (live) {
          setError((e as Error).message);
          onReady?.({ ok: false, erro: (e as Error).message });
        }
      }
    })();
    return () => {
      live = false;
    };
  }, [data]);
  return (
    <div
      className="study-document"
      onClick={(e) => {
        const a = (e.target as Element).closest("a");
        if (a) {
          e.preventDefault();
          const url = a.getAttribute("href");
          if (url && !onReady)
            void api("abrir_link", { url }).catch((e) => setError(e.message));
        }
      }}
    >
      {error && (
        <p role="alert" className="notice">
          {error}
        </p>
      )}
      <div ref={source} className="study-source" aria-hidden="true">
        <section>
          <h1>{data.conteudo.titulo}</h1>
          {data.conteudo.assunto && <p>{data.conteudo.assunto}</p>}
        </section>
        {data.conteudo.secoes.map((s) => (
          <section key={s.id}>
            {s.titulo && <h2>{s.titulo}</h2>}
            <p className="page-origin">{origins[s.origem]}</p>
            {s.recurso && data.recursos[s.recurso] && (
              <>
                <Markdown texto={data.recursos[s.recurso].resumo} semImagens />
                {data.recursos[s.recurso].imagem && (
                  <figure>
                    <img
                      src={data.recursos[s.recurso].imagem!}
                      alt={data.recursos[s.recurso].rotulo}
                    />
                    <figcaption>{data.recursos[s.recurso].rotulo}</figcaption>
                  </figure>
                )}
              </>
            )}
            <Markdown texto={s.texto} semImagens />
          </section>
        ))}
        {!!data.origens?.length && (
          <section>
            <h2>Origem dos registros</h2>
            <ul>
              {data.origens.map((o, i) => (
                <li key={i}>
                  {o.titulo} · {o.tipo}
                  {o.versao ? ` · versão ${o.versao}` : ""}
                  {o.questao ? ` · questão ${o.questao}` : ""} · registro{" "}
                  {String(o.id).slice(0, 8)}
                </li>
              ))}
            </ul>
          </section>
        )}
        {!!data.referencias?.length && (
          <section>
            <h2>Referências e origem dos materiais</h2>
            <ul>
              {data.referencias.map((r, i) => (
                <li key={i}>
                  {r.nome}
                  {r.pagina ? ` · ${r.unidade || "página"} ${r.pagina}` : ""}
                  {r.origem && <span> · {r.origem}</span>}
                  {r.aviso && <span> · Limitação da extração: {r.aviso}</span>}
                </li>
              ))}
            </ul>
          </section>
        )}
        {!!data.avisos?.length && (
          <section>
            <h2>Observações</h2>
            <ul>
              {data.avisos.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
      <div
        ref={target}
        className="study-sheets"
        aria-label="Folhas de estudo"
      />
    </div>
  );
}
export function PageExport() {
  const [data, setData] = useState<PageRender | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    fetch("payload.json")
      .then((r) => {
        if (!r.ok) throw Error("Dados indisponíveis.");
        return r.json();
      })
      .then(setData)
      .catch((e) => {
        setError(e.message);
        window.cadernoMatExportStatus = { ok: false, erro: e.message };
      });
  }, []);
  return data ? (
    <StudyDocument
      data={data}
      onReady={(s) => {
        window.cadernoMatExportStatus = s;
      }}
    />
  ) : (
    <p>{error || "Preparando folhas…"}</p>
  );
}

export function PageChatPreview({
  id,
  notify,
  onOpen,
}: {
  id: string;
  notify: (s: string) => void;
  onOpen: (p: import("./pages-model").Page) => void;
}) {
  const [page, setPage] = useState<import("./pages-model").Page | null>(null);
  useEffect(() => {
    let live = true;
    void api<import("./pages-model").Page>("pagina_obter", { id })
      .then((p) => {
        if (live) setPage(p);
      })
      .catch((e) => notify(e.message));
    return () => {
      live = false;
    };
  }, [id]);
  return page ? (
    <>
      <button className="button soft" onClick={() => onOpen(page)}>
        Abrir editor da página
      </button>
      <p className="muted">
        Prévia do rascunho atual. Versões salvas estão disponíveis no editor.
      </p>
      <div className="paper-viewport">
        <StudyDocument data={page.render} />
      </div>
    </>
  ) : (
    <p>Carregando página…</p>
  );
}
