"""Navegacao, gerenciamento e formularios de cadernos."""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from .cadernos import PREFERENCIAS


class CadernosLateral(ctk.CTkFrame):
    def __init__(self,master,app):
        super().__init__(master,fg_color='transparent')
        self.app = app
        self.arquivados = False
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(2,weight=1)
        cabecalho = ctk.CTkFrame(self,fg_color='transparent')
        cabecalho.grid(row=0,column=0,sticky='ew')
        ctk.CTkLabel(cabecalho,text='Cadernos',font=('Segoe UI',13,'bold')).pack(side='left')
        ctk.CTkButton(cabecalho,text='+',width=28,height=25,command=app.novo_caderno).pack(side='right')
        self.geral = ctk.CTkButton(self,text='Geral',height=28,anchor='w',command=lambda:app.trocar_caderno(None))
        self.geral.grid(row=1,column=0,sticky='ew',pady=4)
        self.lista = ctk.CTkScrollableFrame(self,width=185,height=125,fg_color='transparent')
        self.lista.grid(row=2,column=0,sticky='nsew')
        self.lista.grid_columnconfigure(0,weight=1)
        self.alternar = ctk.CTkButton(self,text='Cadernos arquivados',height=25,fg_color='transparent',text_color='#126F68',command=self.alternar_arquivados)
        self.alternar.grid(row=3,column=0,sticky='ew',pady=3)

    def alternar_arquivados(self):
        self.arquivados = not self.arquivados
        self.atualizar()

    def atualizar(self):
        for filho in self.lista.winfo_children(): filho.destroy()
        self.geral.configure(fg_color='#126F68' if self.app.caderno_id is None else '#536E69')
        self.alternar.configure(text='Cadernos ativos' if self.arquivados else 'Cadernos arquivados')
        registros = self.app.cadernos.listar(self.arquivados)
        for numero,caderno in enumerate(registros):
            cid = caderno['id']
            linha = ctk.CTkFrame(self.lista,fg_color='transparent')
            linha.grid(row=numero,column=0,sticky='ew',pady=2)
            nome = caderno['nome']
            if len(nome)>23: nome = nome[:22]+'…'
            ctk.CTkButton(linha,text=nome,width=155,height=28,anchor='w',font=('Segoe UI',12),
                fg_color='#126F68' if cid==self.app.caderno_id else '#536E69',
                command=lambda ident=cid:self.app.trocar_caderno(ident)).pack(side='left')
            botao = ctk.CTkButton(linha,text='⋯',width=25,height=28)
            botao.configure(command=lambda ident=cid,b=botao:self.menu(ident,b))
            botao.pack(side='left',padx=(3,0))
        if not registros:
            ctk.CTkLabel(self.lista,text='Nenhum caderno nesta lista.',wraplength=175).grid(row=0,column=0)

    def menu(self,ident,botao):
        caderno = self.app.cadernos.obter(ident)
        menu = tk.Menu(self,tearoff=False)
        for rotulo,acao in [('Editar / renomear','editar'),('Mover para cima','subir'),('Mover para baixo','descer'),
                            ('Restaurar' if caderno['arquivado'] else 'Arquivar','arquivar'),('Excluir caderno','excluir')]:
            menu.add_command(label=rotulo,command=lambda a=acao:self.app.acao_caderno(a,ident))
        try:
            menu.tk_popup(botao.winfo_rootx(),botao.winfo_rooty()+28)
        finally: menu.grab_release()


def editor_caderno(app,ident=None):
    registro = app.cadernos.obter(ident) if ident else {}
    janela = ctk.CTkToplevel(app)
    janela.title('Editar caderno' if ident else 'Criar caderno')
    janela.geometry('600x670'); janela.transient(app)
    formulario = ctk.CTkScrollableFrame(janela)
    formulario.pack(fill='both',expand=True,padx=18,pady=12)
    campos = {}
    for chave,rotulo,multilinha in [('nome','Nome',False),('descricao','Descricao',True),
            ('objetivo','Objetivo de estudo',True),('nivel','Nivel do estudante',False),
            ('assuntos','Assuntos principais',True),('orientacao','Orientacoes pedagogicas',True)]:
        ctk.CTkLabel(formulario,text=rotulo,anchor='w').pack(fill='x',pady=(8,2))
        campo = ctk.CTkTextbox(formulario,height=62,wrap='word') if multilinha else ctk.CTkEntry(formulario)
        campo.pack(fill='x')
        campo.insert('1.0' if multilinha else 0,registro.get(chave,''))
        campos[chave] = (campo,multilinha)
    ctk.CTkLabel(formulario,text='Preferencia de explicacao',anchor='w').pack(fill='x',pady=(8,2))
    preferencia = ctk.CTkOptionMenu(formulario,values=list(PREFERENCIAS.values()))
    preferencia.set(PREFERENCIAS[registro.get('preferencia','completa')])
    preferencia.pack(fill='x')
    aviso = ctk.CTkLabel(janela,text='',text_color='#AD4D36',wraplength=540)
    aviso.pack(fill='x',padx=18)
    def salvar():
        valores = {k:(campo.get('1.0','end').strip() if multi else campo.get().strip()) for k,(campo,multi) in campos.items()}
        valores['preferencia'] = next(k for k,v in PREFERENCIAS.items() if v==preferencia.get())
        try:
            app.salvar_caderno(ident,**valores)
            janela.destroy()
        except ValueError as exc: aviso.configure(text=str(exc))
    ctk.CTkButton(janela,text='Salvar caderno',command=salvar).pack(pady=(5,15))
    return janela


def dialogo_mover(app,conversa):
    registro = app.historico.obter(conversa)
    janela = ctk.CTkToplevel(app)
    janela.title('Mover conversa'); janela.geometry('520x235'); janela.transient(app)
    ctk.CTkLabel(janela,text=registro['titulo'],wraplength=470).pack(pady=15)
    destinos = {'Geral':None,**{c['nome']:c['id'] for c in app.cadernos.listar()}}
    campo = ctk.CTkOptionMenu(janela,values=list(destinos),width=460)
    campo.pack(pady=12)
    def mover():
        try:
            app.mover_chat(conversa,destinos[campo.get()])
            janela.destroy()
        except ValueError as exc: messagebox.showerror('Mover conversa',str(exc),parent=janela)
    ctk.CTkButton(janela,text='Mover',command=mover).pack(pady=12)
    return janela
