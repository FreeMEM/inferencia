# Bucle de construcción: Inferencia y Forja

Encargo (2026-10-30): construir los dos programas enteros, según `PLAN.md` de cada repo:
- Inferencia, en este repo.
- Forja, en `~/Projects/forja`.

Un bucle hace las tareas en orden, una por vuelta. Cada tarea termina probada, con commit y subida a GitHub.

## Normas de cada vuelta

1. **Uso semanal**: leer `~/.claude/state/uso-7d.txt` ("porcentaje época"). Con 90 % o más, acabar en un punto
   seguro, anotarlo en la bitácora y parar el bucle sin empezar nada nuevo.
2. **Tarea**: coger la primera tarea sin hacer de la lista. Si es grande, partirla y anotar las partes.
3. **Dash 2.0**: sin `@native`.
   - Antes de escribir Dash, leer `~/Projects/FreeMEMLang/docs/SINTAXIS.md`. Builtins: `docs/BUILTINS.md` de la
     rama que se use.
   - Compilador: si la rama `dashc` ya contiene `ide-piezas`
     (`git -C ~/Projects/FreeMEMLang merge-base --is-ancestor ide-piezas dashc`), el `./dash` de
     `~/Projects/FreeMEMLang/.worktrees/dashc`. Si no, el de `.worktrees/ide-piezas`.
   - Lo que le falte a Dash (un builtin, un fallo del compilador) no se arregla aquí: se encarga a la sesión
     `dashc` con SendMessage, con un ejemplo mínimo que lo muestre. Mientras tanto, seguir con otra tarea.
4. **Pruebas en FS-UAE** con `tools/emu_run.py` de ese mismo worktree:
   - Con MUI y red: `--system ~/.cache/dash-emu/sys31muisslweb --set bsdsocket_library=1`.
   - Para TLS real, además `--set uae_cpu_speed=max --set uae_cpu_compatible=false --set jit_compiler=1`.
   - Para comprobar la ventana: `--autoclose N --screenshot S fichero.png`, y mirar la captura.
   - Clics y teclas: por `input.device`, como en `tests/test_gt_events.dash` de Dash.
   - Otras sesiones usan FS-UAE a la vez: solo se paran procesos propios, por PID.
5. **Sin gastar**:
   - Las pruebas automáticas van contra `tests/servidor_falso.py`, ampliado con lo que haga falta (llamadas a
     herramientas, streaming, errores).
   - Contra OpenRouter de verdad, solo modelos `:free` y pocas veces.
   - La clave está en `~/.config/inferencia/openrouter`. Nunca se imprime ni va a un fichero que quede. Al
     emulador se pasa con `SetEnv` en una copia temporal del sistema que se borra al acabar.
6. **Cerrar la tarea**:
   - Commit en el repo que toque, con la cuenta FreeMEM. Mensaje en castellano, llano y sin rastro de Claude
     (el hook `commit-msg` lo quita).
   - Subir a GitHub con el token de FreeMEM.
   - Marcar la tarea `[x]` y añadir una línea a la bitácora con lo hecho y lo comprobado.
   - Si algo cambia el plan, cambiar `PLAN.md`.
7. **Textos**: README, mensajes y textos de los programas, llanos y sin coletillas. Castellano primero, inglés
   en catálogo.
8. **Seguir**: pasar a la siguiente vuelta sin pausas.

## Tareas

### Inferencia: hasta la primera versión usable

- [ ] I1 Estructura:
  - `src/main.dash`.
  - Configuración: proveedor, URL, clave y modelo. Se leen de `ENV:` y `ENVARC:Inferencia/`.
  - En `src/openrouter.dash`, la conversación como lista de mensajes y las herramientas en formato OpenAI
    (`tools`, `tool_calls`, mensajes `tool`).
