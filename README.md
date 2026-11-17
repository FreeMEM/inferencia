# Inferencia

*[English](README.en.md) | Castellano*

La IA en el Amiga. Hablas con un modelo de lenguaje desde una ventana MUI, y el modelo puede trabajar en tu
sistema: leer y cambiar ficheros, ejecutar órdenes del Shell, mandar órdenes ARexx a otros programas y mirar el
sistema. Antes de cambiar algo, pregunta.

Es una versión de prueba: funciona en el emulador, pero aún no se ha probado en un Amiga de verdad. Habla en
castellano o en inglés, según el idioma de las Preferencias de Locale (el catálogo inglés va en `Catalogs/`).

## Qué necesita

- AmigaOS 3.0 o mejor, con un 68020 o mejor.
- MUI 5, o MUI 3.8. Con MUI 3.8, el cuadro para escribir es de una línea (Return manda la pregunta) salvo que esté
  instalado MCC_Textinput (de Aminet).
- Una pila TCP/IP (Roadshow, AmiTCP, Miami...) y AmiSSL 5 para HTTPS.
- El reloj en hora: AmiSSL comprueba las fechas de los certificados.
- Una clave de [OpenRouter](https://openrouter.ai) o de Anthropic, o un modelo en un PC de tu red (Ollama, LM
  Studio), que no necesita clave.

## Instalar

Copia el cajón Inferencia donde quieras. Ábrelo y pulsa Amiga-P para las preferencias:
- **Proveedor**: OpenRouter, Anthropic, u "OpenAI y compatibles" (para Ollama y LM Studio).
- **Dirección**: la del proveedor. Con Ollama, algo como `http://192.168.1.10:11434/v1/chat/completions`.
- **Clave nueva**: la clave. No se enseña; si dejas el campo vacío, se queda la que había.
- **Modelo**: por ejemplo `anthropic/claude-sonnet-5.5` en OpenRouter, o `claude-sonnet-5-5` en Anthropic.
- **Tope**: los caracteres de conversación a partir de los cuales se resume (60000 si se deja vacío).

"Usar" las deja hasta reiniciar; "Guardar", también en `ENVARC:Inferencia/`.

## Uso

- Escribe abajo. Return empieza otra línea; Amiga+Return o el botón Enviar mandan la pregunta.
- La respuesta va apareciendo según llega. Parar la corta.
- Arriba se ven los tokens y lo que lleva gastado la conversación.
- Menú Proyecto: conversación nueva, abrir y guardar conversaciones, preferencias.

### Lo que puede hacer el modelo

| Herramienta | Qué hace | ¿Pregunta? |
|---|---|---|
| leer, listar, buscar | Ficheros y cajones | No |
| escribir, editar | Cambia ficheros (enseña el cambio antes) | Sí |
| orden | Ejecuta una línea del Shell | Sí |
| arexx, puertos | Órdenes ARexx a otros programas | arexx sí |
| sistema | Memoria, versión, volúmenes, asignaciones, tareas | No |
| entorno | Variables de ENV: | Para poner, sí |
| portapapeles | Lee y escribe el portapapeles | Para escribir, sí |
| ayuda | Busca en la ayuda de Dash (`DASH:Ayuda/Dash.ayuda`, o `ENV:Inferencia/ayuda`) | No |

Al preguntar, sale "Sí", "No" y "Siempre". "Siempre" lo apunta en `ENVARC:Inferencia/sin_permiso` (separado por
comas: `orden list,arexx FORJA.1,entorno`), y ya no vuelve a preguntar por eso.

Si [Forja](https://github.com/FreeMEM/forja), el IDE de Dash, tiene abierto el fichero que se cambia, el cambio se
hace en el editor de Forja: queda sin guardar y se puede deshacer.

### El copiloto de Forja

Forja trae una extensión, Inferencia, que hace de copiloto: explica y arregla errores, documenta funciones, escribe
pruebas, cambia el código que eliges y, si se encienden, sugiere cómo sigue la línea al escribir. Usa esta Inferencia
por ARexx (la arranca si no está): lo que va a la conversación sale en esta ventana; lo que cambia código va en un
encargo aparte (`ENCARGO`), y Forja enseña el cambio para aceptarlo o no. Los encargos pueden leer ficheros y buscar
en la ayuda de Dash, pero no cambiar nada ni ejecutar órdenes. Cómo se usa: el README de Forja.

### ARexx

Puerto `INFERENCIA.1`:
- `PREGUNTA texto`: manda la pregunta, sin esperar.
- `ESTADO`: libre, pidiendo, permiso u orden.
- `RESPUESTA`: la última respuesta, cuando está libre.
- `CONTEXTO fichero [desde hasta]` y `ADJUNTAR título` (con el texto en las líneas siguientes): van con la siguiente pregunta.
- `NUEVA`, `MOSTRAR`, `OCULTAR`, `GUARDAR fichero`, `CARGAR fichero`, `COSTE`, `MENSAJES`.
- `ENCARGO tipo` (con el texto en las líneas siguientes): una petición aparte de la conversación, para el copiloto de
  Forja (RC 5 si ya hay otra; un `completar` nuevo sustituye al que está en marcha). `ENCARGADO` dice `pidiendo`,
  `listo` (con las herramientas que usó en la línea siguiente y la respuesta debajo), `error` (y el motivo) o `nada`.
  `CANCELAR` lo corta.

## Compilar

Con [Dash](https://github.com/FreeMEM/FreeMEMLang) 2.0 (dashc): `./dash src/main.dash -o Inferencia`. El paquete:
`python3 tools/paquete.py 0.1`. Las pruebas, en el emulador: [tests/LEEME.md](tests/LEEME.md).

Escrito en Dash. Licencia MIT.
