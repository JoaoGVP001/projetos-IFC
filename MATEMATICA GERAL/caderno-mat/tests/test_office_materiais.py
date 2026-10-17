import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from pypdf import PdfReader, PdfWriter

from tutor_calculo.armazenamento import Historico
from tutor_calculo.extracao import extrair, tipo_arquivo
from tutor_calculo.materiais import Biblioteca, contexto_documental, referencias
from tutor_calculo.recuperacao import recuperar_estudo
from tests.test_materiais import pdf_texto

M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def pptx(caminho, corpo, destino='slides/slide2.xml'):
    with zipfile.ZipFile(caminho,'w') as z:
        z.writestr('ppt/presentation.xml',f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst><p:sldId r:id="r2"/><p:sldId r:id="r1"/></p:sldIdLst></p:presentation>')
        z.writestr('ppt/_rels/presentation.xml.rels',f'<Relationships><Relationship Id="r1" Target="slides/slide1.xml"/><Relationship Id="r2" Target="{destino}"/></Relationships>')
        z.writestr('ppt/slides/slide1.xml',f'<p:sld xmlns:p="{P}" xmlns:a="{A}"><a:p><a:r><a:t>Conjuntos no segundo slide.</a:t></a:r></a:p></p:sld>')
        z.writestr('ppt/slides/slide2.xml',f'<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:m="{M}">{corpo}</p:sld>')
        z.writestr('ppt/notesSlides/notesSlide1.xml','NOTAS_PRIVADAS_NAO_EXTRAIDAS')


class OfficeMateriaisTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)

    def test_pptx_ordem_real_formula_persistencia_e_citacao_de_slide(self):
        f=self.p/'slides.pptx'
        pptx(f,'<a:p><a:r><a:t>Indução: </a:t></a:r><m:oMath><m:f><m:num><m:r><m:t>n(n+1)</m:t></m:r></m:num><m:den><m:r><m:t>2</m:t></m:r></m:den></m:f></m:oMath></a:p>')
        r=extrair(f,f.name)
        self.assertEqual(tipo_arquivo(f.name),'pptx');self.assertEqual(r.estado,'parcial')
        self.assertEqual([n for n,_ in r.paginas],[1,2])
        self.assertIn(r'\frac{n(n+1)}{2}',r.paginas[0][1])
        self.assertNotIn('NOTAS_PRIVADAS',str(r.paginas))
        h=Historico(self.p/'historico.sqlite3');cid=h.criar();b=Biblioteca(h)
        mid,novo=b.adicionar_arquivo(f,cid);b.processar(mid);b.vincular(mid,cid,True)
        fontes=b.recuperar(cid,'indução')
        self.assertEqual(json.loads(contexto_documental(fontes))[0]['unidade'],'slide')
        self.assertIn('imagens',json.loads(contexto_documental(fontes))[0]['aviso_extracao'])
        self.assertIn('slide 1',referencias(fontes));self.assertEqual(fontes[0]['pagina'],1)
        self.assertEqual(recuperar_estudo(h,[mid],'indução')[0][0]['pagina'],1)
        self.assertEqual(b.adicionar_arquivo(f,cid),(mid,False));h.fechar()
        h=Historico(self.p/'historico.sqlite3')
        try:
            b=Biblioteca(h,recuperar=True);self.assertEqual(len(b.paginas(mid)),2)
            self.assertTrue(b.recuperar(cid,'indução'));b.excluir(mid)
            self.assertFalse(b.recuperar(cid,'indução'))
        finally:h.fechar()

    def test_docx_expoente_fracao_radical_sem_flattening(self):
        f=self.p/'exercicio.docx'
        with zipfile.ZipFile(f,'w') as z:
            z.writestr('word/document.xml',f'''<w:document xmlns:w="{W}" xmlns:m="{M}"><w:body><w:p>
            <w:r><w:t>2</w:t></w:r><w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:t>n</w:t></w:r>
            <w:proofErr/><w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:t>-1</w:t></w:r>
            <m:oMath><m:f><m:num><m:r><m:t>n+1</m:t></m:r></m:num><m:den><m:r><m:t>2</m:t></m:r></m:den></m:f>
            <m:rad><m:deg/><m:e><m:r><m:t>x</m:t></m:r></m:e></m:rad></m:oMath>
            </w:p></w:body></w:document>''')
        r=extrair(f,f.name);self.assertEqual(r.estado,'parcial')
        self.assertIn('2^{n-1}',r.paginas[0][1])
        self.assertIn(r'\frac{n+1}{2}',r.paginas[0][1])
        self.assertIn(r'\sqrt{x}',r.paginas[0][1])

    def test_formula_desconhecida_nao_inventa_resultado(self):
        f=self.p/'slides.pptx';pptx(f,'<a:p><m:oMath><m:desconhecido><m:t>123</m:t></m:desconhecido></m:oMath></a:p>')
        r=extrair(f,f.name)
        self.assertIn('Equação não interpretada',r.paginas[0][1]);self.assertNotIn('123',r.paginas[0][1])
        self.assertIn('Equações não suportadas',r.aviso)

    def test_alternatecontent_nao_duplica_formula_e_texto(self):
        f=self.p/'slides.pptx'
        pptx(f,'<a:p xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"><mc:AlternateContent><mc:Choice><a:r><a:t>Indução</a:t></a:r></mc:Choice><mc:Fallback><a:r><a:t>DUPLICADO</a:t></a:r></mc:Fallback></mc:AlternateContent></a:p>')
        r=extrair(f,f.name);self.assertEqual(r.paginas[0][1],'Indução')

    def test_office_corrompido_relacao_externa_e_entidades_rejeitados(self):
        f=self.p/'slides.pptx';f.write_bytes(b'corrompido')
        self.assertEqual(extrair(f,f.name).estado,'erro')
        pptx(f,'<a:p><a:r><a:t>texto</a:t></a:r></a:p>',destino='https://example.com/slide.xml')
        self.assertEqual(extrair(f,f.name).estado,'erro')
        d=self.p/'equacoes.docx'
        for xml in (b'<!DOCTYPE x [<!ENTITY a "privado">]><x>&a;</x>', '<!DOCTYPE x [<!ENTITY a "privado">]><x>&a;</x>'.encode('utf-16')):
            with zipfile.ZipFile(d,'w') as z:z.writestr('word/document.xml',xml)
            self.assertEqual(extrair(d,d.name).estado,'erro')

    def test_pdf_processa_paginas_depois_da_80_sem_truncamento_silencioso(self):
        original=self.p/'pagina.pdf';pdf_texto(original);r=PdfReader(original);w=PdfWriter()
        for _ in range(81):w.add_page(r.pages[0])
        f=self.p/'livro.pdf';w.write(f);res=extrair(f,f.name)
        self.assertEqual(res.estado,'pronto');self.assertEqual(res.paginas[-1][0],81)


if __name__=='__main__':unittest.main()
