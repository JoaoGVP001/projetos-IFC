"""Janela desktop com interface React compilada e ponte Python restrita."""
import argparse
import os
from pathlib import Path
from threading import Event, Thread

from .ponte import Ponte
from .servico import Aplicacao


def abrir(aplicacao=None,debug=False):
    try:
        import webview
    except ImportError as exc:
        raise RuntimeError('Instale as dependencias de requirements.txt. Consulte docs/INTERFACE.md.') from exc
    pagina=Path(__file__).parent/'web'/'index.html'
    if not pagina.is_file():raise RuntimeError('Interface compilada ausente. Execute pnpm build na pasta frontend.')
    app=aplicacao or Aplicacao()
    ponte=Ponte(app)
    janela=webview.create_window('CadernoMat — seu espaço de matemática',str(pagina.resolve()),
        js_api=ponte,width=1240,height=820,min_size=(1000,650),background_color='#F8F7F4')
    ponte._window=janela
    encerrando=Event()
    def fechar():
        if encerrando.is_set():return True
        encerrando.set()
        # Qt dispara closing na thread da janela. Avaliar JS nela causaria
        # deadlock; adiar o fechamento permite salvar o ultimo caractere.
        def concluir():
            try:
                if janela.events.loaded.is_set():
                    for global_name, operacao in [('cadernoMatDraft','rascunho'),('cadernoMatStudyDraft','tentativa_salvar')]:
                        try:
                            rascunho=janela.evaluate_js(f'window.{global_name} || null')
                            if isinstance(rascunho,dict) and rascunho.get('id'):
                                app.executar(operacao,rascunho)
                        except Exception:pass
            except Exception:pass
            finally:
                app.fechar()
                janela.destroy()
        Thread(target=concluir,name='cadernomat-fechar').start()
        return False
    janela.events.closing+=fechar
    os.environ.setdefault('QT_API','pyside6')
    webview.start(gui='qt' if os.name=='posix' and os.uname().sysname=='Linux' else None,debug=debug,
        storage_path=str(app.caminho.parent/'webview'))
    app.fechar()


def main():
    parser=argparse.ArgumentParser(description='CadernoMat desktop')
    parser.add_argument('--legado',action='store_true',help='Abrir interface CustomTkinter anterior')
    parser.add_argument('--banco',type=Path,help='Banco separado para desenvolvimento ou validacao')
    parser.add_argument('--debug',action='store_true',help='Habilitar ferramentas da WebView')
    args=parser.parse_args()
    if args.legado:
        from .desktop_legado import TutorDesktop
        TutorDesktop(args.banco).mainloop()
        return
    try:abrir(Aplicacao(args.banco),args.debug)
    except (RuntimeError,ImportError) as exc:raise SystemExit(str(exc))


if __name__=='__main__':main()
