from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any

from leitor import LeitorEPUB
from modelos import HQ, Manga, LivroDigital, ObraDigital, StatusLeitura
from servicos import BibliotecaDigital
from validacoes import FORMATOS_ACEITOS, FORMATOS_IMAGEM


class GradeObras:
    LARGURA_CARD = 184

    def __init__(
        self,
        pai: tk.Misc,
        biblioteca: BibliotecaDigital,
        cores: dict[str, str],
        ao_abrir: Any,
    ) -> None:
        self.biblioteca = biblioteca
        self.cores = cores
        self.ao_abrir = ao_abrir
        self.obras: list[ObraDigital] = []
        self.id_selecionado: str | None = None
        self._fotos: dict[str, Any] = {}
        self._cards: dict[str, tk.Frame] = {}
        self._colunas = 1
        self._redimensionamento_id: str | None = None

        self.corpo = tk.Frame(pai, bg=cores["painel"])
        self.corpo.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(
            self.corpo,
            bg=cores["painel"],
            highlightthickness=0,
            borderwidth=0,
        )
        self.barra = ttk.Scrollbar(self.corpo, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.barra.set)
        self.barra.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.interior = tk.Frame(self.canvas, bg=cores["painel"])
        self._janela_interior = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")
        self.interior.bind("<Configure>", self._atualizar_regiao)
        self.canvas.bind("<Configure>", self._redimensionar)
        self.canvas.bind("<Enter>", lambda _evento: self.canvas.bind_all("<MouseWheel>", self._rolar))
        self.canvas.bind("<Leave>", lambda _evento: self.canvas.unbind_all("<MouseWheel>"))

    def atualizar(self, obras: list[ObraDigital]) -> None:
        self.obras = obras
        ids = {obra.id_obra for obra in obras}
        if self.id_selecionado not in ids:
            self.id_selecionado = None
        self._renderizar()

    def selecionado(self) -> str | None:
        return self.id_selecionado

    def selecionar(self, id_obra: str) -> None:
        self.id_selecionado = id_obra
        for identificador, card in self._cards.items():
            selecionado = identificador == id_obra
            card.configure(
                highlightbackground=self.cores["destaque"] if selecionado else self.cores["borda"],
                highlightthickness=3 if selecionado else 1,
            )

    def _renderizar(self) -> None:
        for widget in self.interior.winfo_children():
            widget.destroy()
        self._fotos.clear()
        self._cards.clear()

        if not self.obras:
            tk.Label(
                self.interior,
                text="Nenhuma obra encontrada.\nAdicione um arquivo para começar sua coleção.",
                bg=self.cores["painel"],
                fg=self.cores["suave"],
                font=("Georgia", 13),
                justify="center",
                pady=60,
            ).grid(row=0, column=0, sticky="nsew")
            self.interior.grid_columnconfigure(0, weight=1)
            return

        for indice, obra in enumerate(self.obras):
            linha, coluna = divmod(indice, self._colunas)
            card = self._criar_card(obra)
            card.grid(row=linha, column=coluna, padx=9, pady=9, sticky="n")
            self._cards[obra.id_obra] = card
        for coluna in range(self._colunas):
            self.interior.grid_columnconfigure(coluna, weight=1)
        if self.id_selecionado:
            self.selecionar(self.id_selecionado)

    def _criar_card(self, obra: ObraDigital) -> tk.Frame:
        from PIL import ImageTk

        card = tk.Frame(
            self.interior,
            width=self.LARGURA_CARD,
            height=326,
            bg="#FFFFFF",
            highlightbackground=self.cores["borda"],
            highlightthickness=1,
            cursor="hand2",
        )
        card.grid_propagate(False)
        miniatura = self.biblioteca.obter_miniatura(obra.id_obra, (150, 215))
        foto = ImageTk.PhotoImage(miniatura)
        self._fotos[obra.id_obra] = foto

        capa = tk.Label(card, image=foto, bg="#FFFFFF", cursor="hand2")
        capa.grid(row=0, column=0, padx=16, pady=(14, 8))
        titulo = tk.Label(
            card,
            text=obra.titulo,
            bg="#FFFFFF",
            fg=self.cores["texto"],
            font=("Georgia", 10, "bold"),
            wraplength=152,
            justify="left",
            anchor="w",
            cursor="hand2",
        )
        titulo.grid(row=1, column=0, padx=14, sticky="ew")
        autor = tk.Label(
            card,
            text=obra.autor,
            bg="#FFFFFF",
            fg=self.cores["suave"],
            font=("Segoe UI", 8),
            wraplength=152,
            anchor="w",
            cursor="hand2",
        )
        autor.grid(row=2, column=0, padx=14, pady=(2, 5), sticky="ew")

        progresso = self.biblioteca.obter_progresso(obra.id_obra)
        trilho = tk.Frame(card, bg="#E3DED4", width=152, height=5)
        trilho.grid(row=3, column=0, padx=14, sticky="w")
        trilho.grid_propagate(False)
        preenchimento = max(0, min(152, int(152 * progresso.porcentagem / 100)))
        if preenchimento:
            tk.Frame(trilho, bg=self.cores["destaque"], width=preenchimento, height=5).place(x=0, y=0)

        rodape = tk.Frame(card, bg="#FFFFFF")
        rodape.grid(row=4, column=0, padx=14, pady=(5, 9), sticky="ew")
        tk.Label(
            rodape,
            text=f"{obra.formato} · {progresso.porcentagem:.0f}%",
            bg="#FFFFFF",
            fg=self.cores["suave"],
            font=("Segoe UI", 7, "bold"),
        ).pack(side="left")
        if obra.favorito:
            tk.Label(rodape, text="★", bg="#FFFFFF", fg=self.cores["ouro"], font=("Segoe UI", 10)).pack(side="right")

        widgets = [card]
        pendentes = list(card.winfo_children())
        while pendentes:
            widget = pendentes.pop()
            widgets.append(widget)
            pendentes.extend(widget.winfo_children())
        for widget in widgets:
            widget.bind("<Button-1>", lambda _evento, item=obra.id_obra: self.selecionar(item))
            widget.bind("<Double-1>", lambda _evento, item=obra.id_obra: self.ao_abrir(item))
        return card

    def _redimensionar(self, evento: tk.Event[Any]) -> None:
        self.canvas.itemconfigure(self._janela_interior, width=evento.width)
        novas_colunas = max(1, evento.width // (self.LARGURA_CARD + 24))
        if novas_colunas != self._colunas:
            self._colunas = novas_colunas
            if self._redimensionamento_id:
                self.canvas.after_cancel(self._redimensionamento_id)
            self._redimensionamento_id = self.canvas.after(120, self._renderizar)

    def _atualizar_regiao(self, _evento: tk.Event[Any]) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _rolar(self, evento: tk.Event[Any]) -> None:
        self.canvas.yview_scroll(int(-evento.delta / 120), "units")


class BibliotecaApp:
    CAPA_AUTOMATICA = "<gerar automaticamente>"
    CORES = {
        "fundo": "#F1EEE6",
        "painel": "#FFFDF8",
        "escuro": "#17232D",
        "escuro_2": "#223440",
        "destaque": "#E7643B",
        "destaque_hover": "#C94C28",
        "ouro": "#D9A441",
        "texto": "#1E2A30",
        "suave": "#6B7478",
        "borda": "#D9D5CC",
    }

    def __init__(self, root: tk.Tk, biblioteca: BibliotecaDigital) -> None:
        self.root = root
        self.biblioteca = biblioteca
        self.root.title("BookReadNet | Biblioteca digital")
        self.root.geometry("1180x760")
        self.root.minsize(980, 650)
        self.root.configure(bg=self.CORES["fundo"])
        self._configurar_estilo()

        self.status_var = tk.StringVar(value="Acervo carregado.")
        self.telas: dict[str, ttk.Frame] = {}
        self.botoes_navegacao: dict[str, tk.Button] = {}
        self._construir_layout()
        self.atualizar_tudo()
        self._mostrar_tela("Acervo")

    def _configurar_estilo(self) -> None:
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TFrame", background=self.CORES["fundo"])
        estilo.configure("Panel.TFrame", background=self.CORES["painel"])
        estilo.configure("TLabel", background=self.CORES["fundo"], foreground=self.CORES["texto"], font=("Segoe UI", 10))
        estilo.configure("Panel.TLabel", background=self.CORES["painel"], foreground=self.CORES["texto"], font=("Segoe UI", 10))
        estilo.configure("Title.TLabel", background=self.CORES["fundo"], foreground=self.CORES["texto"], font=("Georgia", 24, "bold"))
        estilo.configure("Subtitle.TLabel", background=self.CORES["fundo"], foreground=self.CORES["suave"], font=("Segoe UI", 10))
        estilo.configure("Section.TLabel", background=self.CORES["painel"], foreground=self.CORES["texto"], font=("Georgia", 15, "bold"))
        estilo.configure("TButton", padding=(12, 8), font=("Segoe UI", 9, "bold"))
        estilo.configure("Primary.TButton", background=self.CORES["destaque"], foreground="white", borderwidth=0)
        estilo.map("Primary.TButton", background=[("active", self.CORES["destaque_hover"])])
        estilo.configure("Danger.TButton", foreground="#A53720")
        estilo.configure("Treeview", background=self.CORES["painel"], fieldbackground=self.CORES["painel"], foreground=self.CORES["texto"], rowheight=34, borderwidth=0, font=("Segoe UI", 9))
        estilo.configure("Treeview.Heading", background="#E7E2D8", foreground=self.CORES["texto"], padding=8, font=("Segoe UI", 9, "bold"))
        estilo.map("Treeview", background=[("selected", self.CORES["escuro_2"])], foreground=[("selected", "white")])
        estilo.configure("Horizontal.TProgressbar", background=self.CORES["destaque"], troughcolor="#DDD8CE")

    def _construir_layout(self) -> None:
        sidebar = tk.Frame(self.root, bg=self.CORES["escuro"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="BOOK", bg=self.CORES["escuro"], fg=self.CORES["ouro"], font=("Georgia", 13, "bold")).pack(anchor="w", padx=24, pady=(28, 0))
        tk.Label(sidebar, text="READ NET", bg=self.CORES["escuro"], fg="white", font=("Georgia", 22, "bold")).pack(anchor="w", padx=24, pady=(0, 32))

        for nome in ("Acervo", "Continuar lendo", "Favoritos", "Histórico"):
            botao = tk.Button(
                sidebar,
                text=nome,
                command=lambda tela=nome: self._mostrar_tela(tela),
                bg=self.CORES["escuro"],
                fg="#DCE3E6",
                activebackground=self.CORES["escuro_2"],
                activeforeground="white",
                relief="flat",
                anchor="w",
                padx=24,
                pady=13,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            )
            botao.pack(fill="x")
            self.botoes_navegacao[nome] = botao

        tk.Button(
            sidebar,
            text="+  Adicionar obra",
            command=self.abrir_dialogo_cadastro,
            bg=self.CORES["destaque"],
            fg="white",
            activebackground=self.CORES["destaque_hover"],
            activeforeground="white",
            relief="flat",
            padx=16,
            pady=11,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        ).pack(side="bottom", fill="x", padx=20, pady=24)

        area = ttk.Frame(self.root, padding=(26, 22, 26, 10))
        area.pack(side="left", fill="both", expand=True)

        cabecalho = ttk.Frame(area)
        cabecalho.pack(fill="x", pady=(0, 18))
        ttk.Label(cabecalho, text="Sua biblioteca, no seu ritmo.", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            cabecalho,
            text="Organize e leia HQs, mangás e livros em PDF, CBZ, CBR e CB7.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        self.container = ttk.Frame(area)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self._construir_tela_acervo()
        self._construir_tela_continuar()
        self._construir_tela_favoritos()
        self._construir_tela_historico()

        ttk.Label(area, textvariable=self.status_var, style="Subtitle.TLabel", anchor="w").pack(fill="x", pady=(9, 0))

    def _nova_tela(self, nome: str) -> ttk.Frame:
        frame = ttk.Frame(self.container)
        frame.grid(row=0, column=0, sticky="nsew")
        self.telas[nome] = frame
        return frame

    def _construir_tela_acervo(self) -> None:
        tela = self._nova_tela("Acervo")
        self.busca_var = tk.StringVar()
        self.tipo_var = tk.StringVar(value="Todos")
        self.status_filtro_var = tk.StringVar(value="Todos")

        metricas = ttk.Frame(tela)
        metricas.pack(fill="x", pady=(0, 14))
        self.total_var = tk.StringVar()
        self.lendo_var = tk.StringVar()
        self.lidos_var = tk.StringVar()
        for coluna, (rotulo, variavel) in enumerate(
            (("NO ACERVO", self.total_var), ("EM LEITURA", self.lendo_var), ("CONCLUÍDOS", self.lidos_var))
        ):
            card = tk.Frame(metricas, bg=self.CORES["painel"], highlightbackground=self.CORES["borda"], highlightthickness=1)
            card.grid(row=0, column=coluna, sticky="ew", padx=(0, 10 if coluna < 2 else 0))
            metricas.grid_columnconfigure(coluna, weight=1)
            tk.Label(card, text=rotulo, bg=self.CORES["painel"], fg=self.CORES["suave"], font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(12, 2))
            tk.Label(card, textvariable=variavel, bg=self.CORES["painel"], fg=self.CORES["texto"], font=("Georgia", 20, "bold")).pack(anchor="w", padx=16, pady=(0, 11))

        painel = ttk.Frame(tela, style="Panel.TFrame", padding=16)
        painel.pack(fill="both", expand=True)
        filtros = ttk.Frame(painel, style="Panel.TFrame")
        filtros.pack(fill="x", pady=(0, 12))
        ttk.Label(filtros, text="Minha biblioteca", style="Section.TLabel").pack(side="left")
        ttk.Entry(filtros, textvariable=self.busca_var, width=28).pack(side="left", padx=(24, 8))
        ttk.Combobox(filtros, textvariable=self.tipo_var, values=("Todos", "HQ", "Mangá", "Livro digital"), state="readonly", width=14).pack(side="left", padx=4)
        ttk.Combobox(
            filtros,
            textvariable=self.status_filtro_var,
            values=("Todos",) + tuple(item.value for item in StatusLeitura),
            state="readonly",
            width=14,
        ).pack(side="left", padx=4)
        ttk.Button(filtros, text="Filtrar", command=self.atualizar_acervo).pack(side="left", padx=(4, 0))

        self.grade_acervo = GradeObras(painel, self.biblioteca, self.CORES, self.abrir_detalhes)

        acoes = ttk.Frame(painel, style="Panel.TFrame")
        acoes.pack(fill="x", pady=(12, 0))
        ttk.Button(acoes, text="Ler / Continuar", style="Primary.TButton", command=self.abrir_leitura).pack(side="left")
        ttk.Button(acoes, text="Favoritar", command=self.alternar_favorito).pack(side="left", padx=7)
        ttk.Button(acoes, text="Editar", command=self.editar_obra).pack(side="left")
        ttk.Button(acoes, text="Excluir", style="Danger.TButton", command=self.excluir_obra).pack(side="right")

        self.busca_var.trace_add("write", lambda *_: self.atualizar_acervo())

    def _construir_tela_continuar(self) -> None:
        tela = self._nova_tela("Continuar lendo")
        painel = ttk.Frame(tela, style="Panel.TFrame", padding=18)
        painel.pack(fill="both", expand=True)
        ttk.Label(painel, text="Continue de onde parou", style="Section.TLabel").pack(anchor="w")
        ttk.Label(painel, text="As leituras mais recentes aparecem primeiro.", style="Panel.TLabel").pack(anchor="w", pady=(4, 14))
        self.grade_continuar = GradeObras(painel, self.biblioteca, self.CORES, self.abrir_detalhes)
        ttk.Button(
            painel,
            text="Continuar leitura",
            style="Primary.TButton",
            command=lambda: self.abrir_leitura(self.grade_continuar.selecionado()),
        ).pack(anchor="w", pady=(12, 0))

    def _construir_tela_favoritos(self) -> None:
        tela = self._nova_tela("Favoritos")
        painel = ttk.Frame(tela, style="Panel.TFrame", padding=18)
        painel.pack(fill="both", expand=True)
        ttk.Label(painel, text="Obras favoritas", style="Section.TLabel").pack(anchor="w", pady=(0, 14))
        self.grade_favoritos = GradeObras(painel, self.biblioteca, self.CORES, self.abrir_detalhes)

    def _construir_tela_historico(self) -> None:
        tela = self._nova_tela("Histórico")
        painel = ttk.Frame(tela, style="Panel.TFrame", padding=18)
        painel.pack(fill="both", expand=True)
        ttk.Label(painel, text="Histórico de leitura", style="Section.TLabel").pack(anchor="w")
        ttk.Label(painel, text="Últimas 100 páginas registradas.", style="Panel.TLabel").pack(anchor="w", pady=(4, 14))
        corpo = ttk.Frame(painel, style="Panel.TFrame")
        corpo.pack(fill="both", expand=True)
        self.lista_historico = tk.Listbox(
            corpo,
            bg=self.CORES["painel"],
            fg=self.CORES["texto"],
            selectbackground=self.CORES["escuro_2"],
            relief="flat",
            borderwidth=0,
            font=("Consolas", 10),
            activestyle="none",
        )
        self.lista_historico.pack(side="left", fill="both", expand=True)
        barra = ttk.Scrollbar(corpo, command=self.lista_historico.yview)
        barra.pack(side="right", fill="y")
        self.lista_historico.configure(yscrollcommand=barra.set)

    def _mostrar_tela(self, nome: str) -> None:
        nome_real = "Favoritos" if nome == "Favoritos" else nome
        self.telas[nome_real].tkraise()
        for titulo, botao in self.botoes_navegacao.items():
            botao.configure(bg=self.CORES["escuro_2"] if titulo == nome else self.CORES["escuro"])
        self.atualizar_tudo()

    def atualizar_tudo(self) -> None:
        self.atualizar_acervo()
        self.grade_continuar.atualizar(self.biblioteca.continuar_lendo())
        self.grade_favoritos.atualizar(self.biblioteca.filtrar(somente_favoritos=True))
        self.lista_historico.delete(0, tk.END)
        for linha in self.biblioteca.listar_historico():
            self.lista_historico.insert(tk.END, linha)
        obras = self.biblioteca.obras
        self.total_var.set(str(len(obras)))
        self.lendo_var.set(str(sum(obra.status_leitura == StatusLeitura.EM_LEITURA for obra in obras)))
        self.lidos_var.set(str(sum(obra.status_leitura == StatusLeitura.LIDO for obra in obras)))

    def atualizar_acervo(self) -> None:
        obras = self.biblioteca.filtrar(
            termo=self.busca_var.get(),
            tipo=self.tipo_var.get(),
            status=self.status_filtro_var.get(),
        )
        self.grade_acervo.atualizar(obras)

    def _obra_selecionada(self) -> ObraDigital | None:
        id_obra = self.grade_acervo.selecionado()
        if not id_obra:
            messagebox.showwarning("Seleção necessária", "Selecione uma obra no acervo.")
            return None
        return self.biblioteca.buscar_por_id(id_obra)

    def abrir_dialogo_cadastro(self) -> None:
        self._dialogo_obra()

    def editar_obra(self, id_obra: str | None = None) -> None:
        obra = self.biblioteca.buscar_por_id(id_obra) if id_obra else self._obra_selecionada()
        if obra:
            self._dialogo_obra(obra)

    def _dialogo_obra(self, obra: ObraDigital | None = None) -> None:
        janela = tk.Toplevel(self.root)
        janela.title("Editar obra" if obra else "Adicionar obra")
        janela.geometry("860x650")
        janela.resizable(False, False)
        janela.configure(bg=self.CORES["fundo"])
        janela.transient(self.root)
        janela.grab_set()

        painel = ttk.Frame(janela, style="Panel.TFrame", padding=22)
        painel.pack(fill="both", expand=True, padx=18, pady=18)
        ttk.Label(painel, text="Editar metadados" if obra else "Nova obra digital", style="Section.TLabel").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 18))

        vars_form = {
            "titulo": tk.StringVar(value=obra.titulo if obra else ""),
            "autor": tk.StringVar(value=obra.autor if obra else ""),
            "tipo": tk.StringVar(value=obra.obter_tipo() if obra else "Mangá"),
            "categoria": tk.StringVar(value=obra.categoria if obra else ""),
            "serie": tk.StringVar(value=obra.serie if obra else ""),
            "editora": tk.StringVar(value=obra.editora if obra else ""),
            "idioma": tk.StringVar(value=obra.idioma if obra else "Português"),
            "detalhe": tk.StringVar(value=self._detalhe_obra(obra) if obra else ""),
            "arquivo": tk.StringVar(value=obra.caminho_arquivo if obra else ""),
            "capa": tk.StringVar(value=obra.caminho_capa if obra else self.CAPA_AUTOMATICA),
        }
        detalhe_label = tk.StringVar()
        capa_original = obra.caminho_capa if obra else ""
        preview_foto: dict[str, Any] = {}

        campos = (
            ("Título *", "titulo"),
            ("Autor", "autor"),
            ("Tipo", "tipo"),
            ("Categoria", "categoria"),
            ("Série", "serie"),
            ("Editora", "editora"),
            ("Idioma", "idioma"),
        )
        for linha, (rotulo, chave) in enumerate(campos, start=1):
            ttk.Label(painel, text=rotulo, style="Panel.TLabel").grid(row=linha, column=0, sticky="w", pady=6, padx=(0, 12))
            if chave == "tipo":
                widget = ttk.Combobox(painel, textvariable=vars_form[chave], values=tuple(self.biblioteca.TIPOS_OBRA), state="disabled" if obra else "readonly", width=39)
            else:
                widget = ttk.Entry(painel, textvariable=vars_form[chave], width=42)
            widget.grid(row=linha, column=1, columnspan=2, sticky="ew", pady=6)

        ttk.Label(painel, textvariable=detalhe_label, style="Panel.TLabel").grid(row=8, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Entry(painel, textvariable=vars_form["detalhe"], width=42).grid(row=8, column=1, columnspan=2, sticky="ew", pady=6)

        ttk.Label(painel, text="Arquivo *", style="Panel.TLabel").grid(row=9, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Entry(painel, textvariable=vars_form["arquivo"], state="readonly", width=34).grid(row=9, column=1, sticky="ew", pady=6)
        ttk.Button(painel, text="Selecionar", state="disabled" if obra else "normal", command=lambda: self._selecionar_arquivo(vars_form)).grid(row=9, column=2, padx=(8, 0))

        ttk.Label(painel, text="Capa", style="Panel.TLabel").grid(row=10, column=0, sticky="w", pady=6, padx=(0, 12))
        ttk.Entry(painel, textvariable=vars_form["capa"], state="readonly", width=34).grid(row=10, column=1, sticky="ew", pady=6)
        acoes_capa = ttk.Frame(painel, style="Panel.TFrame")
        acoes_capa.grid(row=10, column=2, padx=(8, 0))

        preview = tk.Label(
            painel,
            bg=self.CORES["fundo"],
            highlightbackground=self.CORES["borda"],
            highlightthickness=1,
        )
        preview.grid(row=1, column=3, rowspan=8, padx=(24, 0), sticky="n")
        ttk.Label(painel, text="Prévia da capa", style="Panel.TLabel").grid(row=9, column=3, padx=(24, 0), sticky="n")

        def atualizar_preview() -> None:
            from PIL import Image, ImageOps, ImageTk

            caminho = vars_form["capa"].get()
            try:
                if caminho and caminho != self.CAPA_AUTOMATICA and Path(caminho).exists():
                    with Image.open(caminho) as imagem:
                        miniatura = ImageOps.fit(
                            imagem.convert("RGB"),
                            (150, 215),
                            method=Image.Resampling.LANCZOS,
                        )
                else:
                    miniatura = self.biblioteca.servico_capas.criar_capa_padrao(
                        vars_form["titulo"].get() or "BookReadNet",
                        (150, 215),
                    )
                foto = ImageTk.PhotoImage(miniatura)
                preview.configure(image=foto, text="")
                preview_foto["imagem"] = foto
            except (OSError, ValueError):
                preview.configure(image="", text="Imagem inválida", fg="#A53720", width=20, height=12)

        ttk.Button(
            acoes_capa,
            text="Escolher",
            command=lambda: self._selecionar_capa(vars_form, atualizar_preview),
        ).pack(side="left")
        ttk.Button(
            acoes_capa,
            text="Automática",
            command=lambda: (vars_form["capa"].set(self.CAPA_AUTOMATICA), atualizar_preview()),
        ).pack(side="left", padx=4)
        ttk.Button(
            acoes_capa,
            text="Remover",
            command=lambda: (vars_form["capa"].set(""), atualizar_preview()),
        ).pack(side="left")

        def atualizar_detalhe(*_args: Any) -> None:
            detalhe_label.set({"HQ": "Nº da edição", "Mangá": "Volume", "Livro digital": "Edição"}.get(vars_form["tipo"].get(), "Detalhe"))

        vars_form["tipo"].trace_add("write", atualizar_detalhe)
        atualizar_detalhe()

        def salvar() -> None:
            try:
                especifico = self._dados_especificos(vars_form["tipo"].get(), vars_form["detalhe"].get())
                if obra:
                    self.biblioteca.editar_obra(
                        obra.id_obra,
                        titulo=vars_form["titulo"].get(),
                        autor=vars_form["autor"].get(),
                        categoria=vars_form["categoria"].get(),
                        serie=vars_form["serie"].get(),
                        editora=vars_form["editora"].get(),
                        idioma=vars_form["idioma"].get(),
                        **especifico,
                    )
                    capa_escolhida = vars_form["capa"].get()
                    if capa_escolhida == self.CAPA_AUTOMATICA:
                        self.biblioteca.gerar_capa_automatica(obra.id_obra)
                    elif capa_escolhida != capa_original:
                        self.biblioteca.atualizar_capa(obra.id_obra, capa_escolhida)
                    mensagem = "Obra atualizada com sucesso."
                else:
                    capa_escolhida = vars_form["capa"].get()
                    self.biblioteca.cadastrar_obra(
                        tipo=vars_form["tipo"].get(),
                        titulo=vars_form["titulo"].get(),
                        autor=vars_form["autor"].get(),
                        categoria=vars_form["categoria"].get(),
                        serie=vars_form["serie"].get(),
                        editora=vars_form["editora"].get(),
                        idioma=vars_form["idioma"].get(),
                        caminho_arquivo=vars_form["arquivo"].get(),
                        caminho_capa="" if capa_escolhida == self.CAPA_AUTOMATICA else capa_escolhida,
                        extrair_capa_automatica=capa_escolhida == self.CAPA_AUTOMATICA,
                        **especifico,
                    )
                    mensagem = "Obra importada para o acervo."
                self.status_var.set(mensagem)
                self.atualizar_tudo()
                janela.destroy()
                messagebox.showinfo("BookReadNet", mensagem)
            except (OSError, RuntimeError, ValueError) as erro:
                messagebox.showerror("Não foi possível salvar", str(erro), parent=janela)

        painel.grid_columnconfigure(1, weight=1)
        vars_form["titulo"].trace_add("write", lambda *_: atualizar_preview())
        atualizar_preview()
        botoes = ttk.Frame(painel, style="Panel.TFrame")
        botoes.grid(row=11, column=0, columnspan=4, sticky="e", pady=(20, 0))
        ttk.Button(botoes, text="Cancelar", command=janela.destroy).pack(side="left", padx=(0, 8))
        ttk.Button(botoes, text="Salvar obra", style="Primary.TButton", command=salvar).pack(side="left")

    def _selecionar_arquivo(self, vars_form: dict[str, tk.StringVar]) -> None:
        tipos = [("Quadrinhos e documentos", " ".join(f"*{item}" for item in FORMATOS_ACEITOS)), ("Todos", "*.*")]
        caminho = filedialog.askopenfilename(title="Selecionar obra", filetypes=tipos, parent=self.root)
        if caminho:
            if Path(caminho).suffix.lower() == ".epub":
                try:
                    metadados = self.biblioteca.obter_metadados_arquivo(caminho)
                except (OSError, RuntimeError, ValueError) as erro:
                    messagebox.showerror("EPUB inválido", str(erro), parent=self.root)
                    return
                vars_form["tipo"].set("Livro digital")
                for campo in ("titulo", "autor", "editora", "idioma"):
                    if metadados.get(campo):
                        vars_form[campo].set(metadados[campo])
            vars_form["arquivo"].set(caminho)
            if not vars_form["titulo"].get().strip():
                vars_form["titulo"].set(Path(caminho).stem.replace("_", " "))

    def _selecionar_capa(self, vars_form: dict[str, tk.StringVar], ao_selecionar: Any = None) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecionar capa",
            filetypes=[("Imagens", " ".join(f"*{item}" for item in FORMATOS_IMAGEM)), ("Todos", "*.*")],
            parent=self.root,
        )
        if caminho:
            vars_form["capa"].set(caminho)
            if ao_selecionar:
                ao_selecionar()

    @staticmethod
    def _dados_especificos(tipo: str, detalhe: str) -> dict[str, str]:
        return {
            "HQ": {"numero_edicao": detalhe},
            "Mangá": {"volume": detalhe},
            "Livro digital": {"edicao": detalhe},
        }.get(tipo, {})

    @staticmethod
    def _detalhe_obra(obra: ObraDigital | None) -> str:
        if isinstance(obra, HQ):
            return obra.numero_edicao
        if isinstance(obra, Manga):
            return obra.volume
        if isinstance(obra, LivroDigital):
            return obra.edicao
        return ""

    def abrir_detalhes(self, id_obra: str) -> None:
        from PIL import ImageTk

        obra = self.biblioteca.buscar_por_id(id_obra)
        progresso = self.biblioteca.obter_progresso(id_obra)
        janela = tk.Toplevel(self.root)
        janela.title(f"Detalhes | {obra.titulo}")
        janela.geometry("780x520")
        janela.resizable(False, False)
        janela.configure(bg=self.CORES["fundo"])
        janela.transient(self.root)

        painel = ttk.Frame(janela, style="Panel.TFrame", padding=24)
        painel.pack(fill="both", expand=True, padx=18, pady=18)
        miniatura = self.biblioteca.obter_miniatura(id_obra, (220, 320))
        foto = ImageTk.PhotoImage(miniatura)
        capa = tk.Label(painel, image=foto, bg=self.CORES["painel"])
        capa.image = foto
        capa.grid(row=0, column=0, rowspan=10, sticky="n", padx=(0, 26))

        ttk.Label(painel, text=obra.titulo, style="Section.TLabel", font=("Georgia", 20, "bold")).grid(row=0, column=1, columnspan=3, sticky="w")
        ttk.Label(painel, text=obra.autor, style="Panel.TLabel", foreground=self.CORES["suave"]).grid(row=1, column=1, columnspan=3, sticky="w", pady=(2, 16))

        detalhes = [
            ("Tipo", obra.obter_tipo()),
            ("Formato", obra.formato),
            ("Categoria", obra.categoria),
            ("Série", obra.serie or "Sem série"),
            ("Editora", obra.editora or "Não informada"),
            ("Idioma", obra.idioma),
            ("Status", obra.status_leitura.value),
        ]
        detalhe_especifico = self._detalhe_obra(obra)
        if detalhe_especifico:
            detalhes.insert(4, ("Volume/Edição", detalhe_especifico))
        for linha, (rotulo, valor) in enumerate(detalhes, start=2):
            ttk.Label(painel, text=f"{rotulo}:", style="Panel.TLabel", font=("Segoe UI", 9, "bold")).grid(row=linha, column=1, sticky="w", pady=3)
            ttk.Label(painel, text=valor, style="Panel.TLabel").grid(row=linha, column=2, columnspan=2, sticky="w", pady=3)

        linha_progresso = 2 + len(detalhes)
        if progresso.tipo_posicao == "capitulo":
            posicao_atual = progresso.capitulo_atual
            total_posicoes = progresso.total_capitulos
            unidade = "capítulos"
        else:
            posicao_atual = progresso.pagina_atual
            total_posicoes = progresso.total_paginas
            unidade = "páginas"
        ttk.Label(
            painel,
            text=f"Progresso: {posicao_atual}/{total_posicoes or '?'} {unidade} ({progresso.porcentagem:.1f}%)",
            style="Panel.TLabel",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=linha_progresso, column=1, columnspan=3, sticky="w", pady=(14, 5))
        barra = ttk.Progressbar(painel, maximum=100, value=progresso.porcentagem, length=390)
        barra.grid(row=linha_progresso + 1, column=1, columnspan=3, sticky="ew")

        acoes = ttk.Frame(painel, style="Panel.TFrame")
        acoes.grid(row=linha_progresso + 2, column=1, columnspan=3, sticky="w", pady=(18, 0))
        ttk.Button(
            acoes,
            text="Ler / Continuar",
            style="Primary.TButton",
            command=lambda: (janela.destroy(), self.abrir_leitura(id_obra)),
        ).pack(side="left")
        ttk.Button(
            acoes,
            text="Favoritar" if not obra.favorito else "Desfavoritar",
            command=lambda: self._acao_detalhes(janela, id_obra, "favorito"),
        ).pack(side="left", padx=6)
        ttk.Button(
            acoes,
            text="Editar",
            command=lambda: (janela.destroy(), self.editar_obra(id_obra)),
        ).pack(side="left")
        ttk.Button(
            acoes,
            text="Excluir",
            style="Danger.TButton",
            command=lambda: (janela.destroy(), self.excluir_obra(id_obra)),
        ).pack(side="left", padx=(6, 0))

        capas = ttk.Frame(painel, style="Panel.TFrame")
        capas.grid(row=linha_progresso + 3, column=1, columnspan=3, sticky="w", pady=(8, 0))
        ttk.Button(capas, text="Escolher capa", command=lambda: self._acao_detalhes(janela, id_obra, "capa")).pack(side="left")
        ttk.Button(capas, text="Gerar automática", command=lambda: self._acao_detalhes(janela, id_obra, "automatica")).pack(side="left", padx=6)
        ttk.Button(capas, text="Remover capa", command=lambda: self._acao_detalhes(janela, id_obra, "remover_capa")).pack(side="left")

    def _acao_detalhes(self, janela: tk.Toplevel, id_obra: str, acao: str) -> None:
        try:
            if acao == "favorito":
                self.biblioteca.alternar_favorito(id_obra)
            elif acao == "capa":
                caminho = filedialog.askopenfilename(
                    title="Selecionar capa",
                    filetypes=[("Imagens", " ".join(f"*{item}" for item in FORMATOS_IMAGEM)), ("Todos", "*.*")],
                    parent=janela,
                )
                if not caminho:
                    return
                self.biblioteca.atualizar_capa(id_obra, caminho)
            elif acao == "automatica":
                self.biblioteca.gerar_capa_automatica(id_obra)
            elif acao == "remover_capa":
                self.biblioteca.atualizar_capa(id_obra)
            self.atualizar_tudo()
            janela.destroy()
            self.root.after(20, lambda: self.abrir_detalhes(id_obra))
        except (OSError, RuntimeError, ValueError) as erro:
            messagebox.showerror("Não foi possível atualizar", str(erro), parent=janela)

    def alternar_favorito(self, id_obra: str | None = None) -> None:
        obra = self.biblioteca.buscar_por_id(id_obra) if id_obra else self._obra_selecionada()
        if not obra:
            return
        favorito = self.biblioteca.alternar_favorito(obra.id_obra)
        self.status_var.set("Adicionado aos favoritos." if favorito else "Removido dos favoritos.")
        self.atualizar_tudo()

    def excluir_obra(self, id_obra: str | None = None) -> None:
        obra = self.biblioteca.buscar_por_id(id_obra) if id_obra else self._obra_selecionada()
        if not obra:
            return
        if not messagebox.askyesno("Excluir obra", f"Remover '{obra.titulo}' do acervo?"):
            return
        excluir_arquivo = messagebox.askyesno(
            "Arquivo físico",
            "Deseja também excluir a cópia do arquivo armazenada pelo BookReadNet?",
        )
        try:
            self.biblioteca.excluir_obra(obra.id_obra, excluir_arquivo)
            self.status_var.set("Obra excluída do acervo.")
            self.atualizar_tudo()
        except (OSError, ValueError) as erro:
            messagebox.showerror("Falha ao excluir", str(erro))

    def abrir_leitura(self, id_obra: str | None = None) -> None:
        if not id_obra:
            id_obra = self.grade_acervo.selecionado()
        if not id_obra:
            messagebox.showwarning("Seleção necessária", "Selecione uma obra para ler.")
            return
        try:
            obra = self.biblioteca.buscar_por_id(id_obra)
            leitor = self.biblioteca.criar_leitor(id_obra)
            if isinstance(leitor, LeitorEPUB):
                JanelaLeituraEPUB(self.root, self.biblioteca, obra, leitor, self.atualizar_tudo)
            else:
                JanelaLeitura(self.root, self.biblioteca, obra, leitor, self.atualizar_tudo)
            self.status_var.set(f"Leitura aberta: {obra.titulo}")
        except (OSError, RuntimeError, ValueError) as erro:
            messagebox.showerror("Não foi possível abrir a obra", str(erro))


class JanelaLeituraEPUB:
    TEMAS = {
        "Claro": {"fundo": "#FFFDF8", "texto": "#1E2A30", "painel": "#F1EEE6"},
        "Sépia": {"fundo": "#F3E8CF", "texto": "#3F3023", "painel": "#E6D7B7"},
        "Escuro": {"fundo": "#17232D", "texto": "#E8E3D8", "painel": "#223440"},
    }
    ESPACAMENTOS = {
        "Compacto": (1, 3),
        "Confortável": (3, 6),
        "Amplo": (7, 11),
    }

    def __init__(
        self,
        root: tk.Tk,
        biblioteca: BibliotecaDigital,
        obra: ObraDigital,
        leitor: LeitorEPUB,
        ao_fechar: Any,
    ) -> None:
        self.biblioteca = biblioteca
        self.obra = obra
        self.leitor = leitor
        self.ao_fechar = ao_fechar
        self.tamanho_fonte = 15
        self.tema_var = tk.StringVar(value="Sépia")
        self.espacamento_var = tk.StringVar(value="Confortável")
        self.imagens: list[Any] = []
        self._capitulo_carregado = False

        progresso = biblioteca.obter_progresso(obra.id_obra)
        self.capitulo = min(max(progresso.capitulo_atual - 1, 0), leitor.total_paginas - 1)
        self.posicao_inicial = progresso.posicao_capitulo if progresso.tipo_posicao == "capitulo" else 0.0

        self.janela = tk.Toplevel(root)
        self.janela.title(f"Lendo EPUB | {obra.titulo}")
        self.janela.geometry("1160x800")
        self.janela.minsize(860, 600)
        self.janela.configure(bg="#17232D")
        self.janela.protocol("WM_DELETE_WINDOW", self.fechar)

        topo = tk.Frame(self.janela, bg="#17232D", height=62)
        topo.pack(fill="x")
        tk.Label(topo, text=obra.titulo, bg="#17232D", fg="white", font=("Georgia", 14, "bold")).pack(side="left", padx=18)
        tk.Button(topo, text="← Capítulo", command=self.anterior, **JanelaLeitura._estilo_botao()).pack(side="left", padx=(18, 5), pady=12)
        tk.Button(topo, text="Capítulo →", command=self.proximo, **JanelaLeitura._estilo_botao()).pack(side="left", padx=5, pady=12)
        self.capitulo_var = tk.StringVar()
        tk.Label(topo, textvariable=self.capitulo_var, bg="#17232D", fg="#D9A441", font=("Segoe UI", 9, "bold")).pack(side="left", padx=14)

        tk.Button(topo, text="A−", command=self.reduzir_fonte, **JanelaLeitura._estilo_botao()).pack(side="right", padx=(4, 18), pady=12)
        tk.Button(topo, text="A+", command=self.aumentar_fonte, **JanelaLeitura._estilo_botao()).pack(side="right", padx=4, pady=12)
        self.tema = ttk.Combobox(topo, textvariable=self.tema_var, values=tuple(self.TEMAS), state="readonly", width=9)
        self.tema.pack(side="right", padx=8)
        self.tema.bind("<<ComboboxSelected>>", lambda _evento: self._aplicar_tema())
        self.espacamento = ttk.Combobox(
            topo,
            textvariable=self.espacamento_var,
            values=tuple(self.ESPACAMENTOS),
            state="readonly",
            width=11,
        )
        self.espacamento.pack(side="right", padx=4)
        self.espacamento.bind("<<ComboboxSelected>>", lambda _evento: self._configurar_estilos())

        corpo = tk.Frame(self.janela, bg="#17232D")
        corpo.pack(fill="both", expand=True)
        lateral = tk.Frame(corpo, bg="#223440", width=245)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        tk.Label(lateral, text="SUMÁRIO", bg="#223440", fg="#D9A441", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(16, 8))
        self.sumario = tk.Listbox(
            lateral,
            bg="#223440",
            fg="#E8E3D8",
            selectbackground="#E7643B",
            selectforeground="white",
            relief="flat",
            borderwidth=0,
            activestyle="none",
            font=("Segoe UI", 9),
        )
        self.sumario.pack(fill="both", expand=True, padx=8, pady=(0, 12))
        for titulo in leitor.titulos_capitulos:
            self.sumario.insert(tk.END, titulo)
        self.sumario.bind("<<ListboxSelect>>", self._selecionar_sumario)

        area_texto = tk.Frame(corpo, bg="#F3E8CF")
        area_texto.pack(side="left", fill="both", expand=True)
        barra = ttk.Scrollbar(area_texto)
        barra.pack(side="right", fill="y")
        self.texto = tk.Text(
            area_texto,
            wrap="word",
            relief="flat",
            borderwidth=0,
            padx=54,
            pady=34,
            cursor="arrow",
            undo=False,
            yscrollcommand=barra.set,
        )
        self.texto.pack(fill="both", expand=True)
        barra.configure(command=self.texto.yview)

        self.janela.bind("<Alt-Left>", lambda _evento: self.anterior())
        self.janela.bind("<Alt-Right>", lambda _evento: self.proximo())
        self.janela.bind("<Control-plus>", lambda _evento: self.aumentar_fonte())
        self.janela.bind("<Control-minus>", lambda _evento: self.reduzir_fonte())
        self.janela.bind("<Escape>", lambda _evento: self.fechar())
        self._aplicar_tema()
        self._carregar_capitulo(self.capitulo, restaurar=True)

    def _configurar_estilos(self) -> None:
        tema = self.TEMAS[self.tema_var.get()]
        espacamento1, espacamento3 = self.ESPACAMENTOS[self.espacamento_var.get()]
        self.texto.configure(
            bg=tema["fundo"],
            fg=tema["texto"],
            insertbackground=tema["texto"],
            selectbackground="#E7643B",
            font=("Georgia", self.tamanho_fonte),
            spacing1=espacamento1,
            spacing3=espacamento3,
        )
        self.texto.tag_configure("negrito", font=("Georgia", self.tamanho_fonte, "bold"))
        self.texto.tag_configure("italico", font=("Georgia", self.tamanho_fonte, "italic"))
        self.texto.tag_configure("titulo1", font=("Georgia", self.tamanho_fonte + 10, "bold"), spacing1=16, spacing3=10)
        self.texto.tag_configure("titulo2", font=("Georgia", self.tamanho_fonte + 6, "bold"), spacing1=14, spacing3=8)
        self.texto.tag_configure("titulo3", font=("Georgia", self.tamanho_fonte + 3, "bold"), spacing1=10, spacing3=6)
        self.texto.tag_configure("citacao", lmargin1=28, lmargin2=28, foreground="#8B5E3C")
        self.texto.tag_configure("alinhamento_left", justify="left")
        self.texto.tag_configure("alinhamento_center", justify="center")
        self.texto.tag_configure("alinhamento_right", justify="right")
        self.texto.tag_configure("alinhamento_justify", justify="left")

    def _aplicar_tema(self) -> None:
        tema = self.TEMAS[self.tema_var.get()]
        self._configurar_estilos()
        self.sumario.configure(bg=tema["painel"], fg=tema["texto"])

    def _carregar_capitulo(self, numero: int, restaurar: bool = False) -> None:
        if numero < 0 or numero >= self.leitor.total_paginas:
            return
        if self._capitulo_carregado:
            self._salvar_progresso()
        self.capitulo = numero
        capitulo = self.leitor.obter_pagina(numero)
        self.texto.configure(state="normal")
        self.texto.delete("1.0", tk.END)
        self.imagens.clear()
        self._configurar_estilos()
        for token in capitulo.tokens:
            if token.tipo == "texto":
                self.texto.insert(tk.END, token.conteudo, token.estilos)
            elif token.tipo == "imagem":
                self._inserir_imagem(token.conteudo, token.alternativa)
        self.texto.configure(state="disabled")
        self.capitulo_var.set(f"Capítulo {numero + 1} de {self.leitor.total_paginas} · {capitulo.titulo}")
        self.sumario.selection_clear(0, tk.END)
        self.sumario.selection_set(numero)
        self.sumario.see(numero)
        self._capitulo_carregado = True
        posicao = self.posicao_inicial if restaurar else 0.0
        self.janela.after(80, lambda: self.texto.yview_moveto(posicao))

    def _inserir_imagem(self, caminho: str, alternativa: str) -> None:
        try:
            from PIL import Image, ImageTk

            imagem = self.leitor.obter_imagem(caminho)
            imagem.thumbnail((720, 560), Image.Resampling.LANCZOS)
            foto = ImageTk.PhotoImage(imagem)
            self.imagens.append(foto)
            self.texto.insert(tk.END, "\n")
            self.texto.image_create(tk.END, image=foto, padx=8, pady=8)
            self.texto.insert(tk.END, "\n")
        except (OSError, RuntimeError, ValueError):
            if alternativa:
                self.texto.insert(tk.END, f"\n[{alternativa}]\n", ("italico",))

    def _selecionar_sumario(self, _evento: tk.Event[Any]) -> None:
        selecao = self.sumario.curselection()
        if selecao and selecao[0] != self.capitulo:
            self._carregar_capitulo(selecao[0])

    def _salvar_progresso(self) -> None:
        inicio, fim = self.texto.yview()
        posicao = 1.0 if fim >= 0.999 else max(0.001, inicio)
        self.biblioteca.salvar_progresso_epub(
            self.obra.id_obra,
            self.capitulo + 1,
            self.leitor.total_paginas,
            posicao,
        )

    def anterior(self) -> None:
        if self.capitulo > 0:
            self._carregar_capitulo(self.capitulo - 1)

    def proximo(self) -> None:
        if self.capitulo < self.leitor.total_paginas - 1:
            self._carregar_capitulo(self.capitulo + 1)

    def aumentar_fonte(self) -> None:
        self.tamanho_fonte = min(28, self.tamanho_fonte + 1)
        self._configurar_estilos()

    def reduzir_fonte(self) -> None:
        self.tamanho_fonte = max(10, self.tamanho_fonte - 1)
        self._configurar_estilos()

    def fechar(self) -> None:
        try:
            if self._capitulo_carregado:
                self._salvar_progresso()
            self.leitor.fechar()
        finally:
            self.ao_fechar()
            self.janela.destroy()


class JanelaLeitura:
    def __init__(
        self,
        root: tk.Tk,
        biblioteca: BibliotecaDigital,
        obra: ObraDigital,
        leitor: Any,
        ao_fechar: Any,
    ) -> None:
        self.biblioteca = biblioteca
        self.obra = obra
        self.leitor = leitor
        self.ao_fechar = ao_fechar
        self.zoom = 1.0
        self.imagem_original: Any = None
        self.foto: Any = None
        self._redimensionamento_id: str | None = None

        progresso = biblioteca.obter_progresso(obra.id_obra)
        self.pagina = min(max(progresso.pagina_atual - 1, 0), leitor.total_paginas - 1)

        self.janela = tk.Toplevel(root)
        self.janela.title(f"Lendo | {obra.titulo}")
        self.janela.geometry("1120x780")
        self.janela.minsize(760, 560)
        self.janela.configure(bg="#10171C")
        self.janela.protocol("WM_DELETE_WINDOW", self.fechar)

        barra = tk.Frame(self.janela, bg="#17232D", height=62)
        barra.pack(fill="x")
        tk.Label(barra, text=obra.titulo, bg="#17232D", fg="white", font=("Georgia", 14, "bold")).pack(side="left", padx=18)
        tk.Button(barra, text="← Anterior", command=self.anterior, **self._estilo_botao()).pack(side="left", padx=(18, 5), pady=12)
        tk.Button(barra, text="Próxima →", command=self.proxima, **self._estilo_botao()).pack(side="left", padx=5, pady=12)

        self.pagina_var = tk.StringVar()
        tk.Label(barra, textvariable=self.pagina_var, bg="#17232D", fg="#D9A441", font=("Segoe UI", 10, "bold")).pack(side="left", padx=16)
        tk.Button(barra, text="−", command=self.reduzir_zoom, **self._estilo_botao()).pack(side="right", padx=(4, 18), pady=12)
        tk.Button(barra, text="+", command=self.aumentar_zoom, **self._estilo_botao()).pack(side="right", padx=4, pady=12)
        self.zoom_var = tk.StringVar(value="100%")
        tk.Label(barra, textvariable=self.zoom_var, bg="#17232D", fg="#DCE3E6", font=("Segoe UI", 9)).pack(side="right", padx=8)

        corpo = tk.Frame(self.janela, bg="#10171C")
        corpo.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(corpo, bg="#10171C", highlightthickness=0)
        barra_y = ttk.Scrollbar(corpo, orient="vertical", command=self.canvas.yview)
        barra_x = ttk.Scrollbar(corpo, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        barra_y.pack(side="right", fill="y")
        barra_x.pack(side="bottom", fill="x")
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self._agendar_redimensionamento)
        self.janela.bind("<Left>", lambda _evento: self.anterior())
        self.janela.bind("<Right>", lambda _evento: self.proxima())
        self.janela.bind("<Escape>", lambda _evento: self.fechar())
        self._carregar_pagina()

    @staticmethod
    def _estilo_botao() -> dict[str, Any]:
        return {
            "bg": "#223440",
            "fg": "white",
            "activebackground": "#E7643B",
            "activeforeground": "white",
            "relief": "flat",
            "padx": 11,
            "pady": 7,
            "font": ("Segoe UI", 9, "bold"),
            "cursor": "hand2",
        }

    def _carregar_pagina(self) -> None:
        try:
            self.imagem_original = self.leitor.obter_pagina(self.pagina)
            self._renderizar()
            pagina_humana = self.pagina + 1
            self.pagina_var.set(f"Página {pagina_humana} de {self.leitor.total_paginas}")
            self.biblioteca.salvar_progresso(self.obra.id_obra, pagina_humana, self.leitor.total_paginas)
        except (OSError, RuntimeError, ValueError) as erro:
            messagebox.showerror("Erro de leitura", str(erro), parent=self.janela)

    def _renderizar(self) -> None:
        if self.imagem_original is None:
            return
        from PIL import Image, ImageTk

        largura_area = max(self.canvas.winfo_width() - 40, 300)
        altura_area = max(self.canvas.winfo_height() - 40, 300)
        escala_base = min(largura_area / self.imagem_original.width, altura_area / self.imagem_original.height)
        escala = max(0.1, escala_base * self.zoom)
        tamanho = (
            max(1, int(self.imagem_original.width * escala)),
            max(1, int(self.imagem_original.height * escala)),
        )
        imagem = self.imagem_original.resize(tamanho, Image.Resampling.LANCZOS)
        self.foto = ImageTk.PhotoImage(imagem)
        self.canvas.delete("pagina")
        x = max(largura_area // 2 + 20, tamanho[0] // 2 + 20)
        y = max(altura_area // 2 + 20, tamanho[1] // 2 + 20)
        self.canvas.create_image(x, y, image=self.foto, anchor="center", tags="pagina")
        self.canvas.configure(scrollregion=(0, 0, max(largura_area + 40, tamanho[0] + 40), max(altura_area + 40, tamanho[1] + 40)))
        self.zoom_var.set(f"{int(self.zoom * 100)}%")

    def _agendar_redimensionamento(self, _evento: tk.Event[Any]) -> None:
        if self._redimensionamento_id:
            self.janela.after_cancel(self._redimensionamento_id)
        self._redimensionamento_id = self.janela.after(150, self._renderizar)

    def anterior(self) -> None:
        if self.pagina > 0:
            self.pagina -= 1
            self._carregar_pagina()

    def proxima(self) -> None:
        if self.pagina < self.leitor.total_paginas - 1:
            self.pagina += 1
            self._carregar_pagina()

    def aumentar_zoom(self) -> None:
        self.zoom = min(3.0, self.zoom + 0.2)
        self._renderizar()

    def reduzir_zoom(self) -> None:
        self.zoom = max(0.4, self.zoom - 0.2)
        self._renderizar()

    def fechar(self) -> None:
        try:
            self.leitor.fechar()
        finally:
            self.ao_fechar()
            self.janela.destroy()
