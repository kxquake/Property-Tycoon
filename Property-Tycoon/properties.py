import pygame
from board import load_board
from player import Player
from bank import Bank
import sys
import subprocess
from cards import CardDeck

# Load auction screen image and board data
auction = pygame.image.load("pngs/Auction.png").convert_alpha()
SCREEN_WIDTH, SCREEN_HEIGHT = 568, 571
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Scale for aligning button and board positions
SCALE_X = SCREEN_WIDTH / 600  # 0.9467
SCALE_Y = SCREEN_HEIGHT / 600  # 0.9517

# Load game data
board_data = load_board("board_data.json")
board = board_data["board"]
opportunity_knocks = CardDeck("opportunity_knocks.json")
pot_luck = CardDeck("pot_luck.json")


def buy_property(player, position, bank, message_log, price = None):
    """
    Handles purchasing of property by player.
    - player: The current player
    - position: The board space that the player is on. (dict)
    - bank: The bank object.
    - message_log: log to display game messages for users.
    - price: The price of the property which can be overridden by the auction.

    """
    from main import display_msg
    if player.laps_completed == 0:
        display_msg(message_log, "Must pass GO before purchasing")
        return
    elif position.get("can_be_bought") == False and position.get(
            "player") != "Bank":  # ensures the property can be brought
        display_msg(message_log, "Cannot be bought")
    elif position.get("player") != "Bank":
        display_msg(message_log, "Property is already owned")
        return
    elif position.get("player") == player.token_colour:
        display_msg(message_log, "you already own this property")
    elif player.balance <= position.get("cost"):
        display_msg(message_log, "you dont have enough money")
    else:
        cost = price if price is not None else position.get("cost",False)
        player.deduct_money(cost, message_log)# deduct cost from players balance
        bank.deposit(cost, message_log)  # add the cost back to the bank
        new_property = {
            "name": position["name"],
            "group" : position.get("group", ""),
            "houses" : 0,
            "hotels" : 0,
            "mortgaged": False
        }
        player.properties.append(new_property)  # adds the property to the players owned properties
        position["player"] = player.token_colour
        print(player.properties)
        excluded_groups = {"", "Station", "Utilities", "Go to jail"}
        group_to_properties = {}
        for tile in board:
            group = tile.get("group", "")
            if group not in excluded_groups:
                group_to_properties.setdefault(group,[]).append(tile["name"]) #map group to their list of properties
        # Check which colour groups fully owned by player
        for group, properties_in_group in group_to_properties.items():
            player_prop_names = [p["name"] for p in player.properties]
            if all(name in player_prop_names for name in properties_in_group):
                if group not in player.colour_group_owned:
                    player.colour_group_owned.append(group)
        display_msg(message_log, f"color group owned:{player.colour_group_owned}")

def remove_property(player, property_name):
    """
    Removes a property from the player and updates ownerships as well as colour groups
    - player: Player from the property is removed.
    - property_name: Name of the property to remove.
    """
    player.properties = [prop for prop in player.properties if prop["name"] != property_name]

    #finds position on board
    position = next((space for space in board if space.get("name") == property_name), None)
    position["player"] = "Bank"
    position["can_be_bought"] = True

    excluded_groups = {"", "Station", "Utilities", "Go to jail"}
    group_to_properties = {}

    for tile in board:
        group = tile.get("group", "")
        if group not in excluded_groups:
            group_to_properties.setdefault(group, []).append(tile["name"])  # map group to their list of properties

    player_property_names = [p["name"] for p in player.properties]
    player.colour_group_owned = []

    # Check which colour groups fully owned by player
    for group, properties_in_group in group_to_properties.items():
        if all(name in player_property_names for name in properties_in_group):
            player.colour_group_owned.append(group)

    print(f"{property_name} removed from {player.token_colour}'s ownership.")
    print(f"Updated colour groups owned: {player.colour_group_owned}")


def auction_property():
    """ Launches auction system"""
    print("Opening auction screen")


