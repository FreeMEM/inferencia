"""Mover y cambiar de tamaño ventanas arrastrando con el ratón (título y gadget de tamaño)."""
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/Projects/trasfondo/tools/video"))
import amiga
import piloto as p
from amiberry import orden


def arrastrar(desde, hasta, dur=0.8):
    p.mover_a(*desde, dur=0.4)
    orden("SEND_MOUSE", 0, 0, 1)
    time.sleep(0.2)
    p.mover_a(*hasta, dur=dur, botones=1)
    time.sleep(0.2)
    orden("SEND_MOUSE", 0, 0, 0)
    time.sleep(0.6)


def colocar(titulo, x, y, ancho, alto):
    v = amiga.ventana(titulo)
    _, _, vx, vy, va, vh = v
    # por el título (a la derecha del gadget de cerrar)
    arrastrar((vx + 60, vy + 5), (x + 60, y + 5))
    v = amiga.ventana(titulo)
    _, _, vx, vy, va, vh = v
    arrastrar((vx + va - 6, vy + vh - 4), (x + ancho - 6, y + alto - 4))
    return amiga.ventana(titulo)
