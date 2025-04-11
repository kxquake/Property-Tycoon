import pygame
from main import main_game_loop
from tokens import get_default_tokens
from player import Player
import sys
import random
import time
import subprocess


# checks if the script was run in abridged mode
is_abridged = len(sys.argv) > 1 and sys.argv[1] == 'abridged'
if is_abridged and len(sys.argv) > 2 and sys.argv[2].isdigit():
    time_limit_minutes = int(sys.argv[2])


class NumberButton:
    """
    Button to choose the number of players.
    """
    def __init__(self, x, y, width, height, number):
        """Initialisation"""
        self.rect = pygame.Rect(x, y, width, height)
        self.number = number

    def is_clicked(self, mouse_pos):
        """Check if button was clicked based on mouse position"""
        return self.rect.collidepoint(mouse_pos)

class PlayButton:
    """
    Play button used to start the game
    """
    def __init__(self, x, y, width, height):
        """initialisation"""
        self.rect = pygame.Rect(x, y, width, height)\

    def is_clicked(self, mouse_pos):
        """Check if button was clicked based on mouse position"""
        return self.rect.collidepoint(mouse_pos)

class PopupScreen:
    """
    The popup window used for players to select their token after choosing the amount of players.
    """
    def __init__(self, x, y, width, height, text, tokens):
        """
        :param tokens: the *shared* list of remaining tokens that haven't been picked yet
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.close_button = pygame.Rect(x + width - 30, y + 10, 20, 20)

        self.tokens = tokens
        self.offset_x = x
        self.offset_y = y

    def draw(self, screen):
        """
        Draws the popup, text, close button and available tokens
        - screen: The surface to draw on.
        """
        # Draw the popup background
        pygame.draw.rect(screen, (200, 200, 200), self.rect)

        # Draw the close button
        pygame.draw.rect(screen, (255, 0, 0), self.close_button)

        # Draw the text
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 50))

        # Draw the tokens that remain in self.tokens
        for token in self.tokens:

            center = (
                self.offset_x + token.offset_x,
                self.offset_y + token.offset_y
            )
            #pygame.draw.circle(screen, token.color, center, token.radius) #ORIG
            screen.blit(token.token_image, (center[0] - 20, center[1] - 20))

    def is_close_clicked(self, mouse_pos):
        """Check if button was clicked based on mouse position"""
        return self.close_button.collidepoint(mouse_pos)

    def is_token_clicked(self, mouse_pos):
        """
        Checks if the user clicked on any token. Removes token from the shared list
        and returns its color if so.
        """
        for token in self.tokens:
            center = (
                self.offset_x + token.offset_x,
                self.offset_y + token.offset_y
            )
            # Approximate bounding box for the token’s circle
            token_rect = pygame.Rect(
                center[0] - token.radius,
                center[1] - token.radius,
                token.radius * 2,
                token.radius * 2
            )
            if token_rect.collidepoint(mouse_pos):
                # Remove from the shared tokens list
                self.tokens.remove(token)
                return token
        return None


def load_menu(abridged=False, time_limit_minutes=None):
    """
    Launches the main game menu.
    - abridged: boolean, if True abridged mode is activated.
    - time_limit_minutes: time limit for the abridged mode. Set to none for full version.
    """
    pygame.init()

    # Set up display
    screen = pygame.display.set_mode((394, 394))
    pygame.display.set_caption("Player Tycoon - Menu")

    # Load the menu background
    menu_image = pygame.image.load("pngs/menu2.png").convert_alpha()
    menu_image = pygame.transform.scale(menu_image, (394, 394))

    # Create NumberButton instances for numbers 1-5
    number_buttons = [
        NumberButton(35, 181, 52, 43, 1),
        NumberButton(99, 181, 50, 43, 2),
        NumberButton(174, 181, 50, 43, 3),
        NumberButton(241, 181, 50, 43, 4),
        NumberButton(316, 181, 50, 43, 5)
    ]

    play_button = PlayButton(269, 359, 122, 21)

    # This will hold the shared list of tokens available for selection
    # at the start of the game.
    available_tokens = get_default_tokens()

    show_popup = False
    popup = None
    selected_players = 0
    total_players = 0
    player_tokens = []  # stores chosen token colors
    players = []  # stores Player objects
    ai_player = None # set after token selection

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # NumberButtons: choose number of players
                for button in number_buttons:
                    if button.is_clicked(mouse_pos):
                        total_players = button.number
                        selected_players = 0
                        player_tokens = []
                        players = []
                        # Reset available tokens each time you pick a new player count,
                        # if you want to allow them to re-select from the full set.
                        available_tokens = get_default_tokens()
                        show_popup = True

                        popup = PopupScreen(
                            50, 50, 300, 200,
                            f"Player {selected_players + 1}, choose your token",
                            available_tokens
                        )


                # Play Button
                if play_button.is_clicked(mouse_pos):
                    print("Play button clicked")
                    if is_abridged:
                        print("calling main game loop with players:", players)
                        result = main_game_loop(players, abridged_mode=True, time_limit_minutes=time_limit_minutes)
                        running = False
                    else:
                        result = main_game_loop(players, abridged_mode=abridged, time_limit_minutes=time_limit_minutes)
                        running = False
                    if result == "menu":
                        print("Returning to home page")
                        pygame.quit()
                        time.sleep(0.2)
                        subprocess.run(["python", "home.py"])
                    else:
                        running = False


                # Popup close button
                if show_popup and popup.is_close_clicked(mouse_pos):
                    show_popup = False

                # Handle token picking
                if show_popup:
                    selected_token = popup.is_token_clicked(mouse_pos)
                    if selected_token:
                        player = Player(token_image=selected_token.token_image, token_colour=selected_token.colour)
                        players.append(player)
                        player_tokens.append(selected_token)
                        selected_players += 1

                        # If more players still need to choose, show a new popup
                        if selected_players < total_players:
                            popup = PopupScreen(
                                50, 50, 300, 200,
                                f"Player {selected_players + 1}, choose your token",
                                available_tokens
                            )
                        else:
                            print("All players have chosen their tokens:")

                            ai_token = random.choice(available_tokens)
                            available_tokens.remove(ai_token)
                            ai_player = Player(token_image=ai_token.token_image, token_colour=ai_token.colour)
                            ai_player.balance = 1500
                            ai_player.is_ai = True
                            players.append(ai_player)
                            player_tokens.append(ai_token)

                            for i, icon in enumerate(player_tokens):
                                print(f"Player {i + 1}: {icon.name}")
                            show_popup = False

        # Draw the scaled menu
        screen.blit(menu_image, (0, 0))

        # Draw the popup if open
        if show_popup:
            popup.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    load_menu()