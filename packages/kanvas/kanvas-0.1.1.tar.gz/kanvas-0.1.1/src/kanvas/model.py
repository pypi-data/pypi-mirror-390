import numpy as np

class Model:
    """A framebuffer model for pixel-based graphics rendering.
    
    The Model class provides a 2D framebuffer for storing and manipulating pixel data.
    It supports basic operations like clearing the screen and setting individual pixels
    with RGB color values.
    
    Attributes:
        w (int): Width of the framebuffer in pixels.
        h (int): Height of the framebuffer in pixels.
        fb (numpy.ndarray): 3D numpy array storing RGB pixel data with shape (width, height, 3).
    """
    
    def __init__(self, w: int, h: int):
        """Initialize a new Model with specified dimensions.
        
        Creates a framebuffer with the given width and height, initialized to black (0,0,0).
        
        Args:
            w (int): Width of the framebuffer in pixels.
            h (int): Height of the framebuffer in pixels.
        """
        self.w, self.h = w, h
        self.fb = np.zeros((w, h, 3), dtype=np.uint8)

    def clear(self, r: int, g: int = None, b: int = None):
        """Clear the entire framebuffer with a specified color.
        
        Sets all pixels in the framebuffer to the specified RGB color.
        If only the red component is provided, it will be used for all three
        color components (creating a grayscale color).
        
        Args:
            r (int): Red color component (0-255).
            g (int, optional): Green color component (0-255). If None, uses the value of r.
            b (int, optional): Blue color component (0-255). If None, uses the value of r.
        """
        if g is None: g = b = r
        self.fb[:] = (r, g, b)

    def pixel(self, x: int, y: int, r: int, g: int, b: int):
        """Set a single pixel to the specified RGB color.
        
        Sets the pixel at coordinates (x, y) to the given RGB color values.
        The operation is bounds-checked; pixels outside the framebuffer dimensions
        are ignored to prevent array index errors.
        
        Args:
            x (int): X-coordinate of the pixel (0 to width-1).
            y (int): Y-coordinate of the pixel (0 to height-1).
            r (int): Red color component (0-255).
            g (int): Green color component (0-255).
            b (int): Blue color component (0-255).
        """
        if 0 <= x < self.w and 0 <= y < self.h:
            self.fb[x, y] = (r, g, b)