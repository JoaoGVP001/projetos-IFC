"""Interface da biblioteca. Importacao e OCR sao coordenados pelo aplicativo."""

import os
from pathlib import Path
import subprocess
import sys
import webbrowser
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from .extracao import imagem_pdf
from .materiais import ESTADOS
from .armazenamento import TODOS_CADERNOS

TIPOS = {'Todos os tipos': '', 'PDF': 'pdf', 'Imagens': 'imagem', 'Texto': 'texto',
         'DOCX': 'docx', 'PPTX': 'pptx', 'Links': 'link', 'Outros': 'arquivo'}
DATAS = {'Qualquer data': 0, 'Ultimos 7 dias': 7, 'Ultimos 30 dias': 30, 'Ultimos 90 dias': 90}


def tamanho_legivel(tamanho):
    return f'{tamanho / 1024 / 1024:.1f} MiB' if tamanho >= 1024*1024 else f'{tamanho / 1024:.1f} KiB'


def abrir_original(biblioteca, ident):
    m = biblioteca.obter(ident)
    if m['url']:
        webbrowser.open(m['url'])
        return
    caminho = biblioteca.caminho_original(ident)
    if not caminho or not caminho.is_file(): raise ValueError('Original nao encontrado.')
    if caminho.suffix.lower() in {'.exe','.com','.bat','.cmd','.sh','.ps1','.desktop','.app','.msi','.jar','.vbs','.py','.js'}:
        raise ValueError('Arquivo executavel: abra manualmente em um editor. A biblioteca nao executa anexos.')
    if sys.platform == 'win32': os.startfile(caminho)
    elif sys.platform == 'darwin': subprocess.Popen(['open', str(caminho)])
    else: subprocess.Popen(['xdg-open', str(caminho)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class MateriaisPainel(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color='transparent')
        self.app = app
        self._pagina = 0
        self._timer_busca = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        barra = ctk.CTkFrame(self, fg_color='transparent')
        barra.grid(row=0, column=0, sticky='ew', pady=8)
        ctk.CTkButton(barra, text='+ Arquivos', width=110, command=app.anexar_arquivos).pack(side='left', padx=(0,8))
        ctk.CTkButton(barra, text='+ Link', width=100, command=app.anexar_link).pack(side='left')
        self.busca = ctk.CTkEntry(self, placeholder_text='Buscar nome, texto extraido, assunto ou etiquetas')
        self.busca.grid(row=1, column=0, sticky='ew', pady=(0,8))
        self.busca.bind('<KeyRelease>', lambda _e: self._buscar_depois())
        filtros = ctk.CTkFrame(self, fg_color='transparent')
        filtros.grid(row=2, column=0, sticky='ew')
        self.tipo = ctk.CTkOptionMenu(filtros, values=list(TIPOS), width=135, command=lambda _v: self.filtrar())
        self.tipo.grid(row=0,column=0,padx=(0,8))
        self.materia = ctk.CTkOptionMenu(filtros, values=['Todas as materias'], width=170, command=lambda _v: self.filtrar())
        self.materia.grid(row=0,column=1,padx=(0,8))
        self.data = ctk.CTkOptionMenu(filtros, values=list(DATAS), width=145, command=lambda _v: self.filtrar())
        self.data.grid(row=0,column=2,padx=(0,8))
        self.so_chat = ctk.CTkCheckBox(filtros, text='Deste chat', command=self.filtrar, width=100)
        self.so_chat.grid(row=0,column=3)
        self.caderno = ctk.CTkOptionMenu(filtros,values=['Todos os cadernos','Geral (sem caderno)'],width=310,dynamic_resizing=False,command=lambda _v:self.filtrar())
        self.caderno.grid(row=1,column=0,columnspan=2,sticky='ew',pady=(8,0))
        ctk.CTkButton(filtros,text='Do caderno atual',width=145,command=lambda:self.filtrar_caderno(self.app.caderno_id)).grid(row=1,column=2,pady=(8,0))
        self._opcoes_caderno = {'Todos os cadernos':TODOS_CADERNOS,'Geral (sem caderno)':None}
        self.resumo = ctk.CTkLabel(self, text='', anchor='w', wraplength=750, justify='left', text_color='#667674')
        self.resumo.grid(row=3, column=0, sticky='ew', pady=8)
        self.lista = ctk.CTkScrollableFrame(self, fg_color='transparent')
        self.lista.grid(row=4, column=0, sticky='nsew')
        self.lista.grid_columnconfigure(0, weight=1)
        navegacao = ctk.CTkFrame(self, fg_color='transparent')
        navegacao.grid(row=5, column=0, sticky='ew')
        ctk.CTkButton(navegacao, text='Anterior', width=95, command=lambda: self.mudar_pagina(-1)).pack(side='left', padx=4)
        ctk.CTkButton(navegacao, text='Proxima', width=95, command=lambda: self.mudar_pagina(1)).pack(side='left', padx=4)
        self.paginacao = ctk.CTkLabel(navegacao, text='')
        self.paginacao.pack(side='left', padx=10)

    def _buscar_depois(self):
        if self._timer_busca: self.after_cancel(self._timer_busca)
        self._timer_busca = self.after(250, self.filtrar)

    def filtrar(self):
        self._timer_busca = None
        self._pagina = 0
        self.atualizar()

    def mudar_pagina(self, passo):
        self._pagina = max(0, self._pagina+passo)
        self.atualizar()

    def filtrar_caderno(self, ident):
        self.atualizar()
        self.caderno.set(next(nome for nome,cid in self._opcoes_caderno.items() if cid==ident))
        self.filtrar()

    def atualizar(self):
        for filho in self.lista.winfo_children(): filho.destroy()
        biblioteca = self.app.biblioteca
        self._opcoes_caderno = {'Todos os cadernos':TODOS_CADERNOS,'Geral (sem caderno)':None,
            **{'Caderno: '+c['nome']:c['id'] for c in self.app.cadernos.listar(None)}}
        self.caderno.configure(values=list(self._opcoes_caderno))
        if self.caderno.get() not in self._opcoes_caderno: self.caderno.set('Todos os cadernos')
        materias = ['Todas as materias']+biblioteca.materias()
        self.materia.configure(values=materias)
        if self.materia.get() not in materias: self.materia.set(materias[0])
        registros = [] if self.so_chat.get() and not self.app.conversa_id else biblioteca.listar(self.busca.get(), TIPOS[self.tipo.get()],
                    '' if self.materia.get() == materias[0] else self.materia.get(),
                    DATAS[self.data.get()], self.app.conversa_id if self.so_chat.get() else None,
                    caderno=self._opcoes_caderno[self.caderno.get()])
        anexos = {m['id']: m for m in biblioteca.anexos(self.app.conversa_id)}
        self._pagina = min(self._pagina, max(0,(len(registros)-1)//40))
        self.paginacao.configure(text=f'Pagina {self._pagina+1} · {len(registros)} materiais')
        titulo = self.app.historico.obter(self.app.conversa_id)['titulo'] if self.app.conversa_id else 'Nenhuma conversa aberta'
        self.resumo.configure(text=f'Conversa: {titulo}\nMarque Consultar para enviar trechos relevantes a IA. Anexar nao envia arquivos ao provedor.')
        for numero, m in enumerate(registros[self._pagina*40:(self._pagina+1)*40]):
            ident = m['id']
            linha = ctk.CTkFrame(self.lista, fg_color='#FFFFFF', border_width=1, border_color='#DCE5E2')
            linha.grid(row=numero, column=0, sticky='ew', pady=5)
            linha.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(linha, text=m['nome'], anchor='w', wraplength=660, justify='left',
                         font=('Segoe UI',15,'bold')).grid(row=0,column=0,sticky='ew',padx=12,pady=(8,0))
            info = f"{m['tipo'].upper()} · {tamanho_legivel(m['tamanho'])} · {ESTADOS.get(m['estado'],m['estado'])} · {m['criado'][:10]}"
            ctk.CTkLabel(linha,text=info,anchor='w',text_color='#667674').grid(row=1,column=0,sticky='ew',padx=12)
            origem = m['origem_titulo'] + (' (chat excluido)' if not m['origem_id'] else '')
            metadados = f"Origem: {origem} · Materia: {m['materia'] or 'Geral'}"
            associados = biblioteca.cadernos_material(ident)
            metadados += '\nCadernos: '+(', '.join(c['nome']+(' (arquivado)' if c['arquivado'] else '') for c in associados) or 'Geral')
            if m['assunto'] or m['etiquetas']: metadados += f"\n{m['assunto']} · {m['etiquetas']}"
            if m['aviso']: metadados += '\n'+m['aviso']
            ctk.CTkLabel(linha,text=metadados,anchor='w',justify='left',wraplength=660,
                         text_color='#667674').grid(row=2,column=0,sticky='ew',padx=12)
            acoes = ctk.CTkFrame(linha,fg_color='transparent')
            acoes.grid(row=3,column=0,sticky='ew',padx=12,pady=8)
            checkbox = ctk.CTkCheckBox(acoes,text='Consultar neste chat',width=155)
            if anexos.get(ident,{}).get('selecionado'): checkbox.select()
            pode_selecionar = self.app.conversa_id and self.app._caderno_editavel() and not self.app.historico.obter(self.app.conversa_id)['arquivada']
            if m['estado'] not in {'pronto','parcial'} or not pode_selecionar: checkbox.configure(state='disabled')
            checkbox.configure(command=lambda i=ident,c=checkbox: self.app.selecionar_material(i,bool(c.get())))
            checkbox.pack(side='left',padx=(0,8))
            for texto, comando in [
                ('Visualizar',lambda i=ident:self.visualizar(i)),
                ('Editar',lambda i=ident:self.editar(i)),
                ('Mais...',lambda i=ident:self.mais(i)),
            ]:
                ctk.CTkButton(acoes,text=texto,width=85,command=comando).pack(side='left',padx=3)
        if not registros:
            ctk.CTkLabel(self.lista,text='Nenhum material encontrado. Adicione um arquivo ou link.').grid(row=0,column=0,pady=25)

    def editar(self, ident):
        m = self.app.biblioteca.obter(ident)
        janela = ctk.CTkToplevel(self)
        janela.title('Editar material')
        janela.geometry('560x610')
        janela.transient(self.app)
        formulario = ctk.CTkScrollableFrame(janela)
        formulario.pack(fill='both',expand=True,padx=15,pady=10)
        campos = {}
        for chave, rotulo in [('nome','Nome'),('materia','Materia (metadado livre)'),('assunto','Assunto'),('etiquetas','Etiquetas (separadas por virgula)')]:
            ctk.CTkLabel(formulario,text=rotulo).pack(anchor='w',padx=10,pady=(10,0))
            campo = ctk.CTkEntry(formulario,width=470)
            campo.insert(0,m[chave]); campo.pack(padx=20,pady=3)
            campos[chave] = campo
        ctk.CTkLabel(formulario,text='Cadernos associados (nao autoriza envio a IA)').pack(anchor='w',padx=10,pady=12)
        associados = {c['id'] for c in self.app.biblioteca.cadernos_material(ident)}
        escolhas = {}
        for caderno in self.app.cadernos.listar(None):
            cid = caderno['id']
            escolha = ctk.CTkCheckBox(formulario,text=caderno['nome']+(' (arquivado)' if caderno['arquivado'] else ''))
            if cid in associados: escolha.select()
            escolha.pack(anchor='w',padx=10,pady=5)
            escolhas[cid] = escolha
        def salvar():
            try:
                self.app.biblioteca.metadados(ident,**{k:v.get() for k,v in campos.items()},
                    cadernos=[cid for cid,campo in escolhas.items() if campo.get()])
                self.app.atualizar_materiais()
                janela.destroy()
            except (ValueError,OSError) as exc:
                messagebox.showerror('Material',str(exc),parent=janela)
        ctk.CTkButton(janela,text='Salvar',command=salvar).pack(pady=15)
        return janela

    def mais(self, ident):
        m = self.app.biblioteca.obter(ident)
        janela = ctk.CTkToplevel(self)
        janela.title('Acoes do material'); janela.geometry('440x350'); janela.transient(self.app)
        def executar(acao):
            janela.destroy()
            acao()
        acoes = [('Abrir original / link',lambda:self.abrir(ident)),
                 ('Adicionar ao chat atual',lambda:self.app.vincular_material(ident)),
                 ('Remover deste chat',lambda:self.app.desvincular_material(ident)),
                 ('Reprocessar',lambda:self.app.agendar_material(ident)),
                 ('Excluir da biblioteca',lambda:self.app.excluir_material(ident))]
        if m['origem_id']:
            acoes.insert(1,('Ir a conversa de origem',lambda:self.app.ir_origem(m['origem_id'])))
        for nome, acao in acoes:
            ctk.CTkButton(janela,text=nome,command=lambda a=acao:executar(a),width=380).pack(pady=9,padx=20)

    def abrir(self, ident):
        try: abrir_original(self.app.biblioteca,ident)
        except (ValueError,OSError) as exc: messagebox.showerror('Abrir material',str(exc),parent=self.app)

    def visualizar(self, ident):
        m = self.app.biblioteca.obter(ident)
        janela = ctk.CTkToplevel(self)
        janela.title('Material — '+m['nome']); janela.geometry('900x680'); janela.transient(self.app)
        abas = ctk.CTkTabview(janela)
        abas.pack(fill='both',expand=True,padx=15,pady=10)
        texto = abas.add('Texto extraido')
        campo = ctk.CTkTextbox(texto,wrap='word')
        campo.pack(fill='both',expand=True)
        paginas = self.app.biblioteca.paginas(ident)
        cabecalho = f"{m['nome']}\n{ESTADOS[m['estado']]} · {m['metodo']}\n{m['aviso']}\n\n"
        extraido = '\n\n'.join(f"--- Slide {p['numero']} ---\n{p['texto']}" if m['tipo']=='pptx' else f"--- Pagina {p['numero']} ---\n{p['texto']}" if m['tipo']=='pdf' or 'PDF' in m['metodo'] else p['texto'] for p in paginas)
        campo.insert('1.0',cabecalho+(extraido or 'Sem texto disponivel. A IA nao recebera conteudo inventado.'))
        campo.configure(state='disabled')
        if m['tipo'] in {'imagem','pdf'}:
            original = abas.add('Previa original')
            folha = ctk.CTkLabel(original,text='')
            folha.pack(fill='both',expand=True)
            numero = ctk.CTkEntry(original,placeholder_text='Pagina do PDF',width=120)
            numero.insert(0,'1')
            def mostrar():
                try:
                    caminho = self.app.biblioteca.caminho_original(ident)
                    if m['tipo']=='pdf': img = imagem_pdf(caminho,int(numero.get()))
                    else:
                        with Image.open(caminho) as fonte:
                            if fonte.width*fonte.height > 40_000_000: raise ValueError('Imagem muito grande para a previa.')
                            img = fonte.copy()
                    img.thumbnail((760,475))
                    folha.configure(text='',image=ctk.CTkImage(img,size=img.size))
                except Exception:
                    folha.configure(text='Previa indisponivel. Confira o arquivo ou numero de pagina.',image=None)
            if m['tipo']=='pdf':
                numero.pack(side='left',padx=10)
                ctk.CTkButton(original,text='Mostrar pagina',command=mostrar).pack(side='left')
            mostrar()
        ctk.CTkButton(janela,text='Abrir original / link',command=lambda:self.abrir(ident)).pack(pady=(0,10))
        return janela
