import pygame # type: ignore
import json
import sys

SCREEN_WIDTH, SCREEN_HEIGHT = 568, 571
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Property Tycoon - Home")
htp_images = [
    pygame.transform.scale(pygame.image.load("pngs/htp1.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load("pngs/htp2.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
    pygame.transform.scale(pygame.image.load("pngs/htp3.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
]
htp_index = 0


properties = pygame.image.load("pngs/properties2.png").convert_alpha()
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
    
def draw_scrollbar(screen, scrollbar_rect):
    pygame.draw.rect(screen, (0, 0, 0), scrollbar_rect)

def draw_content(screen, content_surface, scroll_offset):
    screen.blit(content_surface, (0, -scroll_offset))

class HelpButton:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None,10)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self,screen):
        pygame.draw.rect(screen,(255,255,255),self.rect)
        pygame.draw.rect(screen,(0,0,0), self.rect, 2)
        text = self.font.render("?",True,(0,0,0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text,text_rect)

    
        
    def display(self,screen):
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
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None,10)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self,screen):
        pygame.draw.rect(screen,(255,255,255),self.rect)
        pygame.draw.rect(screen,(0,0,0), self.rect, 2)
        text = self.font.render("View Properties",True,(0,0,0))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text,text_rect)
        
    def display(self,screen):
        global properties
        showing_properties = True
        exit_button = Button(720, 560, 100, 40, 'exit')
        
        content_surface = pygame.Surface((831, 2860))
        content_surface.blit(properties, (0, 0))
        scrollbar_width = 10
        scrollbar_height = max(int(SCREEN_HEIGHT / 2861 * SCREEN_HEIGHT), 30)
        scrollbar_rect = pygame.Rect(760- scrollbar_width, 0, scrollbar_width, scrollbar_height)
       
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
                    scroll_offset =  max(0, min(scroll_offset - event.y*20, 2861 - SCREEN_HEIGHT))
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

            pygame.display.flip()
            clock.tick(60)
        
def load_board(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def draw_board(screen):
    # Load the board image
    board_image = pygame.image.load("pngs/board.png").convert_alpha()
    # Scale the board image to fit the window size
    board_image = pygame.transform.scale(board_image, (762, 688))
    # Draw the board
    screen.blit(board_image, (0, 0))

position_coordinates = {
    1: (44, 448),   # Go
    2: (44, 402),   # The Old Creek
    3: (44, 363),   # Pot Luck
    4: (44, 324),   # Gangsters Paradise
    5: (44, 285),   # Income Tax
    6: (44, 246),   # Brighton Station
    7: (44, 207),   # The Angels Delight
    8: (44, 168),   # Opportunity Knocks
    9: (44, 129),   # Potter Avenue
    10: (44, 90),   # Granger Drive
    11: (44, 51),   # Jail/Just Visiting
    12: (88, 51),   # Skywalker Drive
    13: (127, 51),  # Tesla Power Co
    14: (166, 51),  # Wookie Hole
    15: (205, 51),  # Rey Lane
    16: (244, 51),  # Hove Station
    17: (283, 51),  # Bishop Drive
    18: (322, 51),  # Pot Luck
    19: (361, 51),  # Dunham Street
    20: (400, 51),  # Broyles Lane
    21: (439, 51),  # Free Parking
    22: (439, 90),  # Yue Fei Square
    23: (439, 129), # Opportunity Knocks
    24: (439, 168), # Mulan Rouge
    25: (439, 207), # Han Xin Gardens
    26: (439, 246), # Falmer Station
    27: (439, 285), # Shatner Close
    28: (439, 324), # Picard Avenue
    29: (439, 363), # Edison Water
    30: (439, 402), # Crusher Creek
    31: (439, 441), # Go to Jail
    32: (400, 441), # Sirat Mews
    33: (361, 441), # Ghengis Crescent
    34: (322, 441), # Pot Luck
    35: (283, 441), # Ibis Close
    36: (244, 441), # Portslade Station
    37: (205, 441), # Opportunity Knocks
    38: (166, 441), # James Webb Way
    39: (127, 441), # Super Tax
    40: (88, 441)   # Turing Heights
}