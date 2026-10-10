"""Configuracao e consultas ao instrutor pela Responses API."""

import os
from pathlib import Path

from dotenv import dotenv_values, set_key

from .prompts import INSTRUCOES

ARQUIVO_ENV = Path(__file__).resolve().parents[1] / ".env"
MODELO_PADRAO = "gpt-6-astra"


def configuracao() -> tuple[str, str]:
    valores = dotenv_values(ARQUIVO_ENV)
    chave = os.environ.get("OPENAI_API_KEY", valores.get("OPENAI_API_KEY") or "").strip()
    modelo = os.environ.get("OPENAI_MODEL", valores.get("OPENAI_MODEL") or MODELO_PADRAO).strip()
    return chave, modelo or MODELO_PADRAO


def salvar_configuracao(chave: str, modelo: str = MODELO_PADRAO) -> None:
    chave = chave.strip()
    modelo = modelo.strip()
    if not chave or "\n" in chave or "\r" in chave:
        raise ValueError("Informe uma chave da API valida.")
    if not modelo or any(c.isspace() for c in modelo):
        raise ValueError("Informe o identificador do modelo sem espacos.")
    ARQUIVO_ENV.touch(mode=0o600, exist_ok=True)
    ARQUIVO_ENV.chmod(0o600)
    set_key(str(ARQUIVO_ENV), "OPENAI_API_KEY", chave)
    set_key(str(ARQUIVO_ENV), "OPENAI_MODEL", modelo)


def perguntar(pergunta: str, modo: str = "Resolver") -> str:
    if not pergunta.strip():
        raise ValueError("Digite um enunciado ou uma duvida.")
    tarefas = {
        "Resolver": "Interprete o enunciado e resolva o exercicio passo a passo.",
        "Explicar": "Explique o conteudo com intuicao, um exemplo e uma pergunta de verificacao.",
        "Corrigir": "Analise a tentativa do aluno, indique o primeiro erro e ensine como continuar. Se a tentativa nao foi fornecida, peca que o aluno a envie.",
    }
    if modo not in tarefas:
        raise ValueError("Modo de estudo invalido.")
    chave, modelo = configuracao()
    if not chave:
        raise RuntimeError("A IA ainda nao esta configurada. Use Configurar IA ou defina OPENAI_API_KEY no arquivo .env do projeto.")

    try:
        import openai
    except ImportError as exc:
        raise RuntimeError("Instale as dependencias com: pip install -r requirements.txt") from exc

    try:
        with openai.OpenAI(api_key=chave, timeout=60.0, max_retries=0) as cliente:
            resposta = cliente.responses.create(
                model=modelo,
                instructions=INSTRUCOES + "\nTarefa desta consulta: " + tarefas[modo],
                input=pergunta,
                max_output_tokens=4096,
                store=False,
            )
    except openai.AuthenticationError as exc:
        raise RuntimeError("A OpenAI recusou a chave. Confira a chave em Configurar IA.") from exc
    except openai.PermissionDeniedError as exc:
        raise RuntimeError("Sua chave nao tem permissao para esta consulta. Confira o projeto e o acesso ao modelo na OpenAI.") from exc
    except openai.NotFoundError as exc:
        raise RuntimeError("Modelo indisponivel para sua conta. Confira OPENAI_MODEL ou altere o modelo em Configurar IA.") from exc
    except openai.RateLimitError as exc:
        raise RuntimeError("Limite de uso ou creditos da API atingido. Confira o saldo e os limites na plataforma OpenAI e tente novamente.") from exc
    except openai.APITimeoutError as exc:
        raise RuntimeError("A consulta demorou mais de 60 segundos. Tente novamente.") from exc
    except openai.APIConnectionError as exc:
        raise RuntimeError("Nao foi possivel conectar a OpenAI. Confira sua conexao com a internet.") from exc
    except openai.APIStatusError as exc:
        raise RuntimeError(f"A OpenAI nao concluiu a consulta (HTTP {exc.status_code}). Confira a configuracao ou tente novamente mais tarde.") from exc
    except openai.APIError as exc:
        raise RuntimeError("Nao foi possivel consultar a OpenAI. Tente novamente.") from exc

    if getattr(resposta, "status", None) in {"failed", "cancelled"}:
        raise RuntimeError("A OpenAI nao concluiu a resposta. Tente novamente.")
    texto = resposta.output_text.strip()
    if not texto:
        raise RuntimeError("A API nao retornou uma explicacao em texto. Tente uma pergunta mais curta.")
    if getattr(resposta, "status", None) == "incomplete":
        texto += "\n\n[Resposta interrompida pelo limite da consulta. Divida o exercicio em etapas e tente novamente.]"
    return texto
