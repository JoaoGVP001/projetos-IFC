"""Interface de estudo para desktop."""

from queue import Empty, Queue
from threading import Thread

import customtkinter as ctk

from .app import EXEMPLO, resolver
from .ia import perguntar


BG = "#F4F7F6"
SURFACE = "#FFFFFF"
INK = "#202B2A"
MUTED = "#667674"
ACCENT = "#126F68"
ACCENT_HOVER = "#0C5953"
BORDER = "#DCE5E2"


class TutorDesktop(ctk.CTk):
    def __init__(self) -> None:
        super().__init__(fg_color=BG)
        self.title("Tutor de Calculo I")
        self.geometry("1080x700")
        self.minsize(780, 560)
        self._fila: Queue[tuple[str, str]] = Queue()
        self._ocupado = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=30, pady=(24, 16))
        cabecalho.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            cabecalho, text="Cálculo I", font=("Segoe UI", 27, "bold"),
            text_color=INK, anchor="w",
        ).grid(row=0, column=0, sticky="w")
        self.estado = ctk.CTkLabel(
            cabecalho, text="Pronto", font=("Segoe UI", 13),
            text_color=MUTED, anchor="e",
        )
        self.estado.grid(row=0, column=1, sticky="e")

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 18))
        barra.grid_columnconfigure(0, weight=1)
        self.modo = ctk.CTkSegmentedButton(
            barra, values=["Resolver", "Explicar", "Corrigir"],
            height=34, corner_radius=6, fg_color="#E7EEEC",
            selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
            unselected_color="#E7EEEC", unselected_hover_color="#DAE6E2",
            text_color=(INK, SURFACE), font=("Segoe UI", 13),
        )
        self.modo.grid(row=0, column=0, sticky="w")
        self.modo.set("Resolver")
        ctk.CTkButton(
            barra, text="Carregar exemplo", width=135, height=34,
            fg_color="transparent", hover_color="#E7EEEC", text_color=ACCENT,
            font=("Segoe UI", 13), command=self.carregar_exemplo,
        ).grid(row=0, column=1, padx=(8, 0))
        ctk.CTkButton(
            barra, text="Limpar", width=72, height=34,
            fg_color="transparent", hover_color="#E7EEEC", text_color=MUTED,
            font=("Segoe UI", 13), command=self.limpar,
        ).grid(row=0, column=2, padx=(4, 0))

        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.grid(row=2, column=0, sticky="nsew", padx=30)
        corpo.grid_columnconfigure((0, 1), weight=1, uniform="painel")
        corpo.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            corpo, text="ENUNCIADO", font=("Segoe UI", 12, "bold"),
            text_color=MUTED, anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(
            corpo, text="RESOLUÇÃO", font=("Segoe UI", 12, "bold"),
            text_color=MUTED, anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=(16, 0), pady=(0, 8))
        self.entrada = ctk.CTkTextbox(
            corpo, wrap="word", fg_color=SURFACE, text_color=INK,
            border_color=BORDER, border_width=1, corner_radius=6,
            font=("Consolas", 15), padx=17, pady=17,
        )
        self.entrada.grid(row=1, column=0, sticky="nsew")
        self.saida = ctk.CTkTextbox(
            corpo, wrap="word", fg_color=SURFACE, text_color=INK,
            border_color=BORDER, border_width=1, corner_radius=6,
            font=("Segoe UI", 15), padx=19, pady=17, state="disabled",
        )
        self.saida.grid(row=1, column=1, sticky="nsew", padx=(16, 0))

        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.grid(row=3, column=0, sticky="ew", padx=30, pady=(17, 24))
        rodape.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(
            rodape, text="Copiar resolução", width=142, height=38,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color="#E7EEEC", text_color=INK, font=("Segoe UI", 13),
            command=self.copiar,
        ).grid(row=0, column=0, sticky="w")
        self.botao_enviar = ctk.CTkButton(
            rodape, text="Resolver", width=130, height=40,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            corner_radius=6, font=("Segoe UI", 14, "bold"),
            command=self.enviar,
        )
        self.botao_enviar.grid(row=0, column=1, sticky="e")

        self.modo.configure(command=self._mudar_modo)
        self.bind("<Control-Return>", lambda _event: self.enviar())
        self.entrada.focus_set()
        self.after(100, self._verificar_fila)

    def _mudar_modo(self, modo: str) -> None:
        self.botao_enviar.configure(text={"Resolver": "Resolver", "Explicar": "Explicar", "Corrigir": "Corrigir"}[modo])

    def carregar_exemplo(self) -> None:
        self.modo.set("Resolver")
        self._mudar_modo("Resolver")
        self.entrada.delete("1.0", "end")
        self.entrada.insert("1.0", EXEMPLO)
        self.entrada.focus_set()
        self.estado.configure(text="Exemplo carregado", text_color=MUTED)

    def limpar(self) -> None:
        if self._ocupado:
            return
        self.entrada.delete("1.0", "end")
        self._mostrar_saida("")
        self.estado.configure(text="Pronto", text_color=MUTED)
        self.entrada.focus_set()

    def copiar(self) -> None:
        texto = self.saida.get("1.0", "end").strip()
        if texto:
            self.clipboard_clear()
            self.clipboard_append(texto)
            self.estado.configure(text="Resolução copiada", text_color=MUTED)

    def _mostrar_saida(self, texto: str) -> None:
        self.saida.configure(state="normal")
        self.saida.delete("1.0", "end")
        self.saida.insert("1.0", texto)
        self.saida.configure(state="disabled")

    def enviar(self) -> None:
        if self._ocupado:
            return
        texto = self.entrada.get("1.0", "end").strip()
        if not texto:
            self.estado.configure(text="Digite um enunciado", text_color="#AD4D36")
            self.entrada.focus_set()
            return
        modo = self.modo.get()
        self._ocupado = True
        self.botao_enviar.configure(state="disabled")
        self.estado.configure(text="Calculando..." if modo == "Resolver" else "Consultando tutor...", text_color=ACCENT)
        self._mostrar_saida("")
        Thread(target=self._executar, args=(modo, texto), daemon=True).start()

    def _executar(self, modo: str, texto: str) -> None:
        try:
            if modo == "Resolver":
                resposta = resolver(texto)
            elif modo == "Explicar":
                resposta = perguntar(f"Explique este conteudo de Calculo I passo a passo:\n{texto}")
            else:
                resposta = perguntar(f"Corrija a tentativa do aluno, mostrando o primeiro erro e como continuar:\n{texto}")
            self._fila.put(("ok", resposta))
        except (ValueError, RuntimeError, ImportError) as exc:
            self._fila.put(("erro", str(exc)))

    def _verificar_fila(self) -> None:
        try:
            tipo, mensagem = self._fila.get_nowait()
        except Empty:
            pass
        else:
            self._ocupado = False
            self.botao_enviar.configure(state="normal")
            self._mostrar_saida(mensagem)
            self.estado.configure(
                text="Concluído" if tipo == "ok" else "Não foi possível concluir",
                text_color=ACCENT if tipo == "ok" else "#AD4D36",
            )
        self.after(100, self._verificar_fila)


def main() -> None:
    ctk.set_appearance_mode("light")
    janela = TutorDesktop()
    janela.mainloop()


if __name__ == "__main__":
    main()
