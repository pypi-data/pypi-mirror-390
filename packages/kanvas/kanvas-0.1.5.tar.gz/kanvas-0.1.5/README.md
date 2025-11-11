# kanvas

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A minimalist creative-coding toolkit for Python, inspired by [Processing](https://processing.org/) and [p5.js](https://p5js.org/).

## Overview

kanvas provides a simple, educational framework for creative coding in Python. It captures the essence of Processing's `setup()` and `draw()` paradigm while maintaining a clean, readable codebase that's perfect for learning how creative coding frameworks work under the hood.

**Key Features:**
- Simple setup/draw loop similar to Processing
- Built on pygame for reliable cross-platform support
- Clean separation of concerns (model-view-controller architecture)
- Lightweight and hackable (~200 lines of core code)
- Beginner-friendly API with educational focus

## Installation

### Requirements
- Python 3.9 or higher
- pygame 2.0+
- numpy 1.23+

### Install from source
```bash
git clone https://github.com/robinoscarsson/kanvas.git
cd kanvas
pip install -e .
```

## Quick Start

```python
from kanvas.core import run

def setup(model):
    """Called once at startup"""
    model.clear(30)  # Set background to gray

def draw(model, frame, dt):
    """Called every frame"""
    x = (frame // 2) % model.w
    for y in range(model.h):
        model.pixel(x, y, 255, 255, 255)

# Run the sketch
run(setup, draw, size=(800, 600), title="My First Sketch")
```

Save this as `sketch.py` and run with:
```bash
python sketch.py
```

Press **ESC** to quit or close the window.

## Examples

Check out the `examples/` directory for more demonstrations:

### Serpinski Triangle
Fractal generation using the chaos game method.

![Serpinski Triangle](examples/output/Serpinski%20Triangle%20Demo_20251110_204627.png)

```python
# Run with: python examples/serpinski_triangle.py
```

### Ulam Spiral  
Prime number visualization in spiral form - a beautiful mathematical pattern where prime numbers create distinctive diagonal structures.

![Ulam Spiral](examples/output/Ulam%20Spiral%20Demo%20(fixed)_20251110_204254.png)

```python  
# Run with: python examples/ulam_sprial.py
```

## API Reference

### Core Functions

#### `run(setup_func, draw_func, **kwargs)`
Main entry point to start a kanvas sketch.

**Parameters:**
- `setup_func`: Function called once at startup, receives `model` parameter
- `draw_func`: Function called every frame, receives `model`, `frame`, and `dt` parameters
- `size`: Tuple of (width, height) for window size (default: (640, 360))
- `title`: Window title string (default: "kanvas")
- `target_fps`: Target frames per second (default: 60)

### Model API

The `model` object provides the drawing surface:

#### `model.pixel(x, y, r, g, b)`
Set a pixel at coordinates (x, y) to RGB color (r, g, b).

#### `model.clear(gray_value)`
Clear the entire canvas to a grayscale value (0-255).

#### Properties
- `model.w`: Canvas width in pixels
- `model.h`: Canvas height in pixels

### Loop Control Functions

#### `noLoop()`
Stop the draw loop from running. Similar to p5.js `noLoop()`, this stops the `draw()` function from being called repeatedly. The application continues to respond to input but `draw()` is no longer executed each frame.

```python
from kanvas import run, noLoop

def draw(model, frame, dt):
    # Draw something
    model.pixel(frame % model.w, model.h // 2, 255, 255, 255)
    
    # Stop drawing after 100 frames
    if frame >= 100:
        noLoop()
```

#### `loop()`
Resume the draw loop after it was stopped with `noLoop()`. Similar to p5.js `loop()`, this resumes calling the `draw()` function each frame.

#### `isLooping()`
Check if the draw loop is currently running.

**Returns:** `bool` - `True` if `draw()` is being called each frame, `False` if stopped with `noLoop()`

### Controls

- **ESC**: Quit the application
- **S**: Save current frame as PNG image

## Advanced Usage

### Loop Control
Create static images or control animation timing using loop control functions:

```python
import math
from kanvas import run, noLoop, loop, isLooping

def setup(model):
    model.clear(0)

def draw(model, frame, dt):
    # Draw a growing circle
    radius = frame // 10
    center_x, center_y = model.w // 2, model.h // 2
    
    # Simple circle drawing
    for angle in range(0, 360, 5):
        x = center_x + int(radius * math.cos(math.radians(angle)))
        y = center_y + int(radius * math.sin(math.radians(angle)))
        if 0 <= x < model.w and 0 <= y < model.h:
            model.pixel(x, y, 255, 255, 255)
    
    # Stop when circle reaches edge
    if radius >= min(model.w, model.h) // 2:
        noLoop()
        print("Animation complete - press ESC to quit")

run(setup, draw, size=(400, 400), title="Growing Circle")
```

### Interactive Control
Toggle drawing with conditional logic:

```python
from kanvas import run, noLoop, loop, isLooping

def setup(model):
    model.clear(20)

def draw(model, frame, dt):
    # Toggle loop every 3 seconds (180 frames at 60 FPS)
    if frame % 180 == 0 and frame > 0:
        if isLooping():
            noLoop()
            print("Paused - animation will resume in 3 seconds")
        else:
            loop()
            print("Resumed")
    
    # Simple animation
    x = (frame * 2) % model.w
    model.pixel(x, model.h // 2, 255, 100, 100)

run(setup, draw, title="Auto-pause Demo")
```

## Architecture

kanvas follows a clean MVC architecture:

```
src/kanvas/
├── core.py         # Main application loop and coordination
├── controller.py   # Input handling (keyboard, mouse, window events)
├── view.py         # Rendering and window management (pygame)
├── model.py        # Canvas state and pixel operations
└── utils.py        # Utility functions
```

## Philosophy

kanvas is designed for **learning by doing**. The entire codebase is intentionally simple and readable, making it easy to understand how creative coding frameworks work internally. There's no magic - you can trace every function call from user input to pixel output.

This makes kanvas ideal for:
- Learning creative coding concepts
- Understanding game loop architecture
- Teaching graphics programming
- Rapid prototyping of visual ideas
- Educational workshops and tutorials

## Contributing

This is primarily an educational project, but contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Submit a pull request

## Roadmap

- [ ] Basic shape primitives (line, circle, rectangle)
- [ ] Color management system
- [ ] Mouse and keyboard input handling
- [ ] Transformation matrix support
- [ ] Image export utilities
- [ ] Animation recording

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- Inspired by [Processing](https://processing.org/) and [p5.js](https://p5js.org/)
- Built with [pygame](https://pygame.org)
- Created for educational purposes and creative exploration

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
