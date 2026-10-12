"""Renderizador isolado: compositor local React/KaTeX -> PDF Qt -> PNG PDFium."""
import argparse
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import secrets
import sys
from threading import Thread
from urllib.parse import urlsplit, unquote


def renderizar(data, saida):
    from PySide6.QtCore import QUrl,QTimer,QMarginsF,QCoreApplication,QEvent
    from PySide6.QtGui import QPageLayout,QPageSize
    from PySide6.QtWidgets import QApplication
    from PySide6.QtWebEngineCore import QWebEnginePage,QWebEngineProfile,QWebEngineUrlRequestInterceptor,QWebEngineSettings
    web=Path(__file__).parent/'web';nonce=secrets.token_hex(24);payload=json.dumps(data,ensure_ascii=False).encode()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            path=unquote(urlsplit(self.path).path)
            if not path.startswith('/'+nonce+'/'):self.send_error(404);return
            name=path[len(nonce)+2:]
            if name=='payload.json':raw=payload;mime='application/json'
            elif name=='index.html' or (name.startswith('assets/') and '/' not in name[7:] and '..' not in name):
                file=web/name
                if not file.is_file() or file.is_symlink():self.send_error(404);return
                raw=file.read_bytes();mime=mimetypes.guess_type(name)[0] or 'application/octet-stream'
            else:self.send_error(404);return
            self.send_response(200);self.send_header('Content-Type',mime);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);Thread(target=server.serve_forever,daemon=True).start();port=server.server_address[1]
    class LocalOnly(QWebEngineUrlRequestInterceptor):
        def interceptRequest(self,info):
            u=info.requestUrl()
            if u.scheme()=='data':return
            if u.scheme()!='http' or u.host()!='127.0.0.1' or u.port()!=port or not u.path().startswith('/'+nonce+'/'):info.block(True)
    app=QApplication.instance() or QApplication([]);profile=QWebEngineProfile();guard=LocalOnly();profile.setUrlRequestInterceptor(guard)
    class Page(QWebEnginePage):
        def javaScriptConsoleMessage(self,level,message,line,source):
            if level==QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:print('Compositor: '+message[:300],file=sys.stderr)
    page=Page(profile);page.settings().setAttribute(QWebEngineSettings.WebAttribute.PrintElementBackgrounds,True)
    result={};finished=False
    def end(ok,error=''):
        nonlocal finished
        if finished:return
        finished=True;result.update(ok=ok,erro=error);app.quit()
    def printed(raw):
        if finished:return
        try:
            raw=bytes(raw)
            if not raw.startswith(b'%PDF') or len(raw)>20*1024*1024:raise ValueError('PDF inválido ou acima de 20 MiB.')
            (saida/'pagina.pdf').write_bytes(raw);end(True)
        except Exception as e:end(False,str(e))
    def status(s):
        if finished:return
        if isinstance(s,str):
            try:s=json.loads(s)
            except ValueError:s=None
        if not isinstance(s,dict):QTimer.singleShot(100,poll);return
        if not s.get('ok'):end(False,s.get('erro','Falha ao compor folhas.'));return
        result['compositor']=s
        page.printToPdf(printed,QPageLayout(QPageSize(QPageSize.PageSizeId.A4),QPageLayout.Orientation.Portrait,QMarginsF(0,0,0,0)))
    def poll():page.runJavaScript('JSON.stringify(window.cadernoMatExportStatus || null)',status)
    def loaded(ok):
        if not ok:end(False,'Interface de exportação indisponível.');return
        poll()
    page.loadFinished.connect(loaded);QTimer.singleShot(60000,lambda:end(False,'Exportação excedeu 60 segundos.'))
    page.load(QUrl(f'http://127.0.0.1:{port}/{nonce}/index.html?pagina-export'))
    app.exec();server.shutdown();page.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);profile.deleteLater();QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete)
    if not result.get('ok'):raise ValueError(result.get('erro','Falha na renderização.'))
    from pypdf import PdfReader
    import pypdfium2 as pdfium
    pdf_path=saida/'pagina.pdf';reader=PdfReader(pdf_path)
    count=len(reader.pages)
    if not 1<=count<=20 or count!=result['compositor']['folhas']:raise ValueError('Paginação do PDF difere da prévia. Nenhum artefato será publicado.')
    manifest={'folhas':count,'avisos':result['compositor'].get('avisos',[]),'runtime':'Qt + KaTeX + PDFium','compositor':'paginas-v1','arquivos':[]}
    total=0
    with pdfium.PdfDocument(pdf_path) as pdf:
        for i in range(count):
            folha=pdf[i]
            try:
                bitmap=folha.render(scale=2);image=bitmap.to_pil();dest=saida/f'folha-{i+1:02}.png';image.save(dest);image.close();bitmap.close()
                total+=dest.stat().st_size
                if total>40*1024*1024:raise ValueError('PNGs excedem 40 MiB.')
            finally:folha.close()
    for file in [pdf_path,*sorted(saida.glob('folha-*.png'))]:manifest['arquivos'].append({'nome':file.name,'tamanho':file.stat().st_size,'hash':sha256(file.read_bytes()).hexdigest()})
    (saida/'manifesto.json').write_text(json.dumps(manifest,ensure_ascii=False));return manifest


def main():
    args=argparse.ArgumentParser();args.add_argument('--saida',type=Path,required=True);d=args.parse_args()
    try:
        raw=sys.stdin.read(20_000_001)
        if len(raw)>20_000_000:raise ValueError('Documento acima do limite.')
        data=json.loads(raw);d.saida.mkdir(parents=True,exist_ok=True)
        print(json.dumps({'ok':True,'manifesto':renderizar(data,d.saida)},ensure_ascii=False))
    except ImportError:print(json.dumps({'ok':False,'erro':'Exportação requer PySide6, Qt WebEngine e PDFium instalados. O editor permanece disponível.'}))
    except (ValueError,RuntimeError) as e:print(json.dumps({'ok':False,'erro':str(e)[:800]},ensure_ascii=False))
    except Exception:print(json.dumps({'ok':False,'erro':'Falha inesperada no renderizador. A versão original foi preservada.'},ensure_ascii=False))
if __name__=='__main__':main()
