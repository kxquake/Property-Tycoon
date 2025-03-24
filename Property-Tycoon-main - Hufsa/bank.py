class Bank:
    def __init__(self):
        self.balance = 50000  # The bank starts with £50,000

    def deposit(self, amount):
        """Increase the bank's balance by the specified amount."""
        self.balance += amount
        print(f"Bank received £{amount}. New bank balance: £{self.balance}")

    def withdraw(self, amount):
        """
        Withdraw an amount from the bank.
        Returns the withdrawn amount if sufficient funds exist; otherwise, returns 0.
        """
        if self.balance >= amount:
            self.balance -= amount
            print(f"Bank paid out £{amount}. New bank balance: £{self.balance}")
            return amount
        else:
            print("Bank has insufficient funds!")
            return 0

    def player_deposit(self, player, amount):
        """
        Process a transaction where the player pays money to the bank.
        Deducts the amount from the player and adds it to the bank.
        """
        if player.balance >= amount:
            player.deduct_money(amount)
            self.deposit(amount)
        else:
            print("Player has insufficient funds for this transaction.")

    def player_withdraw(self, player, amount):
        """
        Process a transaction where the bank gives money to the player.
        Withdraws the amount from the bank and adds it to the player's balance.
        """
        withdrawn = self.withdraw(amount)
        if withdrawn > 0:
            player.add_money(withdrawn)