def rent_payment(player, position, bank, full_players, message_log, dice_total=None):
    """
    Handles rent payments that a player needs to make.
    - player: player who landed on the space.
    - position: players position on the board space
    - bank: The bank object.
    - full_players: List of all the players.
    - message_log: Log which holds user messages for display.
    - dice_total (optional): need for utility rent calculation.
    """
    # If property is available to buy
    if position.get("can_be_bought") and position.get("player") == "Bank":
        if player.laps_completed == 0:
            return "Must pass Go before purchasing"
        return "Property is available to buy"

    if not position.get("can_be_bought"):  # ensures the property can be brought
        action = position.get("action", "")
        if action:
            if "Income Tax" in position["name"]:
                bank.player_deposit(player, 200, message_log)
                return "£200 paid to bank as Income Tax"
            elif "Super Tax" in position["name"]:
                bank.player_deposit(player, 100, message_log)
                return "£100 paid to bank as Super Tax"
            elif action == "Take card":
                if position.get("name") == "Opportunity Knocks":
                    card = opportunity_knocks.draw_card()
                    return opportunity_knocks.card_action(player, bank, card, full_players, board, message_log)
                elif position.get("name") == "Pot Luck":
                    card = pot_luck.draw_card()
                    return pot_luck.card_action(player, bank, card, full_players, board, message_log)
        else:
            return "Cannot be bought"

    # Check if player landed on their own property
    if position.get("player") == player.token_colour:
        return "You landed on your own property"

    # Check if property owned by another player
    if position.get("player") != player.token_colour: #and position.get("player") != "Bank":

        # Identify owner of property
        owner_player = next((p for p in full_players if p and p.token_colour == position.get("player")), None)
        if not owner_player:
            return ""

        if owner_player.in_jail:
            return f"Owner is currently in jail and cannot collect rent."

        if position.get("mortgaged", False):
            return f"{position.get('name')} is mortgaged - no rent to be paid."

        rent_data = position.get("rent", {})
        group = position.get("group")
        rent_type = "normal rent"
        stations_owned = []
        rent_to_pay = 0

        # Calculate rent if property is a station
        if group == "Station":
            for tile in board:
                owner_prop_names = [p["name"] for p in owner_player.properties]
                if tile.get("group") == "Station" and tile.get("name") in owner_prop_names:
                    stations_owned.append(tile.get("name"))
            rent_table = {
                1: 25,
                2: 50,
                3: 100,
                4: 200
            }

            rent_to_pay = rent_table.get(len(stations_owned))
            rent_type = f"{len(stations_owned)} stations owned"

        # Calculate rent if one or both utilities owned
        if group == "Utilities":
            utilities = [tile["name"] for tile in board if tile.get("group") == "Utilities"]
            owner_util_names = [p["name"] for p in owner_player.properties if p["name"] in utilities]
            num_util_owned = len(owner_util_names)

            if dice_total is None:
                rent_to_pay = 0
            elif num_util_owned == 1:
                rent_to_pay = dice_total * 4
                rent_type = "owns 1 utility"
            elif num_util_owned == 2:
                rent_to_pay = dice_total * 10
                rent_type = "owns both utilities"
            else:
                rent_to_pay = 0

        # Calculate rent for normal property
        elif isinstance(rent_data, dict):
            # check if this property has been developed
            owner_prop = next((p for p in owner_player.properties if p["name"] == position["name"]), None)
            if owner_prop:
                houses = owner_prop.get("houses", 0)
                hotels = owner_prop.get("hotels", 0)
            else:
                houses = hotels = 0

            if hotels > 0:
                rent_to_pay = rent_data.get("1_hotel", 0)
                rent_type = "1 hotel"
            elif houses > 0:
                key = f"{houses}_house" if houses == 1 else f"{houses}_houses"
                rent_to_pay = rent_data.get(key, 0)
                rent_type = f"{houses} house{"s" if houses > 1 else ""}"
            # Double rent if owner owns all properties in colour group
            elif position.get("group") in owner_player.colour_group_owned:
                rent_to_pay = rent_data.get("unimproved", 0) * 2
                rent_type = "All colour group owned"
            else:
                rent_to_pay = rent_data.get("unimproved", 0)
        # Execute rent payment
        if player.balance >= rent_to_pay:
            player.deduct_money(rent_to_pay, message_log)
            owner_player.add_money(rent_to_pay, message_log)
            owner_index = full_players.index(owner_player) + 1
            return f"£{rent_to_pay} paid to player {owner_index} as {rent_type}"
        else:
            return "Not enough funds for rent, sell assets", rent_to_pay

class Button:
    """
    For on-screen button
    """
    def __init__(self, x, y, width, height, text="", font=None, colour=(200, 200, 200), text_colour=(0,0,0)):
        """ Initialisation of button"""
        # Scale positions and sizes to match the resized images
        self.rect = pygame.Rect(
            int(x * SCALE_X),
            int(y * SCALE_Y),
            int(width * SCALE_X),
            int(height * SCALE_Y)
        )
        self.text = text
        self.font = font or pygame.font.Font(None, 24)
        self.colour = colour
        self.text_colour = text_colour

    def is_clicked(self, mouse_pos):
        """Checks if button has been clicked, returns true if it has been"""
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Draws button on screen with border and text"""
        pygame.draw.rect(screen, self.colour, self.rect)
        pygame.draw.rect(screen, (0,0,0), self.rect, 2)
        if self.text:
            text_surf = self.font.render(self.text, True, self.text_colour)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)
