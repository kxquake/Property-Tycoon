import pygame
from dice import DiceButton, check_if_double, rolldice, draw_dice
from board import load_board, position_coordinates

def main_game_loop(players):
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((762, 688))  # The window size
    pygame.display.set_caption("Player Tycoon")

    # Load the board image
    board_image = pygame.image.load("pngs/board.png").convert_alpha()
    board_image = pygame.transform.scale(board_image, (762, 688))

    # Create a DiceButton instance
    dice_button = DiceButton(555, 292, 117, 35)

    # Define the text display area under the "Roll" button
    text_display_rect = pygame.Rect(555, 360, 200, 50)  # Adjust position and size as needed
    font = pygame.font.Font(None, 20)  # Font for the text

    # Main game loop
    running = True
    current_number1 = 1
    current_number2 = 1
    dice1_position = (510, 207)
    dice2_position = (649, 207)
    current_player_index = 0  # Start with Player 1
    dice_roll_popup = None  # To store the current popup
    doubles_count = 0  # Track how many doubles have been rolled in a row
    current_landing_piece = ""  # Initialize with an empty string
    current_player_text = f"Player {current_player_index + 1}"  # Initialize with the first player

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the click is within the "Roll" button's rectangle
                if dice_button.is_clicked(pygame.mouse.get_pos()):
                    a, b = rolldice()
                    current_number1 = a
                    current_number2 = b
                    total = a + b

                    # Check if it's a double
                    if check_if_double(a, b):
                        doubles_count += 1
                        print(f"Double thrown! Player {current_player_index + 1} gets another turn.")
                        if doubles_count == 3:  # Three doubles in a row sends the player to jail
                            print(f"Player {current_player_index + 1} rolled three doubles and goes to jail!")
                            players[current_player_index].position = 11  # Jail position
                            doubles_count = 0  # Reset doubles count
                            current_player_index = (current_player_index + 1) % len(players)  # Move to the next player
                        else:
                            # Player gets another turn
                            continue
                    else:
                        # Not a double, reset doubles count
                        doubles_count = 0

                    # Move the current player
                    current_player = players[current_player_index]
                    current_player.position = (current_player.position + total - 1) % 40 + 1

                    # Get the name of the board piece the player landed on
                    board_data = load_board("board_data.json")
                    landing_piece = board_data["board"][current_player.position - 1]["name"]
                    current_landing_piece = f"Landed on: {landing_piece}"

                    # Update the current player text
                    current_player_text = f"Player {current_player_index + 1} "

                    
                    # Switch to the next player
                    current_player_index = (current_player_index + 1) % len(players)

        # Draw the scaled board
        screen.blit(board_image, (0, 0))

        # Draw dice
        draw_dice(screen, current_number1, dice1_position)
        draw_dice(screen, current_number2, dice2_position)

        # Draw player tokens
        for player in players:
            x, y = position_coordinates[player.position]
            pygame.draw.circle(screen, player.token_color, (x, y), 10)  # Adjust size as needed

        # Draw the text display area
        text_surface = font.render(current_landing_piece, True, (0, 0, 0))  # Text color
        screen.blit(text_surface, (text_display_rect.x - 40, text_display_rect.y + 10))  # Adjust text position

         # Render the current player text
        player_text_surface = font.render(current_player_text, True, (0, 0, 0))  # Text color
        screen.blit(player_text_surface, (text_display_rect.x - 40, text_display_rect.y - 15))  # Adjust text position

        



        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main_game_loop()