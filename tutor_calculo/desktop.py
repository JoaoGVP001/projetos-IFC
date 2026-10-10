"""Interface de estudo para desktop."""

from queue import Empty, Queue
from threading import Thread
import webbrowser

import customtkinter as ctk

from .app import EXEMPLO, resolver
from .renderizacao import Renderizador
from .ia import PROVEDORES, configuracao, perguntar, provedor_ativo, salvar_configuracao


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
        self.title("CadernoMat — estudos de matematica")
        self.geometry("1080x700")
        self.minsize(780, 560)
        self._fila: Queue[tuple[str, str]] = Queue()
        self._ocupado = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._janela_config = None

        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=0, sticky="ew", padx=30, pady=(24, 16))
        cabecalho.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            cabecalho, text="CadernoMat", font=("Segoe UI", 27, "bold"),
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
            barra, values=["Resolver", "Resolver com IA", "Explicar", "Corrigir"],
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
        self.renderizador = Renderizador(self.saida._textbox)

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
        self.rotulo_ia = ctk.CTkLabel(rodape, text="", text_color=MUTED, font=("Segoe UI", 12))
        self.rotulo_ia.grid(row=1, column=0, sticky="w", pady=(8, 0))
        ctk.CTkButton(rodape, text="Configurar IA", width=130, height=28,
                      fg_color="transparent", text_color=ACCENT,
                      hover_color="#E7EEEC", command=self.configurar_ia).grid(row=1, column=1, pady=(8, 0))
        self._atualizar_status_ia()
        self.after(100, self._verificar_fila)

    def _mudar_modo(self, modo: str) -> None:
        self.botao_enviar.configure(text=modo)

    def _atualizar_status_ia(self) -> None:
        chave, modelo = configuracao()
        self.rotulo_ia.configure(text=f"IA: {provedor_ativo().title()} · {modelo} · chave configurada" if chave else f"IA: {provedor_ativo().title()} · chave nao configurada · exemplo local funciona sem API")

    def configurar_ia(self) -> None:
        if self._ocupado:
            return
        if self._janela_config is not None and self._janela_config.winfo_exists():
            self._janela_config.focus()
            return
        janela = ctk.CTkToplevel(self)
        self._janela_config = janela
        janela.title("Configurar instrutor com IA")
        janela.geometry("690x530")
        janela.transient(self)
        janela.grid_columnconfigure(0, weight=1)
        opcoes = {"Gemini (gratuito ou pago)": "gemini", "OpenAI (API paga)": "openai"}
        ctk.CTkLabel(janela, text="Servico de IA", anchor="w").grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 6))
        servico = ctk.CTkOptionMenu(janela, values=list(opcoes))
        servico.set(next(nome for nome, valor in opcoes.items() if valor == provedor_ativo()))
        servico.grid(row=1, column=0, sticky="ew", padx=24)
        ctk.CTkLabel(janela, text="Chave da API do servico escolhido", anchor="w").grid(row=2, column=0, sticky="ew", padx=24, pady=(12, 6))
        campo_chave = ctk.CTkEntry(janela, show="*", placeholder_text="Cole a chave ou deixe vazio para manter a chave salva")
        campo_chave.grid(row=3, column=0, sticky="ew", padx=24)
        ctk.CTkLabel(janela, text="Modelo (voce pode editar o identificador)", anchor="w").grid(row=4, column=0, sticky="ew", padx=24, pady=(12, 6))
        campo_modelo = ctk.CTkEntry(janela)
        campo_modelo.grid(row=5, column=0, sticky="ew", padx=24)
        aviso = ctk.CTkLabel(janela, text="", wraplength=630, justify="left", anchor="w")
        aviso.grid(row=6, column=0, sticky="ew", padx=24, pady=12)
        estado_chave = ctk.CTkLabel(janela, text="", anchor="w")
        estado_chave.grid(row=7, column=0, sticky="ew", padx=24)
        def atualizar(_nome=None):
            provedor = opcoes[servico.get()]
            chave, modelo = configuracao(provedor)
            campo_chave.delete(0, "end")
            campo_modelo.delete(0, "end")
            campo_modelo.insert(0, modelo)
            estado_chave.configure(text="Chave deste servico ja configurada; campo vazio preserva a chave." if chave else "Este servico ainda precisa de uma chave.")
            aviso.configure(text=(
                "Gemini: use uma chave de projeto Free Tier para uso gratuito, sujeito a cotas. "
                "Para uso pago, configure faturamento no Google AI Studio. A cobranca depende do projeto e do modelo; "
                "esta tela nao muda seu plano. No gratuito, dados podem ser usados para melhorar produtos Google."
                if provedor == "gemini" else
                "OpenAI: consultas sao cobradas pela API, conforme modelo e uso. A chave e os creditos sao do usuario; "
                "o aplicativo nao usa o login ou a assinatura do ChatGPT."
            ), text_color=MUTED)
        servico.configure(command=atualizar)
        atualizar()
        links = ctk.CTkFrame(janela, fg_color="transparent")
        links.grid(row=8, column=0, sticky="w", padx=24, pady=8)
        def abrir_chaves():
            webbrowser.open("https://aistudio.google.com/apikey" if opcoes[servico.get()] == "gemini" else "https://platform.openai.com/api-keys")
        def abrir_precos():
            webbrowser.open("https://ai.google.dev/gemini-api/docs/pricing" if opcoes[servico.get()] == "gemini" else "https://developers.openai.com/api/docs/pricing")
        ctk.CTkButton(links, text="Obter chave", command=abrir_chaves, width=120).pack(side="left", padx=(0, 8))
        ctk.CTkButton(links, text="Planos e modelos", command=abrir_precos, width=150).pack(side="left")
        def salvar():
            try:
                salvar_configuracao(campo_chave.get(), campo_modelo.get(), opcoes[servico.get()])
            except (ValueError, OSError) as exc:
                estado_chave.configure(text=str(exc), text_color="#AD4D36")
                return
            self._atualizar_status_ia()
            self.estado.configure(text="Configuracao salva. Use Resolver com IA para testar.", text_color=MUTED)
            janela.destroy()
        ctk.CTkButton(janela, text="Salvar", command=salvar).grid(row=9, column=0, sticky="e", padx=24, pady=8)
        campo_chave.focus_set()

    def carregar_exemplo(self) -> None:
        if self._ocupado:
            return
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
        texto = self.renderizador.original.strip()
        if texto:
            self.clipboard_clear()
            self.clipboard_append(texto)
            self.estado.configure(text="Resolução copiada", text_color=MUTED)

    def _mostrar_saida(self, texto: str) -> None:
        self.renderizador.mostrar(texto)

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
            if modo in {"Resolver", "Resolver com IA"}:
                resposta = resolver(texto, usar_ia=modo == "Resolver com IA")
            elif modo == "Explicar":
                resposta = perguntar(texto, modo="Explicar")
            else:
                resposta = perguntar(texto, modo="Corrigir")
            self._fila.put(("ok", resposta))
        except (ValueError, RuntimeError, ImportError) as exc:
            self._fila.put(("erro", str(exc)))
        except Exception:
            self._fila.put(("erro", "Ocorreu uma falha inesperada. Revise o enunciado e tente novamente."))

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
