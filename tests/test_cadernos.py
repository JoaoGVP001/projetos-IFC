"""Organizacao por IDs, migracao atomica e contexto independente do provedor."""
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock, patch

from tutor_calculo.armazenamento import Historico
from tutor_calculo.cadernos import Cadernos, INICIAIS, contexto_pedagogico
from tutor_calculo.materiais import Biblioteca, migrar_materiais
from tutor_calculo.ia import perguntar
from tutor_calculo.app import EXEMPLO, resolver


def banco_v4(caminho):
    with closing(sqlite3.connect(caminho)) as db:
        db.executescript('''CREATE TABLE conversas(id TEXT PRIMARY KEY,titulo TEXT NOT NULL,
            rascunho TEXT DEFAULT '',atualizado TEXT DEFAULT CURRENT_TIMESTAMP,
            arquivada INTEGER DEFAULT 0,fixada INTEGER DEFAULT 0);
            CREATE TABLE mensagens(id INTEGER PRIMARY KEY,conversa_id TEXT REFERENCES conversas(id) ON DELETE CASCADE,
            papel TEXT,texto TEXT,estado TEXT,provedor TEXT,modelo TEXT,criado TEXT DEFAULT CURRENT_TIMESTAMP);
            INSERT INTO conversas VALUES ('antigo','Calculo 1','rascunho intacto',CURRENT_TIMESTAMP,1,1);
            INSERT INTO mensagens VALUES (1,'antigo','user','mensagem antiga','ok','gemini','teste',CURRENT_TIMESTAMP);
            BEGIN;''')
        migrar_materiais(db)
        for ident,materia in [('exato','Cálculo I'),('incerto','Calculo avancado'),('sem','')]:
            db.execute('''INSERT INTO materiais(id,chave,nome,tipo,estado,materia,origem_id,origem_titulo)
                VALUES (?,?,?,'texto','pronto',?,'antigo','Calculo 1')''',(ident,ident,ident+'.txt',materia))
        db.execute("INSERT INTO chat_materiais VALUES ('antigo','exato',1)")
        db.execute("INSERT INTO paginas VALUES ('exato',1,'Limite preservado')")
        db.execute("INSERT INTO trechos(material_id,pagina,ordem,texto) VALUES ('exato',1,0,'Limite preservado')")
        db.execute('PRAGMA user_version=4')
        db.commit()


class CadernosTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pasta = Path(self.tmp.name)
        self.h = Historico(self.pasta/'historico.sqlite3')
        self.addCleanup(lambda:self.h.fechar())
        self.c = Cadernos(self.h)
        self.b = Biblioteca(self.h)
        self.a,self.z = [x['id'] for x in self.c.listar()][:2]

    def material(self,chat):
        arquivo = self.pasta/'aula.txt'
        arquivo.write_text('Derivadas: a derivada de x² e 2x.',encoding='utf-8')
        ident,_ = self.b.adicionar_arquivo(arquivo,chat)
        self.b.processar(ident)
        return ident

    def test_criar_editar_ordenar_e_validar_nome(self):
        novo = self.c.criar('Algebra',objetivo='Revisar',nivel='Inicial',preferencia='dicas')
        self.c.editar(novo,'Álgebra Linear',assuntos='Vetores')
        registro = self.c.obter(novo)
        self.assertEqual(registro['objetivo'],'Revisar')
        self.assertEqual(registro['preferencia'],'dicas')
        self.assertTrue(registro['criado'] and registro['atualizado'])
        self.c.ordenar(novo,-1)
        self.assertEqual(self.c.listar()[-2]['id'],novo)
        self.c.ordenar(novo,1)
        self.assertEqual(self.c.listar()[-1]['id'],novo)
        for nome in ['',' Geral ','algebra linear','a'*101]:
            with self.subTest(nome=nome),self.assertRaises(ValueError):self.c.criar(nome)
        with self.assertRaises(ValueError):self.c.editar(novo,'Outro',preferencia='invalida')

    def test_arquivar_caderno_independente_dos_chats(self):
        chat = self.h.criar(self.a)
        outro = self.h.criar(self.a); self.h.arquivar(outro)
        material = self.material(chat)
        self.c.arquivar(self.a)
        self.assertEqual([x['id'] for x in self.c.listar(True)],[self.a])
        self.assertFalse(self.h.obter(chat)['arquivada'])
        self.assertTrue(self.h.obter(outro)['arquivada'])
        self.assertEqual(self.b.listar(caderno=self.a)[0]['id'],material)
        with self.assertRaises(ValueError):self.h.criar(self.a)
        with self.assertRaises(ValueError):self.c.mover_conversa(self.h.criar(),self.a)
        self.c.arquivar(self.a,False)
        self.assertFalse(self.c.obter(self.a)['arquivado'])
        self.assertTrue(self.h.obter(outro)['arquivada'])

    def test_mover_chat_preserva_ids_mensagens_rascunho_e_fontes(self):
        chat = self.h.criar(self.a)
        self.h.adicionar(chat,'user','Derive x²',provedor='gemini',modelo='teste')
        self.h.rascunho(chat,'Minha tentativa'); self.h.fixar(chat); self.h.arquivar(chat)
        material = self.material(chat); self.b.vincular(material,chat,True)
        antes = self.h.obter(chat); mensagens = self.h.mensagens(chat)
        origem = self.b.obter(material)
        self.c.mover_conversa(chat,self.z)
        depois = self.h.obter(chat)
        for chave in ['id','titulo','rascunho','arquivada','fixada']:
            self.assertEqual(antes[chave],depois[chave])
        self.assertEqual(self.h.mensagens(chat),mensagens)
        self.assertEqual(self.b.obter(material),origem)
        self.assertTrue(self.b.anexos(chat)[0]['selecionado'])
        self.assertEqual({x['id'] for x in self.b.cadernos_material(material)},{self.a,self.z})
        self.c.mover_conversa(chat,None)
        self.assertIsNone(self.h.obter(chat)['caderno_id'])
        self.assertEqual(self.h.listar(arquivadas=True,caderno=None)[0]['id'],chat)

    def test_materiais_compartilhados_sem_duplicar_ou_autorizar(self):
        chat = self.h.criar(self.a); outro = self.h.criar(self.z)
        material = self.material(chat)
        quantidade = self.h.db.execute('SELECT COUNT(*) FROM trechos').fetchone()[0]
        self.b.vincular(material,chat,True)
        segundo,criado = self.b.adicionar_arquivo(self.pasta/'aula.txt',outro)
        self.assertEqual(segundo,material); self.assertFalse(criado)
        self.assertEqual(len(list(self.b.raiz.iterdir())),1)
        self.assertEqual(self.h.db.execute('SELECT COUNT(*) FROM trechos').fetchone()[0],quantidade)
        self.assertFalse(self.b.anexos(outro)[0]['selecionado'])
        self.assertEqual(self.b.recuperar(outro,'derivada'),[])
        self.assertTrue(self.b.recuperar(chat,'derivada'))
        self.b.associar_cadernos(material,[self.z,self.z])
        self.assertEqual(self.b.listar(caderno=self.a),[])
        self.assertEqual(self.b.listar(caderno=self.z)[0]['id'],material)
        self.assertEqual(self.b.listar(caderno=None),[])
        with self.assertRaises(ValueError):self.b.associar_cadernos(material,['inexistente'])
        self.assertEqual(self.b.cadernos_material(material)[0]['id'],self.z)
        self.b.associar_cadernos(material,[])
        self.assertEqual(self.b.listar('derivadas',caderno=None)[0]['id'],material)
        self.b.adicionar_arquivo(self.pasta/'aula.txt',chat)
        self.assertEqual(self.b.cadernos_material(material)[0]['id'],self.a)
        self.assertTrue(self.b.anexos(chat)[0]['selecionado'])

    def test_edicao_de_metadados_e_associacoes_preserva_estado_em_falha(self):
        chat=self.h.criar(self.a); material=self.material(chat)
        antes=self.b.obter(material)
        with self.assertRaises(ValueError):
            self.b.metadados(material,'Nome alterado',cadernos=['inexistente'])
        self.assertEqual(self.b.obter(material),antes)
        self.assertEqual(self.b.cadernos_material(material)[0]['id'],self.a)
        self.b.metadados(material,'Aula revisada',assunto='Limites',cadernos=[self.a,self.z])
        self.assertEqual(self.b.obter(material)['nome'],'Aula revisada')
        self.assertEqual({c['id'] for c in self.b.cadernos_material(material)},{self.a,self.z})

    def test_excluir_caderno_preserva_dados_e_outros_vinculos(self):
        chat = self.h.criar(self.a); material = self.material(chat)
        self.h.adicionar(chat,'user','Preserve esta mensagem')
        self.b.associar_cadernos(material,[self.a,self.z])
        self.c.salvar_navegacao(self.a,chat)
        original = self.b.caminho_original(material)
        self.c.excluir(self.a)
        self.assertIsNone(self.h.obter(chat)['caderno_id'])
        self.assertIsNone(self.c.navegacao()['caderno_id'])
        self.assertEqual(self.c.navegacao()['conversa_id'],chat)
        self.assertEqual(len(self.h.mensagens(chat)),1)
        self.assertTrue(original.is_file())
        self.assertEqual(self.b.cadernos_material(material)[0]['id'],self.z)
        self.assertTrue(self.b.listar('derivadas'))
        self.b.excluir(material)
        self.assertEqual(self.h.db.execute('SELECT COUNT(*) FROM materiais_cadernos').fetchone()[0],0)

    def test_reinicio_preserva_navegacao_e_nao_recria_iniciais(self):
        self.assertEqual([x['nome'] for x in self.c.listar()],[x[0] for x in INICIAIS])
        self.c.excluir(self.a)
        self.c.editar(self.z,'Calculo personalizado')
        self.c.salvar_navegacao(self.z,None)
        self.h.fechar()
        self.h = Historico(self.pasta/'historico.sqlite3'); self.c = Cadernos(self.h)
        self.assertEqual(len(self.c.listar()),2)
        self.assertEqual(self.c.obter(self.z)['nome'],'Calculo personalizado')
        self.assertEqual(self.c.navegacao()['caderno_id'],self.z)
        self.assertIsNone(self.c.navegacao()['conversa_id'])
        self.assertEqual(self.h.listar(),[])


