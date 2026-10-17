#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -x .venv/bin/python ]]; then
    echo 'Prepare o ambiente Python do CadernoMat antes de abrir o piloto.'
    exit 1
fi
piloto_base="${XDG_DATA_HOME:-$HOME/.local/share}/CadernoMat/ia-local"
if [[ ! -f "$piloto_base/runtime-path.txt" ]]; then
    echo 'Runtime do piloto não encontrado. Consulte docs/PILOTO_LOCAL.md.'
    exit 1
fi
piloto_runtime="$(cat -- "$piloto_base/runtime-path.txt")"
if [[ "$piloto_runtime" != "$piloto_base"/runtimes/*/bin/ollama || ! -x "$piloto_runtime" ]]; then
    echo 'Caminho do runtime inválido.'
    exit 1
fi
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_MODELS="$piloto_base/models"
export OLLAMA_NO_CLOUD=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_CONTEXT_LENGTH=4096
export OLLAMA_KEEP_ALIVE=2m
if ! curl --noproxy '*' -fsS --max-time 2 http://127.0.0.1:11434/api/version >/dev/null; then
    "$piloto_runtime" serve >>"$piloto_base/servidor.log" 2>&1 &
    echo "$!" >"$piloto_base/servidor.pid"
    for ((piloto_tentativa=0; piloto_tentativa<30; piloto_tentativa++)); do
        if curl --noproxy '*' -fsS --max-time 1 http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
            break
        fi
        sleep 1
    done
fi
exec .venv/bin/python -m tutor_calculo.piloto_local --chat "$@"
