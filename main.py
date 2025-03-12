import pygame
from dice import DiceButton, rolldice, draw_dice
from board import load_board, position_coordinates

def main_game_loop(players):
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((762, 688))  # The window size
    pygame.display.set_caption("Player Tycoon")

    # Load the board image
    board_image = pygame.image.load("pngs/board.png").convert_alpha()
    # Scale the board image to fit the window size
    board_image = pygame.transform.scale(board_image, (762, 688))

    # Create a DiceButton instance
    dice_button = DiceButton(555, 292, 117, 35)

    # Main game loop
    running = True
    current_number1 = 1 
    current_number2 = 1  
    dice1_position = (510, 207) 
    dice2_position = (649, 207) 

    current_player_index = 0  # Start with Player 1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if dice_button.is_clicked(pygame.mouse.get_pos()):
                    a, b = rolldice()
                    current_number1 = a
                    current_number2 = b
                    total = a + b

                    # Move the current player
                    current_player = players[current_player_index]
                    current_player.position = (current_player.position + total - 1) % 40 + 1

                    # Switch to the next player
                    current_player_index = (current_player_index + 1) % len(players)

                    print(f"Player {current_player_index + 1} moved to position {current_player.position}")

        # Draw the scaled board
        screen.blit(board_image, (0, 0))

        # Draw dice 1
        draw_dice(screen, current_number1, dice1_position)

        # Draw dice 2
        draw_dice(screen, current_number2, dice2_position)

        # Draw player tokens
        for player in players:
            x, y = position_coordinates[player.position]
            pygame.draw.circle(screen, player.token_color, (x, y), 10)  


        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main_game_loop()