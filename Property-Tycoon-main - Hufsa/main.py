import pygame
from dice import DiceButton, rolldice, draw_dice
from board import load_board, position_coordinates, HelpButton, ViewPropertiesButton
from player import Player
from bank import Bank
import pygame
from properties import Button, buy_property, rent_payment
from auction import auction_game_loop
    
def draw_player_laps(screen, interactive_players, laps_positions):
    """
    Draw each interactive player's lap count at the specified positions.
    - interactive_players: the list of human/interactive players (NOT including the AI).
    - laps_positions: a list of (x, y) coordinates for each player's lap counter.
                      The first entry is for player 1, the second for player 2, etc.
    """
    font = pygame.font.Font(None, 24)
    for i, player in enumerate(interactive_players):
        if player is not None:
            # Render the lap count
            text_surface = font.render(f"Laps: {player.laps_completed}", True, (0, 0, 0))
            # Draw at the specified position
            x, y = laps_positions[i]
            screen.blit(text_surface, (x, y))

def draw_player_money(screen, full_players, positions):
    """
    (Unchanged from before)
    Draw each player's balance on the board at specified positions.
    full_players: a list of 6 slots; slots 0 to 4 for interactive players (or None)
                  and slot 5 reserved for the AI player.
    positions: a list of six (x, y) tuples for where to draw each slot's balance.
    """
    font = pygame.font.Font(None, 24)
    if len(positions) != 6:
        raise ValueError("You must provide exactly six positions for six players.")

    for i in range(6):
        # For the AI slot (index 5) always show "£1500"
        if i == 5:
            balance_text = "£1500"
        else:
            if full_players[i] is not None:
                balance_text = f"£{full_players[i].balance}"
            else:
                balance_text = ""
        text_surface = font.render(balance_text, True, (0, 0, 0))
        screen.blit(text_surface, positions[i])

def draw_players_properties(screen, full_players, positions):
    font = pygame.font.Font(None, 14)
    if len(positions) != 6:
        raise ValueError("You must provide exactly six positions for six players.")

    for i in range(6):        
        if full_players[i] is not None:
            properties_text = full_players[i].properties
        else:
            properties_text = []
        y_offset = 0
        for p in properties_text:
            text_surface = font.render(str(p), True, (0, 0, 0))
            screen.blit(text_surface, (positions[i][0], positions[i][1]+y_offset))
            y_offset += font.get_linesize()
            
