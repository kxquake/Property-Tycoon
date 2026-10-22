import json
import random
from board import load_board

# Get relevant data for file
board = load_board("board_data.json")["board"]
opportunity_knocks = "opportunity_knocks.json"
pot_luck = "pot_luck.json"


class CardDeck:
    """
    Represents the deck of game cards such as opportunity knocks or pot luck. Handles drawing and executing the actions
    specified on the cards.
    """
    def __init__(self, file_path):
        """
        Load the card deck from a JSON file and shuffle them for randomisation every game.
        - file_path: Path to the JSON file containing all the card data.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            self.cards = json.load(f)
        random.shuffle(self.cards)

    def draw_card(self):
        """
        Draws the card from the top of the 'deck' and places it at the bottom.
        Returns:
            The card drawn from the deck.
        """
        if not self.cards:
            print("No cards left in deck!")
            return None
        card = self.cards.pop(0)
        self.cards.append(card)  # Put it at the bottom
        return card

    def card_action(self, player, bank, card, full_players, board, message_log):
        """
        Executes the action defined by the card.
        - player: The player who drew the card.
        - bank: The game bank object.
        - card: (dict) of the card that was drawn.
        - full_players: list of all the players in the game.
        - board: The game board.
        - message_log: The log to display game messages.

        Returns:
            (optional) Tuple for movement cards in the format (result, location name).
        """
        from main import display_msg
        from ai_agent import AIAgent

        action = card.get("action", {})
        text = card.get("text", "")

        if action == "add_money":

            amount = card.get("amount")
            bank.player_withdraw(player, amount, message_log)
            display_msg(message_log, f"Card: {text}, {amount} added to your balance")

        elif action == "pay":
            amount = card.get("amount")
            player.deduct_money(amount, message_log)
            bank.free_parking_pool += amount
            display_msg(message_log, f"Card: {text}, You paid {amount}")

        elif action == "collect_from_each_player":
            total = 0
            amount = card.get("amount")
            for p in full_players:
                if p is not None and p != player and p.balance >= amount:
                    p.deduct_money(amount, message_log)
                    total += amount
            player.add_money(total, message_log)
            if total > 0:
                display_msg(message_log, f"Card: {text}, You received {total} from each player")
            else:
                display_msg(message_log, f"Card: {text}, No players could pay you")
        elif action == "repair_fee":
            house_fee = card.get("house")
            hotel_fee = card.get("hotel")
            no_houses = 0
            no_hotels = 0
            for p in player.properties:
                no_houses += p.get("houses", 0)
                no_hotels += p.get("hotels", 0)
            total_house_fee = no_houses * house_fee
            total_hotel_fee = no_hotels * hotel_fee
            total_fee = total_house_fee + total_hotel_fee
            bank.free_parking_pool += total_fee
            player.deduct_money(total_fee, message_log)
            display_msg(message_log, f"Card: {text}, {total_fee} paid for {no_houses} houses and {no_hotels} hotels paid")

        elif action == "move_back" or action == "move_to":
            from properties import rent_payment
            spaces = card.get("spaces")
            if action == "move_back":
                player.position -= spaces
                if player.position < 1:
                    player.position += 40
                display_msg(message_log, f"Card: {text}, Player moved back {spaces} spaces")
                new_position = board[player.position - 1]
                result = rent_payment(player, new_position, bank, full_players, message_log, dice_total=0)
                return result, new_position["name"]

            if action == "move_to":
                position = card.get("position")
                pass_go = card.get("pass_go", False)
                if pass_go and position < player.position:
                    player.add_money(200, message_log)
                    display_msg(message_log, "Passed Go, collected £200")
                player.position = position
                if player.position > 40:
                    player.position -= 40
                new_position = board[player.position - 1]
                display_msg(message_log, f"Card: {text}, Player moved to {new_position['name']}")
                result = rent_payment(player, new_position, bank, full_players, message_log, dice_total=0)
                print(result)
                return result, new_position["name"]

        elif action == "go_to_jail":
            player.position = 11  # Jail position
            player.in_jail = True
            player.jail_turns_remaining = 3
            player.double_roll_count = 0
            display_msg(message_log, f"Card: {text}, You have been sent to jail.")

            if player.balance >= 50:
                if player.is_ai and hasattr(player, 'ai_agent') and player.ai_agent is not None:
                    if player.ai_agent.pay_jail_fine():
                        jail_fee = 50
                        player.deduct_money(jail_fee, message_log)
                        bank.free_parking_pool += jail_fee
                        display_msg(message_log, "AI paid £50 to get out of jail.")
                        print("AI paid £50 fine")
                    else:
                        display_msg(message_log, "AI chose not to pay fine, remains in jail.")
                        print("AI did not pay fine")
                        player.in_jail = True
                        # Three turns as it immediately decrements when it accesses player.in_jail
                        player.jail_turns_remaining = 3
                        player.double_roll_count = 0
                else:
                    display_msg(message_log, "Pay £50 fee for release? Press Y for 'yes' N for 'no'.")
                    player.awaiting_choice = True
                    return "awaiting_choice"
            else:
                display_msg(message_log, "Player cannot afford to pay £50 fine.")
                print("Player cannot afford £50 fine.")
                player.in_jail = True
                # Three turns as it immediately decrements when it accesses player.in_jail
                player.jail_turns_remaining = 2
                player.double_roll_count = 0

        elif action == "get_out_of_jail_free":
            player.get_out_of_jail_free = True
            display_msg(message_log, "You received a 'Get out of Jail Free' card")

        elif action == "choice_fine_or_card":
            amount = card.get("amount")
            display_msg(message_log, f"Card: {text}, press [F] to pay {amount} fine or choose [O] to draw an "
                                     f"Opportunity knocks card:")
            player.awaiting_choice = True
            player.pending_card_choice = {
                "type": "fine_or_card",
                "amount": amount
            }
















