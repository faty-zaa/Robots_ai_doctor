# 🤖 RoboDoctor

**An offline AI assistant that diagnoses robot problems from a text description, a photo, or a short video.**

You describe the fault ("my robot turns on but the wheels don't move") and optionally show the robot. RoboDoctor returns up to three likely causes, three practical checks, and one recommended next action, with safety warnings where needed.

Everything runs **locally** through [Ollama](https://ollama.com). No cloud API, no API key, and no data leaves the machine.

> **Demo URL: http://127.0.0.1:8000**
> (Available once the app is started with `make run`. See Quick start below.)

---

## Quick start

**Requirements:** Python 3.11+, [uv](https://docs.astral.sh/uv/), [Ollama](https://ollama.com)

```bash
make install     # install Python dependencies (only: ollama)
make models      # one-time download of the two AI models
ollama serve     # skip if Ollama is already running
make run         # start the web demo
```

Then open **http://127.0.0.1:8000** in your browser.

Terminal version: `make app`

> The address `127.0.0.1` means "this computer", so it works on the machine where the app is running.

---

## Setup notes (read before running)

The first run needs a one-time download. After that, everything works offline.

| Step | What it downloads | Approx. size | Time |
|---|---|---|---|
| `make install` | Python dependency `ollama` (the only one) | < 1 MB | seconds |
| `ollama pull gemma3:1b` | Text model for the diagnosis | ~800 MB | a few minutes |
| `ollama pull moondream` | Vision model for photos and video | ~1.7 GB | a few minutes |

**To avoid waiting during the demo:**

1. Run `make models` **before** the presentation, on a good connection.
2. Start Ollama and run `make run`.
3. Send **one test diagnosis** to warm up the models. The first request is slower while they load into memory.

**Hardware:** a laptop with 8 GB of RAM and no GPU is enough.

---

## Features

- **Text diagnosis**: describe symptoms in plain English.
- **Photo analysis**: a vision model describes visible damage, loose wires, burn marks, LEDs, and error text.
- **Video analysis**: the browser samples 4 frames from a short clip, and each frame is analyzed in time order.
- **Documentation-grounded answers (RAG)**: relevant sections from our robotics docs are retrieved and given to the model.
- **Robot-lab web interface**: an animated robot face that reacts to the system state (idle, scanning, done, error), plus a console that types out the diagnosis.
- **Safety-aware**: answers separate possibilities from confirmed facts and include safety precautions.
- **Domain guard**: questions unrelated to robotics are politely declined.

---

## Demo script

1. Open http://127.0.0.1:8000
2. Click a fault chip, such as **E-01 Wheels dead**, then press **Run Diagnostic**.
3. Drop a photo of a robot into the scanner bay and add a short description.
4. Drop a 5 to 20 second video of a faulty robot. The page extracts frames and analyzes them.

---

## How it works

```
 Text ─────────────────────────────┐
 Photo ──► vision model ──► text ──┤
 Video ──► 4 frames ──► vision ────┤
                                   ▼
                      keyword retriever (robodoctor_docs/*.md)
                                   │
                                   ▼
                       prompt = problem + visual notes + docs
                                   │
                                   ▼
                      text LLM (gemma3:1b via Ollama)
                                   │
                                   ▼
                       diagnosis shown in the web console
```

Photos and videos are **converted to text first**, so a small, fast text model can reason over everything in one prompt.

| Component | File | Role |
|---|---|---|
| Web interface + server | `web.py` | Standard-library HTTP server, single-page UI |
| Terminal version | `app.py` | Same agent, command-line interface |
| Agent | `src/Agent/agent.py` | Builds the prompt, orchestrates the steps |
| Retriever | `src/RAG/retriever.py` | Keyword search over documentation sections |
| LLM client | `src/llm/client.py` | Ollama wrapper with clear error messages |
| Knowledge base | `robodoctor_docs/data/*.md` | Troubleshooting documentation |

**Models** (both local via Ollama): `gemma3:1b` for diagnosis, `moondream` for photos and video frames.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot reach Ollama` | Start it with `ollama serve` |
| `Model '...' is not installed` | Run `make models` |
| `No module named 'ollama'` | Use `make run` or `uv run python web.py`, not plain `python` |
| `Address already in use` | Another copy is running. Stop it with `pkill -f web.py` |
| Photo or video analysis is slow | Normal on CPU. Video takes 20 to 60 seconds, so try text or a photo first |

---

## Design choices

- **Fully local**: privacy-friendly and works without internet, which suits workshops and labs.
- **Minimal dependencies**: the only runtime dependency is `ollama`. The server uses Python's standard library.
- **Small models**: chosen so it runs on an ordinary laptop CPU.
- **Frame sampling in the browser**: no `ffmpeg` or `opencv` needed for video support.

## Limitations

- Small models give shorter, less detailed answers than large cloud models. A larger model such as `gemma3:4b` can be swapped in by changing one line in `src/llm/client.py`.
- Photo and video descriptions are auto-generated and may be inaccurate. The interface shows what the model "saw" so the user can check.
- Video analysis uses 4 sampled frames, so very short events can be missed. Audio is not analyzed.
- Retrieval is keyword-based, not semantic.
- Diagnoses are **suggestions, not guarantees**. Always power the robot off before inspecting wiring or batteries.

## Future work

- Embedding-based retrieval for better document matching
- Voice input (speech-to-text)
- A larger vision model for finer visual detail
- Robot logs and ROS topics as diagnostic input
- A community-maintained knowledge base

---

## Project structure

```
Robots_ai_doctor/
├── web.py                # web demo
├── app.py                # terminal version
├── Makefile
├── pyproject.toml
├── robodoctor_docs/data/ # troubleshooting docs (markdown)
└── src/
    ├── Agent/agent.py
    ├── RAG/retriever.py
    └── llm/client.py
```