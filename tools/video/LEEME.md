# El vídeo de Inferencia

Cómo se graba el vídeo de demostración (Forja + Inferencia con un hola mundo MUI, el editor de ventanas .dashui de
Forja y la palabra AMIGA en LightWave Modeler). Reutiliza las herramientas del vídeo de Trasfondo (`~/Projects/trasfondo/tools/video`:
socket de Amiberry, piloto del ratón y `Rodaje`, que saca 25 capturas por segundo).

- `preparar.sh DASH_DIR MODELO URL`: el sistema en `~/.cache/video-inferencia/sys` a partir del de RTG del vídeo
  de Trasfondo (AmigaOS 3.2, uaegfx a 1024x768), con Forja, Inferencia y dashc compilados con ese Dash, ARexx,
  LightWave y los encargos de `encargos/`. LightWave, RexxMast y las órdenes de C salen de Coffin R65 y van en
  `~/.cache/video-inferencia/kit` (no van al repo). Inferencia usa un servidor con el formato de OpenAI (Ollama),
  sin clave.
- `arrancar.sh`: Amiberry sin ventana en la pantalla virtual `:78` (`Xvfb :78 -screen 0 1920x1080x24`).
- `toma.sh DASH_DIR forja|lightwave|dashui CARPETA [MODELO]` (con `URL=...`): arranca desde cero y graba la escena con
  `guion.py`. El guion teclea el encargo con el agente (`agente.c`: el de Trasfondo con las teclas muertas, para
  los acentos), pulsa Siempre en cada permiso (lo busca con tesseract) y espera a que salga el resultado. La escena
  dashui no usa el modelo: abre `saludo.dashui`, la vista previa, cambia un botón, guarda y ejecuta `saludo.dash`.
- `montar.py toma1 toma2 toma3 salida.mp4`: el vídeo de 1920x1080, como el segundo de Trasfondo: a la izquierda lo
  que se va haciendo, a la derecha la música con su espectro y la bola Boing, abajo un scroller; los encargos salen
  enteros en una ficha con la toma parada; tramos acelerados (x4 mientras el modelo piensa) y las pantallas
  entrelazadas de LightWave. La música, Space Debris de Captain, en `~/.cache/video-inferencia/musica` (de
  modland.com, pasada a WAV con `openmpt123` y a 16 bits con ffmpeg; no va al repo).

Lo aprendido: un guion ARexx sin comentario en la primera línea da "Program not found" (los modelos pequeños lo
toman por que rx no existe); qwen3-coder 30B en Ollama hace las dos escenas, pero no siempre a la primera, y
gpt-oss 20B no usa las herramientas.
