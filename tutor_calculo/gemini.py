"""Cliente REST do Gemini. A faixa de cobranca e definida pelo projeto Google."""

import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def consultar(chave: str, modelo: str, pergunta: str, instrucoes: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", modelo):
        raise ValueError("Identificador de modelo Gemini invalido.")
    dados = {
        "contents": [{"role": "user", "parts": [{"text": pergunta}]}],
        "systemInstruction": {"parts": [{"text": instrucoes}]},
        "generationConfig": {"maxOutputTokens": 4096},
    }
    requisicao = Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
        data=json.dumps(dados).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": chave},
        method="POST",
    )
    try:
        with urlopen(requisicao, timeout=60) as resposta:
            resultado = json.load(resposta)
    except HTTPError as exc:
        mensagens = {
            400: "O Gemini recusou a consulta. Confira a chave, o modelo e a disponibilidade da faixa gratuita no seu pais.",
            401: "O Gemini recusou a chave. Confira Configurar IA.",
            403: "Sua chave nao tem acesso ao Gemini. Confira o projeto e as permissoes no Google AI Studio.",
            404: "Modelo Gemini indisponivel. Escolha outro modelo disponivel para sua chave.",
            429: "Cota do Gemini atingida. Aguarde a renovacao do limite gratuito ou confira as cotas do seu projeto no AI Studio. O aplicativo nao ativa cobranca automaticamente.",
        }
        raise RuntimeError(mensagens.get(exc.code, f"O Gemini nao concluiu a consulta (HTTP {exc.code}). Tente novamente mais tarde.")) from exc
    except TimeoutError as exc:
        raise RuntimeError("O Gemini demorou mais de 60 segundos. Tente novamente.") from exc
    except URLError as exc:
        raise RuntimeError("Nao foi possivel conectar ao Gemini. Confira sua conexao com a internet.") from exc
    except (ValueError, UnicodeError) as exc:
        raise RuntimeError("O Gemini retornou uma resposta invalida. Tente novamente.") from exc

    candidatos = resultado.get("candidates") or []
    if not candidatos:
        if resultado.get("promptFeedback", {}).get("blockReason"):
            raise RuntimeError("O Gemini bloqueou esta pergunta. Reformule o enunciado de estudo.")
        raise RuntimeError("O Gemini nao retornou uma explicacao em texto.")
    candidato = candidatos[0]
    fim = candidato.get("finishReason", "")
    if fim in {"SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII"}:
        raise RuntimeError("O Gemini bloqueou a resposta. Reformule o enunciado de estudo.")
    partes = candidato.get("content", {}).get("parts", [])
    texto = "\n".join(p.get("text", "") for p in partes if not p.get("thought")).strip()
    if not texto:
        raise RuntimeError("O Gemini nao retornou uma explicacao em texto. Tente uma pergunta mais curta.")
    if fim == "MAX_TOKENS":
        texto += "\n\n[Resposta interrompida pelo limite da consulta. Divida o exercicio em etapas.]"
    elif fim not in {"", "STOP"}:
        raise RuntimeError("O Gemini nao concluiu a resposta. Tente novamente.")
    return texto
