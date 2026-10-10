import type { AttachmentPreview } from "../types";

const sourceTypes: Record<string, { mimeType: string; preview: AttachmentPreview }> = {
  ".txt": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".md": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".csv": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".sql": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".yml": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".yaml": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".ini": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".htm": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".html": { mimeType: "text/plain; charset=utf-8", preview: "text" },
  ".pdf": { mimeType: "application/pdf", preview: "pdf" },
  ".png": { mimeType: "image/png", preview: "image" },
  ".jpg": { mimeType: "image/jpeg", preview: "image" },
  ".jpeg": { mimeType: "image/jpeg", preview: "image" },
  ".gif": { mimeType: "image/gif", preview: "image" },
  ".webp": { mimeType: "image/webp", preview: "image" },
  ".bmp": { mimeType: "image/bmp", preview: "image" },
  ".jfif": { mimeType: "image/jpeg", preview: "image" },
  ".mp4": { mimeType: "video/mp4", preview: "video" },
};

export function sourceFileDescriptor(extension: string) {
  return sourceTypes[extension.toLocaleLowerCase("pt-BR")] ?? {
    mimeType: "application/octet-stream",
    preview: "download" as const,
  };
}

export function privateFileResponse(
  bytes: Uint8Array,
  input: { filename: string; mimeType: string; preview: AttachmentPreview },
) {
  const disposition = input.preview === "download" ? "attachment" : "inline";
  const encodedName = encodeURIComponent(input.filename).replace(/['()]/g, escape);
  const responseBody = Uint8Array.from(bytes).buffer;
  return new Response(responseBody, {
    headers: {
      "Cache-Control": "private, no-store, max-age=0",
      "Content-Disposition": `${disposition}; filename*=UTF-8''${encodedName}`,
      "Content-Length": String(bytes.byteLength),
      "Content-Security-Policy": "default-src 'none'; sandbox",
      "Content-Type": input.mimeType,
      "X-Content-Type-Options": "nosniff",
    },
  });
}
