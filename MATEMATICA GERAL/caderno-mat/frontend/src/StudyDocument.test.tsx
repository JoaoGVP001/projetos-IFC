import { afterEach, it, expect, vi } from "vitest";
import { render, cleanup, waitFor } from "@testing-library/react";
import { StudyDocument, paginate, validateNotation } from "./StudyDocument";
import type { PageRender } from "./pages-model";
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
const data: PageRender = {
  conteudo: { titulo: "Lógica", assunto: "", fundo: "branco", secoes: [] },
  materia: "Discreta",
  versao: 1,
  recursos: {},
};
it("divide tabela longa repetindo o cabeçalho e mantém título com o início do texto", () => {
  const height = (e: HTMLElement): number =>
    e.tagName === "TABLE"
      ? e.querySelectorAll("tr").length * 24
      : e.tagName.startsWith("H")
        ? 35
        : 25;
  vi.spyOn(HTMLElement.prototype, "clientHeight", "get").mockImplementation(
    function (this: HTMLElement) {
      return this.classList.contains("study-sheet-body") ? 300 : height(this);
    },
  );
  vi.spyOn(HTMLElement.prototype, "scrollHeight", "get").mockImplementation(
    function (this: HTMLElement) {
      return this.classList.contains("study-sheet-body")
        ? Math.max(
            300,
            Array.from(this.children).reduce(
              (n, e) => n + height(e as HTMLElement),
              0,
            ),
          )
        : height(this);
    },
  );
  vi.spyOn(HTMLElement.prototype, "clientWidth", "get").mockReturnValue(700);
  vi.spyOn(HTMLElement.prototype, "scrollWidth", "get").mockReturnValue(700);
  vi.spyOn(HTMLElement.prototype, "offsetHeight", "get").mockImplementation(
    function (this: HTMLElement) {
      return height(this);
    },
  );
  vi.spyOn(HTMLElement.prototype, "offsetTop", "get").mockReturnValue(0);
  const source = document.createElement("div");
  source.innerHTML =
    "<h1>Título</h1><p>Enunciado</p><h2>Tabela</h2><table><thead><tr><th>p</th><th>Resultado</th></tr></thead><tbody>" +
    Array.from({ length: 64 }, () => "<tr><td>V</td><td>F</td></tr>").join("") +
    "</tbody></table>";
  const target = document.createElement("div");
  document.body.append(target);
  const result = paginate(source, target, data);
  expect(result.folhas).toBeGreaterThan(1);
  expect(target.querySelectorAll("tbody tr")).toHaveLength(64);
  expect(target.querySelectorAll("thead")).toHaveLength(result.folhas);
  expect(target.querySelector(".study-sheet h1")?.textContent).toBe("Título");
  target.remove();
});
it("fórmula inválida impede publicar uma prévia concluída", async () => {
  Object.defineProperty(document, "fonts", {
    configurable: true,
    value: { ready: Promise.resolve() },
  });
  const ready = vi.fn();
  render(
    <StudyDocument
      data={{
        ...data,
        conteudo: {
          ...data.conteudo,
          secoes: [
            {
              id: "s",
              titulo: "Teste",
              texto: "$\\comandoinexistente{x}$",
              origem: "usuario",
            },
          ],
        },
      }}
      onReady={ready}
    />,
  );
  await waitFor(() =>
    expect(ready).toHaveBeenCalledWith(
      expect.objectContaining({
        ok: false,
        erro: expect.stringContaining("fórmula inválida"),
      }),
    ),
  );
});

it("delimitadores incompletos são recusados e código/dólar escapado são preservados", () => {
  expect(() => validateNotation("$$x^2")).toThrow(/Delimitadores/);
  expect(() => validateNotation("$x^2")).toThrow(/Delimitadores/);
  expect(() => validateNotation("`$variavel` e \\$10")).not.toThrow();
  expect(() => validateNotation("$$x^2$$ e $x<y>z$")).not.toThrow();
});
