"""El montaje del vídeo de Inferencia y Forja: de las tomas (toma.json y sus capturas) a un vídeo de 1920x1080 con
aire de demo. Sale del de Trasfondo (tools/video de ese repo y ~/.cache/video-trasfondo2): mismas columnas, rótulos
y scroller, con los colores de Inferencia.

    python3 montar.py <toma> [<toma>...] <salida.mp4> [--prueba SEGUNDOS]

- En el centro, la pantalla del Amiga (RTG 1024x768 a 1280x960; la entrelazada de LightWave, a 1280x1024), con
  subtítulos, clics, recuadros y acercamientos.
- A la izquierda, el logo, el capítulo y la lista de lo que se va haciendo: se mueve sola y marca lo de ahora.
- A la derecha, la música (un mod de Amiga), con su espectro y una bola Boing que bota.
- Abajo, un scroller con lo que se va viendo; al final, los saludos.
- Los encargos que lee Inferencia salen enteros en una ficha sobre la pantalla, con la toma parada.
- Las esperas (Inferencia pensando, el agente tecleando) van aceleradas, con su aviso. La música se apaga al final.
"""
import bisect
import json
import math
import multiprocessing
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 25
AQUI = os.path.dirname(os.path.abspath(__file__))
TOPAZ = os.path.expanduser("~/.cache/video-trasfondo/fuentes/TopazPlus_a1200_v1.0.ttf")
MUSICA = os.path.expanduser("~/.cache/video-inferencia/musica/space_debris.wav")

AZUL_WB = (0, 85, 170)
ACENTO = (255, 200, 80)           # el ámbar del cursor de Inferencia
AZUL = (90, 150, 230)             # el azul de lo que escribe el usuario en Inferencia
MARCA = (255, 136, 0)
BLANCO = (232, 232, 222)
FONDO = (16, 16, 22)              # el fondo negro de Inferencia y Forja
RAYA = (22, 22, 30)
TENUE = (44, 40, 30)
GRIS = (120, 120, 132)
PX, PY = 320, 0                   # la pantalla del Amiga en el vídeo (1280x1024)
BANDA = 1024                      # la franja del scroller, debajo
RECORTE = (56, 38, 696, 550)      # la pantalla nativa (no RTG) dentro de la captura de Amiberry
PORTADA, RÓTULO, CIERRE_MIN, CIERRE_MAX = 9.0, 2.8, 14.0, 24.0
VEL_SCROLL = 170

# Por escena (el título del capítulo de la toma, en castellano en las dos lenguas): su título en el vídeo, lo de la
# columna izquierda (hora de la toma, texto) si la toma no lo trae, la ficha del encargo (hora de la toma o None: la
# del rasgo "Inferencia trabaja"; segundos; ruta en el Amiga y fichero por lengua), tramos acelerados de más y
# subtítulos corregidos.
ESCENAS = {
    "1 - Forja e Inferencia": {
        "titulo": {"es": ("Forja e Inferencia", "Un hola mundo MUI, pedido en castellano"),
                   "en": ("Forja and Inferencia", "An MUI hello world, asked for in plain English")},
        "rasgos": [(1.0, "Forja e Inferencia"), (5.0, "El modelo, en casa"), (9.0, "El encargo"),
                   (19.6, "Inferencia trabaja"), (58.1, "Pide permiso"), (72.6, "Forja compila"),
                   (85.1, "Hola mundo MUI")],
        "ficha": (None, 13.0, {"es": ("DH0:Encargos/hola.txt", "encargos/hola.txt"),
                               "en": ("DH0:Tasks/hello.txt", "en/hello.txt")}),
    },
    "3 - Ventanas .dashui": {
        "titulo": {"es": ("Ventanas .dashui", "El editor de ventanas de Forja, con MUI de verdad"),
                   "en": (".dashui windows", "Forja's window editor, with real MUI")},
        "rapidos_editar": 3,         # de poco después del rasgo "Cambios en vivo" al recuadro de la vista previa
    },
    "2 - LightWave": {
        "titulo": {"es": ("LightWave", "Inferencia maneja otros programas por ARexx"),
                   "en": ("LightWave", "Inferencia drives other programs over ARexx")},
        "rasgos": [(1.3, "LightWave Modeler 5"), (27.3, "Volver al Workbench"), (31.7, "El encargo"),
                   (42.7, "Inferencia trabaja"), (74.6, "Pide permiso"), (94.8, "Guion ARexx y rx"),
                   (100.8, "AMIGA en 3D")],
        "ficha": (None, 16.0, {"es": ("DH0:Encargos/letras.txt", "encargos/letras.txt"),
                               "en": ("DH0:Tasks/letters.txt", "en/letters.txt")}),
        "subtitulos": {"LightWave Modeler, de 1995, se maneja con guiones ARexx.":
                       "LightWave Modeler 5, de 1996, se maneja con guiones ARexx."},
    },
}
ORDEN = ["1 - Forja e Inferencia", "3 - Ventanas .dashui", "2 - LightWave"]

