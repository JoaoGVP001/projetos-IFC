import { afterEach, it, expect, vi } from "vitest";
import { render, cleanup, fireEvent, screen } from "@testing-library/react";
import { Menu, Dialog } from "./ui";
afterEach(cleanup);
it("menu pode ser usado com teclado e Escape devolve o foco", () => {
  const executar = vi.fn();
  render(
    <Menu
      label="Ações do chat"
      items={[
        { label: "Renomear", action: executar },
        { label: "Fixar", action: executar },
      ]}
    />,
  );
  const btn = screen.getByRole("button", { name: "Ações do chat" });
  fireEvent.click(btn);
  expect(document.activeElement?.textContent).toBe("Renomear");
  fireEvent.keyDown(screen.getByRole("menu"), { key: "ArrowDown" });
  expect(document.activeElement?.textContent).toBe("Fixar");
  fireEvent.keyDown(screen.getByRole("menu"), { key: "Escape" });
  expect(screen.queryByRole("menu")).toBeNull();
  expect(document.activeElement).toBe(btn);
});
it("diálogo é modal nativo e fecha por Escape sem submeter formulários", () => {
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
  const fechar = vi.fn();
  const { container } = render(
    <Dialog title="Criar caderno" onClose={fechar}>
      <input aria-label="Nome" />
    </Dialog>,
  );
  const dialog = document.querySelector("dialog")!;
  expect(dialog.hasAttribute("open")).toBe(true);
  fireEvent(dialog, new Event("cancel", { cancelable: true }));
  expect(fechar).toHaveBeenCalledOnce();
});
