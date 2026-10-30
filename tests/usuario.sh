#!/bin/sh
# Inferencia con un usuario de prueba (un programa de Dash que la maneja por input.device o por ARexx), en FS-UAE
# contra el OpenRouter falso. Enseña lo que anotó el usuario en DH0:Prueba/usuario.txt; si todo fue bien, acaba
# con "TODO BIEN".
#
#   tests/usuario.sh DASH_DIR tests/clics.dash [captura.png segundos...]
#   PERMISO=Si tests/usuario.sh ...   # Inferencia contesta sola a los permisos (Si, No o Siempre)
#   FORJA=~/Projects/forja tests/usuario.sh ...   # con Forja abierta a la vez (DH0:Prueba/juego)
#   SIN_PERMISO="entorno,orden echo" tests/usuario.sh ...   # ENV:Inferencia/sin_permiso
#   OPCIONES=--memcheck tests/usuario.sh ...   # Inferencia compilada con esas opciones de ./dash
#   PROVEEDOR=anthropic URL=http://127.0.0.1:40900/v1/messages tests/usuario.sh ...   # otro proveedor
set -e
dash=$1; usuario=$2; shift 2
png=""
if [ $# -gt 0 ]; then png=$1; shift; fi
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
srv=""
trap '[ -z "$srv" ] || kill $srv 2>/dev/null; rm -rf "$tmp"' EXIT
"$dash/dash" $OPCIONES "$aqui/src/main.dash" -o "$tmp/Inferencia"
cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
mkdir -p "$tmp/sys/Prueba"
[ ! -d "$aqui/tests/prueba" ] || cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
"$dash/dash" "$usuario" -o "$tmp/sys/Prueba/Usuario"
if [ -n "$FORJA" ]; then
  # Forja a la vez, con su proyecto de prueba (tests/prueba/juego de Forja)
  "$dash/dash" "$FORJA/src/main.dash" -o "$tmp/sys/Prueba/Forja"
  cp -r "$FORJA/tests/prueba/juego" "$tmp/sys/Prueba/"
fi
{
  echo "C:MakeDir ENV:Inferencia"
  echo "C:SetEnv Inferencia/url ${URL:-http://127.0.0.1:40900/api/v1/chat/completions}"
  [ -z "$PROVEEDOR" ] || echo "C:SetEnv Inferencia/proveedor $PROVEEDOR"
  echo "C:SetEnv Inferencia/clave clave-falsa"
  echo "C:SetEnv Inferencia/modelo modelo/prueba"
  echo "SetEnv INFERENCIA_SONDA 1"
  [ -z "$PERMISO" ] || echo "SetEnv INFERENCIA_PRUEBA_PERMISO $PERMISO"
  [ -z "$SIN_PERMISO" ] || echo "SetEnv Inferencia/sin_permiso \"$SIN_PERMISO\""
  if [ -n "$FORJA" ]; then
    echo "SetEnv FORJA_SONDA 1"
    echo "Run >NIL: DH0:Prueba/Forja DH0:Prueba/juego/main.dash"
  fi
  echo "Run >NIL: DH0:Prueba/Usuario"
} >> "$tmp/sys/S/Startup-Extra"
python3 "$aqui/tests/servidor_falso.py" 40900 2>/dev/null &
srv=$!
sleep 1
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
python3 "$dash/tools/emu_run.py" --timeout ${TIEMPO:-240} --system "$tmp/sys" --set bsdsocket_library=1 --keep "$tmp/disco" $shots "$tmp/Inferencia" || true
iconv -f latin1 -t utf-8 "$tmp/disco/Prueba/usuario.txt" 2>/dev/null || echo "FALLO: no hay registro"
