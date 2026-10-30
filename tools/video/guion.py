"""El guion del vídeo de Inferencia y Forja: un hola mundo MUI pedido a Inferencia y hecho en Forja, y el logo de
Amiga en LightWave Modeler. Con el sistema del vídeo arrancado (preparar.sh y arrancar.sh) y el agente en marcha.

    python3 guion.py forja|lightwave <carpeta de la toma>
"""
import os
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.expanduser("~/Projects/trasfondo/tools/video"))
import agente
import amiga
import piloto as p
from amiberry import orden
from rodaje import Rodaje
from ventanas import colocar

SYS = os.path.expanduser("~/.cache/video-inferencia/sys")
RCOMMAND, LCOMMAND = 0x0080, 0x0040
RETURN, TECLA_M = 0x44, 0x37


def esperar_ventana(titulo, tope=60):
    t = time.time()
    while time.time() - t < tope:
        v = amiga.ventana(titulo)
        if v:
            return v
        time.sleep(0.5)
    raise RuntimeError("no sale la ventana " + titulo)


def ocr(zona):
    """[(texto, x, y)] de las palabras que se leen en esa zona de la pantalla (coordenadas de la pantalla)."""
    with tempfile.TemporaryDirectory() as d:
        from PIL import Image, ImageOps
        orden("SCREENSHOT", os.path.join(d, "c.png"))
        img = Image.open(os.path.join(d, "c.png")).convert("L").crop(zona)
        img = ImageOps.invert(img).resize((img.width * 3, img.height * 3), Image.LANCZOS)
        img.save(os.path.join(d, "g.png"))
        tsv = subprocess.run(["tesseract", os.path.join(d, "g.png"), "-", "--psm", "11", "tsv"],
                             capture_output=True, text=True).stdout
    r = []
    for linea in tsv.splitlines()[1:]:
        c = linea.split("\t")
        if len(c) == 12 and c[11].strip():
            l, t, w, h = (int(v) for v in c[6:10])
            r.append((c[11].strip(), zona[0] + (l + w / 2) / 3, zona[1] + (t + h / 2) / 3))
    return r


def permiso_pendiente():
    """Si Inferencia pregunta: dónde está su botón Siempre (el más bajo de la vista), o None."""
    v = amiga.ventana("Inferencia")
    if not v:
        return None
    _, _, x, y, w, h = v
    cabecera = ocr((x + 4, y + 14, x + w - 4, y + 40))
    if not any("permites" in t for t, _, _ in cabecera):
        return None
    botones = [(bx, by) for t, bx, by in ocr((x + 4, y + 40, x + w - 30, y + h - 90)) if t == "Siempre"]
    return max(botones, key=lambda b: b[1]) if botones else None


def trabajar(hecho, r, tope=300):
    """Deja trabajar a Inferencia hasta que hecho() sea cierto, pulsando Siempre en cada permiso."""
    t = time.time()
    dicho = False
    while time.time() - t < tope:
        if hecho():
            return True
        b = permiso_pendiente()
        if b:
            if not dicho:
                r.decir("Antes de tocar nada pide permiso: Sí, No o Siempre.")
                dicho = True
            p.mover_a(round(b[0]), round(b[1])); p.clic()
            time.sleep(1.5)

        time.sleep(1.0)
    return False


def escribir_en_inferencia(texto):
    v = amiga.ventana("Inferencia")
    _, _, x, y, w, h = v
    p.mover_a(x + 200, y + h - 58); p.clic()
    for i in range(0, len(texto), 40):
        agente.escribir(texto[i:i + 40])
    time.sleep(0.6)
    agente.tecla(RETURN, RCOMMAND)


def preparar():
    """Sin grabar: Forja con el fichero vacío a la izquierda, Inferencia a la derecha."""
    agente.lanzar("DH0:Programas/Forja DH0:Hola/hola.dash")
    esperar_ventana("Forja"); time.sleep(3)
    colocar("Forja", 0, 14, 700, 744)
    agente.lanzar("DH0:Programas/Inferencia")
    esperar_ventana("Inferencia"); time.sleep(3)
    colocar("Inferencia", 410, 70, 610, 640)
    p.mover_a(860, 40)


