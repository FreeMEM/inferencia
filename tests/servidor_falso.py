#!/usr/bin/env python3
"""Un OpenRouter falso para probar Inferencia sin gastar: contesta a POST /api/v1/chat/completions en el formato
de OpenAI Chat Completions. Sin clave da 401, como el de verdad.

- Si el mensaje de sistema empieza por "Resume", contesta con un resumen fijo.
- Sin herramientas en la petición: repite la pregunta. Si la pregunta empieza por "MARKDOWN", contesta con un
  texto de ejemplo en Markdown (para probar cómo se ve).
- Con herramientas, si el último mensaje es del usuario y dice "LLAMA nombre {json}", pide esa herramienta con
  esos argumentos (varias si hay varias líneas así).
- Con herramientas, si el último mensaje es el resultado de una: "Resultado de <id>: <contenido>".
- "GUION nombre" en la pregunta sigue tests/guiones/<nombre>.json: una lista de turnos, cada uno
  {"llamadas": [["nombre", {argumentos}], ...]} o {"texto": "..."}. El turno es el número de respuestas que
  lleva el modelo desde la última pregunta; en el texto, {resultado} es el contenido del último resultado.

    python3 tests/servidor_falso.py [puerto]      # 40900 por defecto, en 127.0.0.1
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


MARKDOWN = """Esto es un **párrafo** con `código` y una palabra en *cursiva*. Sigue un poco más para que se \
parta en varias líneas al ancho de la ventana.

## Pasos

- Abre el **Shell** desde el Workbench.
- Escribe `dir SYS:` y pulsa Intro.
  - Una sublista, con su sangría.
1. Primero, esto.
2. Después, lo otro.

```
Main
    Print "hola, Amiga"
end
```

> Una cita, en cursiva.

Y un párrafo final con una palabra muy larga: https://github.com/FreeMEM/inferencia/blob/main/PLAN.md"""


class Falso(BaseHTTPRequestHandler):
    def do_POST(self):
        cuerpo = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if not self.headers.get("Authorization", "").startswith("Bearer "):
            self._contestar(401, {"error": {"message": "No auth credentials found", "code": 401}})
            return
        try:
            peticion = json.loads(cuerpo)
            ultimo = peticion["messages"][-1]
            pregunta = ultimo["content"]
        except (ValueError, KeyError, IndexError) as e:
            self._contestar(400, {"error": {"message": f"petición mal formada: {e}", "code": 400}})
            return
        # la petición de un resumen (Inferencia, cuando la conversación crece)
        if peticion["messages"][0]["role"] == "system" and peticion["messages"][0]["content"].startswith("Resume"):
            self._contestar(200, {
                "id": "gen-falso", "model": peticion.get("model", "") + " (falso)",
                "choices": [{"index": 0, "finish_reason": "stop",
                             "message": {"role": "assistant", "content": "RESUMEN DE PRUEBA: se habló de hola."}}],
                "usage": self._uso(peticion)})
            return
        guion = self._guion(peticion["messages"])
        if guion:
            self._contestar_guion(peticion, guion)
            return
        mensaje = {"role": "assistant", "content": f"Recibido: «{pregunta}» ✓"}
        if pregunta.startswith("MARKDOWN"):
            mensaje["content"] = MARKDOWN
        fin = "stop"
        if peticion.get("tools"):
            if ultimo["role"] == "tool":
                mensaje["content"] = f"Resultado de {ultimo['tool_call_id']}: {pregunta}"
            else:
                llamadas = []
                for linea in pregunta.splitlines():
                    if linea.startswith("LLAMA "):
                        nombre, _, args = linea[6:].partition(" ")
                        llamadas.append({"id": f"call_{len(llamadas) + 1}", "type": "function",
                                         "function": {"name": nombre, "arguments": args or "{}"}})
                if llamadas:
                    mensaje = {"role": "assistant", "content": "", "tool_calls": llamadas}
                    fin = "tool_calls"
        self._contestar(200, {
            "id": "gen-falso",
            "model": peticion.get("model", "") + " (falso)",
            "choices": [{"index": 0, "finish_reason": fin, "message": mensaje}],
            "usage": self._uso(peticion),
        })

    def _uso(self, peticion):
        """usage como el de OpenRouter: 10 tokens por mensaje; con usage.include, también cost (0,0001 $ por mensaje)"""
        u = {"prompt_tokens": len(peticion["messages"]) * 10, "completion_tokens": 5, "total_tokens": 0}
        if (peticion.get("usage") or {}).get("include"):
            u["cost"] = len(peticion["messages"]) * 0.0001
        return u

    def _guion(self, mensajes):
        """El guion de la última pregunta y el turno: (turnos, número), o None"""
        ultima = max(i for i, m in enumerate(mensajes) if m["role"] in ("user", "system"))
        texto = mensajes[ultima].get("content") or ""
        if mensajes[ultima]["role"] != "user" or not texto.startswith("GUION "):
            return None
        nombre = texto.split()[1]
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guiones", nombre + ".json")
        with open(ruta, encoding="utf-8") as f:
            turnos = json.load(f)
        hechos = sum(1 for m in mensajes[ultima + 1:] if m["role"] == "assistant")
        return turnos, hechos

    def _contestar_guion(self, peticion, guion):
        turnos, n = guion
        mensajes = peticion["messages"]
        turno = turnos[min(n, len(turnos) - 1)]
        fin = "stop"
        if "llamadas" in turno:
            llamadas = [{"id": f"call_{n}_{i}", "type": "function",
                         "function": {"name": nombre, "arguments": json.dumps(args, ensure_ascii=False)}}
                        for i, (nombre, args) in enumerate(turno["llamadas"])]
            mensaje = {"role": "assistant", "content": turno.get("texto", ""), "tool_calls": llamadas}
            fin = "tool_calls"
        else:
            resultado = mensajes[-1]["content"] if mensajes[-1]["role"] == "tool" else ""
            mensaje = {"role": "assistant", "content": turno["texto"].replace("{resultado}", resultado)}
        self._contestar(200, {
            "id": "gen-falso", "model": peticion.get("model", "") + " (falso)",
            "choices": [{"index": 0, "finish_reason": fin, "message": mensaje}],
            "usage": self._uso(peticion),
        })

    def _contestar(self, estado, datos):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, formato, *args):
        sys.stderr.write("falso: " + formato % args + "\n")


if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 40900
    HTTPServer(("127.0.0.1", puerto), Falso).serve_forever()
