# Lo que falta para publicar la primera versión

Inferencia y Forja funcionan en FS-UAE con todas sus pruebas. Publicarlas lo decide el usuario; antes conviene:

1. **Dash 2.0 publicado.** Las piezas que usan los dos (rama `ide-piezas` de Dash) tienen que llegar a `dashc` y a
   `main`. Forja necesita además dashc para el Amiga (`make amiga`) en su propio paquete o en el de Dash.
2. **Probar en un Amiga de verdad**, con un 68020 a 14 MHz y con algo más rápido (68030, 68060, PiStorm con
   Emu68). Lo que más preocupa: en el emulador, con la CPU a la velocidad de un 68020, el saludo TLS de AmiSSL no
   acabó en un minuto (F0). Con un 68020 sin más, Inferencia puede no llegar a OpenRouter ni a Anthropic; con un
   modelo en casa (Ollama, por HTTP) no hay TLS.
3. **El inglés**: los catálogos de los dos programas (tarea I11b y F10b del bucle). Ahora todo sale en castellano.
4. **Probar con la API de verdad lo que cuesta dinero**: Anthropic directo y el coste que da OpenRouter con un
   modelo de pago. Anthropic aún no va en streaming.
5. **Fallos de Dash pendientes**, rodeados en el código: un temporal pasado a una función se libera antes de
   tiempo (pieza 23) y, en Forja, una orden ARexx que redibuja recibía el RESULT anterior (pieza 24, que dashc no
   reproduce: quizá el `env_set` de la sonda tarda y el cliente se cansa de esperar).
6. **Aminet**: un `.readme` con su formato (Short, Author, Type, Version, Requires...) para cada `.lha`, y capturas.
7. **Opcional**: iconos con más colores (NewIcons o los de 3.5+), y un instalador con Installer como el de Trasfondo.

Los paquetes salen con `python3 tools/paquete.py VERSIÓN [DASH_DIR]` en cada repo: `build/inferencia-0.1.lha` (unos
145 KB) y `build/forja-0.1.lha` (unos 135 KB).
