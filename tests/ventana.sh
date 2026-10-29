#!/bin/sh
# Inferencia con su ventana en FS-UAE, contra el OpenRouter falso, con capturas.
#
#   tests/ventana.sh DASH_DIR "pregunta" captura.png [segundos...]
#   LINEA=0 tests/ventana.sh ...     # la vista sube a esa línea después de la respuesta
#   PERMISO=Si tests/ventana.sh ...  # contesta solo a los permisos (Si, No o Siempre), a los tres segundos
#
# DASH_DIR: el worktree de Dash 2.0 que compila (./dash y tools/emu_run.py). La pregunta se manda al abrir
# (ENV:INFERENCIA_PRUEBA, en Latin-1 como en el Amiga) y el programa se cierra solo 15 segundos después de la
# respuesta. Una captura por cada segundo dado (por defecto 8): captura-8.png...
set -e
dash=$1; pregunta=$2; png=$3; shift 3
[ $# -gt 0 ] || set -- 8
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'kill $srv 2>/dev/null; rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Inferencia"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
{
  echo "C:MakeDir ENV:Inferencia"
  echo "C:SetEnv Inferencia/url http://127.0.0.1:40900/api/v1/chat/completions"
  echo "C:SetEnv Inferencia/clave clave-falsa"
  echo "C:SetEnv Inferencia/modelo modelo/prueba"
  echo "SetEnv INFERENCIA_PRUEBA @DH0:Prueba/pregunta"
  [ -z "$LINEA" ] || echo "SetEnv INFERENCIA_PRUEBA_LINEA $LINEA"
  [ -z "$PERMISO" ] || echo "SetEnv INFERENCIA_PRUEBA_PERMISO $PERMISO"
} >> "$tmp/sys/S/Startup-Extra"
# la pregunta en Latin-1, como la escribiría el Amiga (emu_run escribe el Startup-Sequence en UTF-8)
mkdir -p "$tmp/sys/Prueba"
printf '%s' "$pregunta" | iconv -f utf-8 -t latin1 > "$tmp/sys/Prueba/pregunta"
python3 "$aqui/tests/servidor_falso.py" 40900 2>/dev/null &
srv=$!
sleep 1
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
python3 "$dash/tools/emu_run.py" --timeout ${TIEMPO:-150} --system "$tmp/sys" --set bsdsocket_library=1 $shots "$tmp/Inferencia"
