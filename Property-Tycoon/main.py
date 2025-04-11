import pygame
from dice import DiceButton, rolldice, draw_dice
from board import load_board, load_house_and_hotel_costs, position_coordinates, HelpButton, ViewPropertiesButton
from ai_agent import AIAgent
from bank import Bank
import pygame
from properties import Button, buy_property, rent_payment
from auction import auction_game_loop
from trade import SellAssetsButton, SellAssetsMenuPopUp
from house_hotel_popup import Build_popup
from cards import CardDeck
import time
import random

import sys

def display_msg(message_log, text, max_msgs=3):
    """
    Used to display messages in the board game so players know relevant, important messages regarding the game state.
    - message_log: the list storing current game messages.
    - max_msgs: the maximum messages to keep in the log.
    """
    message_log.append(text)
    if len(message_log) > max_msgs:
        message_log.pop(0)

def wrap_text(text, font, max_width):
    """
    Used to wrap the message log's long strings of text to fit a given width.
    - text: the text to wrap.
    - font: the font object to calculate text width.
    - max_width: the maximum allowed width.
    Returns:
        The wrapped text.
    """
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines


def draw_player_laps(screen, interactive_players, laps_positions):
    """
    Draw each interactive player's lap count at the specified positions.
    - interactive_players: the list of human/interactive players (including the AI).
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


def draw_player_money(screen, interactive_players, positions):
    """
    Draw each player's balance on the board at specified positions.
    interactive_players = all players, human and ai
    positions: a list of six (x, y) tuples for where to draw each slot's balance.
    """
    font = pygame.font.Font(None, 24)
    if len(positions) != 6:
        raise ValueError("You must provide exactly six positions for six players.")

    for i in range(len(positions)):
        if i < len(interactive_players) and interactive_players[i] is not None:
            balance_text = f"£{interactive_players[i].balance}"
        else:
            balance_text = ""
        text_surface = font.render(balance_text, True, (0, 0, 0))
        screen.blit(text_surface, positions[i])


def draw_players_properties(screen, interactive_players, positions, scroll_offset = 0):
    """
    Draws a list of each player's owned properties at their designated positions.
    - screen: The surface to draw on.
    - interactive_players: The list of players.
    - scroll_offset: Vertical offset for scrolling properties
    """
    font = pygame.font.Font(None, 14)
    max_width = 85

    if scroll_offset is None:
        scroll_offset = [0 for _ in range(6)]

    if len(positions) != 6:
        raise ValueError("You must provide exactly six positions for six players.")

    for i in range(len(positions)):
        if i < len(interactive_players) and interactive_players[i] is not None:
            properties_text = interactive_players[i].properties
        else:
            properties_text = []

        y_offset = scroll_offset
        for p in properties_text:
            name = p.get("name")
            wrapped_lines = wrap_text(name, font, max_width)
            for line in wrapped_lines:
                text_surface = font.render(line, True, (0, 0, 0))
                screen.blit(text_surface, (positions[i][0], positions[i][1] + y_offset))
                y_offset += font.get_linesize()

def take_turn(interactive_players, current_player_index, num_interactive, board, bank, message_log, cost_data, ai_agent=None):
    """
    Executes the game logic for each player, it also handles jail logic, movement, rent, property purchases
    and decision flags for the UI of the game so that players can make choices.
    - interactive_players: list of all players
    - current_player_index: Index of the current player taking their turn.
    - num_interactive: The number of human players.
    - board: The game board spaces.
    - bank: The bank object handling transactions.
    - message_log: Log to track messages to be displayed.
    - cost_data: The cost data for building houses and hotels.
    - ai_agent: The AI decision-making logic.
    Returns:
        Tuple of 8 values:
        - current_number1 (int): Value of first die.
        - current_number2 (int): Value of second die.
        - current_player_index (int): Updated index of the current player.
        - awaiting_property_decision (bool): Whether the player has to choose to buy or auction a property.
        - extra_turn (bool): Whether the player gets an extra turn due to rolling a double.
        - current_landing_piece (str): Name of the property/space landed on.
        - current_player_text (str): Name of player, e.g "player 1"
        - awaiting_choice (bool): Determines if the player has a decision to make (e.g. pay a fine or draw a card)
    """
    active_player = interactive_players[current_player_index]
    current_player_text = f"Player {current_player_index + 1}"
    current_landing_piece = "Jail/Just visiting"

    awaiting_choice = False

    a, b = rolldice()
    current_number1 = a
    current_number2 = b
    total = a + b

    # Skip go if player in jail, release if enough turns completed
    if active_player.in_jail:
        # So it decrements whenever this is true
        active_player.jail_turns_remaining = active_player.jail_turns_remaining - 1

        # if they have a get out of jail free card
        if active_player.get_out_of_jail_free == 2:
            display_msg(message_log, f"{current_player_text} released from jail as owns 'Get Out Of Jail Free' card")
            active_player.get_out_of_jail_free -= 1
            active_player.in_jail = False
            current_player_index = (current_player_index + 1) % num_interactive
            return 1, 1, current_player_index, False, False, current_landing_piece, current_player_text, False
        # If player just got into jail, they have a choice to pay £50 fine
        if active_player.jail_turns_remaining == 2:
            active_player.position = 11
            if active_player.balance >= 50:
                if active_player.is_ai and ai_agent:
                    if ai_agent.pay_jail_fine():
                        jail_fee = 50
                        active_player.deduct_money(jail_fee, message_log)
                        bank.free_parking_pool += jail_fee
                        display_msg(message_log, f"AI paid £50 to get out of jail.")
                        print(f"AI paid £50 to get out of jail")
                        active_player.in_jail = False
                        return 1, 1, current_player_index, False, False, current_landing_piece, current_player_text, False
                    else:
                        display_msg(message_log, "AI chose not to pay fine, remains in jail.")
                        print("AI chose to remain in jail.")
                        current_player_index = (current_player_index + 1) % num_interactive
                        return 1, 1, current_player_index, False, False, current_landing_piece, current_player_text, False
                else:
                    display_msg(message_log, "Pay £50 fee for release? Press Y for 'yes' N for 'no'.")
                    return 1, 1, current_player_index, False, False, current_landing_piece, current_player_text, True
            else:
                display_msg(message_log, "Player cannot afford £50 fine, remains in jail.")
                current_player_index = (current_player_index + 1) % num_interactive
                return 1, 1, current_player_index, False, False, current_landing_piece, current_player_text, False

        elif active_player.jail_turns_remaining > 0:
            display_msg(message_log, f"{current_player_text} is in jail. Skipping turn.")
            current_player_index = (current_player_index + 1) % num_interactive
            return 1, 1, current_player_index, False, False, current_landing_piece, current_player_text, False
        else:
            display_msg(message_log, f"{current_player_text} is released from jail.")
            active_player.in_jail = False
            current_player_index = (current_player_index + 1) % num_interactive
            return 1, 1, current_player_index, False, False, current_landing_piece, current_player_text, False

    # Move only if we have at least 1 interactive player
    if num_interactive > 0:
        active_player = interactive_players[current_player_index]
        old_position = active_player.position
        new_position = (old_position + total - 1) % 40 + 1
        active_player.position = new_position

        # Put player in jail if they land on tile 'Go to jail'
    if active_player.position == 31:

        display_msg(message_log, f"{current_player_text} sent to jail")
        print(f"{current_player_text} sent to jail, landed on go to jail.")
        active_player.position = 11
        # can player afford jail fee
        if active_player.balance >= 50:
            # If the current player is AI, it goes through its own if statement
            if active_player.balance >= 50:
                if active_player.is_ai and ai_agent:
                    if ai_agent.pay_jail_fine():
                        jail_fee = 50
                        active_player.deduct_money(jail_fee, message_log)
                        bank.free_parking_pool += jail_fee
                        display_msg(message_log, "AI paid £50 to get out of jail.")
                        print("AI paid £50 fine")
                        current_player_index = (current_player_index + 1) % num_interactive
                    else:
                        display_msg(message_log, "AI chose not to pay fine, remains in jail.")
                        print("AI did not pay fine")
                        active_player.in_jail = True
                        #Three turns as it immediately decrements when it accesses player.in_jail
                        active_player.jail_turns_remaining = 3
                        active_player.double_roll_count = 0
                        current_player_index = (current_player_index + 1) % num_interactive
                else:
                    display_msg(message_log, "Pay £50 fee for release? Press Y for 'yes' N for 'no'.")
                    active_player.awaiting_choice = True
            else:
                display_msg(message_log, "Player cannot afford to pay £50 fine.")
                print("Player cannot afford £50 fine.")
                active_player.in_jail = True
                # Three turns as it immediately decrements when it accesses player.in_jail
                active_player.jail_turns_remaining = 3
                active_player.double_roll_count = 0
                current_player_index = (current_player_index + 1) % num_interactive

            return 1, 1, current_player_index, False, False, current_landing_piece, current_player_text, awaiting_choice

    #If player lands on free parking, they get all the money
    if active_player.position == 21:
        display_msg(message_log, "Player gains all funds in the free parking pool")
        print("Player gains all funds in free parking pool")
        funds = bank.collect_free_parking(active_player, message_log)
        display_msg(message_log, f"Player gains: {funds} from the free parking pool")

    # Check if player passed Go
    if new_position < old_position:
        active_player.laps_completed += 1
        active_player.add_money(200, message_log)  # Add £200 for passing GO
        display_msg(message_log, f"{current_player_text} passed Go, +£200")

    board_tile = board[new_position - 1]
    landing_piece = board_tile["name"]
    rent_text = rent_payment(active_player, board_tile, bank, interactive_players, message_log,
                             dice_total=total)
    rent = 0
    rent_msg = ""
    if rent_text:
        if isinstance(rent_text, tuple):
            rent_msg, rent = rent_text
            for line in rent_text:
                display_msg(message_log, str(line))
        else:
            rent_msg = rent_text
            display_msg(message_log, str(rent_text))

    if rent_msg == "Not enough funds for rent, sell assets":
        if active_player.is_ai and ai_agent:
            if ai_agent.can_cover_rent_with_assets(rent, board, cost_data):
                ai_agent.ai_sell_assets_or_mortgage(rent, board, bank, message_log)
            else:
                declare_bankruptcy(active_player, board, bank, message_log)
        else:
            sell_assets_popup = SellAssetsMenuPopUp(active_player, active_player.properties, board, 100,
                                                    100, 500, 500)
            showing_sell_assets_popup = True

    current_landing_piece = f"Landed on: {landing_piece}"
    current_player_text = f"Player {current_player_index + 1}"

    print(f"Player {current_player_index + 1} moved to position {new_position}")
    can_be_bought = board[active_player.position - 1]["can_be_bought"]

    extra_turn = False
    # Double roll check
    if a == b:
        active_player.double_roll_count += 1
        display_msg(message_log, "You rolled a double")
        if active_player.double_roll_count == 3:
            active_player.position = 11

            if active_player.balance >= 50:
                if active_player.is_ai and ai_agent:
                    if ai_agent.pay_jail_fine():
                        jail_fee = 50
                        active_player.deduct_money(jail_fee, message_log)
                        bank.free_parking_pool += jail_fee
                        display_msg(message_log, "AI paid £50 to get out of jail.")
                        print("AI paid £50 fine")
                    else:
                        display_msg(message_log, "AI chose not to pay fine, remains in jail.")
                        print("AI did not pay fine")
                        active_player.in_jail = True
                        # Three turns as it immediately decrements when it accesses player.in_jail
                        active_player.jail_turns_remaining = 3
                        active_player.double_roll_count = 0
                else:
                    display_msg(message_log, "Pay £50 fee for release? Press Y for 'yes' N for 'no'.")
                    active_player.awaiting_choice = True
            else:
                display_msg(message_log, "Player cannot afford to pay £50 fine.")
                print("Player cannot afford £50 fine.")
                active_player.in_jail = True
                # Three turns as it immediately decrements when it accesses player.in_jail
                active_player.jail_turns_remaining = 2
                active_player.double_roll_count = 0
        else:
            extra_turn = True
    else:
        active_player.double_roll_count = 0
        extra_turn = False

    # make sure player presses 'buy' or 'auction' property before next player's turn
    if can_be_bought and active_player.laps_completed > 0 and board_tile.get("player") == 'Bank':
        if active_player.is_ai and ai_agent:
            wants_to_buy = ai_agent.ai_buy_property(board_tile)
            if wants_to_buy:
                display_msg(message_log, f"AI decided to buy {board_tile['name']}")
                buy_property(active_player, board_tile, bank, message_log)
            else:
                display_msg(message_log, f"AI chose not to buy {board_tile['name']}, starting auction")
                bid_winner, highest_bid = auction_game_loop(interactive_players, ai_agent=ai_agent, auction_property=board_tile)
                if bid_winner is not None:
                    winner = interactive_players[bid_winner]
                    buy_property(winner, board_tile, bank, message_log, price=highest_bid)
                    #added resolution to fix screen size
                original_resolution = (762, 688)
                pygame.display.set_mode(original_resolution)

            ai_agent.ai_build_houses_and_hotels(bank, board, cost_data, message_log)

            awaiting_property_decision = False
            if not extra_turn:
                current_player_index = (current_player_index + 1) % num_interactive

        else:
            awaiting_property_decision = True
            display_msg(message_log, "Please press either keep or auction property")

    else:
        # Cycle to next interactive player
        awaiting_property_decision = False

        if active_player.is_ai and ai_agent:
            ai_agent.ai_build_houses_and_hotels(bank, board, cost_data, message_log)

        if not extra_turn:
            current_player_index = (current_player_index + 1) % num_interactive

    return current_number1, current_number2, current_player_index, awaiting_property_decision, extra_turn, \
        current_landing_piece, current_player_text, awaiting_choice

def main_game_loop(interactive_players, abridged_mode=False, time_limit_minutes=None):
    """
    The main game loop runs the entirety of the monopoly game depending on what type the user picked (abridged/full).
    It handles: turn progression, user input, event handling, AI moves, making sure the game state is drawn and
    checks if endgame conditions are met.
    - interactive_players: the list of players including the AI agent
    - abridged_mode: Whether the game should end after a fixed time. Default is False.
    - time_limit_minutes: The time limit in minutes for abridged mode. Default is None.
    """
    pygame.init()

    board = load_board("board_data.json")["board"]
    cost_data = load_house_and_hotel_costs("board_data.json")

    # Count how many interactive players we have
    num_interactive = len(interactive_players)

    bank = Bank()

    can_build = False
    awaiting_property_decision = False
    showing_build_popup = False
    build_popup = None

    time_limit_reached = False

    # abridged mode
    if abridged_mode and time_limit_minutes is not None:
        time_limit_seconds = time_limit_minutes * 60 #make sure time is in minutes
        start_time = time.time()
        time_limit_reached = False
    else:
        time_limit_seconds = None
        start_time = None

    properties_scroll_offset = 0

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
    auction_button = Button(677, 425, 106, 55)
    buy_button = Button(540, 425, 106, 55)
    view_properties = ViewPropertiesButton(554, 7, 94, 16)
    sell_assets_button = SellAssetsButton(212, 93, 100, 60)
    build_button = Button(228, 183, 100, 40, "BUILD")

    # Positions for displaying money for six slots
    money_display_positions = [
        (62, 511),  # Slot 1: Player 1
        (180, 511),  # Slot 2: Player 2
        (305, 511),  # Slot 3: Player 3
        (429, 511),  # Slot 4: Player 4
        (546, 511),  # Slot 5: Player 5
        (665, 511)  # Slot 6: Player 6
    ]

    # Positions for displaying laps for each interactive player (1–5).
    laps_positions = [
        (52, 669),  # Player 1
        (170, 669),  # Player 2 - placeholder, change as needed
        (294, 669),  # Player 3 - placeholder
        (415, 669),  # Player 4 - placeholder
        (542, 669),  # Player 5 - placeholder
        (655, 669)  # Player 6 - placeholder
    ]

    properties_display_positions = [
        (50, 570),  # Slot 1: Player 1
        (170, 570),  # Slot 2: Player 2
        (295, 570),  # Slot 3: Player 3
        (419, 570),  # Slot 4: Player 4
        (546, 570),  # Slot 5: Player 5
        (665, 570)  # Slot 6: Player 6
    ]

    # Define the text display area under the "Roll" button
    text_display_rect = pygame.Rect(555, 360, 200, 50)  # Adjust position and size as needed
    font = pygame.font.Font(None, 20)  # Font for the text

    # Initialize text variables
    current_landing_piece = ""  # Initialize with an empty string
    rent_text = ""
    message_log = []

    # Game state
    running = True
    current_number1 = 1
    current_number2 = 1
    dice1_position = (516, 207)
    dice2_position = (655, 207)
    current_player_index = 0  # Only cycles among interactive players
    current_player_text = f"Player {current_player_index + 1}"  # Initialize with the first player
    active_player = interactive_players[current_player_index]
    extra_turn = False
    awaiting_choice = False

    ai_player = next((p for p in interactive_players if getattr(p, "is_ai", False)), None)
    ai_agent = AIAgent(ai_player) if ai_player else None

    #sell assets popup
    showing_sell_assets_popup = False
    sell_assets_popup = None

    while running:

        active_player = interactive_players[current_player_index]

        if abridged_mode and time_limit_seconds is not None:
            time_left = max(0, int(time_limit_seconds - (time.time() - start_time))) #stops clock at 0
        else:
            time_left = None

        if abridged_mode and not time_limit_reached and (time.time() - start_time) >= time_limit_seconds:
            print("Time limit reached")
            time_limit_reached = True

        if time_limit_reached and current_player_index == 0:
            player_balances = [(i + 1, calculate_assets(player, board)) for i, player in enumerate(interactive_players)]
            max_value = max(player_balances, key=get_asset_value)[1]
            # work out if players tie.
            tied_players = [p for p in player_balances if p[1] == max_value]

            if len(tied_players) > 1:
                tie_names = ", ".join(f"Player {p[0]}" for p in tied_players)
                print(f"Tie between {tie_names} with £{max_value} in total assets!")
                winner_message = f"Tie! {tie_names} all have £{max_value} in total assets!"
            else:
                winner = tied_players[0]
                print(f"Player {winner[0]} wins with £{winner[1]} in total assets!")
                winner_message = f"Player {winner[0]} wins with £{winner[1]} in total assets!"

            result = endgame_popup(screen, winner_message)

            if result == "quit":
                pygame.quit()
                exit()
            elif result == "menu":
                return "menu"
            running = False

        anybody_waiting = any(player.awaiting_choice for player in interactive_players if player is not None)
        if active_player.is_ai and not awaiting_property_decision and not awaiting_choice and not anybody_waiting:
            time.sleep(1)
            display_msg(message_log, f"AI taking turn")
            current_number1, current_number2, current_player_index, awaiting_property_decision, extra_turn, \
                current_landing_piece, current_player_text, awaiting_choice = take_turn(interactive_players,
                current_player_index, num_interactive, board, bank, message_log, cost_data, ai_agent=ai_agent)
            active_player = interactive_players[current_player_index]

        if active_player.is_ai:
            ai_agent = AIAgent(active_player)

            if active_player.balance > 300:
                ai_agent.ai_build_houses_and_hotels(bank, board, cost_data, message_log)
            elif active_player.balance < 150:
                if random.random() < 0.5:
                    ai_agent.sell_houses_hotels(board, bank, message_log)
                if random.random() < 0.3:
                    ai_agent.mortgage_properties(board, bank, message_log)
                if random.random() < 0.2:
                    ai_agent.sell_properties(board, bank, message_log)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and (awaiting_choice or getattr(active_player, "awaiting_choice", False)):
                if event.key == pygame.K_y:
                    jail_fee = 50
                    if active_player.balance >= jail_fee:
                        active_player.deduct_money(jail_fee, message_log)
                        bank.free_parking_pool += jail_fee
                        display_msg(message_log, "Fine has been paid.")
                        active_player.in_jail = False
                        active_player.awaiting_choice = False
                    else:
                        display_msg(message_log, "You cannot afford the fine.")
                    active_player.double_roll_count = 0
                    awaiting_choice = False
                    active_player.awaiting_choice = False
                    current_player_index = (current_player_index + 1) % num_interactive

                elif event.key == pygame.K_n:
                    display_msg(message_log, "Fine not paid, player remains in jail.")
                    active_player.in_jail = True
                    active_player.jail_turns_remaining = 2
                    active_player.double_roll_count = 0
                    awaiting_choice = False
                    active_player.awaiting_choice = False
                    current_player_index = (current_player_index + 1) % num_interactive

                elif event.key == pygame.K_f:
                    if active_player.pending_card_choice and active_player.pending_card_choice.get(
                            "type") == "fine_or_card":
                        fine_amount = active_player.pending_card_choice.get("fine_amount", 0)
                        active_player.deduct_money(fine_amount, message_log)
                        bank.free_parking_pool += fine_amount
                        display_msg(message_log, f"{fine_amount} fine paid")
                        active_player.awaiting_choice = False
                        active_player.pending_card_choice = None

                elif event.key == pygame.K_o:
                    if active_player.pending_card_choice and active_player.pending_card_choice.get(
                            "type") == "fine_or_card":
                        opportunity_deck = CardDeck("opportunity_knocks.json")
                        new_card = opportunity_deck.draw_card()
                        if new_card:
                            result =opportunity_deck.card_action(active_player, bank, new_card, interactive_players, board,
                                                         message_log)
                            if result == "awaiting_choice":
                                awaiting_choice = True
                                active_player.awaiting_choice = True
                        active_player.awaiting_choice = False
                        active_player.pending_card_choice = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if (
                        dice_button.is_clicked(mouse_pos)
                        and not awaiting_property_decision
                        and not awaiting_choice
                        and not active_player.awaiting_choice
                ):
                    current_number1, current_number2, current_player_index, awaiting_property_decision, extra_turn, \
                        current_landing_piece, current_player_text, awaiting_choice = take_turn(interactive_players, current_player_index, num_interactive,
                                                          board, bank, message_log, cost_data, ai_agent=ai_agent)
                    active_player = interactive_players[current_player_index]

                    if awaiting_choice:
                        active_player.awaiting_choice = True

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
                    board_tile = next((tile for tile in board if tile["position"] == active_player.position), None)
                    bid_winner, highest_bid = auction_game_loop(interactive_players, ai_agent=ai_agent, auction_property=board_tile)
                    board_position = next((i for i in board if i["position"] == active_player.position), None) # gets the position of property
                    screen = pygame.display.set_mode(original_resolution)
                    if bid_winner is not None:
                        bid_winner = interactive_players[bid_winner]
                        buy_property(bid_winner, board_position, bank, message_log, price = highest_bid)# makes who wins the bid own the property
                    awaiting_property_decision = False
                    can_build = True
                    if not extra_turn:
                        current_player_index = (current_player_index + 1) % num_interactive

                if buy_button.is_clicked(mouse_pos):
                    print("buy button clicked")
                    board_position = next((i for i in board if i["position"] == active_player.position), None)
                    buy_property(active_player, board_position, bank, message_log, price=None)
                    awaiting_property_decision = False
                    can_build = True
                    if not extra_turn:
                        current_player_index = (current_player_index + 1) % num_interactive

                if sell_assets_button.is_clicked(mouse_pos):
                    print("Sell assets button clicked")
                    sell_assets_popup = SellAssetsMenuPopUp(active_player, active_player.properties, board, 100, 100, 500, 500)
                    showing_sell_assets_popup = True

                if showing_sell_assets_popup and sell_assets_popup:
                    result = sell_assets_popup.button_clicked(event, message_log)
                    if result == "Sell":
                        showing_sell_assets_popup = False
                    elif result == "Cancel":
                        showing_sell_assets_popup = False
                    continue

                if build_button.is_clicked(mouse_pos):
                    if can_build:
                        print("Build button clicked")
                        eligible_props = [
                            p for p in active_player.properties
                            if p["group"] in active_player.colour_group_owned
                        ]
                        build_popup = Build_popup(active_player, bank, board, cost_data, eligible_props, 100, 100, 500, 400)
                        showing_build_popup = True
                    else:
                        display_msg(message_log, "Complete property purchasing/auctions before building")

                # exit build popup when cancel or confirm selected
                if showing_build_popup and build_popup:
                    result = build_popup.handle_event(event, message_log, player=active_player)
                    if result == "confirm":
                        showing_build_popup = False
                    elif result == "cancel":
                        showing_build_popup = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    properties_scroll_offset = min(properties_scroll_offset + 10, 0)
                elif event.key == pygame.K_DOWN:
                    properties_scroll_offset = max(properties_scroll_offset - 10, -10)

        # Draw board and game elements
        screen.blit(board_image, (0, 0))
        draw_dice(screen, current_number1, dice1_position)
        draw_dice(screen, current_number2, dice2_position)
        help_button.draw(screen)
        view_properties.draw(screen)
        sell_assets_button.draw(screen)
        build_button.draw(screen)

        # Draw tokens for interactive players
        for p in interactive_players:
            x, y = position_coordinates[p.position]
            screen.blit(p.token_image, (x - 20, y - 20))


        # Draw each player's money
        draw_player_money(screen, interactive_players, money_display_positions)

        # Draw the laps for each interactive player
        draw_player_laps(screen, interactive_players, laps_positions)

        draw_players_properties(screen, interactive_players, properties_display_positions, scroll_offset=properties_scroll_offset)

        # Draw the text display area under the "Roll" button
        text_surface = font.render(current_landing_piece, True, (0, 0, 0))  # Text color
        screen.blit(text_surface, (text_display_rect.x - 40, text_display_rect.y - 7))  # Adjust text position

        # Draw the rent message under the "Roll" button
        rent_surface = font.render(str(rent_text or ""), True, (0, 0, 0))
        screen.blit(rent_surface, (text_display_rect.x - 40, text_display_rect.y + 10))

        # Draw Sell Assets popup
        if showing_sell_assets_popup and sell_assets_popup:
            sell_assets_popup.draw(screen)

        # Draw the build houses/hotels popup
        if showing_build_popup and build_popup:
            build_popup.draw(screen)

        # Draw game messages log
        log_start_x = 510
        log_start_y = 50
        log_width = 250
        line_height = 20
        log_font = pygame.font.Font(None, 18)

        draw_y = log_start_y
        for msg in message_log:
            wrapped_lines = wrap_text(msg, log_font, log_width)
            for i, line in enumerate(wrapped_lines):
                prefix = "- " if i == 0 else "  "
                msg_surface = log_font.render(prefix + line, True, (0, 0, 0))
                screen.blit(msg_surface, (log_start_x, draw_y))
                draw_y += line_height

        # Render the current player text
        player_text_surface = font.render(current_player_text, True, (0, 0, 0))  # Text color
        screen.blit(player_text_surface, (text_display_rect.x - 40, text_display_rect.y - 20))  # Adjust text position

        #draw countdown clock
        if time_left is not None:
            minutes = time_left // 60
            seconds = time_left % 60
            time_font = pygame.font.Font(None, 24)
            timer_text = time_font.render(f"Time left: {minutes:02d}:{seconds:02d}", True, (255,0,0))
            screen.blit(timer_text, (190, 70))

        pygame.display.flip()

    pygame.quit()


def get_asset_value(player):
    """
    Helper function to get the asset value from the players' tuple.
    - player: A tuple where second item is asset value.
    Returns:
        int: asset value of player.
    """
    return player[1] #gets players second part of tuple for their asset value


def calculate_assets(player, board_data):
    """
    Calculates the total asset value of a player based on their total money(balance) and their owned properties.
    It also includes the values of house/hotels if not mortgaged and property base value.
    - player: The player whose assets are being calculated.
    - board_data: The game board containing property data.
    Returns:
        int: The total value of the player's assets.
    """
    total_value_of_assets = player.balance
    for prop in player.properties:
        property_data = next((tile for tile in board_data if tile["name"] == prop["name"]), 0)
        base_cost = property_data.get("cost",0)
        mortgaged = prop.get("mortgaged", False)

        if mortgaged:
            total_value_of_assets += base_cost // 2
        else:
            total_value_of_assets += base_cost

        house_hotel_cost = get_property_house_hotel_cost(board_data, property_data["name"])
        total_value_of_assets += prop.get("houses", 0) * house_hotel_cost
        total_value_of_assets += prop.get("hotels", 0) * house_hotel_cost
        print(f"Player {player} has total asset value of: {total_value_of_assets}")
    return total_value_of_assets


def get_property_house_hotel_cost(board_data, property_name):
    """
    For the property name given, this function will return the cost of a house/hotel depending on the tile's colour
    group.
    - board_data: List of all board spaces containing property information.
    - property_name: The name of the property to look up.
    Returns:
        int: The cost of the house/hotel depending on their colour group.
    """
    for space in board_data:
        if space.get("name") == property_name:
            group = space.get("group", "").lower()
            if group in ["brown", "blue"]:
                return 50
            elif group in ["purple", "orange"]:
                return 100
            elif group in ["red", "yellow"]:
                return 150
            elif group in ["green", "deep blue"]:
                return 200
    return 0

def endgame_popup(screen, winner_text):
    """
    Creates a popup at end game which tells the user who the winner is and options to "quit" or go to the menu "menu".
    Wraps long text if needed.
    - screen: The surface on which to draw the popup.
    - winner_text: The text describing the winning player and their asset value.

    Returns:
        String: "menu" if the menu button is clicked, "quit" if the quit button is clicked.
    """
    background = pygame.image.load("pngs/winnerPopup.png").convert_alpha()
    background = pygame.transform.scale(background, (550, 400))

    # Centre popup middle of screen
    popup_position = background.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    font = pygame.font.Font(None, 32)
    line_spacing = 10
    max_width = 460

    # wrap lines so end game message isn't flowing off the screen
    wrapped_lines = wrap_text(winner_text, font, max_width)

    # where to draw wrapped lines
    text_height = len(wrapped_lines) * (font.get_linesize() + line_spacing)
    start_y = popup_position.top + 150 - text_height // 2

    # Buttons for menu
    menu_button = pygame.Rect(204, 484, 140, 45)
    quit_button = pygame.Rect(436, 484, 140, 45)


    while True:
        screen.blit(background, popup_position)
        # Draw the lines
        for i, line in enumerate(wrapped_lines):
            text_surface = font.render(line.strip(), True, (0, 0, 0))
            text = text_surface.get_rect(center=(screen.get_width() // 2, start_y + i * (font.get_linesize() +
                                                                                         line_spacing)))
            screen.blit(text_surface, text)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.collidepoint(event.pos):
                    return "menu"
                elif quit_button.collidepoint(event.pos):
                    return "quit"
def declare_bankruptcy(player, board, bank, message_log):
    """
    Declares the bankruptcy of a player if they lose.
    - player: the player object
    - board: The board list
    - bank: The bank object
    - message_log: The log that displays user messages.
    """
    for prop in player.properties:
        prop_name = prop["name"]
        for tile in board:
            if tile["name"] == prop_name:
                tile["player"] = "Bank"
                tile["mortgaged"] = False
                tile["houses"] = 0
                tile["hotels"] = 0

    player.properties.clear()
    player.colour_group_owned.clear()

    display_msg(message_log, f"{player.token_color} is bankrupt and removed from the game")
    return player

if __name__ == "__main__":
    # Example testing with 2 interactive players
    # from player import Player
    # players = [
    #     Player((255, 0, 0)),  # Player 1
    #     Player((0, 255, 0))   # Player 2
    # ]
    # main_game_loop(players)
    main_game_loop([])