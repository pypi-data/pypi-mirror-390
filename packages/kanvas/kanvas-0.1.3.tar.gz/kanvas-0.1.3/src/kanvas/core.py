import time

from . import view, controller
from .model import Model

def run(setup, draw, target_fps=60, size=(640, 360), title="kanvas"):
    view.create_window(*size, title=title)
    model = Model(size[0], size[1])

    setup(model)

    running = True
    last = time.perf_counter()
    frameCount = 0
    frame_time = 1.0 / target_fps

    while running:
        input_state = controller.handle_input()
        if input_state["quit"]:
            running = False

        # Handle save request
        if input_state["save"]:
            try:
                filepath = view.save_canvas_to_png(filename=title)
                print(f"Image saved successfully to: {filepath}")
            except Exception as e:
                print(f"Error saving image: {e}")

        now = time.perf_counter()
        delta_ms = (now - last) * 1000.0
        last = now

        view.begin_frame()
        draw(model, frameCount, delta_ms)
        view.present_framebuffer(model.fb)
        view.end_frame()

        frameCount += 1

        # enkel frame cap
        elapsed = time.perf_counter() - now
        sleep_for = frame_time - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)

    view.shutdown()