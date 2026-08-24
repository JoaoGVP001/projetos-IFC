import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import path from "node:path";

import type { CentralDirectory } from "unzipper";
import openDirectory from "unzipper/lib/Open/directory.js";

import { sourceCatalog } from "@/features/workspace/source-catalog";

import { sourceFileDescriptor } from "./file-response";

let archiveDirectoryPromise: Promise<CentralDirectory> | null = null;

function archivePath() {
  const configured = process.env.HELP_ARCHIVE_PATH;
  if (!configured) throw new Error("HELP_ARCHIVE_PATH não está configurado no servidor local.");
  return path.resolve(configured);
}

async function archiveDirectory() {
  const filename = archivePath();
  archiveDirectoryPromise ??= openDirectory({
    size: async () => (await stat(filename)).size,
    stream: (start, length) => createReadStream(filename, {
      start,
      end: length ? start + length : undefined,
    }),
  });
  return archiveDirectoryPromise;
}

export async function getHelpArchiveFile(sourceId: string) {
  const match = /^help-(\d{4})$/.exec(sourceId);
  if (!match) return null;

  const catalogItem = sourceCatalog.items.find((item) => item.id === sourceId);
  if (!catalogItem || catalogItem.status === "external" || catalogItem.status === "block") return null;

  const ordinal = Number(match[1]);
  const directory = await archiveDirectory();
  const fileEntries = directory.files.filter((entry) => entry.type === "File");
  const entry = fileEntries[ordinal - 1];
  if (!entry || entry.uncompressedSize !== catalogItem.size_bytes) {
    throw new Error("O arquivo não corresponde ao inventário atual. Regenere o catálogo antes de abrir.");
  }

  const descriptor = sourceFileDescriptor(catalogItem.extension);
  const safeName = catalogItem.masked_title
    ? `${catalogItem.id}${catalogItem.extension.startsWith(".") ? catalogItem.extension : ""}`
    : `${catalogItem.title}${catalogItem.extension.startsWith(".") ? catalogItem.extension : ""}`;

  return {
    bytes: new Uint8Array(await entry.buffer()),
    filename: safeName,
    mimeType: descriptor.mimeType,
    preview: descriptor.preview,
  };
}
