import pygame

class Player:
    def __init__(self, token_color, initial_position=1):
        self.token_color = token_color
        self.position = initial_position  # Start at position 1 (Go)
        self.balance = 1500  # Starting balance
        self.properties = []  # List of properties owned by the player
        self.laps_completed = 0  # Track how many times the player has circled the board

    def add_money(self, amount):
        """Increase the player's balance by the specified amount."""
        self.balance += amount
        print(f"Player received £{amount}. New balance: £{self.balance}")

    def deduct_money(self, amount):
        """Deduct the specified amount from the player's balance if sufficient funds exist."""
        if self.balance >= amount:
            self.balance -= amount
            print(f"Player paid £{amount}. New balance: £{self.balance}")
        else:
            print("Insufficient funds!")

    def move(self, steps):
        """Move the player a certain number of steps around the board."""
        new_position = self.position + steps
        if new_position > 40:  # Assuming the board has 40 positions
            new_position -= 40
            self.laps_completed += 1
            self.add_money(200)  # Player receives £200 for passing GO
        self.position = new_position
        print(f"Player moved to position {self.position}. Laps completed: {self.laps_completed}")