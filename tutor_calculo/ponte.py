"""Unica superficie JavaScript: request com operacoes permitidas e envelopes."""
from pathlib import Path
import os
import subprocess
import sys
import webbrowser

from .servico import ident, texto
from .links import normalizar_url


class Ponte:
    def __init__(self,aplicacao):
        self._app=aplicacao
        self._window=None

    def request(self,operacao,dados=None):
        try:
            if not isinstance(dados,dict):raise ValueError('Parametros invalidos.')
            if operacao=='importar':
                if dados:raise ValueError('A importacao usa somente o seletor nativo.')
                if self._window is None:raise ValueError('Janela nao disponivel.')
                import webview
                caminhos=self._window.create_file_dialog(webview.FileDialog.OPEN,allow_multiple=True,
                    file_types=('Materiais (*.pdf;*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.tif;*.tiff;*.txt;*.md;*.csv;*.json;*.docx;*.pptx;*.log;*.tex)','Todos (*.*)'))
                resultado=self._app.importar(list(caminhos)) if caminhos else None
            elif operacao=='abrir_link':
                url=normalizar_url(texto(dados.get('url'),2000,False));webbrowser.open(url);resultado=None
            elif operacao=='abrir_original':
                mid=ident(dados.get('id'))
                with self._app._lock,self._app._banco() as (h,c,b):
                    material=b.obter(mid)
                    if material['url']:webbrowser.open(normalizar_url(material['url']))
                    else:
                        caminho=b.caminho_original(mid)
                        if not caminho or not caminho.is_file():raise ValueError('Original nao encontrado.')
                        if caminho.suffix.lower() in {'.exe','.com','.bat','.cmd','.sh','.ps1','.desktop','.app','.msi','.jar','.vbs','.py','.js'}:
                            raise ValueError('Arquivo executavel: abra manualmente em um editor. Anexos nao sao executados.')
                        if sys.platform=='win32':os.startfile(caminho)
                        else:subprocess.Popen(['open' if sys.platform=='darwin' else 'xdg-open',str(caminho)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                resultado=None
            elif operacao=='exemplo':
                from .app import EXEMPLO
                resultado=EXEMPLO
            elif operacao in ('math_exportar','discreta_exportar'):
                if self._window is None:raise ValueError('Janela não disponível.')
                raw=self._app._calculos.png(ident(dados.get('id')))
                import webview
                destino=self._window.create_file_dialog(webview.FileDialog.SAVE,save_filename='grafico-cadernomat.png',file_types=('Imagem PNG (*.png)',))
                if destino:
                    p=Path(destino[0]).with_suffix('.png')
                    import tempfile
                    fd,tmp=tempfile.mkstemp(prefix='.cadernomat-',dir=p.parent)
                    try:
                        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
                        os.replace(tmp,p)
                    finally:Path(tmp).unlink(missing_ok=True)
                resultado={'exportado':bool(destino)}
            else:resultado=self._app.executar(operacao,dados)
            return {'ok':True,'data':resultado}
        except (ValueError,RuntimeError,ImportError) as exc:
            return {'ok':False,'error':str(exc)}
        except Exception:
            return {'ok':False,'error':'Nao foi possivel concluir. Confira os dados e tente novamente.'}
