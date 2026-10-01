"""Acesso a explicacoes abertas pela API da OpenAI."""

import os

from .prompts import INSTRUCOES


def perguntar(pergunta: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Configure OPENAI_API_KEY para fazer perguntas abertas.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Instale as dependencias com: pip install -r tutor_calculo/requirements.txt") from exc

    try:
        resposta = OpenAI().responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-6-astra"),
            instructions=INSTRUCOES,
            input=pergunta,
        )
    except Exception as exc:
        raise RuntimeError(f"Nao foi possivel consultar a API: {exc}") from exc

    if not resposta.output_text:
        raise RuntimeError("A API nao retornou uma explicacao em texto.")
    return resposta.output_text
