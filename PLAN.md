# Inferencia: plan

Inferencia es un entorno de desarrollo para Dash que corre en el propio Amiga:
- MUI 5, moderno y con fondo negro.
- Editor de código con colores.
- Compilar y ejecutar desde el propio entorno.
- Depurador paso a paso.
- Editor visual de ventanas (`.dashui`).
- Un asistente que programa contigo a través de OpenRouter.

Escrito en Dash 2.0 (dashc) y con licencia MIT, como Dash y Tachyon. Eso implica:
- Nada de `@native`, porque Dash 2.0 no lo admite en programas de usuario. Lo que falte se hace con
  builtins o con el propio lenguaje.
- Se compila con dashc, y dashc es también el compilador que usa el IDE dentro del Amiga.
- Depende de que dashc tenga diccionarios, `import`, textos, red, TLS y MUI (tareas D3, D5 y D6 de
  `docs/DASHC_LOOP.md`). Si alguna falta, se empieza con `./dash` y se pasa después a dashc.

## Qué necesita la máquina

- 68020 o mejor, porque MUI 5 y AmiSSL 5 lo piden.
- MUI 5.
- Para el asistente: una pila TCP/IP, AmiSSL 5 y el reloj en hora, porque AmiSSL comprueba las fechas del
  certificado. También una clave de OpenRouter.

## La ventana

```
+--------------------------------------------------------------------------------+
| Inferencia: Work:juego                                                   [][]  |
+--------------------------------------------------------------------------------+
| [Compilar] [Ejecutar] [Depurar] [Paso] [Entrar] [Salir] [Seguir]               |
+--------------+-----------------------------------------+-----------------------+
| Proyecto     | main.dash | ventana.dashui | red.dash  | Asistente             |
|  main.dash   |  45   total = lista.count               | Tú: no termina el     |
|  red.dash    |  46   j = 0                             | bucle                 |
|  ventana.ui  |  47 ● while j < total                   | ● Leer main.dash      |
|              |  48 >     procesar(lista[j])            | La condición usa i... |
| Variables    |  49       j = j + 1                     | ● Editar main.dash    |
|  j      3    |  50   end                               |  - while i < total    |
|  total  10   |                                         |  + while j < total    |
|              |                                         | [Sí] [No] [Siempre]   |
+--------------+-----------------------------------------+-----------------------+
| Salida: compilado en 1,2 segundos, 0 avisos                                    |
+--------------------------------------------------------------------------------+
```

- **Fondo negro**: el editor, la salida y el asistente se dibujan sobre `mui_canvas`, así que sus colores
  son los del IDE. Para el resto de la ventana se instalan unas preferencias de MUI propias del programa
  (MUI las guarda por aplicación), con tema oscuro.
- **Editor de código**: hecho sobre el canvas, porque Dash no tiene campo de varias líneas. Lleva colores
  según la sintaxis de Dash, números de línea, puntos de parada, buscar y reemplazar, deshacer y varias
  pestañas. Es la pieza más grande del IDE.
- **Panel del proyecto**: los ficheros. Al depurar, también las variables y la pila de llamadas.
- **Salida**: los errores de dashc. Con un clic se salta a la línea.
- **Asistente**: un panel a la derecha que se puede ocultar. Se describe más abajo.

## Editor visual de ventanas (`.dashui`)

Abrir un `.dashui` muestra una pestaña con tres partes:
- El árbol de objetos.
- La ventana de verdad, construida con MUI a partir del JSON mientras se edita. Como el IDE ya es un
  programa MUI, la vista previa es exacta, cosa que el editor de VS Code no puede dar.
- Las propiedades del objeto elegido.

Usa el mismo formato que el editor de VS Code (`docs/MUI_EDITOR.md`), y los dos tienen que poder abrir los
ficheros del otro. El asistente también puede leer y cambiar `.dashui`.

## Depurador

Ahora el depurador de Dash solo funciona en el emulador (`--debug`, `debug_break`, por uaelib). En un Amiga
de verdad hace falta otro:
- El IDE lanza el programa como proceso propio y recoge sus excepciones con `tc_TrapCode`, como ya hace el
  runtime de Dash.
- Los puntos de parada ponen una instrucción `TRAP` en la dirección de la línea.
- El paso a paso usa el bit de traza del 68k.
- dashc tiene que dar una tabla de líneas y direcciones y la posición de cada variable. Como dashc genera el
  código 68k él mismo, esa información la controla. Hay que pedírsela.

