import pygame
import sys

from menu2 import load_menu

# Initialize pygame
pygame.init()

# Set up display size
SCREEN_WIDTH, SCREEN_HEIGHT = 568, 571
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Property Tycoon - Home")

# Load the home background image
home_image = pygame.image.load("pngs/Home.png").convert_alpha()
home_image = pygame.transform.scale(home_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load How to Play images and scale them down to fit the screen size
htp_images = [
    pygame.transform.scale(pygame.image.load("pngs/htp1.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load("pngs/htp2.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load("pngs/htp3.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
]
htp_index = 0

# Scale factors for button positions
SCALE_X = SCREEN_WIDTH / 600  # 0.9467
SCALE_Y = SCREEN_HEIGHT / 600  # 0.9517


class Button:
    """
    Represents a clickable button on the screen with styling.
    """
    def __init__(self, x, y, width, height, action):
        """Initialisation of the button with the dimensionality."""
        # Scale positions and sizes to match the resized images
        self.rect = pygame.Rect(
            int(x * SCALE_X),
            int(y * SCALE_Y),
            int(width * SCALE_X),
            int(height * SCALE_Y)
        )
        self.action = action 

    def is_clicked(self, mouse_pos):
        """Returns true if button has been clicked by checking mouse position location."""
        return self.rect.collidepoint(mouse_pos)

# Functions for button actions
def open_full_game():
    """Starts the full version of the game"""
    print("Opening Full Game")
    result = load_menu(abridged=False, time_limit_minutes=None)
    return result
def open_abridged_game():
    """Starts the abridged version of the game"""
    time_limit = abridged_popup(screen)
    if time_limit is None:
        return
    print("Opening Abridged Game")
    result = load_menu(abridged=True, time_limit_minutes=time_limit)
    return result

def abridged_popup(screen):
    """
    Displays a popup to enter the time limit for the abridged version of the game.
    - screen: The screen to draw the game on.
    Returns:
        The entered time limit in minutes, or none if user cancels

    """
    input_box = pygame.Rect(217,269,135,51)
    active = False
    text = ''
    background = pygame.image.load("pngs/AbridgedUI.png").convert_alpha()
    background = pygame.transform.scale(background, (550, 400))

    play_button = pygame.Rect(400, 377, 134, 50)
    close_button = pygame.Rect(525, 60, 27, 27)

    clock = pygame.time.Clock()
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                if play_button.collidepoint(event.pos) and int(text) > 0:
                    if text.isdigit():
                        return int(text)
                if close_button.collidepoint(event.pos):
                    return None

            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and text.isdigit() and int(text) > 0:
                    return int(text)
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.unicode.isdigit(): #makes sure only digits are entered
                    if len(text) < 3: #only allows 3 characters
                        text += event.unicode

        screen.blit(background, (10,50))

        font = pygame.font.Font(None, 36)
        input_text = font.render(text, True, (0, 0, 0))
        screen.blit(input_text, (input_box.x + 10, input_box.y + 10))

        #buttons and input boxes
        pygame.draw.rect(screen, (0,0,0), input_box, 2)
        pygame.draw.rect(screen, (0,0,0), play_button, 2)
        pygame.draw.rect(screen, (217,33,33), close_button, 4)

        pygame.display.flip()
        clock.tick(30)

def open_how_to_play():
    """
    Opens the How To Play screen for player.
    """
    global htp_index
    htp_index = 0
    show_how_to_play()

def exit_app():
    """ Exits the game"""
    pygame.quit()
    sys.exit()

def show_how_to_play():
    """
    Displays the how to play screen with relevant buttons and the instructional images.
    """
    global htp_index
    showing_htp = True
    
    # Original button positions for (600, 600) images, now scaled down
    back_button = Button(16, 541, 89, 34, 'back')
    next_button = Button(493, 542, 88, 34, 'next')
    exit_button = Button(493, 542, 88, 34, 'exit')  # Exit button in the same spot as next button

    while showing_htp:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Handle "Next" button click (if not at last image)
                if htp_index < len(htp_images) - 1 and next_button.is_clicked(mouse_pos):
                    htp_index += 1
                
                # Handle "Back" button click
                elif back_button.is_clicked(mouse_pos):
                    if htp_index > 0:
                        htp_index -= 1
                    else:
                        showing_htp = False  # Exit if at first image
                
                # Handle exit button on htp3
                elif htp_index == 2 and exit_button.is_clicked(mouse_pos):
                    showing_htp = False  # Return to home screen
        
        # Draw the current How to Play image
        screen.blit(htp_images[htp_index], (0, 0))

        pygame.display.flip()

# Original button positions and sizes (based on 600x600), now scaled down
buttons = [
    Button(200, 205, 177, 88, open_full_game),   # Full Game Button
    Button(200, 320, 177, 88, open_abridged_game),  # Abridged Game Button
    Button(200, 438, 177, 88, open_how_to_play),  # How to Play Button
    Button(14, 555, 102, 23, exit_app)  # Exit Button on home screen
]

# Main loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.is_clicked(mouse_pos):
                    result = button.action()  # Call the corresponding function
                    if result == "menu":
                        # Go back to home screen
                        break

    # Draw the home background (buttons are part of the image)
    screen.blit(home_image, (0, 0))

    pygame.display.flip()

pygame.quit()
