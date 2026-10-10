#!/usr/bin/env bash
set -e
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ! -x .venv/bin/python ]]; then
    echo 'Prepare o ambiente: python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt'
    exit 1
fi
# Aceita um runtime Tkinter local neste PC, sem exigir instalacao como administrador.
if [[ -d .runtime/usr/lib ]]; then
    versao="$(.venv/bin/python -c 'import sys; print(f"python{sys.version_info.major}.{sys.version_info.minor}")')"
    export PYTHONPATH="$PWD/.runtime/usr/lib/$versao:$PWD/.runtime/usr/lib/$versao/lib-dynload${PYTHONPATH:+:$PYTHONPATH}"
    export LD_LIBRARY_PATH="$PWD/.runtime/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    export TK_LIBRARY="$PWD/.runtime/usr/share/tcltk/tk8.6"
fi
if ! .venv/bin/python -c 'import tkinter' 2>/dev/null; then
    echo 'Falta o Tkinter. No Ubuntu, instale python3-tk e tente novamente.'
    exit 1
fi
exec .venv/bin/python -m tutor_calculo.desktop
