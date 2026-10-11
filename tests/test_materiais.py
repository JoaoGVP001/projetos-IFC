import io
import json
import os
from pathlib import Path
import socket
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock, patch
import zipfile

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from tutor_calculo.armazenamento import Historico
from tutor_calculo.extracao import Extracao, MAX_ARQUIVO, extrair, idiomas_ocr
from tutor_calculo.ia import perguntar
from tutor_calculo.links import baixar_link, endereco_publico, extrair_link, normalizar_url
from tutor_calculo.materiais import Biblioteca, contexto_documental


def pdf_texto(caminho):
    pdf = PdfWriter()
    pagina = pdf.add_blank_page(width=300,height=300)
    fonte = DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    pagina[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):pdf._add_object(fonte)})})
    conteudo = DecodedStreamObject()
    conteudo.set_data(b'BT /F1 16 Tf 20 250 Td (Derivative of x squared is 2x.) Tj ET')
    pagina[NameObject('/Contents')] = pdf._add_object(conteudo)
    pdf.write(caminho)


class BibliotecaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pasta = Path(self.tmp.name)
        self.banco = Historico(self.pasta/'dados'/'historico.sqlite3')
        self.addCleanup(self.banco.fechar)
        self.lib = Biblioteca(self.banco)
        self.a,self.b = self.banco.criar(),self.banco.criar()

    def importar(self, nome='resumo.txt', texto='A derivada de x² é 2x. Limites e continuidade.'):
        caminho = self.pasta/nome
        caminho.write_text(texto,encoding='utf-8')
        ident,_ = self.lib.adicionar_arquivo(caminho,self.a)
        self.lib.processar(ident)
        return ident

    def test_fluxo_completo_persistencia_busca_selecao_e_deduplicacao(self):
        ident = self.importar()
        self.lib.metadados(ident,'Resumo de Cálculo','Cálculo I','Derivadas','revisao, prova')
        self.lib.vincular(ident,self.a,True)
        original = self.lib.caminho_original(ident)
        self.assertTrue(original.is_file())
        self.assertNotEqual(original.parent,self.pasta)
        repetido,novo = self.lib.adicionar_arquivo(self.pasta/'resumo.txt',self.b)
        self.assertEqual(repetido,ident); self.assertFalse(novo)
        self.assertEqual(len(list(self.lib.raiz.iterdir())),1)
        self.assertEqual(len(self.lib.listar()),1)
        for termo in ['calculo','DERIVADA','continuidade','revisao','prova']:
            self.assertEqual(self.lib.listar(termo)[0]['id'],ident)
        self.assertEqual(self.lib.listar("' OR 1=1 --"),[])
        self.assertEqual(len(self.lib.listar(tipo='texto',materia='Cálculo I',dias=7)),1)
        self.assertEqual(self.lib.listar(tipo='pdf'),[])
        self.assertEqual(self.lib.recuperar(self.b,'derivada'),[])
        fontes = self.lib.recuperar(self.a,'Qual é a derivada?')
        self.assertIn('2x',fontes[0]['texto'])
        self.assertEqual(json.loads(contexto_documental(fontes))[0]['nome'],'Resumo de Cálculo')
        # Outra conexao simula reinicio sem reconstruir nem reenviar documentos.
        outro = Historico(self.banco.caminho)
        try:
            lib = Biblioteca(outro,recuperar=True)
            self.assertEqual(lib.anexos(self.a)[0]['selecionado'],1)
            self.assertEqual(lib.paginas(ident)[0]['texto'],self.lib.paginas(ident)[0]['texto'])
            self.assertTrue(lib.recuperar(self.a,'derivada'))
            self.assertEqual(lib.obter(ident)['estado'],'pronto')
        finally: outro.fechar()
        # Renomear sem extensao nao muda o extrator.
        self.lib.processar(ident)
        self.assertEqual(self.lib.obter(ident)['estado'],'pronto')

    def test_remover_atualiza_indice_e_preserva_outros_chats_e_materiais(self):
        a = self.importar('a.txt','Conceito de derivada, 2x.')
        b = self.importar('b.txt','Conceito de conjuntos, uniao.')
        self.lib.vincular(a,self.b,True)
        self.lib.vincular(b,self.a,True)
        caminho = self.lib.caminho_original(a)
        self.lib.excluir(a)
        self.assertFalse(caminho.exists())
        self.assertEqual(self.lib.listar('derivada'),[])
        self.assertEqual(self.lib.recuperar(self.b,'derivada'),[])
        self.assertEqual(self.lib.anexos(self.b),[])
        self.assertTrue(self.lib.recuperar(self.a,'conjuntos'))
        self.lib.db.execute("INSERT INTO trechos_fts(trechos_fts,rank) VALUES ('integrity-check',1)")
        self.lib.db.commit()

    def test_excluir_chat_preserva_biblioteca_e_origem(self):
        ident = self.importar()
        self.banco.renomear(self.a,'Derivadas')
        self.lib.vincular(ident,self.b,True)
        self.banco.excluir(self.a)
        self.assertIsNone(self.lib.obter(ident)['origem_id'])
        self.assertEqual(self.lib.obter(ident)['origem_titulo'],'Derivadas')
        self.assertTrue(self.lib.caminho_original(ident).exists())
        self.assertTrue(self.lib.recuperar(self.b,'derivada'))

    def test_reprocessamento_com_falha_remove_indice_antigo(self):
        ident = self.importar()
        self.lib.vincular(ident,self.a,True)
        self.lib.salvar_extracao(ident,Extracao([],'erro','Falha de extracao.'))
        self.assertEqual(self.lib.paginas(ident),[])
        self.assertEqual(self.lib.recuperar(self.a,'derivada'),[])
        self.assertEqual(self.lib.listar('continuidade'),[])

    def test_limites_e_arquivos_invalidos(self):
        grande = self.pasta/'grande.txt'
        with grande.open('wb') as arquivo: arquivo.truncate(MAX_ARQUIVO+1)
        with self.assertRaisesRegex(ValueError,'20 MiB'):
            self.lib.adicionar_arquivo(grande,self.a)
        with self.assertRaises(ValueError): self.lib.adicionar_arquivo(self.pasta,self.a)
        pdf = self.pasta/'quebrado.pdf'; pdf.write_bytes(b'%PDF-invalido')
        self.assertEqual(extrair(pdf,pdf.name).estado,'erro')
        txt = self.pasta/'binario.txt'; txt.write_bytes(b'\x00\x01')
        self.assertEqual(extrair(txt,txt.name).estado,'erro')
        outro = self.pasta/'arquivo.zip'; outro.write_bytes(b'zip')
        self.assertEqual(extrair(outro,outro.name).estado,'nao_suportado')
        self.assertEqual(list(self.lib.raiz.iterdir()),[])

    def test_pdf_textual_pagina_e_docx(self):
        caminho = self.pasta/'atividade.pdf'; pdf_texto(caminho)
        ident,_ = self.lib.adicionar_arquivo(caminho,self.a)
        self.lib.processar(ident); self.lib.vincular(ident,self.a,True)
        fontes = self.lib.recuperar(self.a,'derivative')
        self.assertEqual(fontes[0]['pagina'],1)
        self.assertIn('2x',fontes[0]['texto'])
        self.assertEqual(json.loads(contexto_documental(fontes))[0]['pagina'],1)
        docx = self.pasta/'nota.docx'
        with zipfile.ZipFile(docx,'w') as doc:
            doc.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Uniao de conjuntos</w:t></w:r></w:p></w:body></w:document>')
        self.assertIn('conjuntos',extrair(docx,docx.name).paginas[0][1])

    def test_sem_ocr_nao_inventa_conteudo(self):
        img = self.pasta/'imagem.png'; Image.new('RGB',(200,100),'white').save(img)
        with patch('tutor_calculo.extracao.idiomas_ocr',return_value=[]):
            resultado = extrair(img,img.name)
        self.assertEqual(resultado.paginas,[])
        self.assertEqual(resultado.estado,'sem_texto')
        self.assertIn('indisponivel',resultado.aviso)

    @unittest.skipUnless(idiomas_ocr(),'OCR opcional nao instalado')
    def test_ocr_real_imagem_e_pdf_digitalizado(self):
        imagem = Image.new('RGB',(900,150),'white')
        try: fonte = ImageFont.truetype('DejaVuSans.ttf',46)
        except OSError: self.skipTest('Fonte de teste nao disponivel')
        ImageDraw.Draw(imagem).text((25,40),'DERIVATIVE 2x + 3',fill='black',font=fonte)
        img = self.pasta/'scan.png'; imagem.save(img)
        pdf = self.pasta/'scan.pdf'; imagem.save(pdf,'PDF')
        for caminho in [img,pdf]:
            resultado = extrair(caminho,caminho.name)
            self.assertTrue(resultado.paginas,resultado.aviso)
            self.assertIn('DERIVATIVE',resultado.paginas[0][1].upper())
            self.assertIn('OCR',resultado.metodo)

    def test_links_html_falhas_copia_persistente_e_duplicatas(self):
        ident,novo = self.lib.adicionar_link('https://example.com/nota#capitulo',self.a)
        self.assertTrue(novo)
        self.assertEqual(self.lib.adicionar_link('https://EXAMPLE.com/nota',self.b),(ident,False))
        with patch('tutor_calculo.links.baixar_link',return_value=(b'<h1>Derivada</h1><p>2x</p><script>segredo</script>','text/html','https://example.com/nota')):
            self.lib.processar(ident)
        self.assertIn('2x',self.lib.paginas(ident)[0]['texto'])
        self.assertNotIn('segredo',self.lib.paginas(ident)[0]['texto'])
        self.assertTrue(self.lib.listar('2x'))
        with patch('tutor_calculo.links.baixar_link',side_effect=ValueError('Link indisponivel (HTTP 404).')):
            self.lib.processar(ident)
        self.assertEqual(self.lib.obter(ident)['estado'],'erro')
        self.assertEqual(self.lib.paginas(ident),[])

    def test_interrompido_recuperavel_reinicio(self):
        caminho = self.pasta/'novo.txt'; caminho.write_text('inducao')
        ident,_ = self.lib.adicionar_arquivo(caminho,self.a)
        Biblioteca(self.banco,recuperar=True)
        self.assertEqual(self.lib.obter(ident)['estado'],'erro')
        self.lib.processar(ident)
        self.assertEqual(self.lib.obter(ident)['estado'],'pronto')

    def test_resumo_generico_identifica_amostra_e_limite_de_contexto(self):
        ident = self.importar(texto='Calculo diferencial. '+('derivada abc ' * 1000))
        self.lib.vincular(ident,self.a,True)
        fontes = self.lib.recuperar(self.a,'Resuma esse documento')
        self.assertTrue(fontes)
        self.assertIn('amostra inicial',fontes[0]['selecao'])
        self.assertLessEqual(sum(len(f['texto']) for f in self.lib.recuperar(self.a,'derivada')),6000)
        self.assertEqual(self.lib.recuperar(self.a,'Astronomia planetaria'),[])

    def test_migracao_falha_reverte_ddl_e_preserva_chats(self):
        caminho = self.pasta/'falha.sqlite3'
        db = sqlite3.connect(caminho)
        db.executescript('''CREATE TABLE conversas(id TEXT PRIMARY KEY,titulo TEXT,rascunho TEXT,atualizado TEXT,arquivada INTEGER,fixada INTEGER);
        INSERT INTO conversas VALUES ('a','Preservado','rascunho','2026-10-10',0,1);
        PRAGMA user_version=3;''')
        db.close()
        def falhar(db):
            db.execute('CREATE TABLE incompleta(id INTEGER)')
            raise RuntimeError('Falha simulada')
        with patch('tutor_calculo.materiais.migrar_materiais',side_effect=falhar):
            with self.assertRaises(RuntimeError): Historico(caminho)
        db = sqlite3.connect(caminho)
        try:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],3)
            self.assertEqual(db.execute('SELECT titulo FROM conversas').fetchone()[0],'Preservado')
            self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='incompleta'").fetchone())
        finally: db.close()

    def test_remocao_interrompida_recupera_arquivo_no_reinicio(self):
        ident = self.importar()
        original = self.lib.caminho_original(ident)
        os.replace(original,self.lib.raiz/('.removido-'+ident))
        Biblioteca(self.banco,recuperar=True)
        self.assertTrue(original.exists())

    def test_migracao_v3_preserva_chat_e_backup(self):
        caminho = self.pasta/'v3.sqlite3'
        db = sqlite3.connect(caminho)
        db.executescript('''CREATE TABLE conversas(id TEXT PRIMARY KEY,titulo TEXT NOT NULL,rascunho TEXT NOT NULL DEFAULT '',atualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,arquivada INTEGER NOT NULL DEFAULT 0,fixada INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE mensagens(id INTEGER PRIMARY KEY,conversa_id TEXT,papel TEXT,texto TEXT,estado TEXT,provedor TEXT,modelo TEXT,criado TEXT);
        INSERT INTO conversas(id,titulo,rascunho,fixada) VALUES ('antigo','Calculo','rascunho',1);
        INSERT INTO mensagens VALUES (1,'antigo','user','Pergunta','ok','gemini','teste','2026-10-10');
        PRAGMA user_version=3;'''); db.close()
        banco = Historico(caminho)
        try:
            self.assertEqual(banco.obter('antigo')['rascunho'],'rascunho')
            self.assertEqual(banco.obter('antigo')['fixada'],1)
            self.assertEqual(banco.mensagens('antigo')[0]['texto'],'Pergunta')
            self.assertEqual(banco.db.execute('PRAGMA user_version').fetchone()[0],9)
            self.assertTrue(Path(str(caminho)+'.v3.backup').exists())
        finally: banco.fechar()
        backup = sqlite3.connect(str(caminho)+'.v3.backup')
        self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0],3)
        backup.close()


