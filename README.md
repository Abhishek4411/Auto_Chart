# AI Auto Diagram Workspace 🎨

Turn plain text into beautiful, exportable diagrams (PNG/SVG/PDF/GIF) using Streamlit + Graphviz, with optional local LLM parsing via Ollama.

> **UI note:** The app is designed for **light mode** and looks best there (dark mode is supported but not optimized).

## Features
- Parse free‑form text into **architecture**, **flowchart**, **sequence**, and more
- Multiple layout engines (`dot`, `neato`, `fdp`, etc.), themes, and auto‑clustering
- Export to **PNG / SVG / PDF / DOT**, plus **animated GIFs**
- Optional local LLM (Ollama) for smarter parsing with small models

## Requirements
- Python 3.9+
- System **Graphviz** (binaries on PATH)
- Optional (recommended): **Ollama** running locally for LLM parsing

Python packages:
```txt
streamlit
graphviz
Pillow
requests
imageio
imageio-ffmpeg
numpy
```

## Quick Start
```bash
# 1) Create a virtual env (recommended)
python -m venv .venv && . .venv/Scripts/activate  # Windows
# or
python3 -m venv .venv && source .venv/bin/activate  # macOS/Linux

# 2) Install dependencies
pip install -r requirements.txt  # or pip install streamlit graphviz Pillow requests imageio imageio-ffmpeg numpy

# 3) Ensure Graphviz is installed (see below) and on your PATH

# 4) (Optional) Start Ollama in background for LLM parsing
#    Install: https://ollama.com/download
#    Start service:
ollama serve
#    Pull a small model (any one of these is fine):
ollama pull gemma2:2b  # or: phi3:mini, llama3.2:1b, tinyllama, qwen2.5:0.5b

# 5) Run the app
streamlit run app.py
```

## Install Graphviz
The Python `graphviz` package **does not** include the Graphviz system binaries. Install Graphviz and ensure its `bin` directory is on **PATH**.

- **Windows (MSI):** https://graphviz.org/download/
  - Typical path: `C:\Program Files\Graphviz\bin`
  - Add to PATH:
    1. Windows Search → *Environment Variables*
    2. *System variables* → select **Path** → **Edit**
    3. **New** → `C:\Program Files\Graphviz\bin` → **OK**
  - You can also set it at runtime in the app (already included):
    ```python
    import os
    os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"
    ```

- **macOS:**
  ```bash
  brew install graphviz
  # PATH is managed by Homebrew; reopen your terminal if needed
  ```

- **Ubuntu/Debian:**
  ```bash
  sudo apt-get update && sudo apt-get install -y graphviz
  ```

- **Fedora/RHEL:**
  ```bash
  sudo dnf install -y graphviz
  ```

**Verify install**
```bash
dot -V
# Graphviz version ... (any recent version works)
```

## Optional: Ollama (Local LLM)
The app will try to connect to `http://localhost:11434`. If found, it uses a small local model for smarter parsing. If not, it falls back to a fast, rule‑based parser.

- Install: https://ollama.com/download
- Start: `ollama serve`
- Pull a model (choose one):
  ```bash
  ollama pull gemma2:2b
  # or: ollama pull phi3:mini
  # or: ollama pull llama3.2:1b
  # or: ollama pull tinyllama
  # or: ollama pull qwen2.5:0.5b
  ```

## Project Structure
```
app.py               # Streamlit app (rename your file to app.py if needed)
README.md            # This file
requirements.txt     # (optional) list of Python deps
```

## Usage Tips
- Use simple arrow or natural phrases, e.g.:
  ```
  User -> API Gateway: HTTP
  API Gateway -> Auth Service: Validate
  Order Service -> Database: Save Order
  ```
- Pick a diagram type in the sidebar and tune **Layout** / **Visual** options
- Use **Export** panel to download PNG/SVG/PDF/DOT or an animated GIF

## Troubleshooting
- **Graphviz not found / `dot` not found**
  - Install system Graphviz and ensure its `bin` is on PATH (see above).
- **Blank/partial diagram**
  - Try a different *Layout Engine* (e.g. `dot`) or reduce spacing.
- **Ollama not detected**
  - Start `ollama serve` and pull at least one small model.
- **GIF export errors**
  - Ensure `imageio-ffmpeg` is installed (`pip install imageio-ffmpeg`).

---

**Design note:** Optimized for **light mode** (preferable). Dark mode is supported but may appear less crisp.