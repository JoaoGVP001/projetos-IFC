#!/usr/bin/env bash
# Aceite real da interface Qt com pesos instalados e rede somente loopback.
set -euo pipefail
integracao_repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "${1:-}" != '--namespace' ]]; then
    exec unshare --user --map-current-user --keep-caps --net "$integracao_repo/scripts/testar_integracao_offline_linux.sh" --namespace "$@"
fi
shift
ip link set lo up
integracao_base="${XDG_DATA_HOME:-$HOME/.local/share}/CadernoMat/ia-local"
integracao_runtime="$(cat -- "$integracao_base/runtime-path.txt")"
if [[ "$integracao_runtime" != "$integracao_base"/runtimes/*/bin/ollama || ! -x "$integracao_runtime" ]]; then
    echo 'Prepare o runtime do piloto antes do aceite real.'
    exit 1
fi
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_MODELS="$integracao_base/models"
export OLLAMA_NO_CLOUD=1 OLLAMA_NUM_PARALLEL=1 OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_CONTEXT_LENGTH=4096 OLLAMA_KEEP_ALIVE=2m
"$integracao_runtime" serve >"$integracao_base/servidor-aceite.log" 2>&1 &
integracao_pid=$!
trap 'kill "$integracao_pid" 2>/dev/null || true; wait "$integracao_pid" 2>/dev/null || true' EXIT
for ((integracao_tentativa=0; integracao_tentativa<30; integracao_tentativa++)); do
    if curl --noproxy '*' -fsS --max-time 1 http://127.0.0.1:11434/api/version >/dev/null 2>&1; then break; fi
    sleep 1
done
export CADERNOMAT_REAL_LOCAL=1
if [[ "${1:-}" != '--so-estudo' ]]; then
    cd -- "$integracao_repo/frontend"
    node tests/local.mjs
fi
cd -- "$integracao_repo"
.venv/bin/python tests/aceite_estudo_local.py
