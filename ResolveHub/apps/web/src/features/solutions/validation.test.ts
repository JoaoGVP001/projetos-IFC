import { describe, expect, it } from "vitest";

import {
  isSafeRecordId,
  uploadDescriptor,
  validateUploadBatch,
} from "./validation";

describe("solution upload validation", () => {
  it("permite documentos e imagens visualizáveis", () => {
    expect(uploadDescriptor("procedimento.txt", 20).preview).toBe("text");
    expect(uploadDescriptor("manual.pdf", 40).preview).toBe("pdf");
    expect(uploadDescriptor("tela.png", 60).preview).toBe("image");
  });

  it("bloqueia certificados, bancos, scripts e arquivos de credencial", () => {
    expect(() => uploadDescriptor("certificado.pfx", 20)).toThrow(/não pode ser enviado/);
    expect(() => uploadDescriptor("base.fdb", 20)).toThrow(/não pode ser enviado/);
    expect(() => uploadDescriptor("senha acesso.txt", 20)).toThrow(/credenciais/);
  });

  it("limita quantidade e tamanho total dos anexos", () => {
    const tooMany = Array.from({ length: 11 }, (_, index) => ({ name: `${index}.txt`, size: 1 }));
    expect(() => validateUploadBatch(tooMany)).toThrow(/no máximo 10/);
    expect(() => validateUploadBatch([{ name: "grande.pdf", size: 26 * 1024 * 1024 }])).toThrow(/25 MB/);
  });

  it("aceita somente identificadores seguros nas rotas", () => {
    expect(isSafeRecordId("small-status-servico")).toBe(true);
    expect(isSafeRecordId("../segredo")).toBe(false);
  });
});
