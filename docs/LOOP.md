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
   - Si el worktree tiene cambios sin commit de dashc (está a medio hacer algo), compilar con una copia del último
     commit (`git archive HEAD` a una carpeta del scratchpad, con los `.o` del runtime y `make` en `dashc/`).
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
8. **Capturas para el usuario**: cuando una tarea cambie algo que se ve, mandarle la captura del emulador con
   SendUserFile, con una línea de qué se ve. Las capturas se guardan en el scratchpad, no en el repo.
9. **Seguir**: pasar a la siguiente vuelta sin pausas.

## Tareas

### Inferencia: hasta la primera versión usable

- [x] I1 Estructura:
  - `src/main.dash`.
  - Configuración: proveedor, URL, clave y modelo. Se leen de `ENV:` y `ENVARC:Inferencia/`.
  - En `src/openrouter.dash`, la conversación como lista de mensajes y las herramientas en formato OpenAI
    (`tools`, `tool_calls`, mensajes `tool`).
- [x] I2 Ventana MUI (`.dashui`):
  - Conversación en `mui_canvas` con `mui_scrollbar`, línea de entrada, botones Enviar y Parar, y modelo.
  - La petición sin bloquear (`http_empezar_metodo` y `http_avanzar` con `mui_wait_event_signals`).
  - Prueba: captura y un intercambio contra el servidor falso.
- [x] I3 Maquetado de la conversación:
  - Ajuste de líneas, desplazamiento y rueda.
  - Markdown básico: párrafos, negrita, listas y código en Topaz.
  - Colores para el usuario, el modelo y las herramientas.
- [x] I4 Herramientas y permisos:
  - `leer`, `listar`, `buscar`, `escribir`, `editar` y `orden`.
  - Permisos "Sí", "No" y "Siempre" dentro de la conversación.
  - Topes de tamaño. Bucle hasta que el modelo acaba.
- [x] I5 Pruebas del bucle:
  - El servidor falso con guiones de llamadas a herramientas.
  - Tests en FS-UAE que pulsan y comprueban los ficheros cambiados.
  - Una prueba real con un modelo `:free` que use herramientas.

### Forja: hasta la primera versión usable

- [x] F1 Ventana oscura:
  - Estructura del repo y `src/main.dash`.
  - Preferencias MUI propias con tema oscuro.
  - Disposición: proyecto, pestañas, salida y botones.
- [x] F1b Tema oscuro también en lo de MUI (botones, bordes de los grupos), cuando dashc entregue
  `mui_set_background` (pieza 11, pedida el 2026-10-30).
- [x] F2 Editor de código en canvas:
  - Texto por líneas, cursor y teclado (con la tabla de teclas).
  - Selección con ratón y teclado, desplazamiento, deshacer y rehacer.
  - Portapapeles.
- [x] F3 Colores de la sintaxis de Dash y números de línea. Rápido en un 68020.
- [x] F4 Ficheros:
  - Pestañas.
  - Abrir y guardar con petición de fichero.
  - Panel del proyecto, con la lista del cajón.
  - Aviso al cerrar sin guardar.
- [x] F5 Compilar y ejecutar:
  - dashc con `run_start`, sin bloquear.
  - Salida con los errores. Un clic salta a la línea.
  - Ejecutar el programa.

### Integración

- [x] I6 ARexx en Inferencia:
  - Puerto `INFERENCIA` con `PREGUNTA`, `CONTEXTO`, `NUEVA`, `MOSTRAR` y `OCULTAR`.
  - Herramientas `arexx` y `puertos`.
- [x] F6 ARexx en Forja:
  - Puerto con `ABRIR`, `SELECCION`, `CAMBIAR`, `COMPILAR` y `EJECUTAR`.
  - Botón Inferencia.
  - Si Forja está abierta, Inferencia la usa para los cambios.

### El resto

- [x] F7 Editor de `.dashui` (F7a y F7b):
  - Árbol de objetos.
  - Vista previa real con `lib/dashui.dash`.
  - Propiedades.
  - Guardar el JSON igual que la extensión de VS Code.
- [x] F8 Depurador (`dbg_*`):
  - Puntos de parada en el margen.
  - Seguir, paso, entrar y salir.
  - Variables, pila y la línea actual resaltada.
- [x] I7 Herramientas `sistema`, `entorno` y `portapapeles`. Lista de órdenes y puertos que no piden permiso.
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
- 2026-10-30, I1: `src/config.dash` (ENV:Inferencia/url, clave, modelo), `src/openrouter.dash` con la conversación,
  las herramientas (tool_calls) y la petición sin esperar, `src/main.dash` en el Shell. El servidor falso pide
  herramientas ("LLAMA nombre {json}"). `tests/prueba_conversacion.dash` en FS-UAE: dos llamadas, sus resultados
  y la respuesta, también sin esperar; la "ñ" va y vuelve.
