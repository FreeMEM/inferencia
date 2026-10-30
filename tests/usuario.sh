#!/bin/sh
# Inferencia con un usuario de prueba (un programa de Dash que la maneja por input.device o por ARexx), en FS-UAE
# contra el OpenRouter falso. Enseña lo que anotó el usuario en DH0:Prueba/usuario.txt; si todo fue bien, acaba
# con "TODO BIEN".
#
#   tests/usuario.sh DASH_DIR tests/clics.dash [captura.png segundos...]
#   PERMISO=Si tests/usuario.sh ...   # Inferencia contesta sola a los permisos (Si, No o Siempre)
set -e
dash=$1; usuario=$2; shift 2
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
srv=""
trap '[ -z "$srv" ] || kill $srv 2>/dev/null; rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Inferencia"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
[ ! -d "$aqui/tests/prueba" ] || cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
"$dash/dash" "$usuario" -o "$tmp/sys/Prueba/Usuario"
{
  echo "C:MakeDir ENV:Inferencia"
  echo "C:SetEnv Inferencia/url http://127.0.0.1:40900/api/v1/chat/completions"
  echo "C:SetEnv Inferencia/clave clave-falsa"
  echo "C:SetEnv Inferencia/modelo modelo/prueba"
  echo "SetEnv INFERENCIA_SONDA 1"
  [ -z "$PERMISO" ] || echo "SetEnv INFERENCIA_PRUEBA_PERMISO $PERMISO"
  echo "Run >NIL: DH0:Prueba/Usuario"
} >> "$tmp/sys/S/Startup-Extra"
python3 "$aqui/tests/servidor_falso.py" 40900 2>/dev/null &
srv=$!
sleep 1
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
python3 "$dash/tools/emu_run.py" --timeout ${TIEMPO:-240} --system "$tmp/sys" --set bsdsocket_library=1 --keep "$tmp/disco" $shots "$tmp/Inferencia" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/usuario.txt" 2>/dev/null || echo "FALLO: no hay registro"