class MigracaoCadernosTest(unittest.TestCase):
    def test_migrar_v4_preserva_todos_os_dados_e_associa_so_alias_exato(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta)/'historico.sqlite3'; banco_v4(caminho)
            with closing(sqlite3.connect(caminho)) as antigo:
                dados = {t:antigo.execute('SELECT * FROM '+t).fetchall() for t in ['mensagens','materiais','chat_materiais','paginas','trechos']}
            h = Historico(caminho)
            try:
                c,b = Cadernos(h),Biblioteca(h)
                self.assertEqual(h.db.execute('PRAGMA user_version').fetchone()[0],8)
                self.assertIsNone(h.obter('antigo')['caderno_id'])
                self.assertTrue(h.obter('antigo')['fixada'])
                self.assertEqual(h.obter('antigo')['rascunho'],'rascunho intacto')
                for tabela,linhas in dados.items():
                    self.assertEqual([tuple(r) for r in h.db.execute('SELECT * FROM '+tabela)],linhas)
                self.assertEqual(b.cadernos_material('exato')[0]['nome'],INICIAIS[1][0])
                self.assertEqual(b.cadernos_material('incerto'),[])
                self.assertEqual(b.cadernos_material('sem'),[])
                self.assertEqual(len(b.listar('limite')),1)
                self.assertEqual(h.db.execute('PRAGMA foreign_key_check').fetchall(),[])
            finally:h.fechar()
            with closing(sqlite3.connect(str(caminho)+'.v4.backup')) as backup:
                self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0],4)
                self.assertEqual(backup.execute('SELECT rascunho FROM conversas').fetchone()[0],'rascunho intacto')
            h=Historico(caminho)
            try:self.assertEqual(len(Cadernos(h).listar()),3)
            finally:h.fechar()

    def test_falha_migracao_reverte_ddl_e_indices(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta)/'historico.sqlite3'; banco_v4(caminho)
            def falhar(db):
                db.execute('CREATE TABLE cadernos(id TEXT PRIMARY KEY)')
                db.execute('ALTER TABLE conversas ADD COLUMN caderno_id TEXT')
                db.execute('DELETE FROM trechos')
                raise RuntimeError('falha simulada')
            with patch('tutor_calculo.cadernos.migrar_cadernos',side_effect=falhar),self.assertRaises(RuntimeError):Historico(caminho)
            with closing(sqlite3.connect(caminho)) as db:
                self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],4)
                self.assertNotIn('caderno_id',[r[1] for r in db.execute('PRAGMA table_info(conversas)')])
                self.assertIsNone(db.execute("SELECT name FROM sqlite_master WHERE name='cadernos'").fetchone())
                self.assertEqual(db.execute('SELECT COUNT(*) FROM trechos_fts WHERE trechos_fts MATCH ?',('limite',)).fetchone()[0],1)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM mensagens').fetchone()[0],1)


