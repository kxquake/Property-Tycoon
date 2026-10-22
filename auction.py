import pygame


class Button:
    """
    Clickable button used for the UI interaction, such as the no bid buttons.
    """
    def __init__(self, x, y, width, height):
        """
        Initialises the button with position and size.
        - x: x coordinate of the button.
        - y: y coordinate of the button.
        - width: width of the button
        - height: height of the button
        """
        self.rect = pygame.Rect(x, y, width, height)

    def is_clicked(self, mouse_pos):
        """
        Check if the button was clicked.
        - mouse_pos: (tuple) x and y coordinates of the mouse click.
        Returns:
            bool: True if the button was clicked, False otherwise.
        """
        return self.rect.collidepoint(mouse_pos)


def auction_game_loop(players, ai_agent=None, auction_property=None):
    """
    Runs the auction screen where players ands AI can place bids for a property.
    - players: list of player objects.
    - ai_agent: the AI for the AI bidding logic if they are present.
    - auction_property: the The property that is being auctioned.
    Returns:
        tuple of the index of the winning player and the winning bid. (index of winning player, winning bid) or
        (None, 0) if no one bids.
    """
    pygame.init()

    SCREEN_WIDTH, SCREEN_HEIGHT = 525, 460
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Player Tycoon")
    auction_image = pygame.image.load("pngs/Auction.png").convert_alpha()
    auction_image = pygame.transform.scale(auction_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()  # for error message
    font = pygame.font.Font(None, 30)
    num_players = len(players)
    user_texts = [""] * num_players  # List to store text for each input box
    input_rects = [pygame.Rect(21 + i * 82, 372, 50, 30) for i in
                   range(num_players)]  # the button for players to enter bids
    # variable initialisation
    active_input = None
    submitted_players = set()
    passed_players = set()
    running = True
    error_message = ""
    error_timer = 0
    current_highest_bid = 0
    current_winner_index = None
    last_ai_bid_time = 0
    ai_bid_delay = 1000  # 1 second delay between AI bids

    nobid_buttons = [Button(24 + i * 81, 414, 70, 21) for i in
                     range(num_players)]  # button for players to not place a bid

    print(f"{len(players)} players entered auction")

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Handle input box clicks
                for i, rect in enumerate(input_rects):  # if a player clicks a user input box it allows the user to type
                    if i in passed_players or i == current_winner_index:
                        continue
                    if rect.collidepoint(event.pos):
                        active_input = i
                        user_texts[i] = ""  # set the user texts to zero when they re-click.
                        break
                else:
                    active_input = None

                # Handle no bid button clicks
                for i, button in enumerate(nobid_buttons):
                    if button.is_clicked(mouse_pos):
                        if i not in passed_players and i != current_winner_index:
                            passed_players.add(i)
                            print(f"Player {i + 1} passed")
                            if hasattr(players[i], "is_ai") and players[i].is_ai:
                                print(f"AI Player {i + 1} chose not to bid")

            elif event.type == pygame.KEYDOWN:
                if active_input is not None:
                    if event.key == pygame.K_BACKSPACE:
                        user_texts[active_input] = user_texts[active_input][:-1]  # removes the last typed digit
                    elif event.unicode.isdigit():
                        user_texts[
                            active_input] += event.unicode  # (user_texts[active_input] * 10) + int(event.unicode) # only allows digits to be entered by the user
                    elif event.key == pygame.K_RETURN:  # enters the bid
                        if user_texts[active_input] == "":
                            bid = 0
                        else:
                            bid = int(user_texts[active_input])

                        player_balance = players[active_input].balance

                        if bid > player_balance:  # if bid is less than players balance
                            print(f"Player {active_input + 1} can't afford bid.")
                            error_message = f"Player {active_input + 1}: Insufficient funds!"
                            error_timer = current_time
                            user_texts[active_input] = ""
                        elif bid <= current_highest_bid:  # if bid is less than the highest bid
                            error_message = f"Bid must be higher than highest bid."
                            error_timer = current_time
                            user_texts[active_input] = ""
                        elif players[active_input].laps_completed < 1:
                            error_message = f"Player has not completed a lap of the board so cannot bid."
                            error_timer = current_time
                            user_texts[active_input] = ""
                        else:  # else bid is submitted
                            current_winner_index = active_input
                            current_highest_bid = bid
                            print(f"Player {active_input + 1} bid: {bid}")
                            submitted_players.add(active_input)
                            passed_players.clear()
                            active_input = None

        # Process AI bids with delay
        if ai_agent and auction_property and current_time - last_ai_bid_time > ai_bid_delay:
            for i, player in enumerate(players):
                if (hasattr(player, "is_ai") and player.is_ai and i != current_winner_index
                        and i not in passed_players):

                    bid = ai_agent.ai_auction(auction_property, player.balance, current_highest_bid)
                    if bid > current_highest_bid:
                        current_highest_bid = bid
                        current_winner_index = i
                        submitted_players.add(i)
                        print(f"AI Player {i + 1} bid £{bid}")
                        user_texts[i] = str(bid)
                        last_ai_bid_time = current_time
                        passed_players.clear()  # Reset passes when new bid comes in
                    else:
                        passed_players.add(i)
                        print(f"AI Player {i + 1} chose not to bid")
            last_ai_bid_time = current_time

        # Draw everything
        screen.blit(auction_image, (0, 0))

        if auction_property:
            prop_name = auction_property.get("name", "Unknown Property")
            prop_cost = auction_property.get("cost")
            property_font = pygame.font.Font(None, 32)
            detail_font = pygame.font.Font(None, 26)
            name_surface = property_font.render(f"Auctioning: {prop_name}", True, (0, 0, 0))
            name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, 20))  # Centered at the top
            screen.blit(name_surface, name_rect)

            cost_surface = detail_font.render(f"Cost: £{prop_cost},", True, (0, 0, 0))
            cost_rect = cost_surface.get_rect(center=(SCREEN_WIDTH // 2, 60))
            screen.blit(cost_surface, cost_rect)

        # Display player balances
        money_font = pygame.font.Font(None, 20)
        for i in range(len(players)):
            money_text = money_font.render(f"£{players[i].balance}", True, (0, 0, 0))
            money_x = input_rects[i].x + 19
            money_y = input_rects[i].y - 34
            screen.blit(money_text, (money_x, money_y))

        # Display current highest bid
        auctionResult_font = pygame.font.Font(None, 20)
        bid_text = auctionResult_font.render(f"Highest Bid: {current_highest_bid}", True, (0, 0, 0))
        screen.blit(bid_text, (360, 240))

        # Display input boxes
        for i, rect in enumerate(input_rects):
            if i == current_winner_index:
                # show bid as locked
                text_surface = font.render(f"£{user_texts[i]}", True, (0, 128, 0))
            elif i in passed_players:
                text_surface = font.render("PASS", True, (255, 0, 0))
            else:
                text_surface = font.render(str(user_texts[i]), True, (12, 12, 12))

            screen.blit(text_surface, (rect.x + 5, rect.y + 5))
            rect.w = max(73, text_surface.get_width() + 10)  # updates the screen with the users input

        # Display error messages
        if error_message and current_time - error_timer < 2000:  # Show for 2 seconds
            error_font = pygame.font.Font(None, 28)
            error_surface = error_font.render(error_message, True, (255, 0, 0))
            error_bg_rect = error_surface.get_rect()
            error_bg_rect.center = (SCREEN_WIDTH // 2, 30)

            # Draw black rectangle
            pygame.draw.rect(screen, (0, 0, 0), error_bg_rect.inflate(20, 10))
            screen.blit(error_surface, error_bg_rect)
        else:
            error_message = ""

        # Check auction end conditions
        active_players = [i for i in range(num_players)
                          if i not in passed_players and i != current_winner_index]

        if not active_players and current_winner_index is not None:
            print(f"Player {current_winner_index + 1} wins with £{current_highest_bid}")
            return current_winner_index, current_highest_bid
        elif not active_players and current_winner_index is None:
            print("No bids - property remains with bank")
            return None, 0

        pygame.display.flip()
        clock.tick(60)

