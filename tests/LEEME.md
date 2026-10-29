# Pruebas

De momento se compila con el Dash 2.0 de la rama `ide-piezas` de FreeMEMLang (`./dash`), que trae
`lib/json.dash` y `lib/red/`.

Contra el OpenRouter falso, sin gastar:

```sh
python3 tests/servidor_falso.py 40900 &
./dash tests/prueba_falsa.dash -o prueba_falsa
tools/emu_run.py --set bsdsocket_library=1 prueba_falsa
```

Contra OpenRouter de verdad hace falta un sistema con AmiSSL (`tools/emu_sys_amissl.sh`) y la CPU emulada
rápida. Con un 68020 a su velocidad, el saludo de TLS no acaba en 60 segundos:

```sh
tools/emu_run.py --system ~/.cache/dash-emu/sys31ssl --set bsdsocket_library=1 \
    --set uae_cpu_speed=max --set uae_cpu_compatible=false --set jit_compiler=1 hola
```
