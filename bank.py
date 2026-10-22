
class Bank:
    """
    Represents the game's bank, handles most money-related transactions between players and bank and also
    takes care of the free parking pool.
    """
    def __init__(self):
        """
        Initializes the bank with default balance of 50000 and empty free parking pool.
        """
        self.balance = 50000  # The bank starts with £50,000
        self.free_parking_pool = 0

    def deposit(self, amount, message_log):
        """
        Increase banks balance by specified amount
        - amount: amount of money to be deposited into the bank.
        - message_log: Log for game messages to alert players.
        """
        from main import display_msg
        """Increase the bank's balance by the specified amount."""
        self.balance += amount
        display_msg(message_log, f"Bank received £{amount}. New bank balance: £{self.balance}")

    def withdraw(self, amount, message_log):
        from main import display_msg
        """
        Withdraw an amount from the bank.
        - amount: amount of money to withdraw from the bank.
        - message_log: Log for game messages to alert players.
        Returns the withdrawn amount if sufficient funds exist; otherwise, returns 0.
        """
        if self.balance >= amount:
            self.balance -= amount
            print(f"Bank paid out £{amount}. New bank balance: £{self.balance}")
            return amount
        else:
            display_msg(message_log, "Bank has insufficient funds!")
            return 0

    def player_deposit(self, player, amount, message_log):
        from main import display_msg
        """
        Process a transaction where the player pays money to the bank.
        Deducts the amount from the player and adds it to the bank.
        - player: The player who is paying money to the bank.
        - amount: The amount of money being given to the bank.
        - message_log: Log for game messages to alert players.
        """
        if player.balance >= amount:
            player.deduct_money(amount, message_log)
            self.deposit(amount, message_log)
            display_msg(message_log, f"{amount} paid to bank")
        else:
            display_msg(message_log,"Player has insufficient funds for this transaction.")

    def player_withdraw(self, player, amount, message_log):
        from main import display_msg
        """
        Process a transaction where the bank gives money to the player.
        - player: The player gaining money from the bank.
        - amount: The amount of money being given to player.
        - message_log: Log for game messages to alert players.
        Withdraws the amount from the bank and adds it to the player's balance.
        """
        withdrawn = self.withdraw(amount, message_log)
        if withdrawn > 0:
            player.add_money(withdrawn, message_log)
            print(f"{withdrawn} withdrawn from bank")
            #display_msg(message_log, f"{withdrawn} withdrawn from bank")

    def collect_free_parking(self, player, message_log):
        """
        To be called when a player lands on free parking space so player can gain all the current funds within the
        free parking pool.
        - player: The player who landed on free parking space.
        - message_log: log for game messages to alert players.
        Returns: The amount of funds that were in the free parking pool before it got set to 0 again.
        """
        player.add_money(self.free_parking_pool, message_log)
        collected = self.free_parking_pool
        self.free_parking_pool = 0
        return collected