class LinksTest(unittest.TestCase):
    def test_urls_e_rede_privada(self):
        for url in ['file:///etc/passwd','javascript:alert(1)','https://a:b@example.com/','http://example.com:8080/']:
            with self.assertRaises(ValueError): normalizar_url(url)
        for ip in ['127.0.0.1','192.168.0.1','169.254.169.254','::1']:
            with patch('socket.getaddrinfo',return_value=[(socket.AF_INET,socket.SOCK_STREAM,6,'',(ip,80))]):
                with self.assertRaises(ValueError): endereco_publico('example.com',80)

    def test_redirecionamento_revalida_destino(self):
        resposta = Mock(status=302)
        resposta.getheader.return_value = 'http://127.0.0.1/'
        with patch('tutor_calculo.links.ConexaoPublica') as cls, patch('tutor_calculo.links.endereco_publico',side_effect=['93.184.216.34',ValueError('rede privada')]) as dns:
            cls.return_value.getresponse.return_value = resposta
            with self.assertRaisesRegex(ValueError,'rede privada'): baixar_link('https://example.com/')
            self.assertEqual(dns.call_count,2)

    def test_conteudo_grande_e_tipo_nao_suportado(self):
        resposta = Mock(status=200)
        resposta.getheader.return_value = str(3*1024*1024)
        with patch('tutor_calculo.links.endereco_publico',return_value='93.184.216.34'),patch('tutor_calculo.links.ConexaoPublica') as cls:
            cls.return_value.getresponse.return_value = resposta
            with self.assertRaisesRegex(ValueError,'2 MiB'): baixar_link('https://example.com/')
        with patch('tutor_calculo.links.baixar_link',return_value=(b'binary','application/octet-stream','https://example.com/')):
            self.assertEqual(extrair_link('https://example.com/')[0].estado,'nao_suportado')


