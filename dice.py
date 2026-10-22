import pygame
import random

class DiceButton:
    """
    Clickable button to roll the dice.
    """
    def __init__(self, x, y, width, height):
        """
        Initialise the buttons area so it can be clicked.
        - x: x coordinate of button
        - y: y-coordinate of button
        - width: width of button
        - height: height of button
        """
        self.rect = pygame.Rect(x, y, width, height)

    def is_clicked(self, mouse_pos):
        """
        Check if the button has been clicked.
        - mouse_pos: position of the mouse
        Returns:
            bool: True if the mouse position is within the button bounds, False otherwise.
        """
        return self.rect.collidepoint(mouse_pos)

def rolldice():
    """
    Simulates rolling two 6 sided dice with random numbers generated.
    Returns:
        Tuple: Two integers between 1 and 6.
    """
    a = random.randrange(1, 7)
    b = random.randrange(1, 7)
    print(f"Dice Roll: {a}, {b}", flush=True)  # flush true as when asking player for choice, dice roll doesn't show up.
    return a, b

def draw_dice(screen, number, position):
    """
    Draws the dice depending on what number was rolled by player.
    - screen: The surface to draw on.
    - number: The number to show on the dice.
    - position: The x and y position where the dice will be drawn
    """
    dice_size = 75  # Adjust size as needed
    dot_color = (0, 0, 0)  # Black
    center = (position[0] + dice_size // 2, position[1] + dice_size // 2)
    radius = 5

    # Draw dice body
    pygame.draw.rect(screen, (255, 255, 255), (*position, dice_size, dice_size))

    # Draw dots based on the number
    if number == 1:
        pygame.draw.circle(screen, dot_color, center, radius)
    elif number == 2:
        pygame.draw.circle(screen, dot_color, (center[0] - 15, center[1] - 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] + 15, center[1] + 15), radius)
    elif number == 3:
        pygame.draw.circle(screen, dot_color, center, radius)
        pygame.draw.circle(screen, dot_color, (center[0] - 15, center[1] - 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] + 15, center[1] + 15), radius)
    elif number == 4:
        pygame.draw.circle(screen, dot_color, (center[0] - 15, center[1] - 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] + 15, center[1] - 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] - 15, center[1] + 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] + 15, center[1] + 15), radius)
    elif number == 5:
        pygame.draw.circle(screen, dot_color, center, radius)
        pygame.draw.circle(screen, dot_color, (center[0] - 15, center[1] - 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] + 15, center[1] - 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] - 15, center[1] + 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] + 15, center[1] + 15), radius)
    elif number == 6:
        pygame.draw.circle(screen, dot_color, (center[0] - 15, center[1] - 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] + 15, center[1] - 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] - 15, center[1]), radius)
        pygame.draw.circle(screen, dot_color, (center[0] + 15, center[1]), radius)
        pygame.draw.circle(screen, dot_color, (center[0] - 15, center[1] + 15), radius)
        pygame.draw.circle(screen, dot_color, (center[0] + 15, center[1] + 15), radius)