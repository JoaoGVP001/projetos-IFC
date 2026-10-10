"""Linha de chat com menu no hover e titulo deslizante."""

import tkinter as tk
import customtkinter as ctk


class ChatItem(ctk.CTkFrame):
    def __init__(self, master, conversa, selecionada, abrir, acao):
        cor = '#126F68' if selecionada else '#E7EEEC'
        super().__init__(master, fg_color=cor, height=36, corner_radius=6)
        self.conversa = conversa
        self.acao = acao
        self._timer = None
        self._hover = False
        self._deslocamento = 0
        self._cor = cor
        self.canvas = tk.Canvas(self, height=36, width=180, highlightthickness=0,
                                bg=cor, cursor='hand2', takefocus=True)
        self.canvas.pack(fill='x', expand=True, padx=3)
        self._titulo = self.canvas.create_text(9,18,anchor='w',text=('★ ' if conversa['fixada'] else '')+conversa['titulo'],
            fill='#FFFFFF' if selecionada else '#202B2A',font=('DejaVu Sans',11))
        self._mascara = self.canvas.create_rectangle(150,0,190,36,fill=cor,outline=cor)
        self._menu = self.canvas.create_text(165,18,text='',fill='#FFFFFF' if selecionada else '#202B2A',font=('DejaVu Sans',17))
        self.canvas.bind('<Configure>',self._configurar)
        self.canvas.bind('<Enter>',self._entrar)
        self.canvas.bind('<Leave>',self._sair)
        self.canvas.bind('<Button-1>',lambda e:self.menu(e) if e.x>=self.canvas.winfo_width()-32 else abrir())
        self.canvas.bind('<Button-3>',self.menu)
        self.canvas.bind('<Return>',lambda _e:abrir())
        self.canvas.bind('<space>',self.menu)
        self.canvas.bind('<FocusIn>',self._entrar)
        self.canvas.bind('<FocusOut>',self._sair)

    def _configurar(self,_evento=None):
        largura=self.canvas.winfo_width()
        self.canvas.coords(self._mascara,largura-32,0,largura,36)
        self.canvas.coords(self._menu,largura-16,18)

    def _entrar(self,_evento=None):
        if self._hover:return
        self._hover=True
        self.canvas.itemconfigure(self._menu,text='⋮')
        self._timer=self.after(650,self._deslizar)

    def _sair(self,_evento=None):
        self._hover=False
        if self._timer:
            self.after_cancel(self._timer)
            self._timer=None
        self._deslocamento=0
        self.canvas.coords(self._titulo,9,18)
        self.canvas.itemconfigure(self._menu,text='')

    def _deslizar(self):
        self._timer=None
        if not self._hover:return
        caixa=self.canvas.bbox(self._titulo)
        excesso=max(0,caixa[2]-caixa[0]-(self.canvas.winfo_width()-45))
        if excesso==0:return
        if self._deslocamento>=excesso:
            self._timer=self.after(1200,self._reiniciar)
        else:
            self._deslocamento=min(excesso,self._deslocamento+2)
            self.canvas.coords(self._titulo,9-self._deslocamento,18)
            self._timer=self.after(35,self._deslizar)

    def _reiniciar(self):
        self._deslocamento=0
        self.canvas.coords(self._titulo,9,18)
        self._timer=self.after(700,self._deslizar)

    def menu(self,evento=None):
        if hasattr(self, "_popup"):
            self._popup.destroy()
        menu=tk.Menu(self,tearoff=False)
        self._popup = menu
        for rotulo,acao in [('Renomear','renomear'),
            ('Desafixar' if self.conversa['fixada'] else 'Fixar no topo','fixar'),
            ('Restaurar' if self.conversa['arquivada'] else 'Arquivar','arquivar'),('Excluir','excluir')]:
            menu.add_command(label=rotulo,command=lambda operacao=acao:self.acao(operacao,self.conversa['id']))
        try:
            menu.tk_popup(self.canvas.winfo_rootx()+self.canvas.winfo_width()-30,self.canvas.winfo_rooty()+36)
        finally:
            menu.grab_release()

    def destroy(self):
        self._sair()
        super().destroy()
