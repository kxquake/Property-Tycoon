
class Player:
    """
    This class represents a single player in the game. It tracks the player, position, balance, ownership,
    jail status, laps completed, and various other flags that are needed when playing the game.
    """
    def __init__(self, token_image, token_colour=None, initial_position=1):
        """
        Initialises a new player.
        - token_image: Image identifying players token, e.g. hatstand, cat, phone
        - token_colour: Colour of the token, used to identify player in some instances.
        - initial_position: Starting board position, default is 1 for GO space.
        """
        self.token_image = token_image
        self.position = initial_position  # Start at position 1 (Go)
        self.balance = 1500  # Starting balance
        self.token_colour = token_colour
        self.properties = []  # List of properties owned by the player
        self.laps_completed = 0  # Track how many times the player has circled the board
        self.colour_group_owned = []  # Track which colour group of properties owned
        self.can_build = False
        self.double_roll_count = 0
        self.in_jail = False
        self.jail_turns_remaining = 0
        self.get_out_of_jail_free = 0
        self.awaiting_choice = False   # If the player is required to make a choice
        self.pending_card_choice = None
        self.is_ai = False  # Is the player AI

    def add_money(self, amount, message_log):
        from main import display_msg
        """
        Increase the player's balance by the specified amount.
        - amount: amount to increase balance by
        - message_log: log to display messages within the game.
        """
        self.balance += amount
        display_msg(message_log, f"Player received £{amount}. New balance: £{self.balance}")

    def deduct_money(self, amount, message_log):
        from main import display_msg
        """
        Deduct the specified amount from the player's balance if sufficient funds exist.
        - amount: amount to deduct from player's balance
        - message_log: log to display messages within the game.
        """
        if self.balance >= amount:
            self.balance -= amount
            display_msg(message_log, f"Player paid £{amount}. New balance: £{self.balance}")
        else:
            display_msg(message_log, "Insufficient funds!")

    def move(self, steps, message_log):
        from main import display_msg
        """
        Move the player a certain number of steps around the board. If they pass GO they receive £200 and complete
        a lap.
        - steps: Number of positions to move.
        - message_log: Log to display messages in the game.
        """
        new_position = self.position + steps
        if new_position > 40:  # Assuming the board has 40 positions
            new_position -= 40
            self.laps_completed += 1
            self.add_money(200, message_log)  # Player receives £200 for passing GO
        self.position = new_position
        display_msg(message_log, f"Player moved to position {self.position}. Laps completed: {self.laps_completed}")




