import pygame
from config import (CELL_SIZE, PLAYER_COLOR, PLAYER_SPEED, MOVE_UP, MOVE_DOWN, 
                   MOVE_LEFT, MOVE_RIGHT)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = PLAYER_SPEED
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.radius = CELL_SIZE // 2 - 4
        self.glow_size = self.radius + 8
        self.glow_alpha = 150
        self.pulse_counter = 0
        self.pulse_direction = 1
        self.facing = 'right'
        
        # Initialize animation variables
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1  # seconds per frame
    
    def handle_event(self, event, maze):
        if event.type == pygame.KEYDOWN:
            move_speed = self.speed * 2 if self.speed_boost else self.speed
            
            if event.key in MOVE_UP and maze.is_valid_move(self.target_x, self.target_y - 1):
                self.target_y -= 1
            elif event.key in MOVE_DOWN and maze.is_valid_move(self.target_x, self.target_y + 1):
                self.target_y += 1
            elif event.key in MOVE_LEFT and maze.is_valid_move(self.target_x - 1, self.target_y):
                self.target_x -= 1
                self.facing = 'left'
            elif event.key in MOVE_RIGHT and maze.is_valid_move(self.target_x + 1, self.target_y):
                self.target_x += 1
                self.facing = 'right'
    
    def update(self, dt):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        move_speed = dt * self.speed * (2 if self.speed_boost else 1)
        
        if abs(dx) > 0.01:
            self.x += dx * min(move_speed, 1.0)
        else:
            self.x = self.target_x
            
        if abs(dy) > 0.01:
            self.y += dy * min(move_speed, 1.0)
        else:
            self.y = self.target_y
        
        # Update speed boost
        if self.speed_boost:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost = False
        
        # Update animation
        if abs(dx) > 0.01 or abs(dy) > 0.01:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        
        # Update pulse effect
        self.pulse_counter += dt * 2 * self.pulse_direction
        if self.pulse_counter > 1:
            self.pulse_counter = 1
            self.pulse_direction = -1
        elif self.pulse_counter < 0:
            self.pulse_counter = 0
            self.pulse_direction = 1
    
    def apply_speed_boost(self, duration):
        self.speed_boost = True
        self.speed_boost_timer = duration
    
    def draw(self, screen, offset_x=0, offset_y=0):
        screen_x = int(self.x * CELL_SIZE + CELL_SIZE // 2) + offset_x
        screen_y = int(self.y * CELL_SIZE + CELL_SIZE // 2) + offset_y
        
        # Draw glow effect
        glow_size = self.glow_size + int(self.pulse_counter * 4)
        glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
        
        # Set color based on speed boost
        if self.speed_boost:
            color = (255, 255, 0)  # Yellow for speed boost
        else:
            color = PLAYER_COLOR
        
        # Draw glowing circle with alpha
        glow_color = (*color, self.glow_alpha)
        pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
        screen.blit(glow_surf, (screen_x - glow_size, screen_y - glow_size))
        
        # Draw enhanced player character
        player_rect = pygame.Rect(
            screen_x - self.radius,
            screen_y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
        # Draw body
        pygame.draw.circle(screen, color, (screen_x, screen_y), self.radius)
        
        # Draw face details based on facing direction
        eye_offset = 4 if self.facing == 'right' else -4
        
        # Draw eyes (white part)
        eye_pos_1 = (screen_x + eye_offset, screen_y - 2)
        pygame.draw.circle(screen, (255, 255, 255), eye_pos_1, 3)
        
        # Draw pupils (black part)
        pupil_offset = 1 if self.facing == 'right' else -1
        pupil_pos_1 = (screen_x + eye_offset + pupil_offset, screen_y - 2)
        pygame.draw.circle(screen, (0, 0, 0), pupil_pos_1, 1)
        
        # Draw "helmet" or hair
        helmet_points = [
            (screen_x - self.radius + 2, screen_y - self.radius + 4),
            (screen_x + self.radius - 2, screen_y - self.radius + 4),
            (screen_x + self.radius - 2, screen_y - 2),
            (screen_x - self.radius + 2, screen_y - 2)
        ]
        pygame.draw.polygon(screen, (color[0]//2, color[1]//2, color[2]//2), helmet_points)
        
        # Draw speed lines when moving
        if abs(self.x - self.target_x) > 0.01 or abs(self.y - self.target_y) > 0.01:
            speed_line_offset = 15 if self.facing == 'right' else -15
            for i in range(3):
                start_pos = (screen_x - speed_line_offset + i*5, screen_y - 5)
                end_pos = (screen_x - speed_line_offset + i*5, screen_y + 5)
                pygame.draw.line(screen, color, start_pos, end_pos, 1)