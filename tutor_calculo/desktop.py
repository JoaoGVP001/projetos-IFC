"""Interface de estudo para desktop."""

from queue import Empty, Queue
from threading import Thread
import webbrowser
from tkinter import messagebox

import customtkinter as ctk

from .chat_item import ChatItem
from .armazenamento import Historico
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
    def __init__(self, caminho_historico=None) -> None:
        super().__init__(fg_color=BG)
        self.title("CadernoMat — estudos de matematica")
        self.geometry("1180x780")
        self.minsize(1000, 650)
        self._fila: Queue[tuple[str, str]] = Queue()
        self._ocupado = False
        self._arquivados = False
        self.historico = Historico(caminho_historico)
        conversas = self.historico.listar()
        self.conversa_id = conversas[0]["id"] if conversas else self.historico.criar()
        self.protocol("WM_DELETE_WINDOW", self.fechar)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._janela_config = None

        cabecalho = ctk.CTkFrame(self, fg_color="transparent")
        cabecalho.grid(row=0, column=1, sticky="ew", padx=30, pady=(24, 16))
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
        barra.grid(row=1, column=1, sticky="ew", padx=30, pady=(0, 18))
        barra.grid_columnconfigure(0, weight=1)
        self.modo = ctk.CTkSegmentedButton(
            barra, values=["Resolver", "Resolver com IA", "Explicar", "Corrigir"],
            height=34, corner_radius=6, fg_color="#E7EEEC",
            selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
            unselected_color="#E7EEEC", unselected_hover_color="#DAE6E2",
            text_color=(INK, SURFACE), font=("Segoe UI", 13),
        )
        self.modo.grid(row=0, column=0, sticky="w")
        self.modo.set("Resolver com IA")
        ctk.CTkButton(
            barra, text="Carregar exemplo", width=135, height=34,
            fg_color="transparent", hover_color="#E7EEEC", text_color=ACCENT,
            font=("Segoe UI", 13), command=self.carregar_exemplo,
        ).grid(row=0, column=1, padx=(8, 0))
        ctk.CTkButton(
            barra, text="Limpar entrada", width=110, height=34,
            fg_color="transparent", hover_color="#E7EEEC", text_color=MUTED,
            font=("Segoe UI", 13), command=self.limpar,
        ).grid(row=0, column=2, padx=(4, 0))

        corpo = ctk.CTkFrame(self, fg_color="transparent")
        corpo.grid(row=2, column=1, sticky="nsew", padx=30)
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_rowconfigure(0, weight=1)
        self.entrada = ctk.CTkTextbox(
            corpo, wrap="word", fg_color=SURFACE, text_color=INK,
            border_color=BORDER, border_width=1, corner_radius=6,
            font=("Consolas", 15), padx=17, pady=17, height=110,
        )
        self.entrada.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        self.saida = ctk.CTkTextbox(
            corpo, wrap="word", fg_color=SURFACE, text_color=INK,
            border_color=BORDER, border_width=1, corner_radius=6,
            font=("Segoe UI", 15), padx=19, pady=17, state="disabled",
        )
        self.saida.grid(row=0, column=0, sticky="nsew")
        self.renderizador = Renderizador(self.saida._textbox)

        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.grid(row=3, column=1, sticky="ew", padx=30, pady=(17, 24))
        rodape.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(
            rodape, text="Copiar conversa", width=142, height=38,
            fg_color="transparent", border_width=1, border_color=BORDER,
            hover_color="#E7EEEC", text_color=INK, font=("Segoe UI", 13),
            command=self.copiar,
        ).grid(row=0, column=0, sticky="w")
        self.botao_enviar = ctk.CTkButton(
            rodape, text="Resolver com IA", width=130, height=40,
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
        lateral = ctk.CTkFrame(self, width=220, fg_color="#E7EEEC", corner_radius=0)
        lateral.grid(row=0, column=0, rowspan=4, sticky="nsew")
        lateral.grid_rowconfigure(3, weight=1)
        lateral.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(lateral, text="+ Novo chat", command=self.novo_chat, fg_color=ACCENT).grid(row=0, column=0, padx=15, pady=20, sticky="ew")
        self.lista_chats = ctk.CTkScrollableFrame(lateral, width=190, fg_color="transparent")
        self.lista_chats.grid(row=3, column=0, sticky="nsew", padx=8)
        ctk.CTkLabel(lateral, text="Historico salvo neste PC", text_color=MUTED).grid(row=6, column=0, padx=10, pady=15)
        self.busca = ctk.CTkEntry(lateral, placeholder_text="Buscar titulo ou mensagem")
        self.busca.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.busca.bind("<KeyRelease>", lambda _evento: self._atualizar_lista())
        self.botao_arquivo = ctk.CTkButton(lateral, text="Ver arquivados", command=self.alternar_arquivados, fg_color=ACCENT)
        self.botao_arquivo.grid(row=4, column=0, padx=15, pady=8, sticky="ew")
        self._atualizar_lista()
        self._abrir_chat(self.conversa_id)
        self._atualizar_status_ia()
        self._timer_fila = self.after(100, self._verificar_fila)

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
        self.historico.rascunho(self.conversa_id, "")
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

    def _atualizar_lista(self):
        for filho in self.lista_chats.winfo_children():
            filho.destroy()
        for conversa in self.historico.listar(self.busca.get(), self._arquivados):
            ident = conversa["id"]
            ChatItem(self.lista_chats, conversa, ident == self.conversa_id,
                     abrir=lambda cid=ident: self.trocar_chat(cid), acao=self.acao_chat).pack(fill="x", pady=3)

    def acao_chat(self, acao, ident):
        if self._ocupado:
            return
        if acao == "fixar":
            self.historico.fixar(ident, not self.historico.obter(ident)["fixada"])
            self._atualizar_lista()
        elif acao == "renomear":
            self.renomear_chat(ident)
        else:
            self.trocar_chat(ident)
            if acao == "arquivar": self.arquivar_chat()
            elif acao == "excluir": self.excluir_chat()

    def _abrir_chat(self, ident):
        self.conversa_id = ident
        self.entrada.delete("1.0", "end")
        conversa = self.historico.obter(ident)
        self.botao_enviar.configure(state="disabled" if conversa["arquivada"] else "normal")
        self.entrada.insert("1.0", conversa["rascunho"])
        self._mostrar_conversa()
        self._atualizar_lista()

    def _mostrar_conversa(self):
        mensagens = self.historico.mensagens(self.conversa_id)
        texto = "\n\n---\n\n".join(
            ("## Voce\n" if m["papel"] == "user" else "## CadernoMat" + (" — erro" if m["estado"] == "erro" else "") + "\n") + m["texto"]
            for m in mensagens)
        self._mostrar_saida(texto or "## Comece uma conversa\nDigite sua duvida de matematica abaixo. Use Novo chat para estudar outro assunto.")
        self.saida._textbox.yview_moveto(1)

    def trocar_chat(self, ident):
        if self._ocupado:
            return
        self.historico.rascunho(self.conversa_id, self.entrada.get("1.0", "end").rstrip())
        self._abrir_chat(ident)

    def novo_chat(self):
        if self._ocupado:
            return
        self.historico.rascunho(self.conversa_id, self.entrada.get("1.0", "end").rstrip())
        self._arquivados = False
        self.botao_arquivo.configure(text="Ver arquivados")
        self.busca.delete(0, "end")
        self._abrir_chat(self.historico.criar())
        self.estado.configure(text="Novo chat", text_color=MUTED)

    def renomear_chat(self, ident=None):
        if self._ocupado:
            return
        titulo = ctk.CTkInputDialog(text="Titulo da conversa:", title="Renomear chat").get_input()
        if titulo and titulo.strip():
            self.historico.renomear(ident or self.conversa_id, titulo)
            self._atualizar_lista()

    def alternar_arquivados(self):
        if self._ocupado:
            return
        self._arquivados = not self._arquivados
        self.botao_arquivo.configure(text="Ver ativos" if self._arquivados else "Ver arquivados")
        self._atualizar_lista()

    def _selecionar_apos_remocao(self):
        conversas = self.historico.listar(arquivadas=self._arquivados)
        if not conversas:
            self._arquivados = False
            self.botao_arquivo.configure(text="Ver arquivados")
            conversas = self.historico.listar()
        self._abrir_chat(conversas[0]["id"] if conversas else self.historico.criar())

    def arquivar_chat(self):
        if self._ocupado:
            return
        conversa = self.historico.obter(self.conversa_id)
        self.historico.rascunho(self.conversa_id, self.entrada.get("1.0", "end").rstrip())
        self.historico.arquivar(self.conversa_id, not conversa["arquivada"])
        self._selecionar_apos_remocao()
        self.estado.configure(text="Chat restaurado" if conversa["arquivada"] else "Chat arquivado", text_color=MUTED)

    def excluir_chat(self):
        if self._ocupado:
            return
        titulo = self.historico.obter(self.conversa_id)["titulo"]
        if not messagebox.askyesno("Excluir conversa", f'Excluir "{titulo}" e todas as suas mensagens? Esta acao nao pode ser desfeita. Voce pode arquivar para preservar o chat.', parent=self):
            return
        self.historico.excluir(self.conversa_id)
        self._selecionar_apos_remocao()
        self.estado.configure(text="Chat excluido", text_color=MUTED)

    def fechar(self):
        self.historico.rascunho(self.conversa_id, self.entrada.get("1.0", "end").rstrip())
        self.historico.fechar()
        self.after_cancel(self._timer_fila)
        self.destroy()

    def enviar(self) -> None:
        if self.historico.obter(self.conversa_id)["arquivada"]:
            self.estado.configure(text="Restaure o chat para continuar", text_color=MUTED)
            return
        if self._ocupado:
            return
        texto = self.entrada.get("1.0", "end").strip()
        if not texto:
            self.estado.configure(text="Digite uma mensagem", text_color="#AD4D36")
            return
        modo = self.modo.get()
        contexto = self.historico.mensagens(self.conversa_id)
        self.historico.adicionar(self.conversa_id, "user", texto)
        if len(self.historico.mensagens(self.conversa_id)) == 1:
            self.historico.renomear(self.conversa_id, texto.splitlines()[0][:80])
        self.historico.rascunho(self.conversa_id, "")
        self.entrada.delete("1.0", "end")
        self._mostrar_conversa()
        self._atualizar_lista()
        self._ocupado = True
        self.botao_enviar.configure(state="disabled")
        self.estado.configure(text="Consultando...", text_color=ACCENT)
        Thread(target=self._executar, args=(modo, texto, contexto), daemon=True).start()

    def _executar(self, modo: str, texto: str, historico=None) -> None:
        try:
            if historico and modo != "Resolver":
                resposta = perguntar(texto, modo="Resolver" if modo == "Resolver com IA" else modo, historico=historico)
            elif modo in {"Resolver", "Resolver com IA"}:
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
            provedor = provedor_ativo()
            _, modelo = configuracao()
            self.historico.adicionar(self.conversa_id, "assistant", mensagem, estado=tipo if tipo == "erro" else "ok", provedor=provedor, modelo=modelo)
            self._mostrar_conversa()
            self.estado.configure(
                text="Concluído" if tipo == "ok" else "Não foi possível concluir",
                text_color=ACCENT if tipo == "ok" else "#AD4D36",
            )
        self._timer_fila = self.after(100, self._verificar_fila)


def main() -> None:
    ctk.set_appearance_mode("light")
    janela = TutorDesktop()
    janela.mainloop()


if __name__ == "__main__":
    main()
