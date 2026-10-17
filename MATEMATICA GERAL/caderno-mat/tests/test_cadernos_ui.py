"""Fluxos reais da janela com armazenamento temporario e IA simulada."""
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

try:
    import customtkinter as ctk
    from tutor_calculo.desktop_legado import TutorDesktop
except ImportError:
    TutorDesktop=None


def widgets(raiz):
    for filho in raiz.winfo_children():
        yield filho
        yield from widgets(filho)


@unittest.skipIf(TutorDesktop is None or (os.name!='nt' and not os.getenv('DISPLAY')),'Tk/display indisponivel')
class CadernosUITest(unittest.TestCase):
    def esperar(self,app,condicao):
        inicio=time.monotonic()
        while not condicao():
            if time.monotonic()-inicio>10:self.fail('Fluxo nao terminou em 10 segundos')
            app.update(); time.sleep(.02)
        app.update()

    def test_criar_anexar_consultar_mover_e_reabrir(self):
        with tempfile.TemporaryDirectory() as pasta,patch('tutor_calculo.desktop_legado.provedor_ativo',return_value='gemini'),patch('tutor_calculo.desktop_legado.configuracao',return_value=('teste','modelo')):
            banco=Path(pasta)/'historico.sqlite3'; arquivo=Path(pasta)/'notas.txt'
            arquivo.write_text('A derivada de x² e 2x.',encoding='utf-8')
            app=TutorDesktop(banco); app.withdraw()
            try:
                self.assertIsNone(app.conversa_id)
                janela=app.novo_caderno(); app.update()
                entradas=[w for w in widgets(janela) if isinstance(w,ctk.CTkEntry)]
                entradas[0].insert(0,'Meu caderno de calculo')
                entradas[1].insert(0,'Iniciante')
                preferencia=next(w for w in widgets(janela) if isinstance(w,ctk.CTkOptionMenu))
                preferencia.set('Dicas progressivas')
                next(w for w in widgets(janela) if isinstance(w,ctk.CTkButton) and w.cget('text')=='Salvar caderno').invoke()
                origem=app.caderno_id
                self.assertEqual(app.caderno_atual()['preferencia'],'dicas')
                self.assertEqual(app.historico.listar(),[])
                app.novo_chat(); chat=app.conversa_id
                app.importar_arquivos([arquivo]); self.esperar(app,lambda:not app._processando)
                material=app.biblioteca.anexos(chat)[0]['id']
                self.assertEqual(app.biblioteca.cadernos_material(material)[0]['id'],origem)
                self.assertFalse(app.biblioteca.anexos(chat)[0]['selecionado'])
                destino=app.cadernos.listar()[2]['id']
                janela=app.painel_materiais.editar(material); app.update()
                next(w for w in widgets(janela) if isinstance(w,ctk.CTkCheckBox)
                     and w.cget('text')==app.cadernos.obter(destino)['nome']).select()
                next(w for w in widgets(janela) if isinstance(w,ctk.CTkButton) and w.cget('text')=='Salvar').invoke()
                self.assertEqual({x['id'] for x in app.biblioteca.cadernos_material(material)},{origem,destino})
                self.assertEqual(len(app.biblioteca.listar()),1)
                self.assertFalse(app.biblioteca.anexos(chat)[0]['selecionado'])
                app.selecionar_material(material,True)
                app.entrada.insert('1.0','Explique a derivada de x²')
                janela=app.previa_envio()
                previa=next(w for w in widgets(janela) if isinstance(w,ctk.CTkTextbox)).get('1.0','end')
                self.assertIn('Meu caderno de calculo',previa)
                self.assertIn('Dicas progressivas',previa)
                self.assertIn('2x',previa); janela.destroy()
                with patch('tutor_calculo.desktop_legado.perguntar',return_value='Dica: use a potencia [M1]') as api:
                    app.enviar(); self.esperar(app,lambda:not app._ocupado)
                    dados=api.call_args.kwargs
                    self.assertEqual(dados['caderno']['id'],origem)
                    self.assertEqual(dados['historico'],[])
                    self.assertIn('2x',dados['fontes'][0]['texto'])
                mensagens=app.historico.mensagens(chat)
                app.historico.fixar(chat)
                app.entrada.insert('1.0','Tentativa para continuar')
                janela=app.acao_chat('mover',chat); app.update()
                campo=next(w for w in widgets(janela) if isinstance(w,ctk.CTkOptionMenu))
                campo.set(app.cadernos.obter(destino)['nome'])
                next(w for w in widgets(janela) if isinstance(w,ctk.CTkButton)).invoke()
                self.assertEqual(app.conversa_id,chat)
                self.assertEqual(app.caderno_id,destino)
                self.assertEqual(app.historico.obter(chat)['rascunho'],'Tentativa para continuar')
                self.assertEqual(app.historico.mensagens(chat),mensagens)
                self.assertEqual({x['id'] for x in app.biblioteca.cadernos_material(material)},{origem,destino})
                app.abrir_materiais(); app.painel_materiais.filtrar_caderno(destino)
                app.painel_materiais.busca.insert(0,'derivada'); app.painel_materiais.filtrar()
                self.assertIn('1 materiais',app.painel_materiais.paginacao.cget('text'))
            finally:app.fechar()
            app=TutorDesktop(banco); app.withdraw()
            try:
                self.assertEqual(app.conversa_id,chat); self.assertEqual(app.caderno_id,destino)
                self.assertIn('Tentativa para continuar',app.entrada.get('1.0','end'))
                self.assertEqual(app.historico.mensagens(chat),mensagens)
                self.assertTrue(app.historico.obter(chat)['fixada'])
                self.assertTrue(app.biblioteca.anexos(chat)[0]['selecionado'])
                self.assertTrue(app.biblioteca.caminho_original(material).is_file())
                # Outro chat da mesma materia nao herda historico nem autorizacao documental.
                app.novo_chat(); app.vincular_material(material)
                app.entrada.insert('1.0','Outra questao')
                with patch('tutor_calculo.desktop_legado.perguntar',return_value='Resposta isolada') as api:
                    app.enviar(); self.esperar(app,lambda:not app._ocupado)
                    self.assertEqual(api.call_args.kwargs['historico'],[])
                    self.assertIsNone(api.call_args.kwargs['fontes'])
                    self.assertNotIn('Dica: use',str(api.call_args))
            finally:app.fechar()

    def test_estados_vazios_arquivo_restauracao_exclusao_e_rascunho(self):
        with tempfile.TemporaryDirectory() as pasta:
            banco=Path(pasta)/'historico.sqlite3'; app=TutorDesktop(banco); app.withdraw()
            try:
                ids=[c['id'] for c in app.cadernos.listar()]
                for ident in ids+[None]+ids:
                    app.trocar_caderno(ident)
                    self.assertIsNone(app.conversa_id)
                self.assertEqual(app.historico.listar(),[])
                app.novo_chat(); chat=app.conversa_id
                app.entrada.insert('1.0','Rascunho salvo na troca')
                app.trocar_caderno(ids[0]); app.trocar_caderno(ids[-1])
                self.assertEqual(app.conversa_id,chat)
                self.assertIn('Rascunho salvo',app.entrada.get('1.0','end'))
                app.acao_caderno('arquivar',ids[-1])
                self.assertFalse(app.historico.obter(chat)['arquivada'])
                self.assertEqual(app.entrada.cget('state'),'disabled')
                app.novo_chat(); self.assertEqual(app.conversa_id,chat)
                app.acao_caderno('arquivar',ids[-1])
                self.assertEqual(app.entrada.cget('state'),'normal')
                with patch('tutor_calculo.desktop_legado.messagebox.askyesno',return_value=True):app.acao_caderno('excluir',ids[-1])
                self.assertIsNone(app.caderno_id); self.assertEqual(app.conversa_id,chat)
                self.assertIn('Geral',app.titulo_conversa.cget('text'))
                self.assertIn('Rascunho salvo',app.entrada.get('1.0','end'))
                app.trocar_caderno(ids[0])
            finally:app.fechar()
            app=TutorDesktop(banco); app.withdraw()
            try:
                self.assertEqual(app.caderno_id,ids[0]); self.assertIsNone(app.conversa_id)
                self.assertEqual(len(app.historico.listar()),1)
            finally:app.fechar()

    def test_tamanho_minimo_cabecalho_e_controles_visiveis(self):
        with tempfile.TemporaryDirectory() as pasta:
            app=TutorDesktop(Path(pasta)/'historico.sqlite3')
            try:
                app.geometry('1000x650'); app.update()
                ident=app.salvar_caderno(None,nome='Um caderno com nome longo para verificar legibilidade no tamanho minimo da janela')
                app.novo_chat()
                app.historico.renomear(app.conversa_id,'Uma conversa com titulo longo '*3)
                app._atualizar_cabecalho(); app.update()
                self.assertEqual(app.winfo_width(),1000)
                self.assertEqual(app.winfo_height(),650)
                app.abrir_materiais(); app.update()
                app.painel_materiais.filtrar_caderno(ident); app.update()
                for controle in [app.lateral_cadernos,app.lista_chats,app.titulo_conversa,
                                 app.botao_enviar,app.painel_materiais.tipo,app.painel_materiais.so_chat,
                                 app.painel_materiais.caderno,app.painel_materiais.paginacao]:
                    x=controle.winfo_rootx()-app.winfo_rootx()
                    y=controle.winfo_rooty()-app.winfo_rooty()
                    self.assertGreaterEqual(x,0); self.assertGreaterEqual(y,0)
                    self.assertLessEqual(x+controle.winfo_width(),app.winfo_width())
                    self.assertLessEqual(y+controle.winfo_height(),app.winfo_height())
                self.assertGreaterEqual(app.lista_chats._parent_canvas.winfo_height(),60)
            finally:app.fechar()


if __name__=='__main__':unittest.main()