class ConsultaDocumentalTest(unittest.TestCase):
    def setUp(self):
        self.fontes = [{'referencia':'M1','nome':'calculo.pdf','url':'','pagina':2,'tipo':'pdf','texto':'Derivada: 2x.'}]

    def test_openai_e_gemini_recebem_mesmo_contexto_e_citacoes(self):
        for provedor in ['openai','gemini']:
            with patch('tutor_calculo.ia.provedor_ativo',return_value=provedor),patch('tutor_calculo.ia.configuracao',return_value=('teste','modelo')):
                if provedor=='openai':
                    with patch('openai.OpenAI') as cls:
                        api = cls.return_value.__enter__.return_value
                        api.responses.create.return_value = Mock(output_text='2x [M1]',status='completed')
                        resposta = perguntar('Derive',fontes=self.fontes)
                        dados = api.responses.create.call_args.kwargs
                        payload,instrucoes = dados['input'],dados['instructions']
                else:
                    with patch('tutor_calculo.gemini.consultar',return_value='2x [M1]') as api:
                        resposta = perguntar('Derive',fontes=self.fontes)
                        payload,instrucoes = api.call_args.args[2:4]
                self.assertIn('Derivada: 2x.',payload)
                self.assertIn('DADOS NAO CONFIAVEIS',instrucoes)
                self.assertIn('calculo.pdf, pagina 2',resposta)

    def test_sem_trechos_e_referencia_inventada(self):
        with patch('tutor_calculo.ia.provedor_ativo',return_value='gemini'),patch('tutor_calculo.ia.configuracao',return_value=('teste','modelo')),patch('tutor_calculo.gemini.consultar',return_value='Veja [M99]') as api:
            resposta = perguntar('Pergunta',fontes=[])
            self.assertNotIn('[M99]',resposta)
            self.assertIn('nenhum trecho relevante',resposta)
            self.assertIn('Nao atribua conteudo',api.call_args.args[2])


if __name__=='__main__': unittest.main()
