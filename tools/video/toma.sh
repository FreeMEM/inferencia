#!/bin/sh
# toma.sh DASH_DIR ESCENA CARPETA [MODELO]: Amiberry desde cero con el sistema del vídeo y la escena grabada
# (forja o lightwave). Xvfb :78 en marcha; Ollama en Pegaso.
set -e
S=$(cd "$(dirname "$0")" && pwd)
cd "$S"
python3 -c "import ventanas; from amiberry import orden; orden('QUIT')" 2>/dev/null || true
while pgrep -x amiberry > /dev/null; do sleep 1; done
dash=$1; shift
"$S/preparar.sh" "$dash" "${3:-qwen3-coder-32k}" "${URL:?URL del servidor con formato de OpenAI, p. ej. http://pc-de-casa:11434/v1/chat/completions}" > /dev/null
"$S/arrancar.sh"
python3 -c "
import ventanas, agente, amiga, time
t = time.time()
while time.time() - t < 180:
    try:
        agente.buzon(); break
    except Exception:
        amiga._ib = None; time.sleep(2)
time.sleep(8)"
rm -rf "$2"
python3 guion.py "$1" "$2"
