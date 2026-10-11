import sqlite3
import tempfile
import unittest
from pathlib import Path

from tutor_calculo.armazenamento import Historico


class OrganizacaoChatsTest(unittest.TestCase):
    def setUp(self):
        self.pasta=tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.caminho=Path(self.pasta.name)/'historico.sqlite3'
        self.banco=Historico(self.caminho)
        self.addCleanup(self.banco.fechar)

    def test_busca_titulo_conteudo_unicode_e_literal(self):
        a,b=self.banco.criar(),self.banco.criar()
        self.banco.renomear(a,'Cálculo I')
        self.banco.adicionar(a,'assistant','Derivada de x²; 50% de _teste')
        self.banco.adicionar(a,'user','Derivada outra vez')
        self.banco.renomear(b,'Discreta')
        for busca in ['CÁLCULO','derivada','50%','_teste']:
            self.assertEqual([c['id'] for c in self.banco.listar(busca)], [a])
        self.assertEqual(self.banco.listar("' OR 1=1 --"),[])

    def test_arquivar_restaurar_preserva_mensagens_e_rascunho(self):
        a=self.banco.criar()
        self.banco.adicionar(a,'user','Questao')
        self.banco.rascunho(a,'Tentativa')
        self.banco.arquivar(a)
        self.assertEqual(self.banco.listar(),[])
        self.assertEqual(self.banco.listar('questao',True)[0]['id'],a)
        self.banco.arquivar(a,False)
        self.assertEqual(self.banco.listar()[0]['rascunho'],'Tentativa')
        self.assertEqual(self.banco.mensagens(a)[0]['texto'],'Questao')

    def test_exclusao_remove_so_a_conversa_e_suas_mensagens(self):
        a,b=self.banco.criar(),self.banco.criar()
        for cid in [a,b]:self.banco.adicionar(cid,'user','Questao')
        self.banco.excluir(a)
        self.assertEqual(self.banco.mensagens(a),[])
        self.assertEqual(len(self.banco.mensagens(b)),1)
        with self.assertRaises(ValueError):self.banco.obter(a)

    def test_fixadas_primeiro_e_persistencia(self):
        a,b=self.banco.criar(),self.banco.criar()
        self.banco.fixar(a)
        self.assertEqual(self.banco.listar()[0]['id'],a)
        outro=Historico(self.caminho)
        self.assertEqual(outro.obter(a)['fixada'],1)
        outro.fechar()
        self.banco.fixar(a,False)
        self.assertEqual(self.banco.obter(a)['fixada'],0)

    def test_migracao_v1_preserva_dados_e_faz_backup(self):
        caminho=Path(self.pasta.name)/'antigo.sqlite3'
        with sqlite3.connect(caminho) as db:
            db.execute('CREATE TABLE conversas (id TEXT PRIMARY KEY, titulo TEXT NOT NULL, rascunho TEXT NOT NULL DEFAULT "", atualizado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
            db.execute('CREATE TABLE mensagens (id INTEGER PRIMARY KEY, conversa_id TEXT, papel TEXT, texto TEXT, estado TEXT, provedor TEXT, modelo TEXT, criado TEXT)')
            db.execute("INSERT INTO conversas(id,titulo) VALUES ('a','Antigo')")
            db.execute('PRAGMA user_version=1')
        banco=Historico(caminho)
        self.assertEqual(banco.listar()[0]['titulo'],'Antigo')
        self.assertEqual(banco.listar()[0]['arquivada'],0)
        self.assertEqual(banco.db.execute('PRAGMA user_version').fetchone()[0],6)
        banco.fechar()
        with sqlite3.connect(str(caminho)+'.v1.backup') as backup:
            self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0],1)
            self.assertEqual(backup.execute('SELECT titulo FROM conversas').fetchone()[0],'Antigo')


if __name__=='__main__':unittest.main()
