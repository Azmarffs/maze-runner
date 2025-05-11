import pygame
from config import CELL_SIZE, SPEED_POWERUP_COLOR, FREEZE_POWERUP_COLOR, POWERUP_SIZE


class PowerUp:
    """Base class for power-ups"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (255, 255, 255)  # Default color
        self.pulse = 0
        self.pulse_direction = 1

    def update(self, dt):
        """
        Update power-up animation.
        """
        # Update pulsating effect
        self.pulse += dt * 2 * self.pulse_direction
        if self.pulse > 1:
            self.pulse = 1
            self.pulse_direction = -1
        elif self.pulse < 0:
            self.pulse = 0
            self.pulse_direction = 1

    def draw(self, screen, offset_x=0, offset_y=0):
        """
        Draw the power-up.
        """
        # Calculate screen position (center of cell)
        screen_x = int(self.x * CELL_SIZE + CELL_SIZE // 2) + offset_x
        screen_y = int(self.y * CELL_SIZE + CELL_SIZE // 2) + offset_y

        # Size with pulsation
        size = POWERUP_SIZE + int(self.pulse * 3)

        # Draw glow
        glow_size = size + 5
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_color = (*self.color, 100)  # Semi-transparent
        pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
        screen.blit(glow_surf, (screen_x - glow_size, screen_y - glow_size))

        # Draw power-up
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), size)


class SpeedPowerUp(PowerUp):
    """Power-up that increases player speed"""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = SPEED_POWERUP_COLOR

    def draw(self, screen, offset_x=0, offset_y=0):
        """
        Draw speed power-up with lightning bolt symbol.
        """
        super().draw(screen, offset_x, offset_y)

        # Calculate screen position
        screen_x = int(self.x * CELL_SIZE + CELL_SIZE // 2) + offset_x
        screen_y = int(self.y * CELL_SIZE + CELL_SIZE // 2) + offset_y

        # Draw lightning bolt symbol
        bolt_points = [
            (screen_x, screen_y - POWERUP_SIZE // 2),  # Top
            (screen_x - POWERUP_SIZE // 3, screen_y),  # Left middle
            (screen_x, screen_y - POWERUP_SIZE // 4),  # Inner top
            (screen_x + POWERUP_SIZE // 3, screen_y - POWERUP_SIZE // 4),  # Right
            (screen_x, screen_y + POWERUP_SIZE // 2),  # Bottom
            (screen_x, screen_y),  # Center
        ]

        pygame.draw.polygon(screen, (0, 0, 0), bolt_points)


class FreezePowerUp(PowerUp):
    """Power-up that gives a shield (blue)"""

    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = FREEZE_POWERUP_COLOR

    def draw(self, screen, offset_x=0, offset_y=0):
        # Draw base blue circle with glow
        super().draw(screen, offset_x, offset_y)
        screen_x = int(self.x * CELL_SIZE + CELL_SIZE // 2) + offset_x
        screen_y = int(self.y * CELL_SIZE + CELL_SIZE // 2) + offset_y
        # Draw shield icon (blue with white border)
        pygame.draw.circle(
            screen, (0, 200, 255), (screen_x, screen_y), POWERUP_SIZE // 2
        )
        pygame.draw.circle(
            screen, (255, 255, 255), (screen_x, screen_y), POWERUP_SIZE // 2, 3
        )
        # Draw a simple shield shape overlay
        pygame.draw.polygon(
            screen,
            (0, 120, 200),
            [
                (screen_x, screen_y - 7),
                (screen_x - 7, screen_y),
                (screen_x, screen_y + 10),
                (screen_x + 7, screen_y),
            ],
        )
