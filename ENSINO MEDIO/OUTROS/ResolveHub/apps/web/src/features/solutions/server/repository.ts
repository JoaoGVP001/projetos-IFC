import { randomUUID } from "node:crypto";
import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import path from "node:path";

import type { KnowledgeSystem } from "@/features/workspace/knowledge-data";

import type {
  SolutionActivity,
  SolutionHistoryEntry,
  SolutionSnapshot,
  SolutionStore,
  UploadedSolution,
} from "../types";
import { uploadDescriptor, validateUploadBatch } from "../validation";

const storageRoot = path.resolve(
  /* turbopackIgnore: true */ process.cwd(),
  process.env.STORAGE_ROOT || "../../storage",
);
const statePath = path.join(storageRoot, "resolvehub-state.json");
const uploadsRoot = path.join(storageRoot, "uploads");

let writeQueue: Promise<unknown> = Promise.resolve();

function emptyStore(): SolutionStore {
  return { schemaVersion: 1, solutions: [], activities: {} };
}

async function readStore(): Promise<SolutionStore> {
  try {
    const contents = await readFile(statePath, "utf8");
    const parsed = JSON.parse(contents) as SolutionStore;
    if (parsed.schemaVersion !== 1 || !Array.isArray(parsed.solutions) || !parsed.activities) {
      throw new Error("O armazenamento local possui um formato incompatível.");
    }
    return parsed;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return emptyStore();
    throw error;
  }
}

async function writeStore(store: SolutionStore) {
  await mkdir(storageRoot, { recursive: true });
  const temporaryPath = `${statePath}.${randomUUID()}.tmp`;
  await writeFile(temporaryPath, `${JSON.stringify(store, null, 2)}\n`, { encoding: "utf8", flag: "wx" });
  await rename(temporaryPath, statePath);
}

function updateStore<T>(mutator: (store: SolutionStore) => Promise<T> | T): Promise<T> {
  const operation = writeQueue.then(async () => {
    const store = await readStore();
    const result = await mutator(store);
    await writeStore(store);
    return result;
  });
  writeQueue = operation.then(() => undefined, () => undefined);
  return operation;
}

function activityFor(store: SolutionStore, solutionId: string): SolutionActivity {
  store.activities[solutionId] ??= { accessCount: 0, history: [] };
  return store.activities[solutionId];
}

export async function getSolutionSnapshot(): Promise<SolutionSnapshot> {
  const store = await readStore();
  return { solutions: store.solutions, activities: store.activities };
}

export async function createUploadedSolution(input: {
  title: string;
  system: KnowledgeSystem;
  procedure: string;
  files: File[];
}) {
  const descriptors = validateUploadBatch(input.files);
  const solutionId = randomUUID();
  const now = new Date().toISOString();
  const solutionDirectory = path.join(uploadsRoot, solutionId);
  await mkdir(solutionDirectory, { recursive: true });

  const attachments = await Promise.all(input.files.map(async (file, index) => {
    const descriptor = descriptors[index] ?? uploadDescriptor(file.name, file.size);
    const attachmentId = randomUUID();
    const storedName = `${attachmentId}${descriptor.extension}`;
    const bytes = new Uint8Array(await file.arrayBuffer());
    await writeFile(path.join(solutionDirectory, storedName), bytes, { flag: "wx" });
    return {
      id: attachmentId,
      name: descriptor.safeName,
      extension: descriptor.extension,
      mimeType: descriptor.mimeType,
      sizeBytes: file.size,
      preview: descriptor.preview,
      storedName,
      createdAt: now,
    };
  }));

  const solution: UploadedSolution = {
    id: solutionId,
    title: input.title,
    system: input.system,
    procedure: input.procedure,
    createdAt: now,
    updatedAt: now,
    attachments,
  };

  await updateStore((store) => {
    store.solutions.unshift(solution);
    activityFor(store, solutionId);
  });
  return solution;
}

export async function incrementSolutionAccess(solutionId: string) {
  return updateStore((store) => {
    const activity = activityFor(store, solutionId);
    activity.accessCount += 1;
    return activity;
  });
}

export async function addSolutionHistory(
  solutionId: string,
  input: { outcome: "success" | "failure"; note: string },
) {
  return updateStore((store) => {
    const activity = activityFor(store, solutionId);
    const entry: SolutionHistoryEntry = {
      id: randomUUID(),
      outcome: input.outcome,
      note: input.note,
      createdAt: new Date().toISOString(),
    };
    activity.history.unshift(entry);
    return { activity, entry };
  });
}

export async function getUploadedAttachment(solutionId: string, attachmentId: string) {
  const store = await readStore();
  const solution = store.solutions.find((candidate) => candidate.id === solutionId);
  const attachment = solution?.attachments.find((candidate) => candidate.id === attachmentId);
  if (!solution || !attachment) return null;

  const filePath = path.resolve(uploadsRoot, solution.id, attachment.storedName);
  const solutionRoot = `${path.resolve(uploadsRoot, solution.id)}${path.sep}`;
  if (!filePath.startsWith(solutionRoot)) throw new Error("Caminho de anexo inválido.");
  return { attachment, bytes: await readFile(filePath) };
}