TEXTOS = {
    "es": {
        "titulo": "Inferencia y Forja: una IA y un IDE para el Amiga",
        "portada": ["Una IA que trabaja en el Amiga", "Con Forja, el IDE de Dash, y LightWave 3D",
                    "AmigaOS 3.2, MUI 5, ARexx - escritos en Dash"],
        "scroll_portada": "*** INFERENCIA Y FORJA *** UNA IA Y UN IDE PARA EL AMIGA, ESCRITOS EN DASH *** "
                          "GRABADO EN DIRECTO EN UN AMIGA EMULADO CON RTG ***",
        "scroll": {
            "Forja e Inferencia": "FORJA, EL IDE DE DASH, E INFERENCIA, UNA IA PARA EL AMIGA, HABLANDO POR AREXX...",
            "El modelo, en casa": "EL MODELO ES QWEN3-CODER EN OLLAMA, EN UN PC DE CASA CON UNA RTX 3050: SIN NUBE Y "
                                  "SIN PAGAR...",
            "Inferencia trabaja": "LEE, ESCRIBE, MANDA ÓRDENES AREXX... Y LO VES TODO EN DIRECTO EN SU VENTANA MUI...",
            "Pide permiso": "NADA DE TOCAR TUS FICHEROS SIN PREGUNTAR: SÍ, NO O SIEMPRE...",
            "Forja compila": "DASHC COMPILA EN EL PROPIO AMIGA: NADA DE COMPILAR EN EL PC...",
            "Abrir un .dashui": "LAS VENTANAS SE DIBUJAN EN UN FICHERO .DASHUI, EL MISMO QUE EDITA LA EXTENSIÓN DE VS "
                                "CODE...",
            "Vista previa con MUI": "LA VISTA PREVIA NO ES UN DIBUJO: ES MUI 5 DE VERDAD...",
            "Compilar y ejecutar": "IMPORT \"SALUDO.DASHUI\" Y LA VENTANA ES UN STRUCT CON SUS OBJETOS POR NOMBRE...",
            "LightWave Modeler 5": "LIGHTWAVE 3D, EL DE LAS SERIES DE LOS NOVENTA, SE DEJA MANEJAR POR AREXX...",
            "Guion ARexx y rx": "INFERENCIA LEE EL MANUAL DEL MODELER, ESCRIBE EL GUION Y LO PRUEBA CON RX...",
            "AMIGA en 3D": "INFERENCIA, FORJA Y DASH: LIBRES, MIT, EN GITHUB.COM/FREEMEM...",
        },
        "saludos": "*** SALUDOS A *** CAPTAIN POR SPACE DEBRIS *** NEWTEK POR LIGHTWAVE *** STEFAN STUNTZ Y EL EQUIPO "
                   "DE MUI *** LA GENTE DE COFFINOS *** AMIBERRY *** OLLAMA *** AMINET *** "
                   "Y A TODOS LOS QUE MANTENÉIS VIVO EL AMIGA! ***",
        "musica": {"suena": "SUENA", "tema": "Space Debris", "autores": ["Captain", "(Markus Kaarlonen)"],
                   "grupo": "Un clásico del Amiga", "demo": ["Un mod de ProTracker", "de 4 canales"],
                   "grabado": ["AmigaOS 3.2, Amiberry", "RTG 1024x768", "Solo se aceleran las esperas"]},
        "encargo": "El encargo:",
        "portada_capitulo": "Inferencia y Forja",
        "creditos_capitulo": "Créditos",
        "creditos": [
            ("t", "INFERENCIA Y FORJA"),
            ("s", "Una IA y un IDE para el Amiga, escritos en Dash"),
            ("n", "github.com/FreeMEM/inferencia"),
            ("n", "github.com/FreeMEM/forja"),
            ("s", ""),
            ("t", "CÓDIGO"),
            ("n", "FreeMEM"),
            ("s", ""),
            ("t", "MÚSICA"),
            ("n", "Space Debris - Captain (Markus Kaarlonen)"),
            ("s", ""),
            ("t", "EL MODELO"),
            ("n", "qwen3-coder en Ollama, en un PC de casa"),
            ("s", ""),
            ("t", "HECHO CON"),
            ("n", "Dash 2.0 - MUI 5 - ARexx"),
            ("s", ""),
            ("t", "GRABADO EN"),
            ("n", "AmigaOS 3.2 - Amiberry - LightWave Modeler 5"),
            ("s", ""),
            ("t", "SALUDOS"),
            ("n", "Captain - NewTek - el equipo de MUI"),
            ("n", "La gente de CoffinOS - Amiberry - Ollama - Aminet"),
            ("s", "y a todos los que mantenéis vivo el Amiga!"),
        ],
    },
    "en": {
        "titulo": "Inferencia and Forja: an AI and an IDE for the Amiga",
        "portada": ["An AI that works on the Amiga", "With Forja, the Dash IDE, and LightWave 3D",
                    "AmigaOS 3.2, MUI 5, ARexx - written in Dash"],
        "scroll_portada": "*** INFERENCIA AND FORJA *** AN AI AND AN IDE FOR THE AMIGA, WRITTEN IN DASH *** "
                          "RECORDED LIVE ON AN EMULATED AMIGA WITH RTG ***",
        "scroll": {
            "Forja and Inferencia": "FORJA, THE DASH IDE, AND INFERENCIA, AN AI FOR THE AMIGA, TALKING OVER AREXX...",
            "A model at home": "THE MODEL IS QWEN3-CODER ON OLLAMA, ON A HOME PC WITH AN RTX 3050: NO CLOUD, NOTHING "
                               "TO PAY...",
            "Inferencia at work": "IT READS, WRITES, SENDS AREXX COMMANDS... AND YOU SEE IT ALL LIVE IN ITS MUI "
                                  "WINDOW...",
            "It asks first": "IT NEVER TOUCHES YOUR FILES WITHOUT ASKING: YES, NO OR ALWAYS...",
            "Forja builds it": "DASHC COMPILES ON THE AMIGA ITSELF: NO CROSS-COMPILING ON A PC...",
            "Opening a .dashui": "WINDOWS ARE DRAWN IN A .DASHUI FILE, THE SAME ONE THE VS CODE EXTENSION EDITS...",
            "Real MUI preview": "THE PREVIEW IS NOT A DRAWING: IT IS REAL MUI 5...",
            "Build and run": "IMPORT \"GREETING.DASHUI\" AND THE WINDOW IS A STRUCT WITH ITS OBJECTS BY NAME...",
            "LightWave Modeler 5": "LIGHTWAVE 3D, THE ONE FROM THE NINETIES TV SHOWS, CAN BE DRIVEN OVER AREXX...",
            "ARexx script and rx": "INFERENCIA READS THE MODELER MANUAL, WRITES THE SCRIPT AND TRIES IT WITH RX...",
            "AMIGA in 3D": "INFERENCIA, FORJA AND DASH: FREE, MIT LICENSED, AT GITHUB.COM/FREEMEM...",
        },
        "saludos": "*** GREETINGS TO *** CAPTAIN FOR SPACE DEBRIS *** NEWTEK FOR LIGHTWAVE *** STEFAN STUNTZ AND THE "
                   "MUI TEAM *** THE COFFINOS FOLKS *** AMIBERRY *** OLLAMA *** AMINET *** "
                   "AND EVERYONE WHO KEEPS THE AMIGA ALIVE! ***",
        "musica": {"suena": "NOW PLAYING", "tema": "Space Debris", "autores": ["Captain", "(Markus Kaarlonen)"],
                   "grupo": "An Amiga classic", "demo": ["A 4-channel", "ProTracker module"],
                   "grabado": ["AmigaOS 3.2, Amiberry", "RTG 1024x768", "Waits sped up, nothing else"]},
        "encargo": "The task:",
        "portada_capitulo": "Inferencia and Forja",
        "creditos_capitulo": "Credits",
        "creditos": [
            ("t", "INFERENCIA AND FORJA"),
            ("s", "An AI and an IDE for the Amiga, written in Dash"),
            ("n", "github.com/FreeMEM/inferencia"),
            ("n", "github.com/FreeMEM/forja"),
            ("s", ""),
            ("t", "CODE"),
            ("n", "FreeMEM"),
            ("s", ""),
            ("t", "MUSIC"),
            ("n", "Space Debris - Captain (Markus Kaarlonen)"),
            ("s", ""),
            ("t", "THE MODEL"),
            ("n", "qwen3-coder on Ollama, on a home PC"),
            ("s", ""),
            ("t", "MADE WITH"),
            ("n", "Dash 2.0 - MUI 5 - ARexx"),
            ("s", ""),
            ("t", "RECORDED ON"),
            ("n", "AmigaOS 3.2 - Amiberry - LightWave Modeler 5"),
            ("s", ""),
            ("t", "GREETINGS"),
            ("n", "Captain - NewTek - the MUI team"),
            ("n", "The CoffinOS folks - Amiberry - Ollama - Aminet"),
            ("s", "and everyone who keeps the Amiga alive!"),
        ],
    },
}
T = TEXTOS["es"]            # la lengua de las tomas: main() la cambia