class ContextoCadernosTest(unittest.TestCase):
    def test_ambos_provedores_recebem_pedagogia_historico_e_documento_separados(self):
        caderno={'nome':'Discreta escolhida','objetivo':'Provas por inducao','preferencia':'dicas'}
        historico=[{'papel':'user','texto':'Minha tentativa','estado':'ok'}, {'papel':'assistant','texto':'Boa base','estado':'ok'}]
        fontes=[{'referencia':'M1','nome':'notas.txt','url':'','tipo':'texto','pagina':1,'texto':'Exemplo consultado'}]
        instrucoes_comuns=[]
        for provedor in ['openai','gemini']:
            with self.subTest(provedor=provedor),patch('tutor_calculo.ia.provedor_ativo',return_value=provedor),patch('tutor_calculo.ia.configuracao',return_value=('teste','modelo')):
                if provedor=='openai':
                    with patch('openai.OpenAI') as cls:
                        api=cls.return_value.__enter__.return_value
                        api.responses.create.return_value=Mock(output_text='Dica [M1]',status='completed')
                        perguntar('Ajude',modo='Corrigir',historico=historico,fontes=fontes,caderno=caderno)
                        args=api.responses.create.call_args.kwargs
                        payload,instrucoes=args['input'],args['instructions']
                else:
                    with patch('tutor_calculo.gemini.consultar',return_value='Dica [M1]') as api:
                        perguntar('Ajude',modo='Corrigir',historico=historico,fontes=fontes,caderno=caderno)
                        payload,instrucoes=api.call_args.args[2:4]
                        self.assertIn('Minha tentativa',str(api.call_args.kwargs['historico']))
                self.assertIn('Discreta escolhida',instrucoes)
                self.assertIn('uma dica por vez',instrucoes)
                self.assertIn('tentativa',instrucoes)
                self.assertIn('DADOS NAO CONFIAVEIS',instrucoes)
                if provedor=='openai':self.assertIn('Minha tentativa',str(payload))
                self.assertIn('Exemplo consultado',str(payload))
                self.assertNotIn('Discreta escolhida',str(payload))
                instrucoes_comuns.append(instrucoes)
        self.assertEqual(*instrucoes_comuns)

    def test_caderno_nao_vaza_para_proxima_consulta(self):
        with patch('tutor_calculo.ia.provedor_ativo',return_value='gemini'),patch('tutor_calculo.ia.configuracao',return_value=('teste','modelo')),patch('tutor_calculo.gemini.consultar',return_value='Resposta') as api:
            perguntar('Primeira',caderno={'nome':'PRIVADO-A','preferencia':'correcao'})
            self.assertIn('primeiro erro',api.call_args.args[3])
            perguntar('Segunda',caderno={'nome':'OUTRO-B','preferencia':'completa'})
            self.assertNotIn('PRIVADO-A',str(api.call_args))
            self.assertIn('OUTRO-B',api.call_args.args[3])
            perguntar('Geral')
            self.assertNotIn('OUTRO-B',str(api.call_args))
        self.assertEqual(contexto_pedagogico(None),'')

    def test_resolver_local_preservado_e_fallback_recebe_contexto(self):
        caderno={'nome':'Calculo','preferencia':'completa'}
        with patch('tutor_calculo.app.perguntar',return_value='IA') as api:
            self.assertIn('nao e continua',resolver(EXEMPLO,caderno=caderno,historico=[]))
            api.assert_not_called()
            self.assertEqual(resolver('Derive x²',caderno=caderno,historico=[]),'IA')
            api.assert_called_once_with('Derive x²',caderno=caderno,historico=[])


if __name__=='__main__':unittest.main()
