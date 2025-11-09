from . import view
import pygame

def handle_input():
    """Handle input events and return an input state dictionary.
    
    Processes pygame events and returns a dictionary with the current input state,
    including quit commands and save requests.
    
    Returns:
        dict: Input state with the following keys:
            - "quit" (bool): True if the application should quit
            - "save" (bool): True if a save was requested (S key pressed)
    """
    ev = view.poll_events()
    input_state = {"quit": False, "save": False}
    
    if ev["QUIT"] or pygame.K_ESCAPE in ev["KEYDOWN"]:
        input_state["quit"] = True
    
    if pygame.K_s in ev["KEYDOWN"]:
        input_state["save"] = True
    
    return input_state