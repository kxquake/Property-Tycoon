from properties import remove_property
import pygame


class SellAssetsButton:
    """
    The button to show the Sell Assets popup menu.
    """
    def __init__(self, x, y, width, height, text = "Sell Assets", font = None, colour = (130, 224, 170),
                 text_colour = (0, 0, 0), border_colour = (82, 190, 128)):
        """
        Initialise the button with size, text and styling.
        - x: x coordinate of button
        - y: y coordinate of button
        - width: width of the button.
        - height: height of the button.
        - text: the button label.
        - font: Font used for the label.
        - colour: the inner fill colour.
        - text_colour: colour of button text.
        - border_colour: Outer border colour
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font or pygame.font.Font(None, 24)
        self.colour = colour
        self.text_colour = text_colour
        self.border_colour = border_colour


    def draw(self, screen):
        """
        Draw the button on the screen.
        - screen: The game screen to draw on.
        """
        pygame.draw.rect(screen, self.border_colour, self.rect, border_radius = 5)
        inner_rect = self.rect.inflate(-6, -6)
        pygame.draw.rect(screen, self.colour, inner_rect, border_radius=5)
        text_surf = self.font.render(self.text, True, self.text_colour)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, mouse_pos):
        """
        Check if the button has been clicked.
        - mouse_pos: The mouse position when it was clicked.
        Returns:
            Bool: True if the button was clicked, False otherwise.
        """
        return self.rect.collidepoint(mouse_pos)


class SellAssetsMenuPopUp:
    """
    The popup for the Sell Assets menu, this includes selling house/hotels, mortgaging/unmortgaging properties
    and selling properties back to the bank.
    """

    def __init__(self, player, properties, board_data, x, y, width, height):
        """
        Initialises the popup with property info and the layout.
        - player: The player interacting with the menu.
        - properties: List of the player own properties.
        - board_data: The full board information for costs.
        - x: The x position of the popup
        - y: y position of the popup
        - width: The width of the popup
        - height: The height of the popup
        """
        self.properties = properties
        self.board_data = board_data
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.player = player

        # load image
        self.bg = pygame.image.load(
            "pngs/SellAssetsImage.png").convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (width, height))
        self.font = pygame.font.Font(None, 20)

        self.sell_button = pygame.Rect(x + 283, y + 440, 122, 40)
        self.cancel_button = pygame.Rect(x + 109, y + 440, 122, 40)
        self.mortgage_buttons = []
        self.sell_property_buttons = []

        self.house_plus_buttons = {}
        self.house_minus_buttons = {}
        self.hotel_plus_buttons = {}
        self.hotel_minus_buttons = {}

        self.pending_transactions = {
            "mortgaged": set(),
            "sell_property": set(),
            "sell_houses": {},
            "sell_hotels": {}
        }


        for i, p in enumerate(properties):
            name = p["name"]
            dev = next((prop for prop in self.player.properties if prop["name"] == name), {"mortgaged": False})

            y_offset = self.y + 112 + i * 18
            self.house_plus_buttons[p["name"]] = pygame.Rect(self.x + 240, y_offset - 15, 16, 16)
            self.house_minus_buttons[p["name"]] = pygame.Rect(self.x + 295, y_offset - 15, 16, 16)

            self.hotel_plus_buttons[p["name"]] = pygame.Rect(self.x + 330, y_offset - 15, 16, 16)
            self.hotel_minus_buttons[p["name"]] = pygame.Rect(self.x + 390, y_offset - 15, 16, 16)

            mortgage_button = pygame.Rect(self.x + 181, y_offset - 13, 50, 10)
            self.mortgage_buttons.append((p, mortgage_button))
            sell_property_button = pygame.Rect(self.x + 147, y_offset - 13, 30, 10)
            self.sell_property_buttons.append((p, sell_property_button))

    def draw(self, screen):
        """
        Draws the popup to the screen with the interactive elements.
        - screen: The screen where the popup is drawn.
        """
        self.refresh_property_states()
        # Draw the popup background
        screen.blit(self.bg, (self.x, self.y))
        y_offset = 100 #where the properties displayed should start
        small_font = pygame.font.Font(None, 14)
        medium_font = pygame.font.Font(None, 16)
        large_font = pygame.font.Font(None, 25)

        #Grand total
        total = self.calculate_grand_total()
        total_text = large_font.render(f"£{total}", True, (0, 0, 0))
        screen.blit(total_text, (self.x + 370, self.y + 410))

        for i, prop in enumerate(self.properties):
            name = prop["name"]
            text_surface = medium_font.render(name, True, (0, 0, 0))
            screen.blit(text_surface, (self.x + 25, self.y + y_offset))
            #dev = self.player.property_development.get(name, {"mortgaged": False})
            dev = next((p for p in self.player.properties if p["name"] == name), {"mortgaged": False})

            # Mortgage button
            _, mortgage_button = self.mortgage_buttons[i]
            pygame.draw.rect(screen, (255, 255, 255), mortgage_button)

            is_mortgaged = dev.get("mortgaged", False)

            if is_mortgaged:
                label = "Unmortgage"
            else:
                label = "Mortgage"

            # mark if it's in pending state
            if name in self.pending_transactions["mortgaged"]:
                label = "Cancel"

            button_text = small_font.render(label, True, (0, 0, 0))
            text_rect = button_text.get_rect(center=mortgage_button.center)
            screen.blit(button_text, text_rect)

            # Sell property button
            _, sell_button = self.sell_property_buttons[i]
            pygame.draw.rect(screen, (255, 255, 255), sell_button)
            if name in self.pending_transactions["sell_property"]:
                button_text = small_font.render("Unsell", True, (0, 0, 0))
            else:
                button_text = small_font.render("Sell", True, (0, 0, 0))
            text_rect = button_text.get_rect(center=sell_button.center)
            screen.blit(button_text, text_rect)

            # House buttons
            #dev = self.player.property_development.get(name, {"houses": 0, "hotels": 0})
            dev = next((p for p in self.player.properties if p["name"] == name), {"houses": 0, "hotels": 0})
            base_house = dev.get("houses", 0)
            base_hotel = dev.get("hotels", 0)

            #allows the dynamic changing of the hotels and houses
            pending_house = self.pending_transactions["sell_houses"].get(name, 0)
            pending_hotel = self.pending_transactions["sell_hotels"].get(name, 0)
            converted_from_hotels = 4 * self.pending_transactions["sell_hotels"].get(name, 0)
            house_count = max(0, base_house + converted_from_hotels - pending_house)
            hotel_count = max(0, base_hotel - pending_hotel)

            plus = self.house_plus_buttons[name]
            minus = self.house_minus_buttons[name]
            pygame.draw.rect(screen, (255, 255, 255), plus)
            pygame.draw.rect(screen, (255, 255, 255), minus)
            screen.blit(self.font.render("+", True, (0, 0, 0)), (plus.x + 4, plus.y))
            screen.blit(self.font.render("-", True, (0, 0, 0)), (minus.x + 4, minus.y))
            center_x = (plus.right + minus.left) // 2
            screen.blit(self.font.render(str(house_count), True, (0, 0, 0)), (center_x - 5, plus.y))

            # Hotel buttons
            plus = self.hotel_plus_buttons[name]
            minus = self.hotel_minus_buttons[name]
            pygame.draw.rect(screen, (255, 255, 255), plus)
            pygame.draw.rect(screen, (255, 255, 255), minus)
            screen.blit(self.font.render("+", True, (0, 0, 0)), (plus.x + 4, plus.y))
            screen.blit(self.font.render("-", True, (0, 0, 0)), (minus.x + 4, minus.y))
            center_x = (plus.right + minus.left) // 2
            screen.blit(self.font.render(str(hotel_count), True, (0, 0, 0)), (center_x - 5, plus.y))
            y_offset += 15

    def refresh_property_states(self):
        """
        Updates the property state of the player.
        """
        for prop in self.properties:
            name = prop["name"]
            #dev = self.player.property_development.get(name, {})
            dev = next((p for p in self.player.properties if p["name"] == name), {})
            prop["houses"] = dev.get("houses", 0)
            prop["hotels"] = dev.get("hotels", 0)
            prop["mortgaged"] = dev.get("mortgaged", False)

    def get_property_house_hotel_cost(self, property_name):
        """
        Returns the cost to build/sell houses or hotels based on the colour group of property.
        """
        for space in self.board_data:
             if space.get("name") == property_name:
                group = space.get("group", "").lower()
                if group in ["brown", "blue"]:
                    return 50
                elif group in ["purple", "orange"]:
                    return 100
                elif group in ["red", "yellow"]:
                    return 150
                elif group in ["green", "deep blue"]:
                    return 200
        return 0

    def handle_property_clicks(self, mouse_pos):
        """
        Handles clickable interactions in the Sell Assets popup such as increment/decrement pending house/hotel sales,
        toggles the mortgaging and property sell/unsell actions.

        Method updates the pending_transactions dictionary.
        - mouse_pos: (x, y) position of the mouse click.
        """
        for prop in self.properties:
            name = prop["name"]
            group = prop["group"]
            group_props = [p for p in self.properties if p["group"] == group]

            if self.house_minus_buttons[name].collidepoint(mouse_pos):
                dev = next((p for p in self.player.properties if p["name"] == name), {})
                base_houses = dev.get("houses", 0)
                converted_houses = 4 * self.pending_transactions["sell_hotels"].get(name, 0)
                total_houses = base_houses + converted_houses
                pending = self.pending_transactions["sell_houses"].get(name, 0)
                if total_houses - pending > 0 and self.can_sell_house(name, group_props):
                    self.pending_transactions["sell_houses"][name] = pending + 1
                    print(f"Added 1 house to sell on {name}")
                else:
                    print(f"No more houses to sell on {name}")

            elif self.house_plus_buttons[name].collidepoint(mouse_pos):
                pending = self.pending_transactions["sell_houses"].get(name, 0)
                if pending > 0:
                    self.pending_transactions["sell_houses"][name] = pending - 1
                    print(f"Removed house to sell for property {name}")

            if self.hotel_minus_buttons[name].collidepoint(mouse_pos):
                current_hotels = next((p for p in self.player.properties if p["name"] == name), {}).get("hotels", 0)
                pending = self.pending_transactions["sell_hotels"].get(name, 0)
                if current_hotels - pending > 0:
                    self.pending_transactions["sell_hotels"][name] = pending + 1
                    print(f"Added hotel to sell for property {name}")
                else:
                    print(f"No more hotels to sell on {name}")

            elif self.hotel_plus_buttons[name].collidepoint(mouse_pos):
                pending = self.pending_transactions["sell_hotels"].get(name, 0)
                if pending > 0:
                    self.pending_transactions["sell_hotels"][name] = pending - 1
                    print(f"Removed hotel to sell for property {name}")

        for p, rect in self.mortgage_buttons:
            name = p["name"]
            #dev = self.player.property_development.get(name, {"mortgaged": False})
            dev = next((prop for prop in self.player.properties if prop["name"] == name), {"mortgaged": False})
            if rect.collidepoint(mouse_pos):
                if dev["mortgaged"] is True:
                    # Plan to unmortgage
                    if name not in self.pending_transactions["mortgaged"]:
                        self.pending_transactions["mortgaged"].add(name)
                        print(f"{name} set to be unmortgaged")
                    else:
                        self.pending_transactions["mortgaged"].remove(name)
                        print(f"{name} unmortgage cancelled")
                else:
                    # Plan to mortgage
                    if name not in self.pending_transactions["mortgaged"]:
                        self.pending_transactions["mortgaged"].add(name)
                        print(f"{name} set to be mortgaged")
                    else:
                        self.pending_transactions["mortgaged"].remove(name)
                        print(f"{name} mortgage cancelled")

        for p, rect in self.sell_property_buttons:
            name = p["name"]
            if rect.collidepoint(mouse_pos):
                if name not in self.pending_transactions["sell_property"]:
                    self.pending_transactions["sell_property"].add(name)
                    print(f"property {name} has been added to be sold")
                else:
                    self.pending_transactions["sell_property"].remove(name)
                    print(f"property {name} has been removed to be sold")

    def can_sell_house(self, name, group_props):

        house_counts = []

        for prop in group_props:
            dev = next((p for p in self.player.properties if p["name"] == prop["name"]), {})
            base_houses = dev.get("houses", 0)
            pending_houses = self.pending_transactions["sell_houses"].get(prop["name"], 0)
            pending_hotels = self.pending_transactions["sell_hotels"].get(prop["name"], 0)

            # Include converted houses from pending hotel sales
            future_count = base_houses + (4 * pending_hotels) - pending_houses

            if prop["name"] == name:
                future_count -= 1  # Simulate removing one house

            house_counts.append(future_count)

        return max(house_counts) - min(house_counts) <= 1

    def get_property_cost(self, property_name):
        """
        Gets the original cost of the property
        - property_name: the name of the property to look up.
        Returns:
            The cost of the property given.
        """
        for space in self.board_data:
            if space.get("name") == property_name:
                return space.get("cost", 0)

    def calculate_grand_total(self):
        """
        Calculates the total refund the player would receive if their selected actions are confirmed.
        Returns:
            The total refund amount.
        """
        total = 0
        # Houses
        for name, count in self.pending_transactions["sell_houses"].items():
            price = self.get_property_house_hotel_cost(name)
            total += count * price

        # Hotels
        for name, count in self.pending_transactions["sell_hotels"].items():
            price = self.get_property_house_hotel_cost(name)
            total += count * price

        # Mortgages
        for name in self.pending_transactions["mortgaged"]:
            #dev = self.player.property_development.get(name, {})
            dev = next((p for p in self.player.properties if p["name"] == name), {})
            cost = self.get_property_cost(name)
            if dev.get("houses", 0) == 0 and dev.get("hotels", 0) == 0: # and not dev.get("mortgaged", False):
               if dev.get("mortgaged", False): #if not dev.get("mortgaged", False):
                   total -= cost // 2
               else:
                   total += cost //2

        # Property sales
        for name in self.pending_transactions["sell_property"]:
            #dev = self.player.property_development.get(name, {})
            dev = next((p for p in self.player.properties if p["name"] == name), {})
            if dev.get("houses", 0) == 0 and dev.get("hotels", 0) == 0:
                cost = self.get_property_cost(name)
                total += cost // 2 if dev.get("mortgaged") else cost

        return total
    def process_sale(self, message_log):
        from main import display_msg
        #sell houses
        for name, count in self.pending_transactions["sell_houses"].items():
            if count > 0:
                #self.player.property_development[name]["houses"] -= count
                next(p for p in self.player.properties if p["name"] == name)["houses"] -= count
                refund = self.get_property_house_hotel_cost(name) * count
                self.player.add_money(refund, message_log)
                print(f"Sold {count} houses on {name} for refund £{refund}")
                display_msg(message_log, f"Sold {count} houses on {name} for refund £{refund}")

        #sell hotels
        for name, count in self.pending_transactions["sell_hotels"].items():
            if count > 0:
                prop = next(p for p in self.player.properties if p["name"] == name)
                for _ in range(count):
                    if prop.get("hotels", 0) > 0:
                        prop["hotels"] -= 1
                        prop["houses"] += 4
                        refund = self.get_property_house_hotel_cost(name)
                        self.player.add_money(refund, message_log)
                        print(f"Sold 1 hotel on {name} for £{refund}, added 4 houses")
                        display_msg(message_log, f"Sold 1 hotel on {name} for £{refund}, added 4 houses")
                self.refresh_property_states()
                '''
                #self.player.property_development[name]["hotels"] -= count
                next(p for p in self.player.properties if p["name"] == name)["hotels"] -= count
                refund = self.get_property_house_hotel_cost(name) * count
                self.player.add_money(refund)
                print(f"Sold {count} hotels on {name} for £({refund}")
                '''

        #mortgage properties
        for name in self.pending_transactions["mortgaged"]:
            #dev = self.player.properties[name]
            dev = next(p for p in self.player.properties if p["name"] == name)
            print(f"dev before: {dev}")

            if dev.get("houses", 0) > 0 or dev.get("hotels", 0) > 0:
                print(f"Player must sell all houses and hotels on {name} before mortgaging")
                continue

            if not dev.get("mortgaged", False):
                # Mortgage property
                dev["mortgaged"] = True
                mortgage_value = self.get_property_cost(name) // 2
                self.player.add_money(mortgage_value, message_log)
                print(f"Mortgaged {name} for £{mortgage_value}")
                display_msg(message_log, f"Mortgaged {name} for £{mortgage_value}")
                print(dev)
            else:
                mortgage_value = self.get_property_cost(name) // 2
                if self.player.balance >= mortgage_value:
                    dev["mortgaged"] = False
                    self.player.deduct_money(mortgage_value, message_log)
                    display_msg(message_log, f"un-mortgaged {name}")
                else:
                    display_msg(message_log, f"Not enough money to un-mortgage {name}")
                    print(f"Not enough money to un-mortgage {name}")



        #Sell properties
        for name in self.pending_transactions["sell_property"]:
            #dev = self.player.property_development.get(name, {"houses": 0, "hotels": 0, "mortgaged": False})
            dev = next((p for p in self.player.properties if p["name"] == name),
                       {"houses": 0, "hotels": 0, "mortgaged": False})
            if dev["houses"] == 0 and dev["hotels"] == 0:
                cost = self.get_property_cost(name)
                value = cost // 2 if dev.get("mortgaged") else cost
                self.player.add_money(value, message_log)
                remove_property(self.player, name)

                for space in self.board_data:
                    if space["name"] == name:
                        space["player"] = "Bank"
                        break
                print(f"Sold {name} for £{value}")
            else:
                print(f"Cannot sell {name} with buildings")
        #Reset for next time
        self.pending_transactions.clear()
        self.refresh_property_states()

    def button_clicked(self, event, message_log):
        """
        Handles the button clicks to sell the pending items or to cancel the transaction.
        """
        from main import display_msg
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_property_clicks(event.pos)
            if self.sell_button.collidepoint(event.pos):
                self.process_sale(message_log)
                display_msg(message_log, "Assets have been sold")
                print("Assets have been sold")
                return "Sell"
            elif self.cancel_button.collidepoint(event.pos):
                display_msg(message_log, "Selling Assets have been cancelled")
                print("Selling Assets has been cancelled")
                self.pending_transactions.clear()
                return "Cancel"
            return None