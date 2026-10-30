#!/bin/sh
# Arranca Amiberry con el sistema del vídeo en la pantalla virtual :78 (Xvfb, que debe estar en marcha)
V=$HOME/.cache/video-inferencia
rm -f "$XDG_RUNTIME_DIR/amiberry.sock"
DISPLAY=:78 SDL_VIDEODRIVER=x11 SDL_AUDIODRIVER=dummy setsid amiberry -f "$V/video.uae" -s use_gui=no > "$V/amiberry.log" 2>&1 &
echo $! > "$V/amiberry.pid"
