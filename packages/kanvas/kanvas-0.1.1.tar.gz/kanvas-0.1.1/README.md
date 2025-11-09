# kanvas 🖌️

> ⚠️ **Note:** This package name (`kanvas`) is currently reserved on PyPI.  
> The project is under active development and not yet ready for public use.

**A lightweight creative-coding experiment in Python.**  
kanvas is a small hobby project inspired by [Processing](https://processing.org/) and [p5.js](https://p5js.org/).  
It’s not meant to replace them — it’s a hands-on homage and a way to explore how such a system might work from scratch in Python.

---

## 🎨 Overview

kanvas aims to capture the *feel* of Processing:  
`setup()` runs once, `draw()` runs every frame, and the rest is up to you.

Under the hood it uses [pygame](https://www.pygame.org/news) for the window and rendering, and a small core loop written to be readable, hackable, and educational.

The goal isn’t performance or feature parity — it’s **understanding**.  
If you’ve ever wondered *“how would I build p5 myself?”*, this is that journey.

---

## ⚙️ Installation

Clone the repository and install it locally in editable mode:

```bash
git clone https://github.com/yourname/kanvas.git
cd kanvas
pip install -e .
```

kanvas requires **Python 3.9+** and **pygame** (automatically installed via pip).

---

## 🚀 Quick Start

Create a new Python file, for example `example.py`:

```python
from kanvas import run

def setup(model):
    model.clear(30)  # background gray

def draw(model, frame, dt):
    x = (frame // 2) % model.w
    for y in range(model.h):
        model.pixel(x, y, 255, 255, 255)

run(setup, draw, size=(320, 200), title="kanvas Example")
```

Then run it:

```bash
python example.py
```

A small window should appear with a white line sweeping across the screen.  
Press **ESC** or click the **X** to quit.

---

## 🧩 Project Structure

```
src/kanvas/
├── core.py         # Main loop orchestration
├── controller.py   # Handles input (ESC / window close)
├── view.py         # Pygame window and rendering
├── model.py        # Framebuffer and pixel operations
└── __init__.py
examples/
└── pixelsmoke.py   # Simple demonstration sketch
```

---

## ✨ Features (so far)

- Minimal setup/draw loop  
- Clean separation of core / view / controller / model  
- ESC and window close handling  
- Simple pixel drawing via NumPy framebuffer  
- Beginner-friendly codebase (~200 lines total)

---

## 🧠 Philosophy

kanvas exists to **learn by building**.  
Every function is deliberately simple and explicit. There’s no magic, no global state, and no framework hiding the logic from you.

You can trace the entire rendering path from `run()` → `controller.handle_input()` → `model.pixel()` → `view.present_framebuffer()` in less than a minute.

If you’re curious about:
- How Processing or p5’s loop actually works  
- How to handle events and rendering cleanly in Python  
- Or just want a compact sandbox for creative-coding ideas  

…this project might make you happy.

---

## 🧩 Roadmap (subject to whim)

- [ ] Basic shape primitives (`line`, `circle`, `rect`)
- [ ] `background()`, `fill()`, `stroke()` API layer
- [ ] Mouse position and keyboard input
- [ ] Higher-level color & transformation helpers
- [ ] Export to image / animation

This is a **hobby project**, not a product. Expect it to evolve (and break) as it grows.

---

## ❤️ Acknowledgements

- Inspired by [Processing](https://processing.org/) and [p5.js](https://p5js.org/)  
- Built with [pygame](https://www.pygame.org/news)  
- Written out of pure curiosity and love for creative coding.

---

## 📄 License

MIT License — do whatever you want, but if you learn something, pass it on.
