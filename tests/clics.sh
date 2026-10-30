#!/bin/sh
# Inferencia con un usuario de prueba (tests/clics.dash) que escribe, pulsa los botones de permiso y comprueba
# los ficheros, en FS-UAE contra el OpenRouter falso (guion tests/guiones/ficheros.json).
#
#   tests/clics.sh DASH_DIR [captura.png segundos...]
#
# Enseña lo que anotó el usuario de prueba; acaba con "TODO BIEN" si todo fue bien.
dash=$1; shift
exec "$(dirname "$0")/usuario.sh" "$dash" "$(dirname "$0")/clics.dash" "$@"
