"""La miniatura de YouTube (1280x720): de fondo, Forja e Inferencia con la ventana del hola mundo, que se funde a
la izquierda con el negro; ahí, el logo y el lema en Topaz. Abajo a la derecha, la palabra AMIGA del Modeler en un
recuadro ámbar.

    python3 miniatura.py <captura de Forja> <captura de LightWave> <salida.jpg>"""
import sys

import numpy as np
from PIL import Image, ImageDraw

from montar import ACENTO, BLANCO, FONDO, fuente, logo, pantalla

LEMA = ["UNA IA QUE TRABAJA", "EN TU AMIGA"]
PIE = "Forja - ventanas .dashui - LightWave 3D"
AMIGA = (190, 590, 700, 790)           # la palabra AMIGA en la pantalla de LightWave (1280x1024)


def miniatura(forja, lightwave):
    W, H = 1280, 720
    cap = pantalla(forja)
    img = Image.new("RGB", (W, H), FONDO)
    esc = H / cap.height
    ew = round(cap.width * esc)
    ex = W - ew
    img.paste(cap.resize((ew, H), Image.LANCZOS), (ex, 0))
    a = np.zeros((H, W), np.uint8)
    x0, x1 = ex + 20, ex + 260
    for x in range(W):
        a[:, x] = 255 if x < x0 else (0 if x > x1 else int(255 * (x1 - x) / (x1 - x0)))
    img = Image.composite(Image.new("RGB", (W, H), FONDO), img, Image.fromarray(a))
    d = ImageDraw.Draw(img, "RGBA")
    lw = pantalla(lightwave).crop(AMIGA)
    lw = lw.resize((lw.width * 4 // 5, lw.height * 4 // 5), Image.LANCZOS)
    zx, zy = W - lw.width - 40, H - lw.height - 40
    d.rectangle([zx + 14, zy + 14, zx + lw.width + 26, zy + lw.height + 26], fill=(0, 0, 0, 150))
    d.rectangle([zx, zy, zx + lw.width + 12, zy + lw.height + 12], fill=ACENTO + (255,))
    img.paste(lw, (zx + 6, zy + 6))
    d = ImageDraw.Draw(img)
    lg = logo(470)
    img.paste(lg, (36, 44), lg)
    y = 44 + lg.height + 50
    for i, l in enumerate(LEMA):
        f = fuente(50)
        d.text((44, y + 4), l, font=f, fill=(0, 0, 0))
        d.text((40, y), l, font=f, fill=BLANCO if i == 0 else ACENTO)
        y += 64
    y += 16
    d.rectangle([40, y, 400, y + 8], fill=ACENTO)
    d.text((40, y + 26), PIE, font=fuente(28), fill=(200, 200, 190))
    fv = fuente(40)
    texto = "AmigaOS 3"
    ancho = int(fv.getlength(texto)) + 40
    d.rounded_rectangle([40, H - 110, 40 + ancho, H - 50], 10, fill=ACENTO)
    d.text((60, H - 102), texto, font=fv, fill=FONDO)
    d.text((40 + ancho + 24, H - 95), "hecho en Dash", font=fuente(30), fill=BLANCO)
    return img


if __name__ == "__main__":
    miniatura(sys.argv[1], sys.argv[2]).save(sys.argv[3], quality=92)
