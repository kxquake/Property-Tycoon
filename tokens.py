import pygame

class Token:
    """
    Represents a single token with a color
    and an (offset_x, offset_y) to position it in the popup.
    """
    def __init__(self, color, offset_x, offset_y):
        self.color = color
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.radius = 20  

def get_default_tokens():
    """
    Return a list of Token objects. Currently color-based, 
    but you can replace them with token images later.
    """
    tokens_list = [
        Token((255, 0, 0),   20, 100),  # Red
        Token((0, 255, 0),   70, 100),  # Green
        Token((0, 0, 255),  120, 100),  # Blue
        Token((255, 255, 0),170, 100),  # Yellow
        Token((255, 0, 255),220, 100)   # Magenta
    ]
    return tokens_list
