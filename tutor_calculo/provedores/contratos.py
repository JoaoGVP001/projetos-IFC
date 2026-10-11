"""Estados e cancelamento comuns; documentos não podem iniciar operações."""
from threading import Event, Lock


class ConsultaCancelada(RuntimeError):
    pass


class RespostaIncompleta(RuntimeError):
    pass


class Cancelamento:
    def __init__(self):
        self.evento = Event()
        self._lock = Lock()
        self._interromper = None

    def verificar(self):
        if self.evento.is_set():
            raise ConsultaCancelada('Consulta cancelada. O texto parcial não é uma resposta concluída.')

    def registrar(self, funcao):
        with self._lock:
            self._interromper = funcao
            if self.evento.is_set() and funcao: funcao()

    def cancelar(self):
        with self._lock:
            self.evento.set()
            if self._interromper: self._interromper()
