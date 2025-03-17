import pygame
import random

class DiceButton:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

def rolldice():
    a = random.randrange(1, 7)
    b = random.randrange(1, 7)
    print(f"Dice Roll: {a}, {b}")  # Debugging output
    return a, b

def check_if_double(a,b):
    return a == b

def draw_dice(screen, number, position):
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

    