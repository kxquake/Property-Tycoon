import pygame

class Token:
    """
    Represents a single token with a color
    and an (offset_x, offset_y) to position it in the popup.
    """
    """
    def __init__(self, color, offset_x, offset_y):
        self.color = color
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.radius = 20
    """
    def __init__(self, token_path, offset_x, offset_y, colour):
        self.token_image = pygame.image.load(token_path).convert_alpha()
        self.token_image = pygame.transform.scale(self.token_image, (30,30))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.colour = colour
        self.radius = 20
        self.name = token_path.split("/")[-1].replace("Icons-", "").replace(".png", "") #sets name of token from filename

def get_default_tokens():
    """
    Return a list of Token objects. Currently color-based, 
    but you can replace them with token images later.
    """
    """
    tokens_list = [
        Token((255, 0, 0), 20, 100),  # Red
        Token((0, 255, 0), 70, 100),  # Green
        Token((0, 0, 255), 120, 100),  # Blue
        Token((255, 255, 0), 170, 100),  # Yellow
        Token((255, 0, 255), 220, 100)  # Magenta
    ]
    return tokens_list
    """

    tokens_list = [
        Token("pngs/Icons-boot.png", 20, 100, (255, 0, 0)),
        Token("pngs/Icons-phone.png", 70, 100, (0, 255, 0)),
        Token("pngs/Icons-ship.png", 120, 100, (0, 0, 255)),
        Token("pngs/Icons-hatstand.png", 170, 100, (255, 255, 0)),
        Token("pngs/Icons-cat.png",220, 100, (255, 0, 255)),
        Token("pngs/Icons-iron.png", 270, 100, (0, 255, 255))
    ]
    return tokens_list