- 2026-10-30, I2: `src/ventana.dashui` (modelo, conversación en canvas con barra, entrada, Enviar y Parar, menú),
  `src/vista.dash` (bloques partidos al ancho, colores por quién habla) y `src/main.dash` con la petición sin
  bloquear (`mui_wait_event_signals(task_signal())` y un tic de 50 ms). `tests/ventana.sh` la prueba en FS-UAE
  contra el servidor falso con captura: tildes bien, texto partido, tokens. Pendiente para I3: comprobar que la
  barra se pone al final (en la captura el mando parece arriba) y la banda del usuario no se ve con 4 colores.
  emu_run escribe el Startup-Sequence en UTF-8 y el sistema no tiene `Copy`: la pregunta de prueba va en un
  fichero Latin-1 (`INFERENCIA_PRUEBA=@fichero`).
- 2026-10-30, I3: `src/vista.dash` lee lo del modelo como Markdown (párrafos, negrita, cursiva, código, títulos,
  listas con sangría, citas, bloques de código) una vez al añadirlo, y solo lo vuelve a partir al cambiar el
  ancho. Texto en Helvetica 11 y código en Topaz 8, en la misma línea base. Con 4 colores, el usuario lleva una
  raya azul a la izquierda (la banda solo si hay color para ella) y los bloques de código una raya. La barra
  sigue a la vista con un tic de 300 ms (también al cambiar el tamaño). Comprobado en FS-UAE con capturas
  (respuesta Markdown del servidor falso, `LINEA=n` para subir la vista): la barra queda al final. La rueda no
  se ha probado en el emulador. Pendiente: elegir las fuentes en las preferencias (I10).
- 2026-10-30, I4: `src/herramientas.dash` con leer (desde, hasta), listar, buscar (en cajones de dentro),
  escribir, editar (trozo exacto, una sola vez) y orden (`run_start`, sin parar la ventana), con topes de
  tamaño y de tiempo. Escribir, editar y orden preguntan con botones Sí, No y Siempre dibujados en la
  conversación; los cambios se ven con líneas "-" y "+". `src/main.dash` lleva el bucle: herramientas una a una,
  resultados al modelo, otra petición, hasta 25 vueltas; Parar da resultado a las que quedan (la API lo pide).
  Comprobado en FS-UAE contra el servidor falso: escribir, editar (y su error), listar, buscar, Echo en el Shell
  y leer, con Sí, Siempre y No; el fichero queda con "Segunda línea con ñ". El clic real en los botones queda
  para I5 (aquí contesta `INFERENCIA_PRUEBA_PERMISO`). Una captura salió mezclada al tomarse a media copia de
  pantalla; repetida cinco veces, sale igual.
- 2026-10-30, I5: el servidor falso sigue guiones (`tests/guiones/*.json`, "GUION nombre"). `tests/clics.sh`
  arranca `tests/clics.dash`, que hace de usuario por input.device: escribe en la línea de entrada (ahora es el
  objeto activo de la ventana), pulsa Sí, Siempre y No en los botones dibujados y comprueba el fichero que
  queda. Inferencia, con `ENV:INFERENCIA_SONDA`, dice su estado y dónde están los botones. Pasa: "TODO BIEN".
  `input_menu` no encuentra el menú de la ventana MUI (da false); se sale con Amiga-Q. Mirarlo al probar los
  menús de Forja y, si es de Dash, encargarlo a dashc. Prueba real (`REAL=nvidia/nemotron-3.5-lightning:free`):
  el modelo usó listar y leer en DH0:Prueba y contestó con los dos ficheros y el texto de la nota, con tildes.
  La clave no quedó en ningún temporal. Tras un "No" a una orden ya no sale "Salida".
- 2026-10-30, F1: Forja con `src/main.dash`, `ventana.dashui` (botones, proyecto, balance, editor con barra,
  salida), `tema.dash` (colores y fuentes), `editor.dash` (pestañas, números de línea, línea del cursor; solo
  dibuja) y `paneles.dash` (ficheros .dash y .dashui del cajón, salida con colores). Los ficheros en UTF-8 de
  un PC se pasan a Latin-1 al abrir y se recuerda para guardarlos igual. Captura en FS-UAE
  (`tests/ventana.sh`): los lienzos en negro, la ñ bien. Los botones del depurador salen solo al depurar
  (los nueve no caben en 640 píxeles y MUI añadía una barra para desplazar la ventana). MUI no deja poner
  fondos desde Dash y unas prefs propias no se pueden escribir a mano: pedido a dashc `mui_set_background`
  (pieza 11); queda F1b.
