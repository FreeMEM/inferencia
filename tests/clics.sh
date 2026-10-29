#!/bin/sh
# Inferencia con un usuario de prueba (tests/clics.dash) que escribe, pulsa los botones de permiso y comprueba
# los ficheros, en FS-UAE contra el OpenRouter falso (guion tests/guiones/ficheros.json).
#
#   tests/clics.sh DASH_DIR [captura.png segundos...]
#
# Enseña lo que anotó el usuario de prueba; acaba con "TODO BIEN" si todo fue bien.
set -e
dash=$1; shift
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'kill $srv 2>/dev/null; rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Inferencia"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
"$dash/dash" "$aqui/tests/clics.dash" -o "$tmp/sys/Prueba/Clics"
{
  echo "C:MakeDir ENV:Inferencia"
  echo "C:SetEnv Inferencia/url http://127.0.0.1:40900/api/v1/chat/completions"
  echo "C:SetEnv Inferencia/clave clave-falsa"
  echo "C:SetEnv Inferencia/modelo modelo/prueba"
  echo "SetEnv INFERENCIA_SONDA 1"
  echo "Run >NIL: DH0:Prueba/Clics"
} >> "$tmp/sys/S/Startup-Extra"
python3 "$aqui/tests/servidor_falso.py" 40900 2>/dev/null &
srv=$!
sleep 1
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
python3 "$dash/tools/emu_run.py" --timeout ${TIEMPO:-240} --system "$tmp/sys" --set bsdsocket_library=1 --keep "$tmp/disco" $shots "$tmp/Inferencia" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/clics.txt" 2>/dev/null || echo "FALLO: no hay registro"
