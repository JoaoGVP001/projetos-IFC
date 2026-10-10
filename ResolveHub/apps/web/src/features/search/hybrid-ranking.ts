export type RankedItem = {
  id: string;
  rank: number;
};

export type FusedItem = {
  id: string;
  score: number;
  textRank?: number;
  vectorRank?: number;
};

type FusionOptions = {
  k?: number;
  textWeight?: number;
  vectorWeight?: number;
};

function uniqueRanks(ids: readonly string[]): RankedItem[] {
  const seen = new Set<string>();

  return ids.flatMap((id, index) => {
    if (seen.has(id)) return [];
    seen.add(id);
    return [{ id, rank: index + 1 }];
  });
}
export function reciprocalRankFusion(
  textIds: readonly string[],
  vectorIds: readonly string[],
  options: FusionOptions = {},
): FusedItem[] {
  const k = options.k ?? 60;
  const textWeight = options.textWeight ?? 1;
  const vectorWeight = options.vectorWeight ?? 1;

  if (k <= 0) throw new Error("O parâmetro k deve ser positivo.");
  if (textWeight < 0 || vectorWeight < 0) throw new Error("Os pesos não podem ser negativos.");

  const fused = new Map<string, FusedItem>();

  for (const item of uniqueRanks(textIds)) {
    fused.set(item.id, {
      id: item.id,
      score: textWeight / (k + item.rank),
      textRank: item.rank,
    });
  }

  for (const item of uniqueRanks(vectorIds)) {
    const current = fused.get(item.id) ?? { id: item.id, score: 0 };
    current.score += vectorWeight / (k + item.rank);
    current.vectorRank = item.rank;
    fused.set(item.id, current);
  }

  return [...fused.values()].sort((left, right) => {
    if (right.score !== left.score) return right.score - left.score;
    return left.id.localeCompare(right.id);
  });
}