- [ ] I2 Ventana MUI (`.dashui`):
  - Conversación en `mui_canvas` con `mui_scrollbar`, línea de entrada, botones Enviar y Parar, y modelo.
  - La petición sin bloquear (`http_empezar_metodo` y `http_avanzar` con `mui_wait_event_signals`).
  - Prueba: captura y un intercambio contra el servidor falso.
- [ ] I3 Maquetado de la conversación:
  - Ajuste de líneas, desplazamiento y rueda.
  - Markdown básico: párrafos, negrita, listas y código en Topaz.
  - Colores para el usuario, el modelo y las herramientas.
- [ ] I4 Herramientas y permisos:
  - `leer`, `listar`, `buscar`, `escribir`, `editar` y `orden`.
  - Permisos "Sí", "No" y "Siempre" dentro de la conversación.
  - Topes de tamaño. Bucle hasta que el modelo acaba.
- [ ] I5 Pruebas del bucle:
  - El servidor falso con guiones de llamadas a herramientas.
  - Tests en FS-UAE que pulsan y comprueban los ficheros cambiados.
  - Una prueba real con un modelo `:free` que use herramientas.

### Forja: hasta la primera versión usable

- [ ] F1 Ventana oscura:
  - Estructura del repo y `src/main.dash`.
  - Preferencias MUI propias con tema oscuro.
  - Disposición: proyecto, pestañas, salida y botones.
- [ ] F2 Editor de código en canvas:
  - Texto por líneas, cursor y teclado (con la tabla de teclas).
  - Selección con ratón y teclado, desplazamiento, deshacer y rehacer.
  - Portapapeles.
- [ ] F3 Colores de la sintaxis de Dash y números de línea. Rápido en un 68020.
- [ ] F4 Ficheros:
  - Pestañas.
  - Abrir y guardar con petición de fichero.
  - Panel del proyecto, con la lista del cajón.
  - Aviso al cerrar sin guardar.
- [ ] F5 Compilar y ejecutar:
  - dashc con `run_start`, sin bloquear.
  - Salida con los errores. Un clic salta a la línea.
  - Ejecutar el programa.

### Integración

- [ ] I6 ARexx en Inferencia:
  - Puerto `INFERENCIA` con `PREGUNTA`, `CONTEXTO`, `NUEVA`, `MOSTRAR` y `OCULTAR`.
  - Herramientas `arexx` y `puertos`.
- [ ] F6 ARexx en Forja:
  - Puerto con `ABRIR`, `SELECCION`, `CAMBIAR`, `COMPILAR` y `EJECUTAR`.
  - Botón Inferencia.
  - Si Forja está abierta, Inferencia la usa para los cambios.

### El resto

- [ ] F7 Editor de `.dashui`:
  - Árbol de objetos.
  - Vista previa real con `lib/dashui.dash`.
  - Propiedades.
  - Guardar el JSON igual que la extensión de VS Code.
- [ ] F8 Depurador (`dbg_*`):
  - Puntos de parada en el margen.
  - Seguir, paso, entrar y salir.
  - Variables, pila y la línea actual resaltada.
- [ ] I7 Herramientas `sistema`, `entorno` y `portapapeles`. Lista de órdenes y puertos que no piden permiso.
- [ ] I8 Memoria y coste:
  - Tokens y gasto (`usage`).
  - Topes por herramienta.
  - Guardar y cargar la conversación.
  - Resumir cuando crece.
- [ ] I9 Ver el texto mientras llega (streaming SSE) y entrada de varias líneas.
- [ ] I10 Más proveedores (Anthropic Messages, Ollama) y una ventana de preferencias.
- [ ] F9 Buscar y reemplazar, preferencias, ir a línea, proyectos guardados.
- [ ] I11 y F10 Acabado:
  - Catálogos en inglés e iconos.
  - Paquete `.lha` y README en inglés.
  - Lista de lo que queda para la primera versión publicada. Publicarla lo decide el usuario.

## Bitácora

- 2026-10-29: F0 hecha (respuesta real de OpenRouter en FS-UAE). Piezas de Dash 1 a 10 en la rama `ide-piezas`.
