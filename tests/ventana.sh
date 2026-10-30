#!/bin/sh
# Inferencia con su ventana en FS-UAE, contra el OpenRouter falso, con capturas.
#
#   tests/ventana.sh DASH_DIR "pregunta" captura.png [segundos...]
#   LINEA=0 tests/ventana.sh ...     # la vista sube a esa línea después de la respuesta
#   PERMISO=Si tests/ventana.sh ...  # contesta solo a los permisos (Si, No o Siempre), a los tres segundos
#   TIEMPO=s tests/ventana.sh ...    # el tope del emulador (150 s por defecto)
#   RTG=1 tests/ventana.sh ...       # en AmigaOS 3.2 con tarjeta gráfica de 256 colores (sys32rtg8): se ven los colores
#   CATALOGOS=1 tests/ventana.sh ...   # con build/Catalogs (tools/paquete.py o catalogo.py): sale en inglés
#   REAL=modelo tests/ventana.sh ... # contra OpenRouter de verdad, con la clave de ~/.config/inferencia/openrouter
#
# DASH_DIR: el worktree de Dash 2.0 que compila (./dash y tools/emu_run.py). La pregunta se manda al abrir
# (ENV:INFERENCIA_PRUEBA, en Latin-1 como en el Amiga) y el programa se cierra solo 15 segundos después de la
# respuesta. Una captura por cada segundo dado (por defecto 8): captura-8.png... En el cajón DH0:Prueba están la
# pregunta y lo que haya en tests/prueba/.
set -e
dash=$1; pregunta=$2; png=$3; shift 3
[ $# -gt 0 ] || set -- 8
aqui=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
srv=""
trap '[ -z "$srv" ] || kill $srv 2>/dev/null; rm -rf "$tmp"' EXIT
"$dash/dash" "$aqui/src/main.dash" -o "$tmp/Inferencia"
maquina=""
if [ -n "$RTG" ]; then
  cp -r "$HOME/.cache/dash-emu/sys32rtg8" "$tmp/sys"
  export DASH_EMU_SYS_32_RTG="$tmp/sys"
  export DASH_KICKSTART_32="${DASH_KICKSTART_32:-$HOME/Descargas/Telegram Desktop/Kickstart v3.2.3 A1200.47.115_Pack_noSCSI.rom}"
  maquina="--machine rtg"
else
  cp -r "$HOME/.cache/dash-emu/sys31muisslweb" "$tmp/sys"
fi
cpu=""
echo "C:MakeDir ENV:Inferencia" >> "$tmp/sys/S/Startup-Extra"
if [ -n "$REAL" ]; then
  # la clave va solo a esta copia temporal del sistema, que se borra al acabar; nunca se imprime
  clave=$(cat "$HOME/.config/inferencia/openrouter")
  echo "C:SetEnv Inferencia/clave $clave" >> "$tmp/sys/S/Startup-Extra"
  unset clave
  echo "C:SetEnv Inferencia/modelo $REAL" >> "$tmp/sys/S/Startup-Extra"
  # el saludo de TLS solo acaba a tiempo con la CPU emulada al máximo
  cpu="--set uae_cpu_speed=max --set uae_cpu_compatible=false --set jit_compiler=1"
else
  {
    echo "C:SetEnv Inferencia/url http://127.0.0.1:40900/api/v1/chat/completions"
    echo "C:SetEnv Inferencia/clave clave-falsa"
    echo "C:SetEnv Inferencia/modelo modelo/prueba"
  } >> "$tmp/sys/S/Startup-Extra"
fi
{
  echo "SetEnv INFERENCIA_PRUEBA @DH0:Prueba/pregunta"
  [ -z "$LINEA" ] || echo "SetEnv INFERENCIA_PRUEBA_LINEA $LINEA"
  [ -z "$PERMISO" ] || echo "SetEnv INFERENCIA_PRUEBA_PERMISO $PERMISO"
} >> "$tmp/sys/S/Startup-Extra"
# la pregunta en Latin-1, como la escribiría el Amiga (emu_run escribe el Startup-Sequence en UTF-8)
mkdir -p "$tmp/sys/Prueba"
# con CATALOGOS=1, el catálogo inglés junto al programa (PROGDIR:Catalogs; el sistema emulado está en inglés)
[ -z "$CATALOGOS" ] || cp -r "$aqui/build/Catalogs" "$tmp/sys/Catalogs"
[ ! -d "$aqui/tests/prueba" ] || cp -r "$aqui/tests/prueba/." "$tmp/sys/Prueba/"
printf '%s' "$pregunta" | iconv -f utf-8 -t latin1 > "$tmp/sys/Prueba/pregunta"
if [ -z "$REAL" ]; then
  python3 "$aqui/tests/servidor_falso.py" 40900 2>/dev/null &
  srv=$!
  sleep 1
fi
shots=""
for s in "$@"; do shots="$shots --screenshot $s ${png%.png}-$s.png"; done
python3 "$dash/tools/emu_run.py" --timeout ${TIEMPO:-150} --system "$tmp/sys" --set bsdsocket_library=1 $maquina $cpu $shots "$tmp/Inferencia"
