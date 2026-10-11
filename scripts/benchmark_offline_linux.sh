#!/usr/bin/env bash
# Teste sem interface de rede externa; não altera a rede dos outros aplicativos.
set -euo pipefail
piloto_repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "${1:-}" != '--namespace' ]]; then
    export CADERNOMAT_NET_ORIGINAL="$(readlink /proc/self/ns/net)"
    exec unshare --user --map-root-user --net "$piloto_repo/scripts/benchmark_offline_linux.sh" --namespace "$@"
fi
shift
ip link set lo up
cd -- "$piloto_repo"
piloto_base="${XDG_DATA_HOME:-$HOME/.local/share}/CadernoMat/ia-local"
piloto_runtime="$(cat -- "$piloto_base/runtime-path.txt")"
if [[ "$piloto_runtime" != "$piloto_base"/runtimes/*/bin/ollama || ! -x "$piloto_runtime" ]]; then
    echo 'Runtime do piloto inválido.'
    exit 1
fi
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_MODELS="$piloto_base/models"
export OLLAMA_NO_CLOUD=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_CONTEXT_LENGTH=4096
export OLLAMA_KEEP_ALIVE=2m
"$piloto_runtime" serve >"$piloto_base/servidor-offline.log" 2>&1 &
piloto_pid=$!
trap 'kill "$piloto_pid" 2>/dev/null || true; wait "$piloto_pid" 2>/dev/null || true' EXIT
for ((piloto_tentativa=0; piloto_tentativa<30; piloto_tentativa++)); do
    if curl --noproxy '*' -fsS --max-time 1 http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
        break
    fi
    sleep 1
done
.venv/bin/python -m tutor_calculo.piloto_local --benchmark "$@"
