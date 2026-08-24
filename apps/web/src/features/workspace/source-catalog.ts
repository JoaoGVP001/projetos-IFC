import catalog from "./source-catalog.json";

export type SourceStatus = "include" | "review" | "defer" | "block" | "skip" | "external";

export type SourceCatalogItem = {
  id: string;
  title: string;
  source: string;
  system: string;
  category: string;
  extension: string;
  size_bytes: number;
  status: SourceStatus;
  status_label: string;
  reason_label: string;
  masked_title: boolean;
  url?: string;
};

export type SourceCatalog = {
  schema_version: number;
  generated_at: string;
  archive_name: string;
  archive_files: number;
  external_sources: number;
  total_sources: number;
  by_decision: Record<string, number>;
  privacy: string;
  items: SourceCatalogItem[];
};

export const sourceCatalog = catalog as SourceCatalog;
