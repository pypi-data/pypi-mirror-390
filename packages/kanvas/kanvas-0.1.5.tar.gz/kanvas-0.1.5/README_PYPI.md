# kanvas

A minimalist creative-coding toolkit for Python, inspired by Processing and p5.js.

## Overview

kanvas provides a simple, educational framework for creative coding in Python. It captures the essence of Processing's `setup()` and `draw()` paradigm while maintaining a clean, readable codebase that's perfect for learning how creative coding frameworks work under the hood.

**Key Features:**
- Simple setup/draw loop similar to Processing
- Built on pygame for reliable cross-platform support
- Clean separation of concerns (model-view-controller architecture)
- Lightweight and hackable (~200 lines of core code)
- Beginner-friendly API with educational focus

## Installation

```bash
pip install kanvas
```

### Requirements
- Python 3.9 or higher
- pygame 2.0+
- numpy 1.23+

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

Press **ESC** to quit or **S** to save the current frame as a PNG image.

## Examples

### Sierpinski Triangle
Generate fractals using the chaos game method:

```python
from kanvas.core import run
import random

def setup(model):
    model.clear(20)

def draw(model, frame, dt):
    # Define triangle vertices
    a = {'x': int(model.w/2), 'y': 0}
    b = {'x': 0, 'y': model.h - 1}
    c = {'x': model.w - 1, 'y': model.h - 1}
    targets = [a, b, c]
    
    # Starting point
    p = {'x': int(model.w/2), 'y': int(model.h/2)}
    
    # Generate 1000 points
    for i in range(1000):
        target = random.choice(targets)
        p['x'] = (p['x'] + target['x']) // 2
        p['y'] = (p['y'] + target['y']) // 2
        model.pixel(p['x'], p['y'], 255, 255, 255)

run(setup, draw, size=(800, 800), title="Sierpinski Triangle")
```

### Ulam Spiral
Visualize prime numbers in a spiral pattern:

```python
from kanvas.core import run

def is_prime(n):
    if n <= 1:
        return False
    if n % 2 == 0:
        return n == 2
    r = int(n**0.5)
    f = 3
    while f <= r:
        if n % f == 0:
            return False
        f += 2
    return True

def setup(model):
    model.clear(20)
    
    # Spiral generation logic
    directions = [(1,0), (0,-1), (-1,0), (0,1)]  # right, up, left, down
    x, y = model.w // 2, model.h // 2
    
    n = 1
    dir_idx = 0
    steps_in_leg = 1
    steps_taken = 0
    legs_done_at_length = 0
    
    while 0 <= x < model.w and 0 <= y < model.h:
        if is_prime(n):
            model.pixel(x, y, 255, 255, 255)
        
        # Move in spiral
        dx, dy = directions[dir_idx]
        x += dx * 4  # Step size
        y += dy * 4
        
        n += 1
        steps_taken += 1
        
        # Turn logic for spiral pattern
        if steps_taken == steps_in_leg:
            dir_idx = (dir_idx + 1) % 4
            steps_taken = 0
            legs_done_at_length += 1
            if legs_done_at_length == 2:
                steps_in_leg += 1
                legs_done_at_length = 0

def draw(model, frame, dt):
    pass

run(setup, draw, size=(800, 800), title="Ulam Spiral")
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

**Parameters:**
- `x, y`: Integer coordinates (0,0 is top-left)
- `r, g, b`: Color values from 0-255

#### `model.clear(gray_value)`
Clear the entire canvas to a grayscale value.

**Parameters:**
- `gray_value`: Integer from 0 (black) to 255 (white)

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
- **S**: Save current frame as PNG image to `./output/` directory

## Philosophy

kanvas is designed for **learning by doing**. The entire codebase is intentionally simple and readable, making it easy to understand how creative coding frameworks work internally. There's no magic - you can trace every function call from user input to pixel output.

This makes kanvas ideal for:
- Learning creative coding concepts
- Understanding game loop architecture  
- Teaching graphics programming
- Rapid prototyping of visual ideas
- Educational workshops and tutorials

## Advanced Usage

### Loop Control
Create static images or control animation timing:

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
        print("Animation complete")

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
            print("Paused")
        else:
            loop() 
            print("Resumed")
    
    # Simple animation
    x = (frame * 2) % model.w
    model.pixel(x, model.h // 2, 255, 100, 100)

run(setup, draw)
```

### Animation Loops
Create smooth animations using the frame counter:

```python
import math

def draw(model, frame, dt):
    model.clear(0)
    
    # Animated circle
    center_x = model.w // 2
    center_y = model.h // 2
    radius = 50
    
    angle = frame * 0.05
    x = center_x + int(radius * math.cos(angle))
    y = center_y + int(radius * math.sin(angle))
    
    # Draw a simple circle by setting pixels
    for dx in range(-5, 6):
        for dy in range(-5, 6):
            if dx*dx + dy*dy <= 25:  # Circle equation
                if 0 <= x+dx < model.w and 0 <= y+dy < model.h:
                    model.pixel(x+dx, y+dy, 255, 255, 255)
```

### Interactive Sketches
While kanvas currently focuses on generative art, you can create interactive elements by using the frame counter and mathematical functions to respond to time-based input.

## Contributing

kanvas is an educational project welcoming contributions! The codebase is intentionally simple to encourage learning and experimentation.

## Source Code

Visit the project on GitHub: https://github.com/robinoscarsson/kanvas

## License

MIT License - see the GitHub repository for full details.

## Acknowledgments

- Inspired by Processing and p5.js
- Built with pygame
- Created for educational purposes and creative exploration