## Asistente (OpenRouter)

Habla el formato de OpenAI Chat Completions, el de OpenRouter. Después vendrán Anthropic Messages, OpenAI,
DeepSeek y Ollama o LM Studio en el PC de casa. Con un modelo local por HTTP no hace falta TLS.

Los planes de suscripción (Claude Pro/Max) no se pueden usar fuera de Claude Code y claude.ai. El asistente
funciona con clave y se paga por uso; OpenRouter tiene además algunos modelos gratis con límite diario.

Herramientas:

| Herramienta | Qué hace | ¿Pide permiso? |
|---|---|---|
| `leer` | Lee un fichero, con un tope de tamaño | No |
| `listar` | Lista un directorio | No |
| `buscar` | Busca un texto en los ficheros del proyecto | No |
| `escribir` | Crea o sustituye un fichero entero | Sí |
| `editar` | Cambia un trozo exacto de un fichero por otro | Sí |
| `orden` | Ejecuta una línea del Shell y devuelve su salida y su código | Sí |
| `compilar` | Compila con dashc y devuelve los errores | No |

Al estar dentro del IDE:
- Ve el fichero abierto y la selección.
- Sus cambios aparecen en el editor y se pueden deshacer.
- Puede compilar para comprobar lo que ha hecho.

Para que no se congele, la petición avanza por trozos con `http_avanzar` y
`mui_wait_event_signals(net_signal())`, como en Tachyon. "Parar" la corta.

Detalles del formato:
- El historial solo crece y se reenvía entero. Con topes por herramienta y, cuando el proveedor lo permita,
  caché de prompt.
- Antes de usar la respuesta se mira por qué paró (`finish_reason`). Si una herramienta falla, se le
  devuelve el error.

## Piezas que faltan en Dash

1. **JSON**: leer un texto JSON a un árbol y escribir un árbol a texto, con escapes y `\uXXXX`.
2. **Ejecutar una orden y recoger su salida**: que espere, guarde la salida y devuelva el código de retorno,
   con un tope de tiempo. `run_program` no espera y tira la salida.
3. **Listar un directorio**: nombres, tamaños y si es directorio.
4. **Leer una variable de entorno.**
5. **Pasar `http.dash` y `red.dash` de Tachyon a `lib/` de Dash**, con POST y cabeceras propias.
6. **Información de depuración en dashc**: líneas, direcciones y variables. Más adelante, una librería de
   depuración para lanzar un programa, parar, ir paso a paso y leer su memoria.
7. **Construir ventanas MUI desde un `.dashui` en tiempo de ejecución**, para la vista previa. Ahora el
   `.dashui` se convierte a código al compilar.

## Fases

- **F0. Prueba del asistente**: un "hola" a OpenRouter desde FS-UAE. Comprueba TLS, cabeceras, UTF-8 y tiempos.
- **F1. El esqueleto del IDE**: la ventana oscura, el editor de código con colores, abrir, guardar, compilar
  con dashc, ejecutar y saltar a los errores.
- **F2. El asistente** en su panel, con las herramientas y los permisos.
- **F3. El editor de `.dashui`** con vista previa en vivo.
- **F4. El depurador**: puntos de parada, paso a paso, variables y pila.
- **F5. Acabado**: proyectos, catálogos de idioma, el paquete `.lha` y la publicación en Aminet, la web y GitHub.

## Pruebas

- Para el asistente, un servidor falso en el PC (Python) que imita OpenRouter con respuestas grabadas, para
  no gastar en cada prueba. Solo unas pocas pruebas a mano con la API de verdad.
- El IDE, en FS-UAE con MUI 5 (`DASH_EMU_SYS_MUI`), con clics reales por `input.device` y capturas de pantalla.

## Riesgos

- **Memoria**: cada petición del asistente reenvía todo el historial; además están el editor y el depurador.
  Hay que medir cuánta RAM rápida necesita.
- **Velocidad**:
  - El editor tiene que dibujar rápido en un 68020 con muchos colores.
  - El saludo de TLS de cada petición puede tardar segundos.
- **Seguridad**: el modelo puede pedir órdenes que borren cosas. Por eso pregunta antes por defecto.
- **Depurador**: es lo más delicado. Un fallo en el programa depurado no debe tumbar el IDE.
