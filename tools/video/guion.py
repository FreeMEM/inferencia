"""El guion del vídeo de Inferencia y Forja: un hola mundo MUI pedido a Inferencia y hecho en Forja, el logo de
Amiga en LightWave Modeler y el editor de ventanas .dashui de Forja. Con el sistema del vídeo arrancado (preparar.sh
y arrancar.sh) y el agente en marcha.

    python3 guion.py forja|lightwave|dashui <carpeta de la toma>
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
EN = os.environ.get("LENGUA") == "en"      # LENGUA=en: el vídeo en inglés (preparar.sh con LENGUA=en)


def L(es, en):
    return en if EN else es


HOLA, TAREAS = L("Hola", "Hello"), L("Encargos", "Tasks")
DERECHA, RETROCESO = 0x4E, 0x41
TECLA_P, TECLA_S, TECLA_D, TECLA_E = 0x19, 0x21, 0x22, 0x12


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
    vista = ocr((x + 4, y + 40, x + w - 30, y + h - 90))
    botones = [(bx, by) for t, bx, by in vista if t == L("Siempre", "Always")]
    # la pregunta de la cabecera; "Allow it?", con su letra espaciada, el OCR no la lee: entonces, Yes junto a Always
    si = [(bx, by) for t, bx, by in vista if t == L("Sí", "Yes")]
    pregunta = any(L("permites", "Allow") in t for t, _, _ in cabecera) or \
        any(abs(sy - by) < 8 for (_, sy) in si for (_, by) in botones)
    if not pregunta:
        return None
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
                r.rasgo(L("Pide permiso", "It asks first"))
                r.decir(L("Antes de tocar nada pide permiso: Sí, No o Siempre.",
                          "Before touching anything it asks: Yes, No or Always."))
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
    agente.lanzar(L("DH0:Programas/Forja DH0:Hola/hola.dash", "DH0:Programas/Forja DH0:Hello/hello.dash"))
    esperar_ventana("Forja"); time.sleep(3)
    colocar("Forja", 0, 14, 700, 744)
    agente.lanzar("DH0:Programas/Inferencia")
    esperar_ventana("Inferencia"); time.sleep(3)
    colocar("Inferencia", 410, 70, 610, 640)
    p.mover_a(860, 40)


for f in ("Hola/hola", "Hola/saludo", "Hello/hello", "Hello/greeting", "amiga.lwo", "amiga.rexx"):
    if os.path.exists(os.path.join(SYS, f)):
        os.remove(os.path.join(SYS, f))

escena = sys.argv[1]
sys.argv = sys.argv[1:]
if escena == "forja":
    preparar()
elif escena == "dashui":
    agente.lanzar(L("DH0:Programas/Forja DH0:Hola/saludo.dashui", "DH0:Programas/Forja DH0:Hello/greeting.dashui"))
    esperar_ventana("Forja"); time.sleep(3)
    colocar("Forja", 0, 14, 700, 744)
    p.mover_a(860, 40)
else:
    agente.lanzar("DH0:Programas/Inferencia")
    esperar_ventana("Inferencia"); time.sleep(3)
    p.mover_a(860, 40)
r = Rodaje(sys.argv[1])
r.rapidos = []             # (t0, t1, veces): tramos que el montaje acelera
r.rasgos = []              # (t, texto): la lista de la columna izquierda del montaje
r.rasgo = lambda texto: r.rasgos.append((r.ahora(), texto))
r.empezar()
time.sleep(1.0)

if escena == "forja":
    # --- 1. Programar con Forja ---
    r.capitulo("1 - Forja e Inferencia", "Un hola mundo MUI pedido en castellano")
    r.rasgo(L("Forja e Inferencia", "Forja and Inferencia"))
    r.decir(L("Forja, el IDE de Dash, con un fichero vacío. A la derecha, Inferencia.",
              "Forja, the Dash IDE, with an empty file. On the right, Inferencia."))
    time.sleep(4)
    r.rasgo(L("El modelo, en casa", "A model at home"))
    r.decir(L("El modelo es qwen3-coder, en Ollama, en otro PC de casa. Sin nube y sin pagar.",
              "The model is qwen3-coder, on Ollama, on another PC at home. No cloud, nothing to pay."))
    time.sleep(4)
    r.rasgo(L("El encargo", "The task"))
    r.decir(L("El encargo, en un fichero: un hola mundo con ventana MUI, guardarlo y ejecutarlo.",
              "The task, in a file: a hello world with an MUI window, saved and run."))
    t_teclas = r.ahora()
    escribir_en_inferencia(L("Lee DH0:Encargos/hola.txt y hazlo.", "Read DH0:Tasks/hello.txt and do it."))
    r.rapidos.append((t_teclas + 3, r.ahora() - 1, 4))
    r.rasgo(L("Inferencia trabaja", "Inferencia at work"))
    r.decir(L("Inferencia piensa y usa sus herramientas: leer, escribir, órdenes ARexx...",
              "Inferencia thinks and uses its tools: read, write, ARexx commands..."))
    inicio = r.ahora()
    ok = trabajar(lambda: any(amiga.ventana(n) for n in ("Hola Mundo", "Hola", "Hello World", "Hello")), r)
    r.rapidos.append((inicio, r.ahora(), 4))
    r.rasgo(L("Forja compila", "Forja builds it"))
    r.decir(L("El código va al editor de Forja. Forja lo compila con dashc en el propio Amiga y lo ejecuta.",
              "The code goes into Forja's editor. Forja builds it with dashc on the Amiga itself and runs it."))
    time.sleep(5)
    fa = amiga.ventana("Forja")
    r.acercar(0, 14, 700, 560, 6)
    time.sleep(7)
    r.rasgo(L("Hola mundo MUI", "MUI hello world"))
    r.decir(L("Y ahí está la ventana MUI del programa.", "And there is the program's MUI window."))
    time.sleep(4)
    hola = next((amiga.ventana(n) for n in ("Hola Mundo", "Hola", "Hello World", "Hello") if amiga.ventana(n)), None)
    if hola:
        _, _, hx, hy, hw, hh = hola
        salir = [(t, bx, by) for t, bx, by in ocr((hx, hy, hx + hw, hy + hh)) if L("Salir", "Quit") in t]
        if salir:
            p.mover_a(round(salir[0][1]), round(salir[0][2])); time.sleep(0.4); p.clic()
    time.sleep(3)

elif escena == "dashui":
    # --- 3. El editor de ventanas ---
    r.capitulo("3 - Ventanas .dashui", "El editor de ventanas de Forja, con MUI de verdad")
    r.rasgo(L("Abrir un .dashui", "Opening a .dashui"))
    r.decir(L("Las ventanas MUI de Dash se dibujan en ficheros .dashui. Forja los abre en su editor de ventanas.",
              "Dash MUI windows are drawn in .dashui files. Forja opens them in its window editor."))
    time.sleep(5)
    r.decir(L("A la izquierda, el árbol de objetos. A la derecha, las propiedades del elegido.",
              "On the left, the object tree. On the right, the properties of the selected one."))
    r.marcar("arbol", 184, 76, 216, 128, 4)
    time.sleep(5)
    r.rasgo(L("Vista previa con MUI", "Real MUI preview"))
    r.decir(L("Amiga+P: la vista previa. No es un dibujo: es la ventana hecha con MUI.",
              "Amiga+P: the preview. Not a drawing: the window built with MUI."))
    p.mover_a(300, 400); time.sleep(0.5)
    agente.tecla(TECLA_P, RCOMMAND)
    time.sleep(5)
    r.rasgo(L("Cambios en vivo", "Live changes"))
    r.decir(L("Elijo el botón Saludar y le cambio el texto. La vista previa cambia sola.",
              "I pick the Greet button and change its text. The preview follows by itself."))
    p.mover_a(268, 181); time.sleep(0.5); p.clic(); time.sleep(1.2)
    agente.tecla(DERECHA, 0); time.sleep(0.6); agente.tecla(RETURN, 0); time.sleep(0.6)
    for i in range(L(8, 6)):
        agente.tecla(RETROCESO, 0); time.sleep(0.12)
    agente.escribir(L("_Di hola", "_Say hello")); time.sleep(0.8)
    agente.tecla(RETURN, 0)
    time.sleep(2)
    vp = amiga.ventana(L("Saludo", "Greeting"))
    if vp:
        r.marcar("vista", vp[2], vp[3], vp[4], vp[5], 3)
    time.sleep(4)
    if vp:
        p.mover_a(vp[2] + 7, vp[3] + 4); time.sleep(0.4); p.clic(); time.sleep(1.5)
    r.rasgo(L("Guardar y ver el JSON", "Save, see the JSON"))
    r.decir(L("Amiga+S guarda. Amiga+D enseña el fichero tal cual: JSON.",
              "Amiga+S saves. Amiga+D shows the file as it is: JSON."))
    p.mover_a(300, 400); time.sleep(0.4); p.clic(); time.sleep(0.6)
    agente.tecla(TECLA_S, RCOMMAND); time.sleep(1.5)
    agente.tecla(TECLA_D, RCOMMAND)
    time.sleep(6)
    r.rasgo(L("El programa que la usa", "The program using it"))
    r.decir(L("El programa importa el .dashui y usa sus objetos por nombre: v.mensaje, v.nombre...",
              "The program imports the .dashui and uses its objects by name: v.message, v.name..."))
    p.mover_a(50, L(124, 110)); time.sleep(0.5); p.clic(); time.sleep(1.5)
    r.acercar(180, 60, 500, 400, 6)
    time.sleep(7)
    r.rasgo(L("Compilar y ejecutar", "Build and run"))
    r.decir(L("Amiga+E: Forja lo compila con dashc, en el Amiga, y lo ejecuta.",
              "Amiga+E: Forja builds it with dashc, on the Amiga, and runs it."))
    p.mover_a(400, 400); time.sleep(0.4)
    agente.tecla(TECLA_E, RCOMMAND)
    esperar_ventana(L("Saludo", "Greeting"), 120)
    time.sleep(2)
    r.rasgo(L("Probar la ventana", "Trying the window"))
    r.decir(L("Y ahí está, con el botón nuevo.", "And there it is, with the new button."))
    _, _, x, y, w, h = amiga.ventana(L("Saludo", "Greeting"))
    p.mover_a(x + w - 50, y + 38); time.sleep(0.5); p.clic(); time.sleep(0.5)
    agente.escribir("Amiga"); time.sleep(1)
    p.mover_a(x + 45, y + 58); time.sleep(0.5); p.clic()
    time.sleep(4)
    p.mover_a(x + w - 45, y + 58); time.sleep(0.5); p.clic()
    time.sleep(2)
    ok = amiga.ventana(L("Saludo", "Greeting")) is None

else:
    v = esperar_ventana("Inferencia")
    # --- 2. LightWave ---
    r.capitulo("2 - LightWave", "Inferencia maneja otros programas por ARexx")
    r.rasgo("LightWave Modeler 5")
    r.decir(L("LightWave Modeler 5, de 1996, se maneja con guiones ARexx.",
              "LightWave Modeler 5, from 1996, can be driven with ARexx scripts."))
    agente.lanzar("SYS:LightWave/Modeler.FP")
    time.sleep(25)
    r.rasgo(L("Volver al Workbench", "Back to Workbench"))
    r.decir(L("Vuelvo al Workbench con Amiga+M.", "Back to the Workbench with Amiga+M."))
    agente.tecla(TECLA_M, LCOMMAND)
    time.sleep(3)
    r.rasgo(L("El encargo", "The task"))
    r.decir(L("El encargo, en un fichero: la palabra AMIGA en 3D, con un guion ARexx.",
              "The task, in a file: the word AMIGA in 3D, with an ARexx script."))
    escribir_en_inferencia(L("Lee DH0:Encargos/letras.txt y hazlo.", "Read DH0:Tasks/letters.txt and do it."))
    inicio = r.ahora()
    r.rasgo(L("Inferencia trabaja", "Inferencia at work"))
    ok2 = trabajar(lambda: os.path.exists(os.path.join(SYS, "amiga.lwo")), r)
    time.sleep(8)
    r.rapidos.append((inicio, r.ahora(), 4))
    r.rasgo(L("Guion ARexx y rx", "ARexx script and rx"))
    r.decir(L("Lee el manual, escribe el guion, lo ejecuta con rx y guarda el objeto.",
              "It reads the manual, writes the script, runs it with rx and saves the object."))
    time.sleep(6)
    r.rasgo(L("AMIGA en 3D", "AMIGA in 3D"))
    r.decir(L("Amiga+M: en el Modeler, AMIGA en 3D.", "Amiga+M: in the Modeler, AMIGA in 3D."))
    agente.tecla(TECLA_M, LCOMMAND)
    time.sleep(10)
r.acabar()
import json
fj = os.path.join(sys.argv[1], "toma.json")
toma = json.load(open(fj))
toma["rapidos"] = r.rapidos
toma["rasgos"] = r.rasgos
toma["lengua"] = L("es", "en")
json.dump(toma, open(fj, "w"), ensure_ascii=False, indent=1)
print("hecho:", escena, ok2 if escena == "lightwave" else ok)
