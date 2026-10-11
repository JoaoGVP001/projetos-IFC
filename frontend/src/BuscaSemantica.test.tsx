import {
  render,
  screen,
  fireEvent,
  waitFor,
  cleanup,
} from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { BuscaSemantica } from "./BuscaSemantica";
import { api } from "./bridge";
vi.mock("./bridge", () => ({ api: vi.fn() }));
afterEach(() => {
  cleanup();
  vi.resetAllMocks();
});
const status = {
  habilitada: 0,
  url: "http://127.0.0.1:11434",
  modelo: "qwen3-embedding:0.6b",
  indexados: 0,
  total: 12,
  trabalho: null,
};
it("exige ação explícita para indexar e avisa o destino dos textos", async () => {
  vi.mocked(api).mockResolvedValue(status);
  const run = vi.fn();
  render(
    <BuscaSemantica revisao={1} occupied={false} run={run} notify={vi.fn()} />,
  );
  await waitFor(() => expect(screen.getByText(/0\/12 trechos/)).toBeTruthy());
  expect(run).not.toHaveBeenCalled();
  expect(screen.getByText(/Isso não seleciona materiais/)).toBeTruthy();
  fireEvent.click(
    screen.getByRole("button", { name: "Indexar / retomar e ativar" }),
  );
  expect(run).toHaveBeenCalledWith("semantica_indexar", {
    confirmado: true,
    url: status.url,
  });
});
it("permite cancelar indexação mesmo com outras mutações bloqueadas", async () => {
  vi.mocked(api).mockResolvedValue({
    ...status,
    trabalho: { estado: "executando", feitos: 4, total: 12, erro: "" },
  });
  const run = vi.fn();
  render(<BuscaSemantica revisao={1} occupied run={run} notify={vi.fn()} />);
  await waitFor(() =>
    expect(
      screen.getByRole("button", { name: "Cancelar indexação" }),
    ).toBeTruthy(),
  );
  expect(
    (
      screen.getByRole("button", {
        name: "Indexar / retomar e ativar",
      }) as HTMLButtonElement
    ).disabled,
  ).toBe(true);
  fireEvent.click(screen.getByRole("button", { name: "Cancelar indexação" }));
  expect(run).toHaveBeenCalledWith("semantica_cancelar");
});
it("desativar consulta híbrida não pede exclusão dos materiais", async () => {
  vi.mocked(api).mockResolvedValue({ ...status, habilitada: 1, indexados: 12 });
  const run = vi.fn();
  render(
    <BuscaSemantica revisao={1} occupied={false} run={run} notify={vi.fn()} />,
  );
  await waitFor(() =>
    expect((screen.getByRole("checkbox") as HTMLInputElement).checked).toBe(
      true,
    ),
  );
  fireEvent.click(screen.getByRole("checkbox"));
  expect(run).toHaveBeenCalledWith("semantica_ativar", { valor: false });
});
