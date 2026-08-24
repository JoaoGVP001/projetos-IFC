import { describe, expect, it } from "vitest";
import { initialKnowledge } from "./knowledge-data";
import type { SourceCatalogItem } from "./source-catalog";
import { buildAiPreview, filterKnowledge, filterSources, normalizeSearchText } from "./workspace-logic";

const sampleSources: SourceCatalogItem[] = [
  {
    id: "help-1",
    title: "Consumo indevido",
    source: "Help.zip",
    system: "Interno",
    category: "Procedimentos",
    extension: ".txt",
    size_bytes: 120,
    status: "include",
    status_label: "Pronto para extração",
    reason_label: "Documento compatível com o MVP",
    masked_title: false,
  },
  {
    id: "bdc-small",
    title: "BDC Small Commerce",
    source: "Base externa",
    system: "Small Commerce",
    category: "Base de conhecimento",
    extension: "web",
    size_bytes: 0,
    status: "external",
    status_label: "Link oficial cadastrado",
    reason_label: "Aguarda autorização",
    masked_title: false,
    url: "https://example.com",
  },
];

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

  it("pesquisa fontes por título e filtra pelo estado", () => {
    expect(filterSources(sampleSources, "consumo", "include")).toHaveLength(1);
    expect(filterSources(sampleSources, "small", "external")[0].id).toBe("bdc-small");
    expect(filterSources(sampleSources, "consumo", "review")).toEqual([]);
  });
});
