import pygame
from board import load_board, load_house_and_hotel_costs

# Load board and cost data
board_data = load_board("board_data.json")["board"]
cost_data = load_house_and_hotel_costs("board_data.json")


class Build_popup:
    """
    Class tro handle the build popup which allows players to build houses and hotels based on the rules:
    maximum 4 houses with no difference of more than 1 house between properties. Hotel can only be built if property
    has 4 houses, with a maximum of only 1 hotel allowed to be built per property.
    """
    def __init__(self, player, bank, board_data, cost_data, properties, x, y, width, height):
        """
        Initialises the build popup UI
        - player: The current player object.
        - bank: The bank object handling deposits/withdrawals.
        - board_data: List of board tiles.
        - cost_data: Dictionary containing house/hotel costs by group.
        - properties: List of player-owned property dicts.
        - x, y: Top-left corner position of the popup.
        - width, height: Dimensions of the popup.
        """
        self.player = player
        self.bank = bank
        self.properties = properties
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Load backgorund image
        self.bg = pygame.image.load("pngs/Houses_hotels.png").convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (width, height))
        self.font = pygame.font.Font(None, 20)
        self.scroll_index = 0
        self.visible_count = 4

        # Scroll button positions
        self.scroll_up_button = pygame.Rect(self.x + self.width - 40, self.y + 60, 30, 30)
        self.scroll_down_button = pygame.Rect(self.x + self.width - 40, self.y + 100, 30, 30)

        self.board_reference = {p["name"]: p for p in board_data}
        self.cost_data = cost_data

        # Positions of confirm and cancel buttons
        self.confirm_button = pygame.Rect(x + 82, y + height - 70, 146, 40)
        self.cancel_button = pygame.Rect(x + 270, y + height - 70, 146, 40)

        # Buttons for user to interacti with
        self.house_plus_buttons = {}
        self.house_minus_buttons = {}
        self.hotel_plus_buttons = {}
        self.hotel_minus_buttons = {}
        for i, p in enumerate(properties):
            y_offset = self.y + 120 + i * 60
            self.house_plus_buttons[p["name"]] = pygame.Rect(self.x + 190, y_offset, 30, 30)
            self.house_minus_buttons[p["name"]] = pygame.Rect(self.x + 230, y_offset, 30, 30)

            self.hotel_plus_buttons[p["name"]] = pygame.Rect(self.x + 290, y_offset, 30, 30)
            self.hotel_minus_buttons[p["name"]] = pygame.Rect(self.x + 330, y_offset, 30, 30)

    def draw(self, screen):
        """
        Draws the build popup to screen
        - screen: The surface to draw on.
        """
        screen.blit(self.bg, (self.x, self.y))

        visible_props = self.properties[self.scroll_index:self.scroll_index + self.visible_count]
        y_offset = self.y + 100

        for p in visible_props:
            name = p["name"]
            group = p["group"]

            house_count = p.get("houses", 0)
            hotel_count = p.get("hotels", 0)

            screen.blit(self.font.render(name, True, (0,0,0)), (self.x + 30, y_offset))
            # Display house and hotel count

            screen.blit(self.font.render(f"{house_count} house", True, (0,0,0)), (self.x + 200, y_offset))
            screen.blit(self.font.render(f"{hotel_count} hotel", True, (0,0,0)), (self.x + 300, y_offset))

            house_plus = pygame.Rect(self.x + 190, y_offset, 30, 30)
            house_minus = pygame.Rect(self.x + 230, y_offset, 30, 30)
            hotel_plus = pygame.Rect(self.x + 290, y_offset, 30, 30)
            hotel_minus = pygame.Rect(self.x + 330, y_offset, 30, 30)

            # Buttons for adding/removing houses
            screen.blit(self.font.render("+", True, (0,0,0)), (house_plus.x + 7, house_plus.y + 15))
            screen.blit(self.font.render("-", True, (0,0,0)), (house_minus.x + 7, house_minus.y + 15))

            # Buttons for adding/removing hotels
            screen.blit(self.font.render("+", True, (0, 0, 0)),
                        (hotel_plus.x + 7, hotel_plus.y + 15))
            screen.blit(self.font.render("-", True, (0, 0, 0)),
                        (hotel_minus.x + 7, hotel_minus.y + 15))

            y_offset += 60

        # Scroll up/down buttons
        pygame.draw.rect(screen, (200, 200, 200), self.scroll_up_button)
        pygame.draw.rect(screen, (200, 200, 200), self.scroll_down_button)

        up_arrow = self.font.render("↑", True, (0, 0, 0))
        down_arrow = self.font.render("↓", True, (0, 0, 0))
        screen.blit(up_arrow, up_arrow.get_rect(center=self.scroll_up_button.center))
        screen.blit(down_arrow, down_arrow.get_rect(center=self.scroll_down_button.center))

    def get_cat_cost_for_group(self, group_name):
        """
        Returns the cost of the colour category of the properties.
        - group_name: The colour group of the property.
        Returns:
            A category string used for cost data.
        """
        category_map = {
            "brown_blue": ["Brown", "Blue"],
            "purple_orange": ["Purple", "Orange"],
            "red_yellow": ["Red", "Yellow"],
            "green_deep_blue": ["Green", "Deep blue"]
        }
        for cat, groups in category_map.items():
            if group_name in groups:
                return cat
        return None

    def can_build_house(self, property_name):
        """
        Checks if house can be built on the given property to maintain the 1 build difference allowing even
        distribution.
        - property_name: The name of the property to be built on.

        Returns:
            True if allowed to build, false otherwise.
        """
        prop = next(p for p in self.properties if p["name"] == property_name)
        group = prop["group"]
        group_prop = [p for p in self.properties if p["group"] == group]
        values = [(p.get("houses", 0) + 1 if p["name"] == property_name else p.get("houses", 0)) for p in group_prop]
        return max(values) - min(values) <= 1

    def can_build_hotel(self, property_name):
        """
        Checks if hotel can be built on the given property (4 houses needed on all properties)
        - property_name: The name of the property to be built on.
        Returns:
            True if allowed to build hotel, otherwise False.
        """
        prop = next(p for p in self.properties if p["name"] == property_name)
        group = prop["group"]
        group_props = [p for p in self.properties if p["group"] == group]
        if prop.get("houses", 0) != 4 or prop.get("hotels", 0) != 0:
            return False
        for p in group_props:
            if p["name"] != property_name:
                if p.get("houses", 0) < 4 and p.get("hotels", 0) == 0:
                    return False
        return True

    def can_remove_house(self, property_name):
        """
        Validates house removal rules to allow even distribution between properties of the colour group.
        - property_name: The name of the property to remove house.
        Returns:
            True if allowed to remove a house, otherwise False.
        """
        prop = next(p for p in self.properties if p["name"] == property_name)
        group = prop["group"]
        house_counts = []
        for p in self.properties:
            if p["group"] == group:
                count = 5 if p.get("hotels", 0) > 0 else p.get("houses", 0)
                if p["name"] == property_name:
                    count -= 1
                house_counts.append(count)
        return max(house_counts) - min(house_counts) <= 1

    def handle_event(self, event,message_log, player):
        """
        Handles the user interactions like the button clicks in the popup.
        - event: Pygame event object.
        - message_log: Log to display messages to players.
        - player: The current player on the build menu.
        Returns:
            "confirm", "cancel" or None depending on interaction.
        """
        visible_props = self.properties[self.scroll_index:self.scroll_index + self.visible_count]

        if self.scroll_up_button.collidepoint(event.pos):
            if self.scroll_index > 0:
                self.scroll_index -= 1
            return None

        if self.scroll_down_button.collidepoint(event.pos):
            if self.scroll_index + self.visible_count < len(self.properties):
                self.scroll_index += 1
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.confirm_button.collidepoint(event.pos):
                print("Build confirmed")
                return "confirm"
            elif self.cancel_button.collidepoint(event.pos):
                print("Build cancelled")
                return "cancel"

            y_offset = self.y + 100

            for p in visible_props:
                name = p["name"]
                group = p["group"]
                cat = self.get_cat_cost_for_group(group)
                if not cat:
                    continue
                house_cost = self.cost_data[cat]["house"]

                house_plus = pygame.Rect(self.x + 190, y_offset, 30, 30)
                house_minus = pygame.Rect(self.x + 230, y_offset, 30, 30)
                hotel_plus = pygame.Rect(self.x + 290, y_offset, 30, 30)
                hotel_minus = pygame.Rect(self.x + 330, y_offset, 30, 30)

                # Build houses
                if house_plus.collidepoint(event.pos):
                    if p.get("houses", 0) < 4 and p.get("hotels", 0) == 0:
                        if self.can_build_house(name) and self.player.balance >= house_cost:
                                p["houses"] = p.get("houses", 0) + 1
                                self.bank.player_deposit(player, house_cost, message_log)
                                print(f"built house on {name}, now: {self.player.properties}")

                # Remove houses
                elif house_minus.collidepoint(event.pos):
                    if p.get("houses", 0) > 0 and self.can_remove_house(name):
                        p["houses"] -= 1
                        self.bank.player_withdraw(player, house_cost, message_log)
                        print(f"house removed from {name}")

                # Build hotels
                elif hotel_plus.collidepoint(event.pos):
                    if p.get("hotels", 0) == 0 and self.can_build_hotel(name) and self.player.balance >= house_cost:
                        p["houses"] = 0
                        p["hotels"] = 1
                        self.bank.player_deposit(player, house_cost, message_log)
                        print(f"hotel built on {name}. now: {p}")

                #Remove hotels
                elif hotel_minus.collidepoint(event.pos):
                    if p.get("hotels", 0) > 0:
                        p["hotels"] -= 1
                        p["houses"] = 4
                        self.bank.player_withdraw(player, house_cost, message_log)
                        print(f"hotel removed from {name}")

                y_offset += 60
        return None