def fuente(tam):
    return ImageFont.truetype(TOPAZ, tam)


def envolver(texto, f, ancho):
    palabras, lineas, l = texto.split(), [], ""
    for p in palabras:
        prueba = (l + " " + p).strip()
        if f.getlength(prueba) <= ancho:
            l = prueba
        else:
            lineas.append(l)
            l = p
    if l:
        lineas.append(l)
    return lineas


def bola_boing(d, giro=0.0):
    """La bola Boing: esfera de cuadros rojos y blancos, girada (giro en radianes) como en la demo de 1984."""
    y, x = np.mgrid[0:d, 0:d].astype(float)
    r = d / 2
    nx, ny = (x - r + 0.5) / r, (y - r + 0.5) / r
    dentro = nx * nx + ny * ny <= 1
    nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
    inc = math.radians(-20)
    rx = nx * math.cos(inc) - ny * math.sin(inc)
    ry = nx * math.sin(inc) + ny * math.cos(inc)
    lon = np.arctan2(rx, nz) + giro
    lat = np.arcsin(np.clip(ry, -1, 1))
    c = (np.floor((lon + math.pi) / (math.pi / 8)) + np.floor((lat + math.pi / 2) / (math.pi / 8))) % 2
    luz = 0.55 + 0.45 * np.clip(-0.4 * nx - 0.5 * ny + 0.75 * nz, 0, None)
    rojo = np.stack([230 * luz, 30 * luz, 30 * luz], -1)
    blanco = np.stack([245 * luz] * 3, -1)
    rgb = np.where(c[..., None] == 1, rojo, blanco)
    a = np.where(dentro, 255, 0)
    return Image.fromarray(np.dstack([rgb, a]).astype("uint8"), "RGBA")


def rotulo(titulo, subtitulo="", numero=""):
    """Un rótulo entre capítulos: azul Workbench 1.3, Topaz, raya ámbar."""
    img = Image.new("RGB", (W, H), AZUL_WB)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 4):
        d.line([(0, y + 3), (W, y + 3)], fill=(0, 76, 153))
    x0, y = 180, 360
    if numero:
        d.text((x0, y - 70), numero, font=fuente(40), fill=(150, 185, 235))
    d.text((x0, y), titulo, font=fuente(96), fill=(255, 255, 255))
    y += 96 + 30
    d.rectangle([x0, y, x0 + 520, y + 10], fill=ACENTO)
    y += 50
    for l in envolver(subtitulo, fuente(44), 1500):
        d.text((x0, y), l, font=fuente(44), fill=(220, 230, 255))
        y += 64
    bola = bola_boing(220, 0.6)
    img.paste(bola, (W - 420, 330), bola)
    return img


