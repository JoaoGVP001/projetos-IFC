"""Preferências sem segredos no diretório de dados do aplicativo."""
import json
import os
from pathlib import Path
from uuid import uuid4
from .provedores.ollama import PADRAO, validar_config


class PreferenciasIA:
    def __init__(self, pasta): self.caminho = Path(pasta)/'ia.json'

    def ler(self):
        if not self.caminho.exists(): return {'padrao': None, 'ollama': dict(PADRAO)}
        try:
            data = json.loads(self.caminho.read_text())
            provider = data.get('padrao')
            if provider is not None and provider not in ('openai', 'gemini', 'ollama'): raise ValueError()
            return {'padrao': provider, 'ollama': validar_config(data.get('ollama', {}))}
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            # Uma configuração local inválida nunca troca silenciosamente para nuvem.
            raise RuntimeError('Preferências de IA inválidas. Restaure o arquivo ia.json do backup local.') from exc

    def salvar(self, provider, local=None):
        data = self.ler()
        if provider not in ('openai', 'gemini', 'ollama'): raise ValueError('Provedor inválido.')
        data['padrao'] = provider
        if local is not None: data['ollama'] = validar_config(local)
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        temp = self.caminho.with_name('ia-'+str(uuid4())+'.tmp')
        try:
            with open(os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), 'w') as file:
                json.dump(data, file, ensure_ascii=False)
            os.replace(temp, self.caminho)
        finally:
            temp.unlink(missing_ok=True)


def migrar_ia(db):
    db.execute('''CREATE TABLE chat_ia (
        conversa_id TEXT PRIMARY KEY REFERENCES conversas(id) ON DELETE CASCADE,
        provedor TEXT NOT NULL, modelo TEXT NOT NULL, config TEXT NOT NULL DEFAULT '{}')''')
    db.execute('''CREATE TABLE consultas_ia (
        id TEXT PRIMARY KEY, conversa_id TEXT NOT NULL REFERENCES conversas(id) ON DELETE CASCADE,
        usuario_id INTEGER REFERENCES mensagens(id) ON DELETE SET NULL,
        resposta_id INTEGER REFERENCES mensagens(id) ON DELETE SET NULL,
        snapshot TEXT NOT NULL, estado TEXT NOT NULL, parcial TEXT NOT NULL DEFAULT '',
        erro TEXT NOT NULL DEFAULT '', metricas TEXT NOT NULL DEFAULT '{}',
        criado TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
    db.execute('CREATE INDEX consultas_chat ON consultas_ia(conversa_id,estado)')
