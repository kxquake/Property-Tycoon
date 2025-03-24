import pygame

class Button:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
                    
def auction_game_loop():
    pygame.init()
    
    SCREEN_WIDTH, SCREEN_HEIGHT = 525, 460
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Player Tycoon")
    auction_image = pygame.image.load("pngs/Auction.png").convert_alpha()
    auction_image = pygame.transform.scale(auction_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30) 
    user_texts = [0, 0, 0, 0, 0, 0]  # List to store text for each input box
    input_rects = [
        pygame.Rect(21, 372, 20, 30), 
        pygame.Rect(103, 381, 60, 30),
        pygame.Rect(191, 383, 70, 28),
        pygame.Rect(276, 382, 70, 28),
        pygame.Rect(357, 381, 70, 30),
        pygame.Rect(445, 381, 70, 30),
    ]  # the button for players to enter bids
    active_input = None  
    input = 0
    no_inputs = 0
    running = True
    max_bid = 0
    player = 0
    nobid_buttons = [
        Button(21, 424, 70, 21),
        Button(102, 424, 72, 21),
        Button(190, 424, 69, 20),
        Button(275, 424, 70, 21),
        Button(356, 424, 71, 21),
        Button(444, 425, 70, 29)
    ] # button for players to not place a bid
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(input_rects): # if a player clicks a user input box it allows the user to type
                    if rect.collidepoint(event.pos):
                        active_input = i
                        break  
                else:
                    active_input = None  

                for i, button in enumerate(nobid_buttons):
                    if button.is_clicked(mouse_pos):
                        print(f"No bid player {i + 1}")
                        no_inputs += 1 # sees if the no bid button is presses
            elif event.type == pygame.KEYDOWN:
                if active_input is not None:
                    if event.key == pygame.K_BACKSPACE:
                        user_texts[active_input] = user_texts[active_input][:-1] # removes the last typed digit
                    else:
                        user_texts[active_input] = (user_texts[active_input] * 10) + int(event.unicode) # only allows digits to be entered by user
        
        screen.blit(auction_image, (0, 0)) 
        
        for i, rect in enumerate(input_rects):
            text_surface = font.render(str(user_texts[i]), True, (12, 12, 12))
            screen.blit(text_surface, (rect.x + 5, rect.y + 5))
            rect.w = max(100, text_surface.get_width() + 10)  # updates the screen with the users input
        pygame.display.flip() 
        clock.tick(60)
        
        if no_inputs == 6:
            print("No bids places")
            return 1
        for i in user_texts:
            if i!= 0:
                input += 1
        if input == 6:
            for i in user_texts:
                if i > max_bid:
                    max_bid = i
            if user_texts != max_bid:
                player += 1
            print("all bids placed")
            return player