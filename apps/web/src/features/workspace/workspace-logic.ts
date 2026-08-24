import type { KnowledgeItem, KnowledgeSystem } from "./knowledge-data";

export type SystemFilter = "Todos" | KnowledgeSystem;

export type AiPreview = {
  status: "answerable" | "insufficient";
  answer: string;
  sources: KnowledgeItem[];
};

export function normalizeSearchText(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .trim();
}

export function filterKnowledge(
  items: readonly KnowledgeItem[],
  query: string,
  system: SystemFilter,
) {
  const normalizedQuery = normalizeSearchText(query);

  return items.filter((item) => {
    if (system !== "Todos" && item.system !== system) return false;
    if (!normalizedQuery) return true;

    const searchable = normalizeSearchText([
      item.title,
      item.category,
      item.module,
      item.excerpt,
      ...item.tags,
    ].join(" "));

    return normalizedQuery
      .split(/\s+/)
      .filter(Boolean)
      .every((term) => searchable.includes(term));
  });
}

export function buildAiPreview(
  question: string,
  items: readonly KnowledgeItem[],
  system: SystemFilter,
): AiPreview {
  const normalizedQuestion = normalizeSearchText(question);
  if (!normalizedQuestion) {
    return {
      status: "insufficient",
      answer: "Digite uma pergunta para que eu possa procurar evidências na base cadastrada.",
      sources: [],
    };
  }

  const directMatches = filterKnowledge(items, question, system);
  const sources = directMatches.slice(0, 2);

  if (sources.length === 0) {
    return {
      status: "insufficient",
      answer: "Não encontrei informação suficiente nas fontes cadastradas para responder com segurança.",
      sources: [],
    };
  }

  return {
    status: "answerable",
    answer: `A fonte mais relacionada é “${sources[0].title}”. ${sources[0].procedure}`,
    sources,
  };
}

