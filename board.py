import pygame
import json

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