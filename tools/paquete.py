#!/usr/bin/env python3
"""El paquete de Inferencia: el cajón Inferencia con sus iconos, y el .lha.

    python3 tools/paquete.py 0.1 [DASH_DIR]   →  build/paquete/Inferencia/...  y  build/inferencia-0.1.lha

Compila src/main.dash con el ./dash de DASH_DIR (por defecto ~/Projects/FreeMEMLang). Los iconos son .info
clásicos de 4 colores (tools/iconos_wb.py, el generador de Tachyon). El lha de 68k (/opt/amiga/bin/lha) guarda
bien los atributos y los nombres en Latin-1.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(raiz / "tools"))
from iconos_wb import Lienzo, info, cajon, documento, NEGRO, BLANCO, AZUL, WBTOOL, WBDRAWER, WBPROJECT   # noqa: E402


def icono():
    """Un bocadillo de conversación con tres puntos, sobre una ventana."""
    l = Lienzo(40, 26)
    l.rect(0, 0, 39, 25, NEGRO)
    l.rect(1, 1, 38, 24, AZUL)
    l.elipse(20, 11, 15, 8, BLANCO, llena=True)
    l.elipse(20, 11, 15, 8, NEGRO)
    for i in range(5):                       # el pico del bocadillo
        l.linea(9 + i, 17 + i, 13, 17 + i, BLANCO)
    l.linea(9, 17, 13, 22, NEGRO)
    for x in (13, 20, 27):
        l.rect(x - 1, 10, x + 1, 12, AZUL)
    return l


def situar(icono, x, y):
    """El icono en (x, y) de su cajón (do_CurrentX/Y)"""
    b = bytearray(icono)
    b[58:62] = x.to_bytes(4, "big")
    b[62:66] = y.to_bytes(4, "big")
    return bytes(b)


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else "0.0"
    dash = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "Projects/FreeMEMLang"
    build = raiz / "build"
    build.mkdir(exist_ok=True)
    subprocess.run([str(dash / "dash"), str(raiz / "src/main.dash"), "-o", str(build / "Inferencia")], check=True)
    dest = build / "paquete"
    shutil.rmtree(dest, ignore_errors=True)
    caj = dest / "Inferencia"
    caj.mkdir(parents=True)
    (dest / "Inferencia.info").write_bytes(situar(info(cajon(), WBDRAWER), 10, 6))
    shutil.copy(build / "Inferencia", caj / "Inferencia")
    os.chmod(caj / "Inferencia", 0o755)
    (caj / "Inferencia.info").write_bytes(situar(info(icono(), WBTOOL, pila=65536), 10, 6))
    # el Amiga lee ISO-8859-1: los LEEME, de UTF-8 a Latin-1
    for nombre, md in (("LEEME", "README.md"), ("README", "README.en.md")):
        (caj / nombre).write_bytes((raiz / md).read_text().encode("latin-1", "replace"))
    (caj / "LEEME.info").write_bytes(situar(info(documento(), WBPROJECT, herramienta="SYS:Utilities/MultiView"), 90, 6))
    (caj / "README.info").write_bytes(situar(info(documento(), WBPROJECT, herramienta="SYS:Utilities/MultiView"), 160, 6))
    shutil.copy(raiz / "LICENSE", caj / "LICENSE")
    lha = build / f"inferencia-{version}.lha"
    lha.unlink(missing_ok=True)
    subprocess.run(["/opt/amiga/bin/lha", "ao5q", str(lha), "Inferencia", "Inferencia.info"], cwd=dest, check=True)
    print(lha, lha.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
