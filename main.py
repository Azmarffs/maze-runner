import pygame
import sys
from game import Game
from config import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS, BACKGROUND_COLOR

def main():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()  # For sound
    
    # Create screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    
    # Create clock for controlling frame rate
    clock = pygame.time.Clock()
    
    # Create game instance
    game = Game(screen)
    
    # Main game loop
    running = True
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        
        # Update game state
        game.update()
        
        # Clear the screen
        screen.fill(BACKGROUND_COLOR)
        
        # Draw the game
        game.draw()
        
        # Update the display
        pygame.display.flip()
        
        # Control the frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()