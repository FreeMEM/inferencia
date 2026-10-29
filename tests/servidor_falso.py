#!/usr/bin/env python3
"""Un OpenRouter falso para probar Inferencia sin gastar: contesta a POST /api/v1/chat/completions con una
respuesta en el formato de OpenAI Chat Completions que repite la pregunta. Sin clave da 401, como el de verdad.

    python3 tests/servidor_falso.py [puerto]      # 40900 por defecto, en 127.0.0.1
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


class Falso(BaseHTTPRequestHandler):
    def do_POST(self):
        cuerpo = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if not self.headers.get("Authorization", "").startswith("Bearer "):
            self._contestar(401, {"error": {"message": "No auth credentials found", "code": 401}})
            return
        try:
            peticion = json.loads(cuerpo)
            pregunta = peticion["messages"][-1]["content"]
        except (ValueError, KeyError, IndexError) as e:
            self._contestar(400, {"error": {"message": f"petición mal formada: {e}", "code": 400}})
            return
        self._contestar(200, {
            "id": "gen-falso",
            "model": peticion.get("model", "") + " (falso)",
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": f"Recibido: «{pregunta}» ✓"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
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
