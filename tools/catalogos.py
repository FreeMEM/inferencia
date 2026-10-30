#!/usr/bin/env python3
"""Los catálogos de Inferencia, con tools/catalogo.py de Dash.

    python3 tools/catalogos.py [DASH_DIR] cd        # catalogos/Inferencia.cd con los textos de src/ (tr y "tr" de los .dashui)
    python3 tools/catalogos.py [DASH_DIR] ct        # pone al día catalogos/english.ct (guarda lo traducido)
    python3 tools/catalogos.py [DASH_DIR] catalog   # build/Catalogs/english/Inferencia.catalog

DASH_DIR: la carpeta de Dash (por defecto ~/Projects/FreeMEMLang). catalogo.py sigue los import junto al fichero y
no encuentra los de lib/ de Dash: aquí se saltan (los textos de lib/ no van en este catálogo).
"""
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
dash = Path(args.pop(0)) if args and args[0] not in ("cd", "ct", "catalog") else Path.home() / "Projects/FreeMEMLang"
orden = args[0] if args else "catalog"
sys.path.insert(0, str(dash / "tools"))
sys.path.insert(0, str(dash))
import catalogo   # noqa: E402

_leer = Path.read_text


def _leer_o_nada(self, *a, **k):
    return _leer(self, *a, **k) if self.exists() else ""


Path.read_text = _leer_o_nada
cd = raiz / "catalogos/Inferencia.cd"
ct = raiz / "catalogos/english.ct"
if orden == "cd":
    sys.argv = ["catalogo.py", "cd", str(raiz / "src/main.dash"), "-o", str(cd)]
elif orden == "ct":
    sys.argv = ["catalogo.py", "ct", str(cd), "--language", "english", "--name", "Inferencia.catalog", "--version", "1.0",
                "--update", str(ct), "-o", str(ct)]
else:
    sys.argv = ["catalogo.py", "catalog", str(ct), "-o", str(raiz / "build/Catalogs/english/Inferencia.catalog")]
catalogo.main()
