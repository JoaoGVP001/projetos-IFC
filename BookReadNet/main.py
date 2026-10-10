from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from interface import BibliotecaApp
from servicos import BibliotecaDigital


def executar_demo_console(biblioteca: BibliotecaDigital) -> None:
    print(f"{biblioteca.nome} iniciado")
    print(f"Obras no acervo: {len(biblioteca.obras)}")
    print("Formatos aceitos: PDF, CBZ, CBR e CB7")


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    try:
        biblioteca = BibliotecaDigital("BookReadNet", Path(__file__).parent)
    except (OSError, ValueError) as erro:
        messagebox.showerror("BookReadNet", str(erro), parent=root)
        root.destroy()
        return

    executar_demo_console(biblioteca)
    root.deiconify()
    BibliotecaApp(root, biblioteca)
    root.mainloop()


if __name__ == "__main__":
    main()