def main_game_loop(interactive_players):
    pygame.init()

    board_data = load_board("board_data.json")
    board = board_data["board"]

    # Count how many interactive (human) players we have
    num_interactive = len(interactive_players)

    # Create the AI player (always present) with fixed balance of £1500
    ai_player = Player((0, 255, 255))  # Example: Cyan token for AI
    ai_player.balance = 1500
    
    bank = Bank()

    # For display, build a list of 6 slots: 0-4 for interactive players, 5 for AI
    full_players = interactive_players[:]
    while len(full_players) < 5:
        full_players.append(None)
    full_players.append(ai_player)

    # Set up display
    original_resolution = (762, 688)
    screen = pygame.display.set_mode(original_resolution)
    pygame.display.set_caption("Player Tycoon")

    # Load the board image
    board_image = pygame.image.load("pngs/board.png").convert_alpha()
    board_image = pygame.transform.scale(board_image, original_resolution)

    # Create UI elements
    dice_button = DiceButton(555, 292, 117, 35)
    help_button = HelpButton(653, 7, 20, 16)
    auction_button = Button(637, 401, 104, 53)
    buy_button = Button(508, 401, 103, 53)
    view_properties = ViewPropertiesButton(554, 7, 94, 16)

    # Positions for displaying money for six slots
    money_display_positions = [
        (52, 511),   # Slot 1: Player 1
        (170, 511),  # Slot 2: Player 2
        (295, 511),  # Slot 3: Player 3
        (419, 511),  # Slot 4: Player 4
        (546, 511),  # Slot 5: Player 5
        (665, 511)   # Slot 6: AI
    ]

    # Positions for displaying laps for each interactive player (1–5).
    laps_positions = [
        (52, 666),   # Player 1
        (170, 666),  # Player 2 - placeholder, change as needed
        (294, 666),  # Player 3 - placeholder
        (415, 666),  # Player 4 - placeholder
        (542, 666)   # Player 5 - placeholder
    ]
    
    properties_display_positions = [
        (40, 570),   # Slot 1: Player 1
        (160, 570),  # Slot 2: Player 2
        (295, 570),  # Slot 3: Player 3
        (419, 570),  # Slot 4: Player 4
        (546, 570),  # Slot 5: Player 5
        (665, 570)   # Slot 6: AI
    ]

    # Define the text display area under the "Roll" button
    text_display_rect = pygame.Rect(555, 360, 200, 50)  # Adjust position and size as needed
    font = pygame.font.Font(None, 20)  # Font for the text

    # Initialize text variables
    current_landing_piece = ""  # Initialize with an empty string
    rent_text = ""

    # Game state
    running = True
    current_number1 = 1
    current_number2 = 1
    dice1_position = (510, 207)
    dice2_position = (649, 207)
    current_player_index = 0  # Only cycles among interactive players
    current_player_text = f"Player {current_player_index + 1}"  # Initialize with the first player

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if dice_button.is_clicked(mouse_pos):
                    a, b = rolldice()
                    current_number1 = a
                    current_number2 = b
                    total = a + b

                    # Move only if we have at least 1 interactive player
                    if num_interactive > 0:
                        current_player = interactive_players[current_player_index]
                        old_position = current_player.position
                        new_position = (old_position + total - 1) % 40 + 1
                        current_player.position = new_position

                        # Check if we passed Go: new_position < old_position
                        if new_position < old_position:
                            current_player.laps_completed += 1
                            current_player.add_money(200)  # Add £200 for passing GO

                        # Get the name of the board piece the player landed on
                        #board_data = load_board("board_data.json")
                        landing_piece = board[current_player.position - 1]["name"]
                        board_tile = board[current_player.position - 1]
                        rent_text = rent_payment(current_player, board_tile, bank, full_players)
                        current_landing_piece = f"Landed on: {landing_piece}"
                        current_player_text = f"Player {current_player_index + 1}"

                        print(f"Player {current_player_index + 1} moved to position {new_position}")
                        
                        # Cycle to next interactive player
                        current_player_index = (current_player_index + 1) % num_interactive

                if help_button.is_clicked(mouse_pos):
                    print("open help menu")
                    help_button.display(screen)

                if view_properties.is_clicked(mouse_pos):
                    print("view properties")
                    properties_resolution = (760, 570)
                    screen = pygame.display.set_mode(properties_resolution)
                    view_properties.display(screen)
                    screen = pygame.display.set_mode(original_resolution)

                if auction_button.is_clicked(mouse_pos):
                    print("auction button clicked")
                    bid_winner = auction_game_loop()  
                    #board_data = load_board("board_data.json")
                    #board = board_data["board"]
                    board_position = next((i for i in board if i["position"] == current_player.position), None) # gets the position of property
                    screen = pygame.display.set_mode(original_resolution)            
                    bid_winner = interactive_players[bid_winner]
                    buy_property(bid_winner, board_position,bank) # makes who wins the bid own the property
                    
                if buy_button.is_clicked(mouse_pos):
                    print("buy button clicked")
                    #board_data = load_board("board_data.json")
                    #board = board_data["board"]
                    board_position = next((i for i in board if i["position"] == current_player.position), None)
                    buy_property(current_player, board_position,bank)
                    

        # Draw board and game elements
        screen.blit(board_image, (0, 0))
        draw_dice(screen, current_number1, dice1_position)
        draw_dice(screen, current_number2, dice2_position)
        help_button.draw(screen)
        view_properties.draw(screen)

        # Draw tokens for interactive players
        for p in interactive_players:
            x, y = position_coordinates[p.position]
            pygame.draw.circle(screen, p.token_color, (x, y), 10)

        # Draw AI token
        x_ai, y_ai = position_coordinates[ai_player.position]
        pygame.draw.circle(screen, ai_player.token_color, (x_ai, y_ai), 10)

        # Draw each player's money
        draw_player_money(screen, full_players, money_display_positions)

        # Draw the laps for each interactive player
        draw_player_laps(screen, interactive_players, laps_positions)
        
        draw_players_properties(screen, full_players, properties_display_positions)

        # Draw the text display area under the "Roll" button
        text_surface = font.render(current_landing_piece, True, (0, 0, 0))  # Text color
        screen.blit(text_surface, (text_display_rect.x - 40, text_display_rect.y - 7))  # Adjust text position

        # Draw the rent message under the "Roll" button
        rent_surface = font.render(rent_text, True, (0,0,0))
        screen.blit(rent_surface, (text_display_rect.x - 40, text_display_rect.y + 10))


        # Render the current player text
        player_text_surface = font.render(current_player_text, True, (0, 0, 0))  # Text color
        screen.blit(player_text_surface, (text_display_rect.x - 40, text_display_rect.y - 20))  # Adjust text position

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    # Example testing with 2 interactive players
    # from player import Player
    # players = [
    #     Player((255, 0, 0)),  # Player 1
    #     Player((0, 255, 0))   # Player 2
    # ]
    # main_game_loop(players)
    main_game_loop([])
