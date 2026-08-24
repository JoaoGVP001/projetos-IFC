import { describe, expect, it } from "vitest";
import { reciprocalRankFusion } from "./hybrid-ranking";

describe("reciprocalRankFusion", () => {
  it("combina resultados textuais e vetoriais sem misturar as escalas", () => {
    const result = reciprocalRankFusion(["a", "b", "c"], ["b", "d", "a"]);

    expect(result.map((item) => item.id)).toEqual(["b", "a", "d", "c"]);
    expect(result[0]).toMatchObject({ textRank: 2, vectorRank: 1 });
  });

  it("ignora identificadores duplicados dentro da mesma lista", () => {
    const result = reciprocalRankFusion(["a", "a", "b"], []);

    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({ id: "a", textRank: 1 });
    expect(result[1]).toMatchObject({ id: "b", textRank: 3 });
  });

  it("rejeita parâmetros que produziriam ranking inválido", () => {
    expect(() => reciprocalRankFusion([], [], { k: 0 })).toThrow(/positivo/);
    expect(() => reciprocalRankFusion([], [], { textWeight: -1 })).toThrow(/negativos/);
  });
});
