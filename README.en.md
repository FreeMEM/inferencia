# Inferencia

*English | [Castellano](README.md)*

AI on the Amiga. You talk to a language model from an MUI window, and the model can work on your system: read and
change files, run Shell commands, send ARexx commands to other programs and look at the system. It asks before
changing anything.

This is a test version: it works in the emulator, but it has not been tried on a real Amiga yet. The program
itself is in Spanish for now; an English catalog will come.

## Requirements

- AmigaOS 3.0 or later, with a 68020 or better.
- MUI 5.
- A TCP/IP stack (Roadshow, AmiTCP, Miami...) and AmiSSL 5 for HTTPS.
- The clock set right: AmiSSL checks the certificate dates.
- An [OpenRouter](https://openrouter.ai) or Anthropic key, or a model on a PC in your network (Ollama, LM Studio),
  which needs no key.

## Install

Copy the Inferencia drawer anywhere. Open it and press Amiga-P for the preferences:
- **Proveedor** (provider): OpenRouter, Anthropic, or "OpenAI y compatibles" (for Ollama and LM Studio).
- **Dirección** (address): the provider's. With Ollama, something like `http://192.168.1.10:11434/v1/chat/completions`.
- **Clave nueva** (new key): the key. It is not shown; if you leave the field empty, the current one stays.
- **Modelo** (model): for example `anthropic/claude-sonnet-5.5` on OpenRouter, or `claude-sonnet-5-5` on Anthropic.
- **Tope** (limit): the conversation size in characters from which it gets summarized (60000 if empty).

"Usar" (use) keeps them until reboot; "Guardar" (save) also writes them to `ENVARC:Inferencia/`.

## Use

- Type at the bottom. Return starts a new line; Amiga+Return or the Enviar button send the question.
- The answer shows up as it arrives. Parar stops it.
- The top line shows the tokens and what the conversation has cost so far.
- Proyecto menu: new conversation, open and save conversations, preferences.

### What the model can do

| Tool | What it does | Asks? |
|---|---|---|
| leer, listar, buscar | Files and drawers | No |
| escribir, editar | Changes files (shows the change first) | Yes |
| orden | Runs a Shell line | Yes |
| arexx, puertos | ARexx commands to other programs | arexx yes |
| sistema | Memory, version, volumes, assigns, tasks | No |
| entorno | ENV: variables | To set, yes |
| portapapeles | Reads and writes the clipboard | To write, yes |

When it asks, you get "Sí" (yes), "No" and "Siempre" (always). "Siempre" writes it to
`ENVARC:Inferencia/sin_permiso` (comma separated: `orden list,arexx FORJA.1,entorno`), and it won't ask about that
again.

If [Forja](https://github.com/FreeMEM/forja), the Dash IDE, has the file open, the change is made in Forja's
editor: unsaved, and it can be undone.

### ARexx

Port `INFERENCIA.1`:
- `PREGUNTA text`: sends the question, without waiting.
- `ESTADO`: libre (free), pidiendo (asking), permiso (waiting for permission) or orden (running a command).
- `RESPUESTA`: the last answer, when free.
- `CONTEXTO file [from to]` and `ADJUNTAR title` (with the text on the following lines): go with the next question.
- `NUEVA` (new), `MOSTRAR` (show), `OCULTAR` (hide), `GUARDAR file` (save), `CARGAR file` (load), `COSTE` (cost),
  `MENSAJES` (message count).

## Build

With [Dash](https://github.com/FreeMEM/FreeMEMLang) 2.0 (dashc): `./dash src/main.dash -o Inferencia`. The package:
`python3 tools/paquete.py 0.1`. The tests run in the emulator: [tests/LEEME.md](tests/LEEME.md) (in Spanish).

Written in Dash. MIT license.
