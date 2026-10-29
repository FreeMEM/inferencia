# Inferencia: plan

Inferencia lleva la IA al Amiga. Es un programa MUI con el que hablas con un modelo, que actúa sobre el sistema
operativo igual que Claude Code en un PC:
- Lee y cambia ficheros.
- Ejecuta órdenes del Shell.
- Manda órdenes ARexx a otros programas.
- Mira el sistema.

Siempre pide permiso antes de cambiar algo.

Es un programa independiente y sirve para cualquier tarea, no solo para programar. Se integra por ARexx con Forja, el IDE
de Dash, que es otra aplicación (plan aparte, `~/Projects/forja/PLAN.md`), y con cualquier otro programa.

Escrito en Dash 2.0 (dashc) y con licencia MIT, como Dash y Tachyon:
- Nada de `@native`, porque Dash 2.0 no lo admite en programas de usuario. Lo que falte va a Dash como builtin
  o como módulo de `lib/`.
- Depende de que dashc tenga diccionarios, `import`, textos, red, TLS y MUI (tareas D3, D5 y D6 de
  `docs/DASHC_LOOP.md`). Si alguna falta, se empieza con `./dash` y se pasa después a dashc.

## Qué necesita la máquina

- 68020 o mejor, porque MUI 5 y AmiSSL 5 lo piden.
- MUI 5, una pila TCP/IP y AmiSSL 5.
- El reloj en hora, porque AmiSSL comprueba las fechas del certificado.
- Una clave de OpenRouter, o un modelo en un PC de casa (Ollama, LM Studio) por HTTP, sin TLS.

## La ventana

```
+--------------------------------------------------------------------+
| Inferencia                                                    [][] |
+--------------------------------------------------------------------+
| Modelo [anthropic/claude-sonnet-5.5 v]   12.400 tokens · 0,03 $    |
+--------------------------------------------------------------------+
| Tú: ¿por qué no arranca la red al encender?                        |
|                                                                    |
| ● Leer S:User-Startup                                              |
| ● Orden  ShowNetStatus                                             |
|                                                                    |
| User-Startup arranca Roadshow antes de montar la tarjeta. Muevo    |
| AddNetInterface detrás de la línea del driver:                     |
|                                                                    |
| ● Editar S:User-Startup                                            |
|   - AddNetInterface DEVS:NetInterfaces/wifi                        |
|   + (dos líneas más abajo)                                         |
|                         [ Sí ]  [ No ]  [ Siempre ]                |
+--------------------------------------------------------------------+
| [ escribe aquí...                                 ] [Enviar][Parar]|
+--------------------------------------------------------------------+
```

- La conversación se dibuja sobre un `mui_canvas` con su `mui_scrollbar`.
  - Las respuestas llegan en Markdown y se pasan a negrita, listas y código en Topaz.
  - Los cambios se muestran con las líneas quitadas y las puestas en color.
  - Se aprovecha lo que ya hace Tachyon para maquetar texto.
- Se escribe en un `mui_string` de una línea. Varias líneas, más adelante.
- Los permisos van en la propia conversación, con "Sí", "No" y "Siempre". Así se ve la orden o el cambio
  completo antes de aceptar.
- Para que no se congele, la petición avanza por trozos (`http_avanzar` con
  `mui_wait_event_signals(net_signal())`), como en Tachyon. "Parar" la corta.
- En el menú están el proveedor, la clave y el modelo, guardar y cargar la conversación, empezar de cero y
  el directorio de trabajo.

## Herramientas (lo que puede hacer en el sistema)

| Herramienta | Qué hace | ¿Pide permiso? |
|---|---|---|
| `leer` | Lee un fichero, con un tope de tamaño | No |
| `listar` | Lista un directorio | No |
| `buscar` | Busca un texto en los ficheros de un directorio | No |
| `escribir` | Crea o sustituye un fichero entero | Sí |
| `editar` | Cambia un trozo exacto de un fichero por otro | Sí |
| `orden` | Ejecuta una línea del Shell y devuelve su salida y su código, con un tope de tiempo | Sí |
| `arexx` | Manda una orden ARexx al puerto de un programa y devuelve el resultado | Sí |
| `puertos` | Lista los puertos ARexx abiertos, para saber con qué programas puede hablar | No |
| `sistema` | Memoria libre, versión del sistema, volúmenes, asignaciones y tareas en marcha | No |
| `entorno` | Lee y cambia variables de `ENV:` | Leer no; cambiar sí |
| `portapapeles` | Lee y escribe el portapapeles | Leer no; escribir sí |

