import pygame
import sys
import subprocess


# Initialize pygame
pygame.init()

# Set up display size
SCREEN_WIDTH, SCREEN_HEIGHT = 568, 571
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Property Tycoon - Home")

# Load the home background image
home_image = pygame.image.load("pngs/home.png").convert_alpha()
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
    def __init__(self, x, y, width, height, action):
        # Scale positions and sizes to match the resized images
        self.rect = pygame.Rect(
            int(x * SCALE_X),
            int(y * SCALE_Y),
            int(width * SCALE_X),
            int(height * SCALE_Y)
        )
        self.action = action 

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# Functions for button actions
def open_full_game():
    print("Opening Full Game")
    pygame.quit()
    subprocess.Popen(["python", "menu2.py"]) # Launch menu2.py
    sys.exit()

def open_abridged_game():
    print("Opening Abridged Game")
    pygame.quit()
    subprocess.Popen(["python", "menu2.py"])  # Launch menu2.py
    sys.exit()
    
def open_how_to_play():
    global htp_index
    htp_index = 0
    show_how_to_play()

def exit_app():
    pygame.quit()
    sys.exit()

def show_how_to_play():
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
                    button.action()  # Call the corresponding function

    # Draw the home background (buttons are part of the image)
    screen.blit(home_image, (0, 0))

    pygame.display.flip()

pygame.quit()
