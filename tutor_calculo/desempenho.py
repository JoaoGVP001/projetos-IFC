"""Perfis finitos e medição local limitada, sem consultas extras de geração."""
import os
from pathlib import Path
from threading import Event, Thread

PERFIS = {'rapido': ('Rápido no notebook', 640, 180, 180),
          'estudo': ('Estudo', 1024, 240, 260),
          'completo': ('Completo', 1536, 360, 380),
          'legado': ('Configuração anterior', 1024, 180, 240)}
ESTRUTURADAS = {'Gerar atividade', 'Organizar página', 'Rotular blocos', 'Propor cálculo', 'Propor Discreta'}


def politica(config, modo='Resolver'):
    perfil = config.get('perfil', 'legado')
    if not isinstance(perfil,str) or perfil not in PERFIS: raise ValueError('Perfil local inválido.')
    nome, saida, prazo, palavras = PERFIS[perfil]
    if perfil == 'legado': saida = 640 if config['contexto'] == 2048 else 1024
    if modo in ESTRUTURADAS: saida = max(saida, 1024)
    if modo == 'Dica de atividade': saida = min(saida, 384)
    if modo == 'Feedback de atividade': saida = min(saida, 512)
    return {'perfil': perfil, 'perfil_nome': nome, 'reserva_saida': saida,
            'timeout': config['timeout'], 'timeout_sugerido': prazo,
            'palavras_alvo': palavras, 'tarefa': modo}


def memoria():
    """Linux: valores observados. Outros sistemas retornam desconhecido."""
    out = {'ram_total': None, 'ram_disponivel': None, 'swap_usada': None,
           'rss_aplicativo': None, 'rss_filhos_aplicativo': None, 'rss_ollama': None}
    try:
        info = {p[0].rstrip(':'): int(p[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if len(p := line.split()) >= 2}
        out.update(ram_total=info['MemTotal'], ram_disponivel=info['MemAvailable'], swap_usada=info['SwapTotal']-info['SwapFree'])
        def rss(pid): return int((Path('/proc')/str(pid)/'statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')
        out['rss_aplicativo'] = rss(os.getpid())
        children=[os.getpid()]; child_rss=0; visited=set()
        for _ in range(32):
            if not children:break
            pid=children.pop()
            if pid in visited:continue
            visited.add(pid)
            try:
                children.extend(int(x) for x in (Path('/proc')/str(pid)/'task'/str(pid)/'children').read_text().split())
                if pid!=os.getpid():child_rss+=rss(pid)
            except (OSError,ValueError,IndexError):pass
        out['rss_filhos_aplicativo']=child_rss
        total = 0; found = False
        for pid in list(Path('/proc').iterdir())[:4096]:
            if not pid.name.isdigit(): continue
            try:
                command = (pid/'cmdline').read_bytes()[:1000].split(b'\0')[0].decode(errors='ignore')
                if Path(command).name in ('ollama', 'runner', 'llama-server'):
                    total += rss(pid.name); found = True
            except (OSError, ValueError, IndexError): pass
        out['rss_ollama'] = total if found else None
    except (OSError, ValueError, KeyError, IndexError, AttributeError): pass
    return out


def dispositivo(modelos, nome):
    m = next((m for m in modelos if isinstance(m,dict) and (m.get('name') == nome or m.get('model') == nome)), None) if isinstance(modelos,list) else None
    if not m: return {'estado': 'nao_carregado', 'processador': 'desconhecido', 'size': None, 'size_vram': None, 'contexto': None}
    def number(k):
        v=m.get(k); return v if type(v) is int and v >= 0 else None
    size=number('size'); vram=number('size_vram')
    processor='desconhecido' if vram is None or not size else 'CPU' if vram == 0 else 'GPU' if vram >= size else 'CPU/GPU'
    return {'estado': 'carregado', 'processador': processor, 'size': size, 'size_vram': vram, 'contexto': number('context_length')}


class Amostragem:
    def __init__(self):
        self.stop=Event(); self.dados={'amostras': 0, 'rss_aplicativo_max': None, 'rss_filhos_aplicativo_max': None, 'rss_ollama_max': None, 'swap_usada_max': None, 'ram_disponivel_min': None}
        self.thread=Thread(target=self._run,daemon=True,name='cadernomat-memoria')
    def _run(self):
        for _ in range(180):
            m=memoria(); self.dados['amostras']+=1
            for dest,source,fun in [('rss_aplicativo_max','rss_aplicativo',max),('rss_filhos_aplicativo_max','rss_filhos_aplicativo',max),('rss_ollama_max','rss_ollama',max),('swap_usada_max','swap_usada',max),('ram_disponivel_min','ram_disponivel',min)]:
                if m[source] is not None: self.dados[dest]=m[source] if self.dados[dest] is None else fun(self.dados[dest],m[source])
            if self.stop.wait(2):break
    def __enter__(self):self.thread.start();return self
    def __exit__(self,*a):self.stop.set();self.thread.join(timeout=3)
