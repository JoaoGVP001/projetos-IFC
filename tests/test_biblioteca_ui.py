"""Fluxo de janela com banco temporario e provedores simulados."""
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
    TutorDesktop = None


@unittest.skipIf(TutorDesktop is None or (os.name!='nt' and not os.getenv('DISPLAY')), 'Tk/display indisponivel')
class FluxoBibliotecaUITest(unittest.TestCase):
    def esperar(self, app, condicao):
        inicio=time.monotonic()
        while not condicao():
            if time.monotonic()-inicio>10: self.fail('Fluxo da janela nao concluiu em 10 segundos')
            app.update()
            time.sleep(.02)
        app.update()

    def test_anexar_visualizar_buscar_reiniciar_e_consultar(self):
        with tempfile.TemporaryDirectory() as pasta,patch('tutor_calculo.desktop_legado.provedor_ativo',return_value='gemini'),patch('tutor_calculo.desktop_legado.configuracao',return_value=('teste','modelo')):
            banco = Path(pasta)/'dados'/'historico.sqlite3'
            arquivo = Path(pasta)/'notas.md'
            arquivo.write_text('A derivada de x² é 2x. Para x³, temos 3x².',encoding='utf-8')
            app=TutorDesktop(banco); app.withdraw()
            try:
                app.importar_arquivos([arquivo])
                self.esperar(app,lambda:not app._processando)
                ident=app.biblioteca.listar()[0]['id']
                self.assertEqual(app.biblioteca.obter(ident)['estado'],'pronto')
                app.selecionar_material(ident,True)
                self.assertIn('1 para IA',app.rotulo_anexos.cget('text'))
                app.abrir_materiais()
                self.assertEqual(app.abas.get(),'Materiais')
                painel=app.painel_materiais
                painel.busca.insert(0,'derivada'); painel.filtrar()
                self.assertIn('1 materiais',painel.paginacao.cget('text'))
                janela=painel.visualizar(ident)
                self.assertTrue(janela.winfo_exists())
                app.update()
                janela.destroy()
                conversa=app.conversa_id
                app.entrada.insert('1.0','Explique a derivada de x²')
            finally: app.fechar()
            app=TutorDesktop(banco); app.withdraw()
            try:
                self.assertEqual(app.conversa_id,conversa)
                self.assertIn('derivada',app.entrada.get('1.0','end'))
                self.assertEqual(app.biblioteca.anexos(conversa)[0]['selecionado'],1)
                with patch('tutor_calculo.desktop_legado.perguntar',return_value='A derivada e 2x [M1]') as api:
                    app.enviar()
                    self.esperar(app,lambda:not app._ocupado)
                    fontes=api.call_args.kwargs['fontes']
                    self.assertIn('2x',fontes[0]['texto'])
                mensagens=app.historico.mensagens(conversa)
                self.assertEqual(len(mensagens),2)
                self.assertIn('[M1]',mensagens[-1]['texto'])
                # Reutilizar sem misturar selecoes entre chats.
                app.novo_chat(); novo=app.conversa_id
                app.vincular_material(ident)
                self.assertEqual(app.biblioteca.anexos(novo)[0]['selecionado'],0)
                app.desvincular_material(ident)
                self.assertEqual(app.biblioteca.anexos(novo),[])
                self.assertEqual(len(app.biblioteca.listar()),1)
                with patch('tutor_calculo.desktop_legado.messagebox.askyesno',return_value=False):
                    app.excluir_material(ident)
                self.assertEqual(len(app.biblioteca.listar()),1)
                with patch('tutor_calculo.desktop_legado.messagebox.askyesno',return_value=True):
                    app.excluir_material(ident)
                self.assertEqual(app.biblioteca.listar(),[])
                self.assertEqual(app.historico.mensagens(conversa),mensagens)
            finally: app.fechar()

    def test_falha_recuperavel_nao_trava_chat(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo=Path(pasta)/'invalido.pdf'; arquivo.write_bytes(b'nao e PDF')
            app=TutorDesktop(Path(pasta)/'historico.sqlite3'); app.withdraw()
            try:
                app.importar_arquivos([arquivo])
                self.esperar(app,lambda:not app._processando)
                ident=app.biblioteca.listar()[0]['id']
                self.assertEqual(app.biblioteca.obter(ident)['estado'],'erro')
                self.assertFalse(app._ocupado)
                self.assertEqual(app.botao_enviar.cget('state'),'normal')
                app.agendar_material(ident)
                self.esperar(app,lambda:not app._processando)
                self.assertEqual(app.biblioteca.obter(ident)['estado'],'erro')
                app.novo_chat()
            finally: app.fechar()


if __name__=='__main__': unittest.main()