- 2026-10-30, F2: el editor de Forja escribe: cursor, flechas (Alt: línea y página; Ctrl: palabra y texto),
  selección con Mayúsculas y con el ratón (clic, Mayúsculas + clic, arrastrar), sangría automática, Tab y
  Mayúsculas + Tab, Retroceso hasta la parada de sangría, deshacer y rehacer (las letras seguidas van juntas),
  cortar, copiar y pegar con el portapapeles del sistema, menú Edición, rueda y barra. El teclado va al editor
  con el puntero encima (así lo da el lienzo); Amiga + letra sobre el editor se pasa a la opción del menú.
  `tests/teclas.sh` lo prueba por input.device en FS-UAE: dos veces seguidas "TODO BIEN" (la primera vez, la
  prueba leyó la sonda a medio escribir: ahora reintenta). La captura de la selección no salió a tiempo.
  dashc entregó la pieza 11 (`mui_set_background`, `mui_set_text_pen`, "background" y "color" en .dashui) y
  confirmó que `input_menu` no puede ir con MUI 5 (menús propios, sin tira de Intuition): Amiga + tecla es el
  camino.
- 2026-10-30, F1b: "background" en la ventana y "background" y "color" en los botones (pieza 11 de dashc).
  Captura en FS-UAE: todo negro con texto claro, también con los 4 colores del Workbench; la barra de
  desplazamiento sigue gris (no es de los objetos que admite).
- 2026-10-30, F3: `src/sintaxis.dash` parte cada línea en trozos (palabra clave, tipo, texto, número,
  comentario, llamada, constante) con `str_code` y un diccionario de palabras clave; el editor dibuja cada trozo
  con su color. Al escribir dentro de una línea solo se redibuja esa línea (`mui_canvas_update_area`). Medido en
  FS-UAE con la CPU a la velocidad de un A1200: un dibujo entero de unas 20 líneas, 38 ms (con la CPU al máximo,
  45: lo marca el blitter). `tests/teclas.sh` sigue en "TODO BIEN". Captura en 256 colores con `RTG=1`
  (AmigaOS 3.2, `sys32rtg8`): los colores bien. Con 4 colores casi todo sale blanco.
- 2026-10-30, F4: pestañas con clic, Nuevo, Abrir y Guardar como con el diálogo ASL, Guardar (en UTF-8 si
  el fichero venía así), Cerrar pestaña; el panel del proyecto abre ficheros con un clic y entra en cajones
  ("/ (arriba)" para subir). Cerrar o salir con cambios sin guardar avisa en la salida y pide la orden otra
  vez: Dash no tiene una petición de confirmación, pedida a dashc (`mui_request`, pieza 12); cuando llegue, se
  cambia. `tests/ficheros.sh` en FS-UAE: "TODO BIEN" (abrir desde el proyecto, pestañas, guardar, UTF-8, aviso y
  cierre). `tests/teclas.sh` sigue bien. Los diálogos ASL no se prueban solos.
- 2026-10-30, F5: Compilar (Amiga-K) y Ejecutar (Amiga-E) llaman a dashc con `run_start` sin parar la
  ventana (ENV:Forja/dashc o "dashc"); guardan antes lo cambiado; los errores "fichero:línea:columna: Error:"
  van a la salida en rojo y un clic lleva a su línea; Ejecutar pasa a Parar mientras corre el programa.
  dashc para el Amiga: `make amiga` en una copia aparte de ide-piezas (no en la carpeta donde trabaja dashc).
  Pieza 13 (dashc): en el Amiga una orden de System no tiene canal de errores; ahora dashc escribe sus errores
  por stdout en Latin-1. Pieza 12 (`mui_request`): cerrar o salir con cambios pregunta Guardar, Descartar o
  Cancelar. Pruebas en FS-UAE, todas "TODO BIEN": `compilar.sh` (compila en 1,4 s con la CPU al máximo, ejecuta
  y escribe "Naves: 2", el clic en el error lleva a la línea 25), `ficheros.sh` (con la petición: la tecla hay
  que pulsarla un momento después de que salga) y `teclas.sh`. Dos capturas salieron a medio dibujar.
- 2026-10-30, I6: puerto INFERENCIA.1 (`mui_app_rexx`): PREGUNTA (sin esperar: una orden ARexx contesta
  enseguida), ESTADO, RESPUESTA, CONTEXTO fichero [desde hasta] (va con la siguiente pregunta), NUEVA, MOSTRAR
  y OCULTAR. Herramientas puertos y arexx (con permiso; no a su propio puerto). `tests/usuario.sh` arranca
  cualquier usuario de prueba; `tests/arexx.dash` maneja Inferencia solo por ARexx con dos guiones nuevos del
  servidor falso: "TODO BIEN" en FS-UAE, y `clics.sh` sigue bien. No probado: arexx contra el puerto de otro
  programa (llega con Forja, F6).