Hay una lista de órdenes y puertos que no piden permiso, configurable, como en Claude Code. "Siempre" añade a
esa lista la orden que se acaba de aceptar.

## ARexx

Inferencia tiene su propio puerto, `INFERENCIA`:
- `PREGUNTA "texto"`: hace la pregunta en la conversación y devuelve la respuesta.
- `CONTEXTO fichero [desde hasta]`: añade a la conversación un fichero o unas líneas.
- `NUEVA`: empieza una conversación nueva.
- `MOSTRAR` y `OCULTAR`: la ventana.

Con eso, cualquier programa le puede preguntar. Desde el IDE de Dash: "explica esto", "arregla este error",
con el fichero abierto y la selección. Si el IDE está abierto, Inferencia usa su puerto para abrir ficheros,
aplicar cambios que se pueden deshacer y compilar.

## Proveedores

- **Primero, OpenRouter**, con el formato de OpenAI Chat Completions. Con una clave tienes cientos de modelos,
  Claude incluido, y algunos gratis con límite diario.
- **Ese mismo formato** sirve para OpenAI, DeepSeek, Groq, y Ollama o LM Studio en casa.
- **Después, Anthropic Messages**, para la API de Claude directa.
- Los planes de suscripción (Claude Pro/Max) no se pueden usar fuera de Claude Code y claude.ai.

Detalles:
- El historial solo crece y se reenvía entero. Lleva topes por herramienta y, cuando el proveedor lo
  permita, caché de prompt.
- Antes de usar la respuesta se mira por qué paró (`finish_reason`). Si una herramienta falla, se le devuelve
  el error.

## Piezas de Dash

Encargadas a la sesión `dashc`. Hechas en la rama `ide-piezas`, todavía sin fusionar:
1. JSON: `lib/json.dash`.
2. Ejecutar una orden y recoger su salida: `run_capture`, `run_rc`, y la versión sin bloquear `run_start`.
3. Listar un directorio: `dir_read` y `dir_entry_*`.
4. Variables de entorno: `env_get` y `env_set`.

Pendientes:
5. `http.dash` y `red.dash` de Tachyon a `lib/` de Dash. Además, que un programa de fuera del repo de Dash
   encuentre `lib/` al importar.
6. **ARexx como cliente**: mandar una orden a un puerto y recoger el resultado y el código. Listar los
   puertos públicos.
7. **ARexx como servidor en MUI**: órdenes propias en el puerto de la aplicación MUI.
8. **Información del sistema**: tareas en marcha, volúmenes y asignaciones. Las de Trasfondo, si ya están
   como builtins.

## Fases

- **F0**: un "hola" a OpenRouter desde FS-UAE. Comprueba TLS, cabeceras, UTF-8 y tiempos.
- **F1**: la ventana con la conversación y las herramientas de ficheros y órdenes, con permisos. Es la
  primera versión usable.
- **F2**: ARexx (cliente, servidor y la herramienta `arexx`) y las herramientas de sistema, entorno y
  portapapeles.
- **F3**: memoria y coste. Topes, caché, guardar la conversación y resumir la conversación cuando crece.
- **F4**: ver el texto mientras llega (streaming), entrada de varias líneas y más proveedores.
- **F5**: catálogos de idioma, el paquete `.lha` y la publicación en Aminet, la web y GitHub.

## Pruebas

- Un servidor falso en el PC (Python) que imita OpenRouter con respuestas grabadas, para no gastar en cada
  prueba. Solo unas pocas pruebas a mano con la API de verdad.
- En FS-UAE con MUI 5 (`DASH_EMU_SYS_MUI`), con clics reales por `input.device` y capturas de pantalla.

## Riesgos

- **Memoria**: cada petición reenvía todo el historial en JSON. Hay que medir cuánta RAM rápida necesita.
- **Velocidad**: el saludo de TLS de cada petición puede tardar segundos en un 68020.
- **Seguridad**: el modelo puede pedir órdenes que borren cosas o mandar ARexx a cualquier programa. Por eso
  pregunta antes por defecto. Lo que hace queda en un registro.
- **Certificados**: AmiSSL trae los suyos. Si caducan, falla la conexión.
