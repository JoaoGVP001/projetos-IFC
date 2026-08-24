import type { KnowledgeSystem } from "@/features/workspace/knowledge-data";

export type AttachmentPreview = "image" | "pdf" | "text" | "video" | "download";

export type SolutionAttachment = {
  id: string;
  name: string;
  extension: string;
  mimeType: string;
  sizeBytes: number;
  preview: AttachmentPreview;
  storedName: string;
  createdAt: string;
};

export type SolutionHistoryEntry = {
  id: string;
  outcome: "success" | "failure";
  note: string;
  createdAt: string;
};

export type SolutionActivity = {
  accessCount: number;
  history: SolutionHistoryEntry[];
};

export type UploadedSolution = {
  id: string;
  title: string;
  system: KnowledgeSystem;
  procedure: string;
  createdAt: string;
  updatedAt: string;
  attachments: SolutionAttachment[];
};

export type SolutionStore = {
  schemaVersion: 1;
  solutions: UploadedSolution[];
  activities: Record<string, SolutionActivity>;
};

export type SolutionSnapshot = Pick<SolutionStore, "solutions" | "activities">;
