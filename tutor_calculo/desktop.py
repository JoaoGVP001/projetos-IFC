"""Interface de estudo para desktop."""

from queue import Empty, Queue
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import webbrowser
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .chat_item import ChatItem
from .armazenamento import Historico
from .cadernos import Cadernos, contexto_pedagogico
from .cadernos_ui import CadernosLateral, dialogo_mover, editor_caderno
from .materiais import Biblioteca, Extracao, ESTADOS, referencias
from .biblioteca_ui import MateriaisPainel
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
        self.cadernos = Cadernos(self.historico)
        self.biblioteca = Biblioteca(self.historico, recuperar=True)
        self._fila_materiais = Queue()
        self._processador = ThreadPoolExecutor(max_workers=1, thread_name_prefix='materiais')
        self._processando = set()
        navegacao = self.cadernos.navegacao()
        self.caderno_id = navegacao['caderno_id']
        self.conversa_id = navegacao['conversa_id']
        if self.conversa_id:
            conversa = self.historico.obter(self.conversa_id)
            self.caderno_id = conversa['caderno_id']
            self._arquivados = bool(conversa['arquivada'])
        else:
            conversas = self.historico.listar(caderno=self.caderno_id)
            self.conversa_id = conversas[0]['id'] if conversas else None
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
        self.titulo_conversa = ctk.CTkLabel(cabecalho,text="",anchor="w",justify="left",wraplength=700,text_color=MUTED)
        self.titulo_conversa.grid(row=1,column=0,columnspan=2,sticky="ew",pady=(5,0))
        cabecalho.bind('<Configure>',lambda evento:self.titulo_conversa.configure(wraplength=max(200,evento.width-10)))

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

        self.abas = ctk.CTkTabview(self, fg_color="transparent")
        self.abas.grid(row=2, column=1, sticky="nsew", padx=30)
        corpo = self.abas.add("Chat")
        self.abas.add("Materiais")
        corpo.grid_columnconfigure(0, weight=1)
        corpo.grid_rowconfigure(0, weight=1)
        self.entrada = ctk.CTkTextbox(
            corpo, wrap="word", fg_color=SURFACE, text_color=INK,
            border_color=BORDER, border_width=1, corner_radius=6,
            font=("Consolas", 15), padx=17, pady=17, height=110,
        )
        self.entrada.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.saida = ctk.CTkTextbox(
            corpo, wrap="word", fg_color=SURFACE, text_color=INK,
            border_color=BORDER, border_width=1, corner_radius=6,
            font=("Segoe UI", 15), padx=19, pady=17, state="disabled",
        )
        self.saida.grid(row=0, column=0, sticky="nsew")
        self.renderizador = Renderizador(self.saida._textbox)
        anexos = ctk.CTkFrame(corpo, fg_color="transparent")
        anexos.grid(row=1,column=0,sticky="ew",pady=(8,0))
        anexos.grid_columnconfigure(0,weight=1)
        self.rotulo_anexos = ctk.CTkLabel(anexos,text="",anchor="w",justify="left",wraplength=490,text_color=MUTED)
        self.rotulo_anexos.grid(row=0,column=0,sticky="ew")
        ctk.CTkButton(anexos,text="+ Arquivo",width=90,command=self.anexar_arquivos).grid(row=0,column=1,padx=3)
        ctk.CTkButton(anexos,text="+ Link",width=70,command=self.anexar_link).grid(row=0,column=2,padx=3)
        ctk.CTkButton(anexos,text="Gerenciar",width=90,command=self.abrir_materiais).grid(row=0,column=3,padx=3)
        self.painel_materiais = MateriaisPainel(self.abas.tab("Materiais"),self)
        self.painel_materiais.pack(fill="both",expand=True)

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
        self.rotulo_envio = ctk.CTkLabel(rodape,text="",anchor="w",justify="left",wraplength=700,text_color=MUTED,font=("Segoe UI",12))
        self.rotulo_envio.grid(row=2,column=0,sticky="ew",pady=(6,0))
        ctk.CTkButton(rodape,text="Previa do envio",width=130,height=28,command=self.previa_envio).grid(row=2,column=1,pady=(6,0))
        ctk.CTkButton(rodape, text="Configurar IA", width=130, height=28,
                      fg_color="transparent", text_color=ACCENT,
                      hover_color="#E7EEEC", command=self.configurar_ia).grid(row=1, column=1, pady=(8, 0))
        lateral = ctk.CTkFrame(self, width=220, fg_color="#E7EEEC", corner_radius=0)
        lateral.grid(row=0, column=0, rowspan=4, sticky="nsew")
        lateral.grid_rowconfigure(4, weight=1)
        lateral.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(lateral, text="+ Novo chat", command=self.novo_chat, fg_color=ACCENT).grid(row=0, column=0, padx=15, pady=20, sticky="ew")
        ctk.CTkButton(lateral,text="Materiais",command=self.abrir_materiais,fg_color=ACCENT).grid(row=1,column=0,padx=15,pady=(0,12),sticky="ew")
        self.lista_chats = ctk.CTkScrollableFrame(lateral, width=190, fg_color="transparent")
        self.lista_chats.grid(row=4, column=0, sticky="nsew", padx=8)
        self.lateral_cadernos = CadernosLateral(lateral,self)
        self.lateral_cadernos.grid(row=2,column=0,sticky="ew",padx=12,pady=(0,8))
        ctk.CTkLabel(lateral, text="Historico salvo neste PC", text_color=MUTED).grid(row=6, column=0, padx=10, pady=15)
        self.busca = ctk.CTkEntry(lateral, placeholder_text="Buscar titulo ou mensagem")
        self.busca.grid(row=3, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.busca.bind("<KeyRelease>", lambda _evento: self._atualizar_lista())
        self.botao_arquivo = ctk.CTkButton(lateral, text="Ver arquivados", command=self.alternar_arquivados, fg_color=ACCENT)
        self.botao_arquivo.grid(row=5, column=0, padx=15, pady=8, sticky="ew")
        self._atualizar_lista()
        self._abrir_chat(self.conversa_id)
        self._atualizar_status_ia()
        self._timer_fila = self.after(100, self._verificar_fila)

    def _mudar_modo(self, modo: str) -> None:
        self.botao_enviar.configure(text=modo)

    def caderno_atual(self):
        return self.cadernos.obter(self.caderno_id) if self.caderno_id else None

    def _salvar_rascunho(self):
        if self.conversa_id:
            self.historico.rascunho(self.conversa_id,self.entrada.get('1.0','end').rstrip())

    def _salvar_navegacao(self):
        self.cadernos.salvar_navegacao(self.caderno_id,self.conversa_id,self._arquivados)

    def _caderno_editavel(self):
        caderno = self.caderno_atual()
        return not caderno or not caderno['arquivado']

    def _garantir_chat(self):
        if self._ocupado or not self._caderno_editavel():
            self.estado.configure(text='Aguarde a consulta ou restaure o caderno para continuar.',text_color=MUTED)
            return False
        if self.conversa_id and self.historico.obter(self.conversa_id)['arquivada']:
            self.estado.configure(text='Restaure a conversa para adicionar materiais.',text_color=MUTED)
            return False
        if not self.conversa_id: self.novo_chat()
        return bool(self.conversa_id)

    def _atualizar_cabecalho(self):
        caderno = self.caderno_atual()
        nome = caderno['nome'] if caderno else 'Geral'
        titulo = self.historico.obter(self.conversa_id)['titulo'] if self.conversa_id else 'Nenhuma conversa — use Novo chat'
        self.titulo_conversa.configure(text=nome+(' (caderno arquivado)' if caderno and caderno['arquivado'] else '')+'\n'+titulo)
        self.lateral_cadernos.atualizar()

    def trocar_caderno(self,ident):
        if self._ocupado: return
        if ident: self.cadernos.obter(ident)
        self._salvar_rascunho()
        self.caderno_id = ident
        self._arquivados = False
        self.busca.delete(0,'end')
        self.lateral_cadernos.arquivados = bool(ident and self.cadernos.obter(ident)['arquivado'])
        conversas = self.historico.listar(caderno=ident)
        self._abrir_chat(conversas[0]['id'] if conversas else None)

    def novo_caderno(self):
        if not self._ocupado: return editor_caderno(self)

    def salvar_caderno(self,ident,**campos):
        if self._ocupado: raise ValueError('Aguarde a consulta antes de editar o caderno.')
        if ident:
            self.cadernos.editar(ident,**campos)
            self._atualizar_cabecalho()
            self.atualizar_materiais()
        else:
            ident = self.cadernos.criar(**campos)
            self.trocar_caderno(ident)
        return ident

    def acao_caderno(self,acao,ident):
        if self._ocupado: return
        if acao=='editar': return editor_caderno(self,ident)
        if acao in {'subir','descer'}:
            self.cadernos.ordenar(ident,-1 if acao=='subir' else 1)
        elif acao=='arquivar':
            caderno = self.cadernos.obter(ident)
            self._salvar_rascunho()
            self.cadernos.arquivar(ident,not caderno['arquivado'])
            if self.caderno_id==ident:
                self.lateral_cadernos.arquivados = not caderno['arquivado']
                self._abrir_chat(self.conversa_id)
        elif acao=='excluir':
            nome = self.cadernos.obter(ident)['nome']
            if not messagebox.askyesno('Excluir caderno',f'Excluir "{nome}"? As conversas passam para Geral e os materiais permanecem na biblioteca. Apenas a organizacao do caderno sera removida.',parent=self): return
            self._salvar_rascunho()
            self.cadernos.excluir(ident)
            if self.caderno_id==ident:
                self.caderno_id = None
                self.lateral_cadernos.arquivados = False
                self._abrir_chat(self.conversa_id)
        self._atualizar_cabecalho()
        self.atualizar_materiais()

    def mover_chat(self,ident,destino):
        if self._ocupado: raise ValueError('Aguarde a consulta antes de mover a conversa.')
        self._salvar_rascunho()
        self.cadernos.mover_conversa(ident,destino)
        self._abrir_chat(ident)
        self.estado.configure(text='Conversa movida; mensagens e anexos preservados.',text_color=MUTED)

    def _atualizar_status_ia(self) -> None:
        chave, modelo = configuracao()
        self.rotulo_ia.configure(text=f"IA: {provedor_ativo().title()} · {modelo} · chave configurada" if chave else f"IA: {provedor_ativo().title()} · chave nao configurada · exemplo local funciona sem API")
        self.atualizar_materiais()

    def abrir_materiais(self):
        self.abas.set("Materiais")
        self.painel_materiais.atualizar()

    def atualizar_materiais(self):
        anexos = self.biblioteca.anexos(self.conversa_id)
        selecionados = [m for m in anexos if m['selecionado']]
        nomes = ', '.join(m['nome'][:35] for m in anexos[:3])
        if len(anexos)>3: nomes += f" e mais {len(anexos)-3}"
        self.rotulo_anexos.configure(text=f"{len(anexos)} anexos · {len(selecionados)} para IA" + (f"\n{nomes}" if nomes else "\nAdicione materiais de estudo."))
        self.rotulo_envio.configure(text=f"Envio a {provedor_ativo().title()}: preferencias do caderno, mensagem, historico deste chat e trechos de {len(selecionados)} materiais marcados. Originais ficam no PC.")
        self.painel_materiais.atualizar()

    def anexar_arquivos(self):
        caminhos = filedialog.askopenfilenames(parent=self,title="Anexar materiais de estudo",
            filetypes=[("Materiais", "*.pdf *.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff *.txt *.md *.csv *.json *.docx *.log *.tex"),("Todos os arquivos","*")])
        self.importar_arquivos(caminhos)

    def importar_arquivos(self, caminhos):
        if not caminhos or not self._garantir_chat(): return
        erros = []
        for caminho in caminhos:
            try:
                ident, novo = self.biblioteca.adicionar_arquivo(caminho,self.conversa_id)
                if novo: self.agendar_material(ident)
            except (ValueError,OSError) as exc:
                erros.append(str(exc))
        self.atualizar_materiais()
        self.estado.configure(text="; ".join(dict.fromkeys(erros)) if erros else "Anexos adicionados; escolha Consultar na aba Materiais.",text_color=MUTED)

    def anexar_link(self):
        url = ctk.CTkInputDialog(text="Link publico de estudo (HTTP/HTTPS):",title="Adicionar link").get_input()
        if not url: return
        if not self._garantir_chat(): return
        try:
            ident, novo = self.biblioteca.adicionar_link(url,self.conversa_id)
            if novo: self.agendar_material(ident)
            self.atualizar_materiais()
            self.estado.configure(text="Link adicionado. Escolha Consultar apos o processamento.",text_color=MUTED)
        except (ValueError,OSError) as exc:
            messagebox.showerror("Adicionar link",str(exc),parent=self)

    def agendar_material(self, ident):
        if ident in self._processando: return
        self.biblioteca.obter(ident)
        self._processando.add(ident)
        with self.historico.db:
            self.historico.db.execute("UPDATE materiais SET estado='pendente',aviso='Aguardando processamento local.' WHERE id=?",(ident,))
        self.atualizar_materiais()
        self._processador.submit(self._processar_material,self.historico.caminho,ident)

    def _processar_material(self, caminho, ident):
        banco = None
        try:
            self._fila_materiais.put(('inicio',ident))
            # Limite real de tempo, incluindo parsing de arquivos invalidos e bibliotecas nativas.
            subprocess.run([sys.executable,'-m','tutor_calculo.processamento',str(caminho),ident],
                cwd=Path(__file__).resolve().parents[1],capture_output=True,timeout=150,check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=='win32' else 0)
        except Exception:
            try:
                banco = Historico(caminho)
                Biblioteca(banco).salvar_extracao(ident,Extracao([], 'erro', 'Falha ou limite de 150 segundos no processamento. Tente reprocessar.'))
            except Exception: pass
        finally:
            if banco: banco.fechar()
            self._fila_materiais.put(('fim',ident))

    def selecionar_material(self, ident, selecionado):
        if not self._garantir_chat(): return
        self.biblioteca.vincular(ident,self.conversa_id,selecionado)
        self.atualizar_materiais()

    def vincular_material(self, ident):
        if not self._garantir_chat(): return
        self.biblioteca.vincular(ident,self.conversa_id)
        self.atualizar_materiais()

    def desvincular_material(self, ident):
        if not self.conversa_id: return
        self.biblioteca.desvincular(ident,self.conversa_id)
        self.atualizar_materiais()

    def excluir_material(self, ident):
        if ident in self._processando:
            self.estado.configure(text="Aguarde o processamento para excluir o material.",text_color=MUTED)
            return
        nome = self.biblioteca.obter(ident)['nome']
        if not messagebox.askyesno("Excluir material",f'Excluir "{nome}" de toda a biblioteca? O original copiado, o texto, o indice e os vinculos aos chats serao removidos. Citacoes antigas nas mensagens permanecem.',parent=self): return
        try:
            self.biblioteca.excluir(ident)
            self.atualizar_materiais()
        except OSError:
            messagebox.showerror("Excluir material","Nao foi possivel remover o original. Confira as permissoes e tente novamente.",parent=self)

    def ir_origem(self, ident):
        if self._ocupado: return
        self.trocar_chat(ident)
        self.abas.set("Chat")

    def fontes_consulta(self, texto):
        anexos = self.biblioteca.anexos(self.conversa_id)
        if not any(m['selecionado'] for m in anexos): return None
        # Perguntas curtas de continuacao podem aproveitar o assunto da ultima pergunta.
        if len(texto.split())<4:
            anteriores = [m['texto'] for m in self.historico.mensagens(self.conversa_id) if m['papel']=='user']
            if anteriores: texto += ' '+anteriores[-1][:400]
        return self.biblioteca.recuperar(self.conversa_id,texto)

    def previa_envio(self):
        texto = self.entrada.get("1.0","end").strip()
        fontes = self.fontes_consulta(texto)
        janela = ctk.CTkToplevel(self)
        janela.title("Dados da proxima consulta"); janela.geometry("820x610"); janela.transient(self)
        campo = ctk.CTkTextbox(janela,wrap="word")
        campo.pack(fill="both",expand=True,padx=15,pady=15)
        from .ia import limitar_contexto
        historico = limitar_contexto(self.historico.mensagens(self.conversa_id))
        previa = f"Provedor: {provedor_ativo().title()}\nModelo: {configuracao()[1]}\nEnvia tambem instrucoes gerais de estudo e de uso seguro das fontes.\nOs originais binarios nao sao enviados.\n\nCONTEXTO PEDAGOGICO DO CADERNO\n"
        previa += (contexto_pedagogico(self.caderno_atual()) or 'Geral: sem configuracoes adicionais de caderno.')+f"\n\nMENSAGEM\n{texto}\n\nHISTORICO RECENTE\n"
        previa += '\n\n'.join(m['role']+': '+m['content'] for m in historico) or '(vazio)'
        previa += '\n\nTRECHOS RECUPERADOS\n'+(referencias(fontes) if fontes else 'Nenhum trecho relevante. A IA sera informada se ha materiais selecionados sem correspondencia.')
        for f in fontes or []: previa += f"\n\n[{f['referencia']}]\n{f['texto']}"
        campo.insert('1.0',previa); campo.configure(state="disabled")
        return janela

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
        if not self._garantir_chat():
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
        if self.conversa_id: self.historico.rascunho(self.conversa_id, "")
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
        conversas = self.historico.listar(self.busca.get(), self._arquivados,caderno=self.caderno_id)
        for conversa in conversas:
            ident = conversa["id"]
            ChatItem(self.lista_chats, conversa, ident == self.conversa_id,
                     abrir=lambda cid=ident: self.trocar_chat(cid), acao=self.acao_chat).pack(fill="x", pady=3)
        if not conversas:
            ctk.CTkLabel(self.lista_chats,text='Nenhuma conversa encontrada.\nUse Novo chat para comecar.',wraplength=180).pack(pady=15)

    def acao_chat(self, acao, ident):
        if self._ocupado:
            return
        if acao == "fixar":
            self.historico.fixar(ident, not self.historico.obter(ident)["fixada"])
            self._atualizar_lista()
        elif acao == "renomear":
            self.renomear_chat(ident)
        elif acao == "mover":
            return dialogo_mover(self,ident)
        else:
            self.trocar_chat(ident)
            if acao == "arquivar": self.arquivar_chat()
            elif acao == "excluir": self.excluir_chat()

    def _abrir_chat(self, ident):
        self.conversa_id = ident
        self.entrada.configure(state='normal')
        self.entrada.delete("1.0", "end")
        conversa = self.historico.obter(ident) if ident else None
        if conversa:
            self.caderno_id = conversa['caderno_id']
            self._arquivados = bool(conversa['arquivada'])
            self.entrada.insert("1.0", conversa["rascunho"])
        self.lateral_cadernos.arquivados = bool(self.caderno_id and self.caderno_atual()['arquivado'])
        editavel = bool(conversa and not conversa['arquivada'] and self._caderno_editavel())
        self.botao_enviar.configure(state='normal' if editavel else 'disabled')
        self.entrada.configure(state='normal' if editavel else 'disabled')
        self.botao_arquivo.configure(text='Ver ativos' if self._arquivados else 'Ver arquivados')
        self._mostrar_conversa()
        self._atualizar_lista()
        self.abas.set("Chat")
        self.atualizar_materiais()
        self._atualizar_cabecalho()
        self._salvar_navegacao()

    def _mostrar_conversa(self):
        mensagens = self.historico.mensagens(self.conversa_id)
        texto = "\n\n---\n\n".join(
            ("## Voce\n" if m["papel"] == "user" else "## CadernoMat" + (" — erro" if m["estado"] == "erro" else "") + "\n") + m["texto"]
            for m in mensagens)
        self._mostrar_saida(texto or ("## Caderno sem conversa aberta\nUse **Novo chat** para iniciar seus estudos. A biblioteca continua disponivel na aba Materiais." if not self.conversa_id else "## Comece uma conversa\nDigite sua duvida de matematica abaixo. Use Novo chat para estudar outro assunto."))
        self.saida._textbox.yview_moveto(1)

    def trocar_chat(self, ident):
        if self._ocupado:
            return
        self._salvar_rascunho()
        self._abrir_chat(ident)

    def novo_chat(self):
        if self._ocupado:
            return
        if not self._caderno_editavel():
            self.estado.configure(text='Restaure o caderno para iniciar uma conversa.',text_color=MUTED)
            return
        self._salvar_rascunho()
        self._arquivados = False
        self.botao_arquivo.configure(text="Ver arquivados")
        self.busca.delete(0, "end")
        self._abrir_chat(self.historico.criar(self.caderno_id))
        self.estado.configure(text="Novo chat", text_color=MUTED)

    def renomear_chat(self, ident=None):
        if self._ocupado:
            return
        titulo = ctk.CTkInputDialog(text="Titulo da conversa:", title="Renomear chat").get_input()
        if titulo and titulo.strip():
            self.historico.renomear(ident or self.conversa_id, titulo)
            self._atualizar_lista()
            self._atualizar_cabecalho()

    def alternar_arquivados(self):
        if self._ocupado:
            return
        self._arquivados = not self._arquivados
        self.botao_arquivo.configure(text="Ver ativos" if self._arquivados else "Ver arquivados")
        self._atualizar_lista()

    def _selecionar_apos_remocao(self):
        conversas = self.historico.listar(arquivadas=self._arquivados,caderno=self.caderno_id)
        if not conversas:
            self._arquivados = False
            self.botao_arquivo.configure(text="Ver arquivados")
            conversas = self.historico.listar(caderno=self.caderno_id)
        self._abrir_chat(conversas[0]["id"] if conversas else None)

    def arquivar_chat(self):
        if self._ocupado or not self.conversa_id:
            return
        conversa = self.historico.obter(self.conversa_id)
        self.historico.rascunho(self.conversa_id, self.entrada.get("1.0", "end").rstrip())
        self.historico.arquivar(self.conversa_id, not conversa["arquivada"])
        self._selecionar_apos_remocao()
        self.estado.configure(text="Chat restaurado" if conversa["arquivada"] else "Chat arquivado", text_color=MUTED)

    def excluir_chat(self):
        if self._ocupado or not self.conversa_id:
            return
        titulo = self.historico.obter(self.conversa_id)["titulo"]
        if not messagebox.askyesno("Excluir conversa", f'Excluir "{titulo}" e todas as suas mensagens? Esta acao nao pode ser desfeita. Voce pode arquivar para preservar o chat.', parent=self):
            return
        self.historico.excluir(self.conversa_id)
        self._selecionar_apos_remocao()
        self.estado.configure(text="Chat excluido", text_color=MUTED)

    def fechar(self):
        self._salvar_rascunho()
        self._salvar_navegacao()
        self.historico.fechar()
        self.after_cancel(self._timer_fila)
        if self.painel_materiais._timer_busca:
            self.painel_materiais.after_cancel(self.painel_materiais._timer_busca)
        self._processador.shutdown(wait=False,cancel_futures=True)
        # Cancelar no Tcl preserva a limpeza dos comandos por seus widgets proprietarios.
        # Evita callbacks de previews/CustomTkinter depois de destruir esta raiz.
        for timer in self.tk.call('after','info'):
            self.tk.call('after','cancel',timer)
        self.destroy()

    def enviar(self) -> None:
        if not self.conversa_id or not self._caderno_editavel():
            self.estado.configure(text='Use Novo chat ou restaure o caderno para continuar.',text_color=MUTED)
            return
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
        fontes = self.fontes_consulta(texto)
        if modo == "Resolver" and fontes is not None:
            self.estado.configure(text="Para consultar materiais, escolha Resolver com IA, Explicar ou Corrigir.",text_color=MUTED)
            return
        contexto = self.historico.mensagens(self.conversa_id)
        self.historico.adicionar(self.conversa_id, "user", texto)
        if len(self.historico.mensagens(self.conversa_id)) == 1:
            self.historico.renomear(self.conversa_id, texto.splitlines()[0][:80])
        self.historico.rascunho(self.conversa_id, "")
        self.entrada.delete("1.0", "end")
        self._mostrar_conversa()
        self._atualizar_lista()
        self._atualizar_cabecalho()
        self._ocupado = True
        self.botao_enviar.configure(state="disabled")
        self.estado.configure(text="Consultando...", text_color=ACCENT)
        caderno = self.caderno_atual()
        Thread(target=self._executar, args=(modo, texto, contexto, fontes, caderno), daemon=True).start()

    def _executar(self, modo: str, texto: str, historico=None, fontes=None, caderno=None) -> None:
        try:
            if (fontes is not None or caderno is not None) and modo!="Resolver":
                resposta = perguntar(texto,modo="Resolver" if modo=="Resolver com IA" else modo,historico=historico,fontes=fontes,caderno=caderno)
            elif historico and modo != "Resolver":
                resposta = perguntar(texto, modo="Resolver" if modo == "Resolver com IA" else modo, historico=historico)
            elif modo == "Resolver" and caderno is not None:
                resposta = resolver(texto, caderno=caderno, historico=historico)
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
        mudou = False
        while True:
            try:
                evento, ident = self._fila_materiais.get_nowait()
            except Empty:
                break
            if evento == 'fim': self._processando.discard(ident)
            elif evento == 'inicio':
                with self.historico.db:
                    self.historico.db.execute("UPDATE materiais SET estado='processando' WHERE id=? AND estado='pendente'",(ident,))
            mudou = True
        if mudou: self.atualizar_materiais()


def main() -> None:
    ctk.set_appearance_mode("light")
    janela = TutorDesktop()
    janela.mainloop()


if __name__ == "__main__":
    main()
