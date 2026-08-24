import { describe, expect, it } from "vitest";
import { initialKnowledge } from "./knowledge-data";
import { buildAiPreview, filterKnowledge, normalizeSearchText } from "./workspace-logic";

describe("workspace logic", () => {
  it("normaliza acentos e caixa para a pesquisa", () => {
    expect(normalizeSearchText("  Rejeição CNPJ  ")).toBe("rejeicao cnpj");
  });

  it("pesquisa por palavras distribuídas nos metadados", () => {
    const result = filterKnowledge(initialKnowledge, "status sefaz", "Todos");
    expect(result.map((item) => item.id)).toEqual(["small-status-servico"]);
  });

  it("respeita o filtro de sistema antes de mostrar resultados", () => {
    const result = filterKnowledge(initialKnowledge, "rejeição", "ZWeb");
    expect(result).toHaveLength(1);
    expect(result[0].system).toBe("ZWeb");
  });

  it("recusa uma resposta quando não encontra evidência", () => {
    const preview = buildAiPreview("erro completamente inexistente xyz", initialKnowledge, "Todos");
    expect(preview.status).toBe("insufficient");
    expect(preview.sources).toEqual([]);
  });
});

