# Pruebas

De momento se compila con el Dash 2.0 de la rama `ide-piezas` de FreeMEMLang (`./dash`), que trae
`lib/json.dash` y `lib/red/`.

La ventana, con captura: `tests/ventana.sh <worktree de Dash> "pregunta" captura.png 8`.
- `LINEA=n`: la vista sube a esa línea después de la respuesta.
- `PERMISO=Si` (o `No`, `Siempre`): contesta solo a los permisos, a los tres segundos.
- `TIEMPO=s`: el tope del emulador (150 s por defecto).
- `REAL=modelo`: contra OpenRouter de verdad (solo modelos `:free`), con la clave de
  `~/.config/inferencia/openrouter`, que va solo a la copia temporal del sistema.
- En `DH0:Prueba` están la pregunta y lo que haya en `tests/prueba/`.

Con un usuario de prueba: `tests/usuario.sh <worktree de Dash> <programa.dash> [captura.png segundos...]` arranca
el programa a la vez que Inferencia (con `ENV:INFERENCIA_SONDA`) y enseña lo que anotó en `DH0:Prueba/usuario.txt`;
`PERMISO=Si` contesta solo a los permisos.

- `tests/arexx.dash` (con `PERMISO=Si`): el puerto ARexx entero y las herramientas puertos y arexx.
- `tests/clics.sh <worktree de Dash> [captura.png segundos...]`, que es `usuario.sh` con `tests/clics.dash`. `tests/clics.dash`
escribe "GUION ficheros", pulsa los botones Sí, Siempre y No con el ratón (input.device), comprueba el fichero
y sale con Amiga-Q. Lo que anota sale al final; si todo fue bien, "TODO BIEN".

Guiones del servidor falso: `tests/guiones/<nombre>.json`, que se eligen con "GUION nombre" en la pregunta.
- Con herramientas: cada línea `LLAMA nombre {json}` de la pregunta hace que el servidor falso pida esa
  herramienta. Después contesta con el resultado de la última; si es `leer`, se ve el fichero en la respuesta.

Contra el OpenRouter falso, sin gastar (`prueba_falsa` y `prueba_conversacion`):

```sh
python3 tests/servidor_falso.py 40900 &
./dash tests/prueba_falsa.dash -o prueba_falsa
tools/emu_run.py --set bsdsocket_library=1 prueba_falsa
```

Contra OpenRouter de verdad (la clave en `ENV:OPENROUTER_API_KEY`, por ejemplo con un `SetEnv` en el
`S/Startup-Extra` de una copia del sistema que se borra después) hace falta un sistema con AmiSSL (`tools/emu_sys_amissl.sh`) y la CPU emulada
rápida. Con un 68020 a su velocidad, el saludo de TLS no acaba en 60 segundos:

```sh
tools/emu_run.py --system ~/.cache/dash-emu/sys31ssl --set bsdsocket_library=1 \
    --set uae_cpu_speed=max --set uae_cpu_compatible=false --set jit_compiler=1 hola
```