def logo(ancho):
    """El logo: una bola Boing pequeña y "Inferencia" en Topaz, con fondo transparente."""
    f = fuente(200)
    texto = "Inferencia"
    x0, y0, x1, y1 = f.getbbox(texto)
    bola = bola_boing(180, 0.4)
    alto = max(bola.height, y1 - y0)
    im = Image.new("RGBA", (bola.width + 50 + x1 - x0, alto), (0, 0, 0, 0))
    im.paste(bola, (0, (alto - bola.height) // 2), bola)
    ImageDraw.Draw(im).text((bola.width + 50 - x0, (alto - (y1 - y0)) // 2 - y0), texto, font=f,
                            fill=BLANCO + (255,))
    return im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)


# --- La música: su espectro, cuadro a cuadro ------------------------------------------------------------------------
def espectro(wav, n_cuadros, bandas=16):
    """Para cada cuadro del vídeo, la altura (0-1) de cada banda del espectro de la música."""
    import wave
    w = wave.open(wav)
    sr, nch = w.getframerate(), w.getnchannels()
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, nch).mean(1)
    a /= np.abs(a).max() + 1e-9
    n = 2048
    lim = np.geomspace(40, 12000, bandas + 1)
    frec = np.fft.rfftfreq(n, 1 / sr)
    r = np.zeros((n_cuadros, bandas), np.float32)
    ventana = np.hanning(n)
    for i in range(n_cuadros):
        s = int(i / FPS * sr)
        trozo = a[s:s + n]
        if len(trozo) < n:
            break
        m = np.abs(np.fft.rfft(trozo * ventana))
        for b in range(bandas):
            sel = (frec >= lim[b]) & (frec < lim[b + 1])
            r[i, b] = m[sel].mean() if sel.any() else 0
    r = np.log1p(r * 4) / np.log1p(r.max() * 4 + 1e-9) if r.max() else r
    for i in range(1, n_cuadros):                                     # caen despacio, como en un VU
        r[i] = np.maximum(r[i], r[i - 1] * 0.86)
    return r


def duracion_wav(wav):
    import wave
    w = wave.open(wav)
    return w.getnframes() / w.getframerate()


# --- La pantalla del Amiga ------------------------------------------------------------------------------------------
def pantalla(fichero):
    """La captura a 1280x1024: la de RTG a escala, centrada; la nativa con líneas dobles y barrido."""
    cap = Image.open(fichero).convert("RGB")
    if cap.width >= 1000:
        k = min(1280 / cap.width, 1024 / cap.height)
        cap = cap.resize((round(cap.width * k), round(cap.height * k)), Image.LANCZOS)
        lienzo = Image.new("RGB", (1280, 1024), (0, 0, 0))
        lienzo.paste(cap, ((1280 - cap.width) // 2, (1024 - cap.height) // 2))
        return lienzo
    cap = cap.crop(RECORTE)
    # de cada par de líneas, la más clara: en una pantalla entrelazada (LightWave) una de las dos sale negra
    a = np.asarray(cap).reshape(256, 2, 640, 3).max(axis=1)
    cap = Image.fromarray(a.astype("uint8")).resize((1280, 1024), Image.NEAREST)
    d = ImageDraw.Draw(cap, "RGBA")
    for y in range(3, 1024, 4):
        d.line([(0, y), (1279, y)], fill=(0, 0, 0, 70))
    return cap


def escala(toma):
    """(px del vídeo por px del Amiga en x, en y, margen x, margen y) dentro de los 1280x1024."""
    w, h = toma.get("pantalla", (640, 256))
    if h < 400:
        return (2, 4, 0, 0)
    k = min(1280 / w, 1024 / h)
    return (k, k, (1280 - w * k) / 2, (1024 - h * k) / 2)


def acercar(cap, t, toma, esc):
    for (t0, t1, x, y, an, al) in toma.get("zooms", []):
        if t0 <= t <= t1:
            a = max(0.0, min(1.0, (t - t0) / 0.8, (t1 - t) / 0.8))
            a = a * a * (3 - 2 * a)
            rx, ry, rw, rh = esc[2] + x * esc[0], esc[3] + y * esc[1], an * esc[0], an * esc[0] * 4 / 5
            rx = max(0, min(1280 - rw, rx)); ry = max(0, min(1024 - rh, ry))
            caja = (rx * a, ry * a, 1280 + (rx + rw - 1280) * a, 1024 + (ry + rh - 1024) * a)
            return cap.resize((1280, 1024), Image.LANCZOS, box=caja), caja
    return cap, None


def a_video(x, y, esc, z):
    x, y = esc[2] + x * esc[0], esc[3] + y * esc[1]
    if z:
        cx0, cy0, cx1, cy1 = z
        x = (x - cx0) * 1280 / (cx1 - cx0); y = (y - cy0) * 1024 / (cy1 - cy0)
    return PX + int(x), PY + int(y)


def ficha(titulo, fichero):
    """El encargo tal cual, en una ficha oscura que tapa la pantalla del Amiga."""
    texto = open(os.path.join(AQUI, fichero), encoding="utf-8").read().strip()
    f, ft = fuente(26), fuente(34)
    lineas = []
    for parrafo in texto.split("\n"):
        sangria = len(parrafo) - len(parrafo.lstrip())
        if not parrafo.strip():
            lineas.append("")
            continue
        for i, l in enumerate(envolver(parrafo, f, 1080 - sangria * 14)):
            lineas.append(" " * sangria + l)
    alto = 150 + len(lineas) * 34 + 40
    img = Image.new("RGBA", (1180, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, 1179, alto - 1], 14, fill=(10, 10, 14, 240), outline=ACENTO + (255,), width=3)
    d.text((40, 30), T["encargo"], font=fuente(26), fill=GRIS)
    d.text((40, 66), titulo, font=ft, fill=ACENTO)
    d.rectangle([40, 116, 1140, 117], fill=(70, 66, 50))
    y = 140
    for l in lineas:
        d.text((40, y), l, font=f, fill=BLANCO)
        y += 34
    return img


# --- Las columnas ---------------------------------------------------------------------------------------------------
class Montaje:
    def __init__(self, n_cuadros, lista, scroller, tomas, fichas):
        self.lista, self.tomas, self.fichas = lista, tomas, fichas
        self.logo = logo(290)
        self.f22, self.f26, self.f30, self.f32, self.f20 = fuente(22), fuente(26), fuente(30), fuente(32), fuente(20)
        self.espec = espectro(MUSICA, n_cuadros)
        self.bolas = [bola_boing(110, k * 2 * math.pi / 16 / 8) for k in range(16)]
        self.scroller = scroller
        self.lado = self._lado_derecho()

    def _lado_derecho(self):
        t = T["musica"]
        img = Image.new("RGB", (320, BANDA), FONDO)
        d = ImageDraw.Draw(img)
        y = 30
        d.text((20, y), t["suena"], font=self.f22, fill=ACENTO); y += 40
        d.text((20, y), t["tema"], font=fuente(36), fill=BLANCO); y += 48
        for l in t["autores"]:
            d.text((20, y), l, font=self.f26, fill=(210, 210, 200)); y += 32
        d.text((20, y), t["grupo"], font=self.f22, fill=GRIS); y += 44
        for l in t["demo"]:
            d.text((20, y), l, font=self.f20, fill=(170, 170, 160)); y += 26
        d.rectangle([20, 924, 300, 925], fill=(50, 50, 60))
        for i, l in enumerate(t["grabado"]):
            d.text((20, 936 + i * 26), l, font=self.f20, fill=GRIS)
        return img

    def fondo(self, capitulo, numero):
        img = Image.new("RGB", (W, H), FONDO)
        img.paste(self.logo, (15, 40), self.logo)
        d = ImageDraw.Draw(img)
        d.text((20, 112), numero, font=self.f22, fill=ACENTO)
        y = 142
        for l in envolver(capitulo, self.f30, 285):
            d.text((20, y), l, font=self.f30, fill=BLANCO); y += 36
        d.rectangle([20, 236, 300, 237], fill=(50, 50, 60))
        img.paste(self.lado, (1600, 0))
        return img

    def lista_en(self, d, tv):
        """Lo que se va haciendo, a la izquierda: hecho (azul), lo de ahora (blanco, con barra ámbar) y lo que falta
        (gris). Se desplaza suave para que lo de ahora quede a media altura."""
        hechos = [i for i, (tr, _) in enumerate(self.lista) if tr <= tv]
        act = hechos[-1] if hechos else -1
        paso = 34
        objetivo = act
        if act >= 0:
            a = min(1, (tv - self.lista[act][0]) / 0.6)
            objetivo = act - 1 + a * a * (3 - 2 * a)
        y0 = 560 - objetivo * paso
        for i, (tr, texto) in enumerate(self.lista):
            y = y0 + i * paso
            if y < 250 or y > 990:
                continue
            if i == act:
                a = min(1, (tv - tr) / 0.4)
                d.rectangle([12, y - 4, 12 + int(296 * a), y + 26], fill=TENUE)
                d.rectangle([12, y - 4, 16, y + 26], fill=ACENTO)
                d.text((26, y), texto, font=self.f22, fill=BLANCO)
            elif i < act:
                d.text((26, y), texto, font=self.f22, fill=AZUL)
            else:
                d.text((26, y), texto, font=self.f22, fill=(70, 70, 84))

    def derecha_viva(self, img, k, tv):
        d = ImageDraw.Draw(img)
        e = self.espec[min(k, len(self.espec) - 1)]
        x0, y0, alto = 1620, 520, 150
        for b, v in enumerate(e):
            h = int(alto * float(v))
            x = x0 + b * 17
            for y in range(y0 - h, y0, 6):
                frac = (y0 - y) / alto
                col = (int(90 + 165 * frac), int(150 + 50 * frac), int(230 - 150 * frac)) if frac < 0.8 else MARCA
                d.rectangle([x, y, x + 12, y + 3], fill=col)
        d.rectangle([1620, y0 + 4, 1890, y0 + 5], fill=(50, 50, 60))
        # la bola Boing bota (Space Debris va a unos 125 pulsos por minuto: un bote cada dos)
        fase = (tv * 125 / 60 / 2) % 1
        yb = 820 - int(200 * (1 - (2 * fase - 1) ** 2))
        xb = 1700 + int(60 * math.sin(tv * 0.9))
        sombra = Image.new("RGBA", (110, 110), (0, 0, 0, 0))
        bola = self.bolas[int(tv * 16) % 16]
        sombra.paste((0, 0, 0, 110), mask=bola.split()[3])
        img.paste(sombra, (xb + 18, yb + 14), sombra)
        img.paste(bola, (xb, yb), bola)

    def banda(self, img, tv):
        """El scroller de abajo, con onda y colores de copper."""
        off = int(tv * VEL_SCROLL)
        trozo = self.scroller.crop((off, 0, off + W, self.scroller.height))
        d = ImageDraw.Draw(img)
        d.rectangle([0, BANDA, W, H], fill=(8, 8, 12))
        d.line([(0, BANDA), (W, BANDA)], fill=ACENTO, width=2)
        for x in range(0, W, 8):
            dy = int(5 * math.sin(x / 140 + tv * 3))
            col = trozo.crop((x, 0, x + 8, trozo.height))
            img.paste(col, (x, BANDA + 8 + dy), col)


def tira_scroller(eventos, texto_final, t_total):
    """El scroller entero en una tira: cada texto entra por la derecha cuando toca, sin pisarse; al final, los
    saludos. Letras con un degradado de copper."""
    f = fuente(36)
    pos, x_fin = [], W
    for (tv, texto) in eventos:
        x = max(int(tv * VEL_SCROLL) + W, x_fin + 120)
        pos.append((x, texto))
        x_fin = x + int(f.getlength(texto))
    x = max(x_fin + 200, int(t_total * VEL_SCROLL) + W - int(f.getlength(texto_final)))
    pos.append((x, texto_final))
    largo = max(x + int(f.getlength(texto_final)) + W, int(t_total * VEL_SCROLL) + 2 * W)
    mascara = Image.new("L", (largo, 40), 0)
    for x, t in pos:                       # cada frase aparte: Pillow no dibuja bien texto más allá de x = 32767
        trozo = Image.new("L", (int(f.getlength(t)) + 8, 40), 0)
        ImageDraw.Draw(trozo).text((0, 0), t, font=f, fill=255)
        mascara.paste(trozo, (x, 0))
    grad = np.zeros((40, 1, 3), np.uint8)
    for y in range(40):                                               # copper: ámbar, blanco, azul
        s = y / 39
        c = np.array([255, 200, 80]) * (1 - s) * 2 if s < 0.5 else np.array([90, 150, 230]) * (s - 0.5) * 2
        c = c + np.array([255, 255, 255]) * (1 - abs(s - 0.5) * 2) * 0.6
        grad[y, 0] = np.clip(c, 0, 255)
    tira = Image.fromarray(np.repeat(grad, largo, 1)).convert("RGBA")
    tira.putalpha(mascara)
    return tira


# --- Componer un cuadro ---------------------------------------------------------------------------------------------
_m = None


def _iniciar(m):
    global _m
    _m = m


def _cuadro(trabajo):
    m = _m
    if trabajo[0] == "fijo":               # portada, rótulo o créditos: una imagen hecha, con el scroller
        _, k, tv, datos = trabajo
        img = Image.frombytes("RGB", (W, H), datos)
        m.banda(img, tv)
        return img.tobytes()
    _, k, tv, t, fichero, n, rapido, ficha_n = trabajo
    toma = m.tomas[n]
    esc = escala(toma)
    img = m.bases[n].copy()
    cap, z = acercar(pantalla(fichero), t, toma, esc)
    img.paste(cap, (PX, PY))
    d = ImageDraw.Draw(img, "RGBA")
    for (tm, dur, _, x, y, an, al) in toma["marcas"]:
        if tm <= t <= tm + dur:
            a = min(1, (t - tm) / 0.3, (tm + dur - t) / 0.3)
            x0, y0 = a_video(x, y, esc, z); x1, y1 = a_video(x + an, y + al, esc, z)
            for q in range(3):
                d.rectangle([x0 - 4 - q, y0 - 4 - q, x1 + 4 + q, y1 + 4 + q], outline=MARCA + (int(230 * a),))
    for (tc, x, y) in toma["clics"]:
        q = (t - tc) * FPS
        if 0 <= q < 8:
            cx, cy = a_video(x, y, esc, z)
            rr = 10 + q * 5
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=MARCA + (int(255 * (1 - q / 8)),), width=5)
    if ficha_n is not None:
        f_img, a = m.fichas[ficha_n[0]], ficha_n[1]
        capa = f_img.copy()
        capa.putalpha(capa.split()[3].point(lambda v: int(v * a)))
        img.paste(capa, (PX + (1280 - capa.width) // 2, PY + max(20, (1024 - capa.height) // 2)), capa)
    else:
        for (a, b, texto) in m.subs:
            if a <= tv < b:
                f = m.f32
                lineas = envolver(texto, f, 1180)[:2]
                alto = 46 * len(lineas) + 24
                y0 = PY + 1024 - alto - 24
                ancho = max(f.getlength(l) for l in lineas) + 48
                d.rounded_rectangle([960 - ancho / 2, y0, 960 + ancho / 2, y0 + alto], 10, fill=(0, 0, 0, 228))
                for i, l in enumerate(lineas):
                    d.text((960 - f.getlength(l) / 2, y0 + 14 + i * 46), l, font=f, fill=BLANCO)
        if rapido:
            d.rounded_rectangle([PX + 1280 - 150, 40, PX + 1280 - 20, 90], 8, fill=(0, 0, 0, 190))
            d.text((PX + 1280 - 135, 50), f">> x{rapido}", font=m.f30, fill=ACENTO)
    m.lista_en(ImageDraw.Draw(img), tv)
    m.derecha_viva(img, k, tv)
    m.banda(img, tv)
    return img.tobytes()


def srt_tiempo(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    args = sys.argv[1:]
    prueba = None
    if "--prueba" in args:
        i = args.index("--prueba"); prueba = float(args[i + 1]); del args[i:i + 2]
    carpetas, salida = args[:-1], args[-1]
    tomas = []
    for c in carpetas:
        toma = json.load(open(os.path.join(c, "toma.json")))
        toma["escena"] = ESCENAS[toma["capitulos"][0][1]]
        toma["clave"] = toma["capitulos"][0][1]
        toma["horas"] = [q[0] for q in toma["cuadros"]]
        toma["rapidos"] = toma.get("rapidos", []) + toma["escena"].get("rapidos", [])
        cambios = toma["escena"].get("subtitulos", {})
        toma["subtitulos"] = [[a, b, cambios.get(s, s)] for (a, b, s) in toma["subtitulos"]]
        tomas.append(toma)
    tomas.sort(key=lambda tm: ORDEN.index(tm["clave"]))
    global T
    lengua = tomas[0].get("lengua", "es")
    T = TEXTOS[lengua]
    for tm in tomas:
        esc_t = tm["escena"]
        tm["titulo"] = esc_t["titulo"][lengua]
        rasgos = tm.get("rasgos") or esc_t.get("rasgos", [])
        if "ficha" in esc_t:
            hora, dur, por_lengua = esc_t["ficha"]
            if hora is None:
                hora = next(t for (t, x) in rasgos if x in ("Inferencia trabaja", "Inferencia at work")) - 0.15
            tm["ficha"] = (hora, dur) + por_lengua[lengua]
        if "rapidos_editar" in esc_t:
            a = rasgos[2][0] + 2.1
            b = next(m[0] for m in tm["marcas"] if m[2] == "vista") - 0.8
            tm["rapidos"] = tm["rapidos"] + [(a, b, esc_t["rapidos_editar"])]
    fichas = [ficha(tm["ficha"][2], tm["ficha"][3]) if "ficha" in tm else None for tm in tomas]

    # El guion: portada; por toma, su rótulo y su trozo (esperas aceleradas, la ficha del encargo con la toma
    # parada); créditos
    plan, tv = [], PORTADA
    lista, subs, eventos = [], [], [(PORTADA - 4, T["scroll_portada"])]
    for n, toma in enumerate(tomas):
        esc_t = toma["escena"]
        plan.append(("rotulo", n, tv)); tv += RÓTULO
        t0, t1 = toma["capitulos"][0][0], toma["fin"]
        marcas_t, pasos = [], []
        ficha_t = toma.get("ficha")

        def factor(t):
            for (a, b, f) in toma["rapidos"]:
                if a <= t < b:
                    return f
            return 0
        t = t0
        while t < t1:
            if ficha_t and t >= ficha_t[0]:
                nf = int(ficha_t[1] * FPS)
                ficha_t = None
                for q in range(nf):
                    a = min(1.0, q / 12, (nf - q) / 12)
                    pasos.append((t, 0, (n, a)))
            marcas_t.append((t, tv + len(pasos) / FPS))
            pasos.append((t, factor(t), None))
            t += (factor(t) or 1) / FPS
        plan.append(("toma", n, tv, pasos))

        def a_video_t(ts, marcas_t=marcas_t):
            i = bisect.bisect_left([q[0] for q in marcas_t], ts)
            return marcas_t[min(i, len(marcas_t) - 1)][1]
        rasgos = toma.get("rasgos") or esc_t.get("rasgos", [])
        for (tr, texto) in rasgos:
            lista.append((a_video_t(tr), texto))
            if texto in T["scroll"]:
                eventos.append((a_video_t(tr), T["scroll"][texto]))
        ss = toma["subtitulos"]
        for i, (s0, s1, texto) in enumerate(ss):
            a = a_video_t(s0)
            b = a_video_t(s1 if s1 is not None else t1)
            sig = a_video_t(ss[i + 1][0]) if i + 1 < len(ss) else tv + len(pasos) / FPS
            b = min(max(b, a + 2.4 + len(texto) * 0.035), sig)
            subs.append((a, b, texto))
        tv += len(pasos) / FPS
    t_musica = duracion_wav(MUSICA)
    cierre = min(max(CIERRE_MIN, t_musica - tv), CIERRE_MAX)
    t_total = tv + cierre
    scroller = tira_scroller(eventos, T["saludos"], t_total)

    n_total = int(t_total * FPS)
    m = Montaje(n_total + FPS, lista, scroller, tomas, fichas)
    m.subs = subs
    m.bases = {n: m.fondo(tm["titulo"][0], f"{n + 1:02d} / {len(tomas):02d}") for n, tm in enumerate(tomas)}
    print(f"vídeo: {t_total:.1f} s (música {t_musica:.1f} s, créditos {cierre:.1f} s)", flush=True)
    t_completo = t_total
    if prueba:
        t_total = min(t_total, prueba)
        n_total = int(t_total * FPS)

    crudo = salida + ".crudo.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", crudo], stdin=subprocess.PIPE)
    pool = multiprocessing.Pool(int(os.environ.get("PROCESOS", max(4, os.cpu_count() - 4))),
                                initializer=_iniciar, initargs=(m,))

    def trabajos():
        k = 0
        fondo_portada = imagen_portada()
        while k < PORTADA * FPS and k < n_total:
            yield ("fijo", k, k / FPS, cuadro_portada(fondo_portada, k / FPS)); k += 1
        for paso in plan:
            if k >= n_total:
                return
            if paso[0] == "rotulo":
                _, n, _ = paso
                titulo, sub = tomas[n]["titulo"]
                datos = rotulo(titulo, sub, f"{n + 1:02d} / {len(tomas):02d}").tobytes()
                for _ in range(int(RÓTULO * FPS)):
                    if k >= n_total:
                        return
                    yield ("fijo", k, k / FPS, datos); k += 1
                continue
            _, n, _, pasos = paso
            toma = tomas[n]
            for (t, rapido, fch) in pasos:
                if k >= n_total:
                    return
                j = max(0, bisect.bisect_right(toma["horas"], t) - 1)
                yield ("toma", k, k / FPS, t, toma["cuadros"][j][1], n, rapido, fch)
                k += 1
        for img in imagenes_creditos(n_total - k):
            yield ("fijo", k, k / FPS, img); k += 1

    for datos in pool.imap(_cuadro, trabajos(), chunksize=8):
        ff.stdin.write(datos)
    ff.stdin.close()
    ff.wait()
    pool.close()

    with open(salida + ".srt", "w") as f:
        for i, (a, b, texto) in enumerate(subs, 1):
            f.write(f"{i}\n{srt_tiempo(a)} --> {srt_tiempo(b)}\n{texto}\n\n")
    capitulos = [(0.0, T["portada_capitulo"])] + [(p[2], tomas[p[1]]["titulo"][0])
                                                  for p in plan if p[0] == "rotulo"]
    capitulos = [c for c in capitulos + [(t_completo - cierre, T["creditos_capitulo"])] if c[0] < t_total]
    with open(salida + ".capitulos.txt", "w") as f:
        for (a, nombre) in capitulos:
            f.write(f"{int(a) // 60}:{int(a) % 60:02d} {nombre}\n")
    with open(salida + ".ffmeta", "w") as f:
        f.write(";FFMETADATA1\ntitle=" + T["titulo"] + "\n")
        for i, (a, nombre) in enumerate(capitulos):
            b = capitulos[i + 1][0] if i + 1 < len(capitulos) else t_total
            f.write(f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(a * 1000)}\nEND={int(b * 1000)}\ntitle={nombre}\n")
    fin = n_total / FPS
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", crudo, "-i", MUSICA, "-i", salida + ".ffmeta",
                    "-map", "0:v", "-map", "1:a", "-map_metadata", "2", "-map_chapters", "2",
                    "-af", f"afade=t=in:d=0.5,afade=t=out:st={max(0, fin - 3):.2f}:d=3", "-t", f"{fin:.2f}",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", salida], check=True)
    os.remove(crudo)
    print(salida, f"{fin:.1f} s")


def imagen_portada():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    for y in range(0, BANDA, 4):
        d.line([(0, y + 3), (W, y + 3)], fill=RAYA)
    return img


def cuadro_portada(fondo, t):
    """La portada animada: el logo entra desde la izquierda, la raya crece, los textos aparecen como tecleados y la
    bola Boing bota a la derecha."""
    img = fondo.copy()
    d = ImageDraw.Draw(img)
    suave = lambda a: max(0.0, min(1.0, a)) ** 0.5
    lg = logo(1000)
    a = suave((t - 0.2) / 1.2)
    img.paste(lg, (int(180 - 700 * (1 - a)), 300), lg)
    y = 300 + lg.height + 50
    d.rectangle([200, y, 200 + int(520 * suave((t - 1.2) / 0.8)), y + 10], fill=ACENTO)
    y += 50
    lineas = [(T["portada"][0], 44, BLANCO)] + [(l, 34, (180, 180, 170)) for l in T["portada"][1:]]
    for i, (texto, tam, col) in enumerate(lineas):
        a = max(0.0, min(1.0, (t - 2.0 - i * 0.7) / 0.5))
        if a > 0:
            d.text((200, y), texto[:int(len(texto) * a)], font=fuente(tam), fill=col)
        y += 76 if i == 0 else 50
    fase = (t * 0.9) % 1
    yb = 640 - int(330 * (1 - (2 * fase - 1) ** 2))
    bola = bola_boing(300, t * 2.2)
    alto = (640 - yb) / 330
    sw = int(260 * (1 - 0.45 * alto))
    ds = ImageDraw.Draw(img, "RGBA")
    ds.ellipse([W - 370 - sw // 2, 952, W - 370 + sw // 2, 984], fill=(0, 0, 0, int(140 - 70 * alto)))
    img.paste(bola, (W - 520, yb), bola)
    return img.tobytes()


def imagenes_creditos(n):
    """Los créditos suben despacio sobre el fondo, con el logo arriba; n cuadros."""
    lineas = T["creditos"]
    alto_l = 52
    fijo = imagen_portada()
    lg = logo(560)
    fijo.paste(lg, ((W - lg.width) // 2, 40), lg)
    tira = Image.new("RGB", (W, len(lineas) * alto_l + BANDA), FONDO)
    dt = ImageDraw.Draw(tira)
    for i, (estilo, texto) in enumerate(lineas):
        f = fuente(44 if estilo == "t" else 34)
        col = {"t": ACENTO, "n": BLANCO, "s": (170, 170, 160)}[estilo]
        dt.text(((W - f.getlength(texto)) / 2, BANDA * 0.6 + i * alto_l), texto, font=f, fill=col)
    zona = (0, 200, W, BANDA - 10)
    recorrido = tira.height - (zona[3] - zona[1]) - int(BANDA * 0.25)
    for k in range(n):
        a = k / max(1, n - 1)
        off = int(recorrido * min(1, a * 1.08))
        img = fijo.copy()
        img.paste(tira.crop((0, off, W, off + zona[3] - zona[1])), (0, zona[1]))
        yield img.tobytes()


if __name__ == "__main__":
    main()
