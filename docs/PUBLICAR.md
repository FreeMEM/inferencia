# Lo que falta para publicar la primera versión

Inferencia y Forja funcionan en FS-UAE con todas sus pruebas. Publicarlas lo decide el usuario; antes conviene:

1. **Dash 2.0 publicado.** Las piezas que usan los dos (rama `ide-piezas` de Dash) tienen que llegar a `dashc` y a
   `main`. Forja necesita además dashc para el Amiga (`make amiga`) en su propio paquete o en el de Dash.
2. **Probar en un Amiga de verdad**, con un 68020 a 14 MHz y con algo más rápido (68030, 68060, PiStorm con
   Emu68). Lo que más preocupa: en el emulador, con la CPU a la velocidad de un 68020, el saludo TLS de AmiSSL no
   acabó en un minuto (F0). Con un 68020 sin más, Inferencia puede no llegar a OpenRouter ni a Anthropic; con un
   modelo en casa (Ollama, por HTTP) no hay TLS.
3. **El inglés**: hecho con catálogos. Falta que alguien de habla inglesa los repase, y que los errores de red de
   lib/red (en inglés de origen) tengan versión en castellano: hoy salen en inglés en los dos idiomas.
4. **Probar con la API de verdad lo que cuesta dinero**: Anthropic directo y el coste que da OpenRouter con un
   modelo de pago. Anthropic aún no va en streaming.
5. **Sin fallos de Dash pendientes.** La pieza 23 (un temporal liberado antes de tiempo) está arreglada en Dash
   (6df8f2d). La 24 (el RESULT anterior al redibujar en una orden ARexx) ya no sale con Dash 2e972f6: Forja
   redibuja dentro de la orden otra vez, sin el rodeo, y sus pruebas pasan.
6. **Aminet**: un `.readme` con su formato (Short, Author, Type, Version, Requires...) para cada `.lha`, y capturas.
7. **Opcional**: iconos con más colores (NewIcons o los de 3.5+), y un instalador con Installer como el de Trasfondo.

Los paquetes salen con `python3 tools/paquete.py VERSIÓN [DASH_DIR]` en cada repo: `build/inferencia-0.1.lha` (unos
145 KB) y `build/forja-0.1.lha` (unos 135 KB).
