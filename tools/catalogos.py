#!/usr/bin/env python3
"""Los catálogos de Inferencia, con tools/catalogo.py de Dash.

    python3 tools/catalogos.py [DASH_DIR] cd        # catalogos/Inferencia.cd con los textos de src/ (tr y "tr" de los .dashui)
    python3 tools/catalogos.py [DASH_DIR] ct        # pone al día catalogos/english.ct (guarda lo traducido)
    python3 tools/catalogos.py [DASH_DIR] catalog   # build/Catalogs/english/Inferencia.catalog

DASH_DIR: la carpeta de Dash (por defecto ~/Projects/FreeMEMLang). Los textos de lib/ que se usan (los errores de
red de lib/red, números 400 a 442) también van en el catálogo: el programa no usa esos números.
"""
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
dash = Path(args.pop(0)) if args and args[0] not in ("cd", "ct", "catalog") else Path.home() / "Projects/FreeMEMLang"
orden = args[0] if args else "catalog"
sys.path.insert(0, str(dash / "tools"))
sys.path.insert(0, str(dash))
import os   # noqa: E402
os.environ["DASH_HOME"] = str(dash)
import catalogo   # noqa: E402

cd = raiz / "catalogos/Inferencia.cd"
ct = raiz / "catalogos/english.ct"
cd.parent.mkdir(exist_ok=True)
if orden == "cd":
    sys.argv = ["catalogo.py", "cd", str(raiz / "src/main.dash"), "-o", str(cd)]
elif orden == "ct":
    sys.argv = ["catalogo.py", "ct", str(cd), "--language", "english", "--name", "Inferencia.catalog", "--version", "1.0",
                "-o", str(ct)]
    if ct.exists():
        sys.argv[-2:-2] = ["--update", str(ct)]
else:
    sys.argv = ["catalogo.py", "catalog", str(ct), "-o", str(raiz / "build/Catalogs/english/Inferencia.catalog")]
catalogo.main()