for f in ("Hola/hola", "amiga.lwo", "amiga.rexx"):
    if os.path.exists(os.path.join(SYS, f)):
        os.remove(os.path.join(SYS, f))

escena = sys.argv[1]
sys.argv = sys.argv[1:]
if escena == "forja":
    preparar()
else:
    agente.lanzar("DH0:Programas/Inferencia")
    esperar_ventana("Inferencia"); time.sleep(3)
    p.mover_a(860, 40)
r = Rodaje(sys.argv[1])
r.rapidos = []             # (t0, t1, veces): tramos que el montaje acelera
r.empezar()
time.sleep(1.0)

if escena == "forja":
    # --- 1. Programar con Forja ---
    r.capitulo("1 - Forja e Inferencia", "Un hola mundo MUI pedido en castellano")
    r.decir("Forja, el IDE de Dash, con un fichero vacío. A la derecha, Inferencia.")
    time.sleep(4)
    r.decir("El modelo es qwen3-coder, en Ollama, en otro PC de casa. Sin nube y sin pagar.")
    time.sleep(4)
    r.decir("El encargo, en un fichero: un hola mundo con ventana MUI, guardarlo y ejecutarlo.")
    t_teclas = r.ahora()
    escribir_en_inferencia("Lee DH0:Encargos/hola.txt y hazlo.")
    r.rapidos.append((t_teclas + 3, r.ahora() - 1, 4))
    r.decir("Inferencia piensa y usa sus herramientas: leer, escribir, órdenes ARexx...")
    inicio = r.ahora()
    ok = trabajar(lambda: amiga.ventana("Hola Mundo") is not None or amiga.ventana("Hola") is not None, r)
    r.rapidos.append((inicio, r.ahora(), 4))
    r.decir("El código va al editor de Forja. Forja lo compila con dashc en el propio Amiga y lo ejecuta.")
    time.sleep(5)
    fa = amiga.ventana("Forja")
    r.acercar(0, 14, 700, 560, 6)
    time.sleep(7)
    r.decir("Y ahí está la ventana MUI del programa.")
    time.sleep(4)
    hola = amiga.ventana("Hola Mundo") or amiga.ventana("Hola")
    if hola:
        _, _, hx, hy, hw, hh = hola
        salir = [(t, bx, by) for t, bx, by in ocr((hx, hy, hx + hw, hy + hh)) if "Salir" in t]
        if salir:
            p.mover_a(round(salir[0][1]), round(salir[0][2])); time.sleep(0.4); p.clic()
    time.sleep(3)

else:
    v = esperar_ventana("Inferencia")
    # --- 2. LightWave ---
    r.capitulo("2 - LightWave", "Inferencia maneja otros programas por ARexx")
    r.decir("LightWave Modeler, de 1995, se maneja con guiones ARexx.")
    agente.lanzar("SYS:LightWave/Modeler.FP")
    time.sleep(25)
    r.decir("Vuelvo al Workbench con Amiga+M.")
    agente.tecla(TECLA_M, LCOMMAND)
    time.sleep(3)
    r.decir("El encargo, en un fichero: la palabra AMIGA en 3D, con un guion ARexx.")
    escribir_en_inferencia("Lee DH0:Encargos/letras.txt y hazlo.")
    inicio = r.ahora()
    ok2 = trabajar(lambda: os.path.exists(os.path.join(SYS, "amiga.lwo")), r)
    time.sleep(8)
    r.rapidos.append((inicio, r.ahora(), 4))
    r.decir("Lee el manual, escribe el guion, lo ejecuta con rx y guarda el objeto.")
    time.sleep(6)
    r.decir("Amiga+M: en el Modeler, AMIGA en 3D.")
    agente.tecla(TECLA_M, LCOMMAND)
    time.sleep(10)
r.acabar()
import json
fj = os.path.join(sys.argv[1], "toma.json")
toma = json.load(open(fj))
toma["rapidos"] = r.rapidos
json.dump(toma, open(fj, "w"), ensure_ascii=False, indent=1)
print("hecho:", escena, ok if escena == "forja" else ok2)
