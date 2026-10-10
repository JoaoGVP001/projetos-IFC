"""Configuracao e consultas ao instrutor pela Responses API."""

import os
import re
from pathlib import Path

from dotenv import dotenv_values, set_key

from .prompts import INSTRUCOES

ARQUIVO_ENV = Path(__file__).resolve().parents[1] / ".env"
MODELO_PADRAO = "gpt-6-astra"


PROVEDORES = {"openai": ("OPENAI", MODELO_PADRAO), "gemini": ("GEMINI", "gemini-3.8-flash")}


def provedor_ativo() -> str:
    valores = dotenv_values(ARQUIVO_ENV)
    provedor = os.environ.get("AI_PROVIDER", valores.get("AI_PROVIDER") or "openai").strip().lower()
    if provedor not in PROVEDORES:
        raise ValueError("Provedor invalido. Escolha Gemini ou OpenAI em Configurar IA.")
    return provedor


def configuracao(provedor: str | None = None) -> tuple[str, str]:
    provedor = provedor or provedor_ativo()
    if provedor not in PROVEDORES:
        raise ValueError("Provedor invalido.")
    prefixo, padrao = PROVEDORES[provedor]
    valores = dotenv_values(ARQUIVO_ENV)
    chave = os.environ.get(prefixo + "_API_KEY", valores.get(prefixo + "_API_KEY") or "").strip()
    modelo = os.environ.get(prefixo + "_MODEL", valores.get(prefixo + "_MODEL") or padrao).strip()
    return chave, modelo or padrao


def salvar_configuracao(chave: str, modelo: str = MODELO_PADRAO, provedor: str = "openai") -> None:
    if provedor not in PROVEDORES:
        raise ValueError("Provedor invalido.")
    chave = chave.strip()
    modelo = modelo.strip()
    if not chave:
        chave = configuracao(provedor)[0]
    if not chave or any(c.isspace() for c in chave):
        raise ValueError("Informe uma chave da API valida para o servico escolhido.")
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", modelo):
        raise ValueError("Informe o identificador do modelo sem espacos ou barras.")
    prefixo, _ = PROVEDORES[provedor]
    ARQUIVO_ENV.touch(mode=0o600, exist_ok=True)
    ARQUIVO_ENV.chmod(0o600)
    set_key(str(ARQUIVO_ENV), prefixo + "_API_KEY", chave)
    set_key(str(ARQUIVO_ENV), prefixo + "_MODEL", modelo)
    set_key(str(ARQUIVO_ENV), "AI_PROVIDER", provedor)


def perguntar(pergunta: str, modo: str = "Resolver", historico: list[dict] | None = None) -> str:
    if not pergunta.strip():
        raise ValueError("Digite um enunciado ou uma duvida.")
    tarefas = {
        "Resolver": "Interprete o enunciado e resolva o exercicio passo a passo.",
        "Explicar": "Explique o conteudo com intuicao, um exemplo e uma pergunta de verificacao.",
        "Corrigir": "Analise a tentativa do aluno, indique o primeiro erro e ensine como continuar. Se a tentativa nao foi fornecida, peca que o aluno a envie.",
    }
    if modo not in tarefas:
        raise ValueError("Modo de estudo invalido.")
    provedor = provedor_ativo()
    chave, modelo = configuracao()
    if not chave:
        raise RuntimeError(f"A IA {provedor} ainda nao esta configurada. Use Configurar IA ou defina {PROVEDORES[provedor][0]}_API_KEY no arquivo .env.")

    contexto = limitar_contexto(historico or [])
    entrada = contexto + [{"role": "user", "content": pergunta}] if contexto else pergunta
    instrucoes = INSTRUCOES + "\nTarefa desta consulta: " + tarefas[modo]
    if provedor == "gemini":
        from .gemini import consultar
        return consultar(chave, modelo, pergunta, instrucoes, historico=contexto) if contexto else consultar(chave, modelo, pergunta, instrucoes)

    try:
        import openai
    except ImportError as exc:
        raise RuntimeError("Instale as dependencias com: pip install -r requirements.txt") from exc

    try:
        with openai.OpenAI(api_key=chave, timeout=60.0, max_retries=0) as cliente:
            resposta = cliente.responses.create(
                model=modelo,
                instructions=instrucoes,
                input=entrada,
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


def limitar_contexto(mensagens: list[dict], limite: int = 16000) -> list[dict]:
    """Preserva pares recentes completos; erros e pares incompletos ficam fora."""
    pares = []
    usuario = None
    for m in mensagens:
        if m.get("estado", "ok") != "ok":
            usuario = None
            continue
        papel = m.get("papel", m.get("role"))
        texto = m.get("texto", m.get("content", ""))
        if papel == "user":
            usuario = {"role": "user", "content": texto}
        elif papel == "assistant" and usuario:
            pares.append([usuario, {"role": "assistant", "content": texto}])
            usuario = None
    contexto = []
    tamanho = 0
    for par in reversed(pares[-10:]):
        custo = sum(len(m["content"]) for m in par)
        if tamanho + custo > limite:
            break
        contexto = par + contexto
        tamanho += custo
    return contexto
