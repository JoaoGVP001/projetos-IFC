import { afterEach, describe, it, expect, vi } from "vitest";
import { render, cleanup, fireEvent, screen } from "@testing-library/react";
import { Markdown, normalizarMatematica } from "./Markdown";
vi.mock("./bridge", () => ({ api: vi.fn(() => Promise.resolve()) }));
afterEach(cleanup);
describe("Markdown e matemática", () => {
  it("preserva uma citação literal com fence interno e LaTeX sem renderizar instruções", () => {
    const raw =
      "````text\n```\n# instrução documental\n\\(x>1\\) e [M99]\n````\n\n\\(y=2\\)";
    const normalized = normalizarMatematica(raw);
    expect(normalized).toContain("\\(x>1\\) e [M99]");
    expect(normalized).toContain("$y=2$");
    const { container } = render(<Markdown texto={raw} />);
    expect(container.querySelector("pre")?.textContent).toContain(
      "\\(x>1\\) e [M99]",
    );
    expect(container.querySelectorAll(".katex")).toHaveLength(1);
  });
  it("normaliza delimitadores preservando exemplos de código", () => {
    expect(normalizarMatematica(String.raw`\(x^2\)`)).toBe("$x^2$");
    expect(normalizarMatematica(String.raw`\[x^2\]`)).toContain("$$\nx^2\n$$");
    const code = "```tex\n\\(x^2\\)\n``` e `\\[x\\]`";
    expect(normalizarMatematica(code)).toBe(code);
  });
  it("renderiza títulos, tabelas e os quatro delimitadores matemáticos", () => {
    const { container } = render(
      <Markdown
        texto={
          "## Conceito\n\n$x^2$\n\n$$\ny=2x\n$$\n\n\\(x+1\\)\n\n\\[z=3\\]\n\n| Item | Valor |\n|---|---|\n| A | 1 |"
        }
      />,
    );
    expect(screen.getByRole("heading", { name: "Conceito" })).toBeTruthy();
    expect(container.querySelectorAll(".katex")).toHaveLength(4);
    expect(container.querySelector(".table-scroll table")).toBeTruthy();
  });
  it("não executa HTML, scripts, eventos nem links JavaScript", () => {
    const { container } = render(
      <Markdown
        texto={
          '<script>window.pywebview.api.request("exec",{})</script>\n\n<img src=x onerror=alert(1)>\n\n[malicioso](javascript:alert(1))'
        }
      />,
    );
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("[onerror]")).toBeNull();
    expect(container.innerHTML).not.toContain('href="javascript:');
  });
  it("oferece fórmula inválida legível e bloqueia comandos LaTeX com HTML", () => {
    const { container } = render(
      <Markdown
        texto={String.raw`$\comandoInexistente{x}$ e $\htmlClass{ponte}{x}$`}
      />,
    );
    expect(container.textContent).toContain("comandoInexistente");
    expect(container.querySelector(".ponte")).toBeNull();
  });
  it("abre links pela operação restrita da ponte", async () => {
    const { api } = await import("./bridge");
    render(<Markdown texto="[Fonte](https://example.com)" />);
    fireEvent.click(screen.getByRole("link", { name: "Fonte" }));
    expect(api).toHaveBeenCalledWith("abrir_link", {
      url: "https://example.com",
    });
  });
});
