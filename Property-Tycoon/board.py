import pygame  # type: ignore
import json
import sys

# screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 568, 571
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Property Tycoon - Home")
htp_images = [
    pygame.transform.scale(pygame.image.load("pngs/htp1.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load("pngs/htp2.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load("pngs/htp3.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
]
htp_index = 0

# Load how to play image
properties = pygame.image.load("pngs/properties2.png").convert_alpha()
# Scale factors for button positions
SCALE_X = SCREEN_WIDTH / 600  # 0.9467
SCALE_Y = SCREEN_HEIGHT / 600  # 0.9517


class Button:
    """
    Generic button for the game.
    """
    def __init__(self, x, y, width, height, action):
        """
        Initialisation of the button
        - x: x position of the button
        - y: y position of the button
        - width: width of the button
        - height: height of the button
        - action: action of the button
        """
        # Scale positions and sizes to match the resized images
        self.rect = pygame.Rect(
            int(x * SCALE_X),
            int(y * SCALE_Y),
            int(width * SCALE_X),
            int(height * SCALE_Y)
        )
        self.action = action

    def is_clicked(self, mouse_pos):
        """ returns True if the button was clicked otherwise False."""
        return self.rect.collidepoint(mouse_pos)


def draw_scrollbar(screen, scrollbar_rect):
    """ Scroll bar for the how to play """
    pygame.draw.rect(screen, (0, 0, 0), scrollbar_rect)


def draw_content(screen, content_surface, scroll_offset):
    """ Draw the content to the screen """
    screen.blit(content_surface, (0, -scroll_offset))


class HelpButton:
    """
    Button to display the how to play page.
    """
    def __init__(self, x, y, width, height):
        """ Initialise the button with styling elements """
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 10)

    def is_clicked(self, mouse_pos):
        """ returns True if the button was clicked otherwise False."""
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """
        Draws onto the screen.
        """
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        text = self.font.render("?", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def display(self, screen):
        """
        Handles the navigation of the how to play with back, next, exit button and contains the display logic.
        - screen: The screen to draw on.
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


class ViewPropertiesButton:
    """
    A button to view all the cards of properties, scrollable.
    """
    def __init__(self, x, y, width, height):
        """Initialisation of the button"""
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 10)

    def is_clicked(self, mouse_pos):
        """ returns True if the button was clicked otherwise False."""
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """ Draws to the screen """
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        text = self.font.render("View Properties", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def display(self, screen):
        """ Handles the scrollable view of the property cards for user to see, drawn to screen."""
        global properties
        showing_properties = True
        exit_button = Button(690, 560, 100, 40, 'exit')
        image_width, image_height = properties.get_size()
        content_surface = pygame.Surface((image_width, image_height))
        content_surface.blit(properties, (0, 0))
        scrollbar_width = 10
        scrollbar_height = max(int(SCREEN_HEIGHT / 2861 * SCREEN_HEIGHT), 30)
        scrollbar_rect = pygame.Rect(760 - scrollbar_width, 0, scrollbar_width, scrollbar_height)

        scroll_offset = 0
        scrollbar_dragging = False
        drag_offset_y = 0

        clock = pygame.time.Clock()

        while showing_properties:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEWHEEL:
                    scroll_offset = max(0, min(scroll_offset - event.y * 20, 2861 - SCREEN_HEIGHT))
                    scrollbar_rect.y = int((scroll_offset / 2861) * SCREEN_HEIGHT)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if scrollbar_rect.collidepoint(event.pos):
                        scrollbar_dragging = True
                        drag_offset_y = event.pos[1] - scrollbar_rect.y

                    # Handle exit button on htp3
                    elif exit_button.is_clicked(mouse_pos):
                        showing_properties = False  # Return to home screen

                elif event.type == pygame.MOUSEBUTTONUP:
                    scrollbar_dragging = False

                # Handle dragging motion
                elif event.type == pygame.MOUSEMOTION and scrollbar_dragging:
                    if scrollbar_dragging:
                        scrollbar_rect.y = event.pos[1] - drag_offset_y
                        scrollbar_rect.y = max(0, min(scrollbar_rect.y, SCREEN_HEIGHT - scrollbar_height))
                        scroll_offset = int((scrollbar_rect.y / SCREEN_HEIGHT) * 2861)
            screen.fill((255, 255, 255))
            draw_content(screen, content_surface, scroll_offset)
            draw_scrollbar(screen, scrollbar_rect)
            # draw button
            pygame.draw.rect(screen, (255, 255, 255), exit_button.rect)
            pygame.draw.rect(screen, (0, 0, 0), exit_button.rect, 2)

            font = pygame.font.Font(None, 20)
            text = font.render("Exit", True, (0, 0, 0))
            text_rect = text.get_rect(center=exit_button.rect.center)
            screen.blit(text, text_rect)

            pygame.display.flip()
            clock.tick(60)


def load_board(file_path):
    """
    Loads the board from JSON file.
    - file_path: The path to the JSON file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def load_house_and_hotel_costs(filepath):
    """ Extracts the house and hotel costs from the JSON file"""
    with open(filepath, 'r') as file:
        data = json.load(file)
        return data["notes"]["house_and_hotel_costs"]


def draw_board(screen):
    """ Draws the board image to the screen """
    # Load the board image
    board_image = pygame.image.load("pngs/board.jpg").convert_alpha()
    # Scale the board image to fit the window size
    board_image = pygame.transform.scale(board_image, (762, 688))
    # Draw the board
    screen.blit(board_image, (0, 0))


position_coordinates = {
    1: (54, 448),  # Go
    2: (54, 402),  # The Old Creek
    3: (54, 363),  # Pot Luck
    4: (54, 324),  # Gangsters Paradise
    5: (54, 285),  # Income Tax
    6: (54, 246),  # Brighton Station
    7: (54, 207),  # The Angels Delight
    8: (54, 168),  # Opportunity Knocks
    9: (54, 129),  # Potter Avenue
    10: (54, 90),  # Granger Drive
    11: (54, 51),  # Jail/Just Visiting
    12: (108, 51),  # Skywalker Drive
    13: (147, 51),  # Tesla Power Co
    14: (186, 51),  # Wookie Hole
    15: (225, 51),  # Rey Lane
    16: (264, 51),  # Hove Station
    17: (303, 51),  # Bishop Drive
    18: (342, 51),  # Pot Luck
    19: (381, 51),  # Dunham Street
    20: (420, 51),  # Broyles Lane
    21: (459, 51),  # Free Parking
    22: (469, 90),  # Yue Fei Square
    23: (459, 129),  # Opportunity Knocks
    24: (459, 168),  # Mulan Rouge
    25: (459, 207),  # Han Xin Gardens
    26: (459, 246),  # Falmer Station
    27: (459, 285),  # Shatner Close
    28: (459, 324),  # Picard Avenue
    29: (459, 363),  # Edison Water
    30: (459, 402),  # Crusher Creek
    31: (459, 441),  # Go to Jail
    32: (420, 441),  # Sirat Mews
    33: (381, 441),  # Ghengis Crescent
    34: (330, 441),  # Pot Luck
    35: (303, 441),  # Ibis Close
    36: (264, 441),  # Portslade Station
    37: (215, 441),  # Opportunity Knocks
    38: (186, 441),  # James Webb Way
    39: (137, 441),  # Super Tax
    40: (108, 441)  # Turing Heights
}