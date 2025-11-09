from .core import run
import random


def main():
    def setup(model):
        model.clear(20)

    def draw(model, frame, dt):
        # Define the three vertices of the triangle (fixed boundary issue)
        a = {'x': int(model.w/2), 'y': 0}
        b = {'x': 0, 'y': model.h - 1}
        c = {'x': model.w - 1, 'y': model.h - 1}
        targets = [a, b, c]
        
        # Start with a separate point, not referencing the targets
        p = {'x': int(model.w/2), 'y': int(model.h/2)}
        
        for i in range(1000):
            target = random.choice(targets)
            # Draw a point halfway between p and target
            p['x'] = (p['x'] + target['x']) // 2
            p['y'] = (p['y'] + target['y']) // 2
            model.pixel(p['x'], p['y'], 255, 255, 255)

    run(setup, draw, size=(800, 800), title="Serpinski Triangle Demo")

if __name__ == "__main__":
    main()