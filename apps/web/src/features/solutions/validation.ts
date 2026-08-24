import type { AttachmentPreview } from "./types";

export const MAX_UPLOAD_FILES = 10;
export const MAX_FILE_BYTES = 25 * 1024 * 1024;
export const MAX_TOTAL_UPLOAD_BYTES = 100 * 1024 * 1024;

const allowedExtensions: Record<string, { mimeType: string; preview: AttachmentPreview }> = {
  ".txt": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".md": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".csv": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".pdf": { mimeType: "application/pdf", preview: "pdf" },
  ".png": { mimeType: "image/png", preview: "image" },
  ".jpg": { mimeType: "image/jpeg", preview: "image" },
  ".jpeg": { mimeType: "image/jpeg", preview: "image" },
  ".gif": { mimeType: "image/gif", preview: "image" },
  ".webp": { mimeType: "image/webp", preview: "image" },
  ".bmp": { mimeType: "image/bmp", preview: "image" },
  ".mp4": { mimeType: "video/mp4", preview: "video" },
  ".docx": { mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", preview: "download" },
  ".xlsx": { mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", preview: "download" },
  ".odt": { mimeType: "application/vnd.oasis.opendocument.text", preview: "download" },
};

const blockedExtensions = new Set([
  ".pfx", ".p12", ".pem", ".key", ".kdb", ".fdb", ".db", ".sqlite", ".sqlite3",
  ".exe", ".dll", ".sys", ".inf", ".cat", ".msi", ".apk", ".bat", ".cmd", ".ps1",
  ".vbs", ".reg", ".rar", ".7z", ".zip", ".tar", ".gz", ".sql", ".yml", ".yaml",
]);

const secretNamePattern = /(^|[\s._-])(senhas?|passwords?|credentials?|secrets?|tokens?|api[_-]?keys?)([\s._-]|$)/i;

export function extensionFromName(name: string) {
  const normalized = name.replace(/\\/g, "/").split("/").pop() ?? "";
  const dotIndex = normalized.lastIndexOf(".");
  return dotIndex > 0 ? normalized.slice(dotIndex).toLocaleLowerCase("pt-BR") : "";
}

export function safeDisplayFilename(name: string) {
  const basename = name.replace(/\\/g, "/").split("/").pop() ?? "arquivo";
  return basename.replace(/[\u0000-\u001f\u007f]/g, "").trim().slice(0, 180) || "arquivo";
}

export function uploadDescriptor(name: string, size: number) {
  const safeName = safeDisplayFilename(name);
  const extension = extensionFromName(safeName);

  if (secretNamePattern.test(safeName)) {
    throw new Error(`O arquivo “${safeName}” parece conter credenciais no nome e foi bloqueado.`);
  }
  if (blockedExtensions.has(extension)) {
    throw new Error(`O formato ${extension || "sem extensão"} não pode ser enviado por segurança.`);
  }
  const descriptor = allowedExtensions[extension];
  if (!descriptor) {
    throw new Error(`O formato ${extension || "sem extensão"} ainda não é aceito.`);
  }
  if (size <= 0) {
    throw new Error(`O arquivo “${safeName}” está vazio.`);
  }
  if (size > MAX_FILE_BYTES) {
    throw new Error(`O arquivo “${safeName}” ultrapassa o limite de 25 MB.`);
  }

  return { ...descriptor, extension, safeName };
}

export function validateUploadBatch(files: readonly { name: string; size: number }[]) {
  if (files.length > MAX_UPLOAD_FILES) {
    throw new Error(`Envie no máximo ${MAX_UPLOAD_FILES} arquivos por solução.`);
  }
  const total = files.reduce((sum, file) => sum + file.size, 0);
  if (total > MAX_TOTAL_UPLOAD_BYTES) {
    throw new Error("O conjunto de anexos ultrapassa o limite de 100 MB.");
  }
  return files.map((file) => uploadDescriptor(file.name, file.size));
}

export function isSafeRecordId(value: string) {
  return /^[a-zA-Z0-9-]{1,100}$/.test(value);
}
