"""Leitura limitada de links publicos, sem cookies, scripts ou acesso a rede privada."""

import http.client
import ipaddress
from pathlib import Path
import socket
import ssl
import tempfile
import time
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

from .extracao import Extracao, MAX_TEXTO, TextoHTML, extrair

MAX_LINK = 2 * 1024 * 1024


def normalizar_url(url):
    url = url.strip()
    partes = urlsplit(url)
    if partes.scheme.lower() not in {'https', 'http'} or not partes.hostname:
        raise ValueError('Use um link publico http:// ou https://.')
    if partes.username is not None or partes.password is not None:
        raise ValueError('Links com usuario/senha nao sao permitidos.')
    try:
        porta = partes.port
        host = partes.hostname.encode('idna').decode('ascii').lower()
    except (ValueError, UnicodeError) as exc:
        raise ValueError('Link invalido.') from exc
    if porta not in {None, 80 if partes.scheme.lower() == 'http' else 443}:
        raise ValueError('Use a porta padrao HTTP ou HTTPS.')
    if any(ord(c) < 32 or c.isspace() for c in url):
        raise ValueError('Link contem espacos ou caracteres invalidos.')
    host = f'[{host}]' if ':' in host else host
    caminho = quote(partes.path or '/',safe="/%:@!$&'()*+,;=-._~")
    query = quote(partes.query,safe="%:/?@!$&'()*+,;=-._~")
    resultado = urlunsplit((partes.scheme.lower(), host, caminho, query, ''))
    if len(resultado) > 2048:
        raise ValueError('Link excede 2048 caracteres.')
    return resultado


def endereco_publico(host, porta):
    enderecos = socket.getaddrinfo(host, porta, type=socket.SOCK_STREAM)
    if not enderecos:
        raise ValueError('Dominio nao encontrado.')
    ips = [e[4][0] for e in enderecos]
    if any(not ipaddress.ip_address(ip).is_global for ip in ips):
        raise ValueError('A biblioteca aceita apenas links da internet publica.')
    return ips[0]


class ConexaoPublica(http.client.HTTPConnection):
    """Fixa o IP validado para evitar uma segunda resolucao DNS ao conectar."""
    def __init__(self, host, ip, porta, https):
        super().__init__(host, porta, timeout=10)
        self.ip, self.https = ip, https

    def connect(self):
        self.sock = socket.create_connection((self.ip, self.port), timeout=self.timeout)
        if self.https:
            self.sock = ssl.create_default_context().wrap_socket(self.sock, server_hostname=self.host)


def baixar_link(url):
    inicio = time.monotonic()
    for _ in range(5):
        url = normalizar_url(url)
        p = urlsplit(url)
        porta = 443 if p.scheme == 'https' else 80
        ip = endereco_publico(p.hostname, porta)
        conexao = ConexaoPublica(p.hostname, ip, porta, p.scheme == 'https')
        try:
            conexao.request('GET', urlunsplit(('', '', p.path, p.query, '')),
                            headers={'User-Agent': 'CadernoMat/1.0', 'Accept-Encoding': 'identity'})
            resposta = conexao.getresponse()
            if resposta.status in {301, 302, 303, 307, 308}:
                destino = resposta.getheader('Location')
                if not destino: raise ValueError('Redirecionamento sem destino.')
                url = urljoin(url, destino)
                continue
            if resposta.status != 200:
                raise ValueError(f'Link indisponivel (HTTP {resposta.status}).')
            tamanho = resposta.getheader('Content-Length')
            if tamanho and int(tamanho) > MAX_LINK:
                raise ValueError('Link excede o limite de 2 MiB.')
            partes, total = [], 0
            while True:
                if time.monotonic() - inicio > 30:
                    raise ValueError('Link excedeu o tempo de leitura de 30 segundos.')
                bloco = resposta.read(min(65536, MAX_LINK+1-total))
                if not bloco: break
                total += len(bloco)
                if total > MAX_LINK: raise ValueError('Link excede o limite de 2 MiB.')
                partes.append(bloco)
            return b''.join(partes), resposta.getheader('Content-Type', ''), url
        finally:
            conexao.close()
    raise ValueError('Link tem redirecionamentos demais.')


def extrair_link(url):
    try:
        bruto, mime, destino = baixar_link(url)
        if 'application/pdf' in mime or bruto.startswith(b'%PDF-'):
            with tempfile.TemporaryDirectory(prefix='cadernomat-link-') as pasta:
                pdf = Path(pasta)/'link.pdf'
                pdf.write_bytes(bruto)
                resultado = extrair(pdf, 'link.pdf')
            resultado.aviso = (resultado.aviso + ' Copia textual do PDF no link; original nao armazenado.').strip()
        elif any(t in mime for t in ('text/', 'application/json', 'application/xhtml+xml')):
            texto = bruto.decode('utf-8-sig', errors='replace')
            if 'html' in mime:
                leitor = TextoHTML()
                leitor.feed(texto)
                texto = leitor.texto()
            truncado = len(texto) > MAX_TEXTO
            resultado = Extracao([(1, texto.strip()[:MAX_TEXTO])] if texto.strip() else [],
                                'parcial' if truncado else ('pronto' if texto.strip() else 'sem_texto'),
                                'Conteudo truncado.' if truncado else '', 'link textual')
        else:
            resultado = Extracao([], 'nao_suportado', 'Link nao fornece HTML, texto ou PDF. Paginas com login/JavaScript nao sao interpretadas.')
        resultado.aviso = (resultado.aviso + (f' Redirecionado para {destino}.' if destino != url else '')).strip()
        return resultado, len(bruto)
    except ValueError as exc:
        return Extracao([], 'erro', str(exc)), 0
    except Exception:
        return Extracao([], 'erro', 'Nao foi possivel acessar o link. Confira a internet e se a pagina e publica.'), 0
