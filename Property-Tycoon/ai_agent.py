import random
from properties import remove_property
from build_house_hotel_utils import can_build_house, can_build_hotel, get_cost_cat_for_group, can_sell_house

class AIAgent:
    """
    AI agent that simulates decision-making. It can buy, auction, build, sell, mortgage, and manage assets
    just like a real player would.
    """
    def __init__(self, player):
        """Initialises the player"""
        self.player = player

    def ai_buy_property(self, property):
        """
        Determines if an AI should buy a property when landing on it. It is a random choice.
        - property: The property the AI landed on.
        Returns:
            True if AI should buy, False otherwise.
        """
        cost = property.get("cost", 0)
        decision = self.player.laps_completed > 0 and self.player.balance >= cost and random.choice([True, False])
        return decision

    def ai_auction(self, property, max_bid, current_bid):
        """
        Determines AI's bid in auction.
        - property: The property being auctioned
        - max_bid: Maximum amount allowed for bidding.
        - current_bid: The current highest bid made.
        Returns:
            The AI's bid amount of 0 to pass.
        """
        cost = property.get("cost", 0)
        if self.player.laps_completed == 0 or self.player.balance < cost:
            return 0
        max_bid = min(self.player.balance, cost * 2)
        if current_bid >= max_bid:
            return 0
        return random.randint(current_bid + 1, max_bid)

    def can_cover_rent_with_assets(self, rent_amount, board, cost_data):
        """
        Evaluates if the AI can cover rent by selling/mortgaging assets.
        - rent_amount: The amount of rent due.
        - board: The board data list.
        - cost_data: The cost data for houses and hotels.
        Returns:
            True if AI can cover rent with current balance and assets.
        """
        total_value = 0
        for prop in self.player.properties:
            prop_name = prop["name"]
            prop_group = prop["group"]

            # Get cost category
            cost_cat = get_cost_cat_for_group(prop_group)
            if cost_cat and cost_cat in cost_data:
                house_cost = cost_data[cost_cat]["house"]
            else:
                house_cost = 0

            # Add value from houses
            total_value += prop.get("houses", 0) * (house_cost // 2)

            # Add value from hotel
            total_value += prop.get("hotels", 0) * (4 * (house_cost // 2))

            # Add mortgage value if not already mortgaged
            if not prop.get("mortgaged", False):
                board_tile = next(tile for tile in board if tile["name"] == prop_name)
                base_cost = board_tile.get("cost", 0)
                total_value += base_cost // 2

        return self.player.balance + total_value >= rent_amount

    def sell_houses_hotels(self, board, bank, message_log):
        """
        Sells AI's houses when cash is needed.
        - board: The board data list.
        - bank: The bank object.
        - message_log: A list to log messages.
        """
        for prop in self.player.properties:
            prop_name = prop["name"]
            prop_group = prop["group"]
            cost_cat = get_cost_cat_for_group(prop_group)
            group_props = [p for p in self.player.properties if p["group"] == prop_group]

            if not cost_cat:
                continue
            house_cost = bank.get_property_house_hotel_cost(prop_name)

            while prop.get("hotels", 0) > 0:
                prop["hotels"] -= 1
                prop["houses"] += 4
                self.player.add_money(house_cost, message_log)
                message_log.append(f"AI sold hotel on {prop_name} for £{house_cost}")


            while prop.get("houses", 0) > 0 and can_sell_house(prop_name, group_props, self.player):
                prop["houses"] -= 1
                self.player.add_money(house_cost, message_log)
                message_log.append(f"AI sold house on {prop_name} for £{house_cost}")

    def mortgage_properties(self, board, bank, message_log):
        """
        Mortgages properties to raise funds.
        - board: The board data.
        - bank: The bank object.
        - message_log: Log to display messages to users.
        """
        for prop in self.player.properties:
            if prop.get("mortgaged"):
                continue
            if prop.get("houses", 0) > 0 or prop.get("hotels", 0) > 0:
                continue

            base_cost = next(tile for tile in board if tile["name"] == prop["name"]).get("cost", 0)
            mortgage_value = base_cost // 2
            prop["mortgaged"] = True
            self.player.add_money(mortgage_value, message_log)
            message_log.append(f"AI mortgaged {prop['name']} for £{mortgage_value}")

    def sell_properties(self, board, bank, message_log):
        """
        Fully sells off unmortgaged and undeveloped properties.
        - board: The board list.
        - bank: The bank object.
        - message_log: A log to display messages to users.

        """
        for prop in self.player.properties[:]:
            if prop.get("houses", 0) > 0 or prop.get("hotels", 0) > 0:
                continue

            base_cost = next(tile for tile in board if tile["name"] == prop["name"]).get("cost", 0)
            value = base_cost // 2 if prop.get("mortgaged") else base_cost
            self.player.add_money(value, message_log)
            remove_property(self.player, prop["name"])

            for tile in board:
                if tile["name"] == prop["name"]:
                    tile["player"] = "Bank"
                    break

            message_log.append(f"AI sold {prop['name']} for £{value}")

    def ai_sell_assets_or_mortgage(self, amount_needed, board, bank, message_log):
        """
        Attempts to raise money by selling or mortgaging assets.
        - amount_needed: The required money to be raised.
        - board: Board spaces list.
        - bank: The bank object.
        - message_log: Log of messages to be displayed to user.
        """
        self.sell_houses_hotels(board, bank, message_log)
        if self.player.balance >= amount_needed:
            return

        self.mortgage_properties(board, bank, message_log)
        if self.player.balance >= amount_needed:
            return

        self.sell_properties(board, bank, message_log)

    def ai_build_houses_and_hotels(self, bank, board_data, cost_data, message_log):
        """
        Determines if AI should build houses and hotels.
        - bank: The bank object
        - board_data: The board spaces list
        - cost_data: The data which holds all the costs.
        - message_log: Log of messages to be displayed to the users.
        """
        player = self.player
        for group in player.colour_group_owned:
            group_props = [p for p in player.properties if p["group"] == group]
            if any(p.get("mortgaged", False) for p in group_props):
                continue

            category = get_cost_cat_for_group(group)
            if not category or category not in cost_data:
                continue

            house_cost = cost_data[category]["house"]

            group_props.sort(key=lambda p: (p.get("hotels", 0), p.get("houses", 0)))

            build_count = 0

            for prop in group_props:
                name = prop["name"]
                if player.balance < house_cost:
                    return

                if random.choice([True, False]) and can_build_hotel(name, group_props):
                    prop["houses"] = 0
                    prop["hotels"] = 1
                    bank.player_deposit(player, house_cost, message_log)
                    message_log.append(f"AI built a hotel on {name}")
                elif can_build_house(name, group_props):
                    prop["houses"] += 1
                    bank.player_deposit(player, house_cost, message_log)
                    message_log.append(f"AI build a house on {name}")

                build_count += 1

                if build_count >= 4 or random.random() < 0.4:
                    return

    def pay_jail_fine(self):
        """
        AI's decision whether to pay jail fine, 60 percent chance if AI can afford it.
        Returns:
            True if AI chooses to pay fine, else False.
        """
        #ai has a 60 percent chance of paying the fine
        if self.player.balance < 50:
            return False
        return random.random() < 0.6
