import pygame

class Player:
    def __init__(self, token_color, initial_position=1):
        self.token_color = token_color
        self.position = initial_position  # Start at position 1 (Go)
        self.balance = 1500  # Starting balance
        self.properties = []  # List of properties owned by the player