- 2026-10-30, F6: puerto FORJA.1 (ABRIR, ABIERTO, TEXTO, SELECCION, CAMBIAR con deshacer, GUARDAR, COMPILAR,
  EJECUTAR, ESTADO, ERRORES) y botón Inferencia (Amiga-I): manda el fichero o la selección con ADJUNTAR (orden
  nueva de Inferencia, para que Inferencia no tenga que pedírselo a Forja mientras Forja espera) y la arranca si
  no está. Inferencia lee, escribe y edita a través de Forja los ficheros que tiene abiertos (sin guardar, con
  deshacer). Pruebas en FS-UAE, "TODO BIEN": `tests/juntos.dash` (los dos programas a la vez) y
  `forja/tests/rexx.dash`. Pieza 14 de dashc (b440e6b): un RESULT vacío llegaba como el de la orden anterior;
  arreglado, y la prueba vuelve a exigir "".
- 2026-10-30, F7a: `src/diseno.dash`: un .dashui se abre en el editor de ventanas (Amiga-D cambia a texto): el
  árbol de objetos y las propiedades del elegido (las de su tipo y las comunes), editables en el sitio, con
  comprobación de números, true/false, listas y nombres. Lo cambiado pasa al texto con json_pretty (como la
  extensión de VS Code) y se deshace en un paso (cambios "juntos" en el deshacer). Vista previa (Amiga-P): la ventana
  MUI de verdad con lib/dashui.dash, sin eventos ni atajos ni id (no deben llegar a Forja), rehecha con cada
  cambio; la anterior se destruye con `mui_window_dispose` (pieza 15). `tests/diseno.sh` en FS-UAE: "TODO BIEN";
  `teclas.sh` sigue bien. Rehacer la vista tarda más de 2 s con la CPU al máximo: por medir. El teclado vuelve a
  Forja buscándola por título (rodeo); pedida la pieza 16 (activar ventanas MUI).
- 2026-10-30, F7b: en el árbol, "+" añade (en un grupo, un hijo; en otro objeto, uno detrás, eligiendo el tipo en
  una lista; en la ventana, un menú; en un menú, una opción), Supr quita, Alt + arriba o abajo cambia de sitio; los
  menús y sus opciones salen en el árbol con sus propiedades (key de una letra); el árbol se desplaza para que se vea
  la fila elegida. `tests/diseno.sh` en FS-UAE: "TODO BIEN" dos de tres veces; la otra, Return se perdió, creo que
  porque la vista previa rehecha se quedó el teclado (lo arregla la pieza 16). La sonda dice también el estado del
  editor de ventanas (ENV:FORJA_DISENO).
- 2026-10-30, F8: depurar (Amiga-G o F5) compila con `dashc --debug` y lanza con `dbg_start`; puntos de parada con F9
  o un clic en el margen (un cuadrado rojo; se ponen también con el programa en marcha); Seguir F5, Paso F10,
  Entrar F6, Salir F7 y Parar, en botones que sustituyen a los de siempre mientras se depura; la línea parada con
  fondo y una flecha en el margen; el panel de la izquierda enseña la pila, las variables y las globales
  (`dbg_value`); la salida del programa (`dbg_output`) va a la salida. La espera, con `dbg_signal()` en
  `mui_wait_event_signals` y un tic de respaldo. `tests/depurar.sh` en FS-UAE: "TODO BIEN" tres veces (antes, la
  prueba leía ENV: mientras Forja lo escribía). Pieza 16 de dashc (`mui_window_open_back`): la vista previa rehecha
  ya no se queda el teclado; `diseno.sh` pasa dos de dos. dashc midió rehacer la vista: 0,9 s (json_parse en Dash
  y MUI calculando la ventana).
- 2026-10-30, I7: herramientas sistema (resumen: AmigaOS por la versión de exec, procesador, MUI y memoria;
  volúmenes, asignaciones, tareas), entorno (leer, listar, poner, con permiso para poner y ENVARC: si se pide) y
  portapapeles (leer; escribir con permiso). Lista de lo que no pide permiso en ENV:Inferencia/sin_permiso, con
  comas; "Siempre" la amplía y la guarda en ENVARC:. `tests/sistema.dash` en FS-UAE: "TODO BIEN" (ñ en entorno y
  portapapeles; escribir, fuera de la lista, pregunta). Un string liberado dos veces al reasignar la variable de
  un for colgaba el Amiga entero: pieza 18 a dashc, rodeado. dashc entregó la pieza 17 (json_parse en C, 2,2 veces
  más rápido).
