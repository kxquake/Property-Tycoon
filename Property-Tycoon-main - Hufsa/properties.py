import pygame
from board import load_board
from player import Player
from bank import Bank
import sys
import subprocess

auction = pygame.image.load("pngs/Auction.png").convert_alpha()
SCREEN_WIDTH, SCREEN_HEIGHT = 568, 571
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
SCALE_X = SCREEN_WIDTH / 600  # 0.9467
SCALE_Y = SCREEN_HEIGHT / 600  # 0.9517
board_data = load_board("board_data.json")
board = board_data["board"]


def buy_property(player,position,bank):
    if position.get("can_be_bought") == False and position.get("player") != "Bank": #ensures the property can be brought
        print (position.get("name") + " cannot be bought")
    elif position.get("player") == player.token_color:
        print ("you already own this property")
    else:
        cost = position.get("cost",False) 
        player.deduct_money(cost) #deduct cost from players balance
        bank.deposit(cost) # add the cost back to the bank
        player.properties.append(position.get("name")) # adds the property to the players owned properties
        position["player"] = player.token_color
        print(player.properties)
        
def auction_property():
    print("Opening auction screen")

def rent_payment(player, position, bank, full_players):

    if position.get("player") == "Bank" and position.get("can_be_bought") == True:
        return "This property is available to buy"

    elif position.get("can_be_bought") == False: #ensures the property can be brought
        return position.get("name") + " cannot be bought"

    # Check if property owned by another player
    elif position.get("player") != player.token_color:

        # Identify owner of property
        owner_player = None
        for p in full_players:  # type: Player
            if p and p.token_color == position.get("player"):
                owner_player = p
                break

        rent_data = position.get("rent", {})
        group = position.get("group")
        rent_type = "normal rent"
        group_tiles = []
        stations_owned = []

        rent_to_pay = 0

        # Calculate rent if property is a station
        if group == "Station":
            for tile in board:
                if tile.get("group") == "Station" and tile.get("name") in owner_player.properties:
                    stations_owned.append(tile.get("name"))
            rent_table = {
                1: 25,
                2: 50,
                3: 100,
                4: 200
            }

            rent_to_pay = rent_table.get(len(stations_owned))
            rent_type = f"{len(stations_owned)} owned"

        # Calculate rent for normal property
        elif isinstance(rent_data, dict):

            for tile in board:
                if tile.get("group") == group:
                    group_tiles.append(tile.get("name"))

            # Double rent if owner owns all properties in colour group
            if all(title_name in owner_player.properties for title_name in group_tiles):
                rent_to_pay = rent_data.get("unimproved", 0) * 2
                rent_type = "All colour group owned"

            else:
                rent_to_pay = rent_data.get("unimproved", 0)
        # Execute rent payment
        player.deduct_money(rent_to_pay)
        owner_player.add_money(rent_to_pay)
        player_to_pay = position.get("player")
        return f"£{rent_to_pay} paid to player {player_to_pay} as {rent_type}"

    # Check if player landed on their own property
    elif position.get("player") == player.token_color:
        return "You landed on your own property"
    # Handle any other action
    else:
        action = position.get("action","")
        if action:
            return f"Action: {action}"
        return ""
        
class Button:
    def __init__(self, x, y, width, height):
        # Scale positions and sizes to match the resized images
        self.rect = pygame.Rect(
            int(x * SCALE_X),
            int(y * SCALE_Y),
            int(width * SCALE_X),
            int(height * SCALE_Y)
        )
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)        