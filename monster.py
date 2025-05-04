import pygame
import heapq
from config import (CELL_SIZE, MONSTER_COLOR, MONSTER_MOVE_DELAY, MONSTER_BASE_SPEED)

class Monster:
    def __init__(self, x, y, index=0):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.path = []
        self.move_timer = 0
        self.frozen = False
        self.freeze_timer = 0
        self.speed = MONSTER_BASE_SPEED * (0.8 if index > 0 else 1.0)
        self.index = index
        self.pulse = 0
        self.pulse_direction = 1
        self.facing = 'right'
        
        # Animation variables
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
    
    def update(self, dt, player, maze):
        if self.frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.frozen = False
        
        if self.frozen:
            return
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        if abs(dx) > 0.01 or abs(dy) > 0.01:
            move_speed = dt * self.speed
            
            if abs(dx) > 0.01:
                self.x += dx * min(move_speed, 1.0)
                self.facing = 'left' if dx < 0 else 'right'
            else:
                self.x = self.target_x
                
            if abs(dy) > 0.01:
                self.y += dy * min(move_speed, 1.0)
            else:
                self.y = self.target_y
                
            # Update animation
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.x = self.target_x
            self.y = self.target_y
            
            self.move_timer -= dt
            if self.move_timer <= 0:
                self.move_timer = MONSTER_MOVE_DELAY
                
                if not self.frozen:
                    player_x = int(player.x + 0.5)
                    player_y = int(player.y + 0.5)
                    
                    self.path = self._find_path_to_player(maze, 
                                                         (int(self.x), int(self.y)), 
                                                         (player_x, player_y))
                    
                    if len(self.path) > 1:
                        next_pos = self.path[1]
                        self.target_x, self.target_y = next_pos
        
        self.pulse += dt * 2 * self.pulse_direction
        if self.pulse > 1:
            self.pulse = 1
            self.pulse_direction = -1
        elif self.pulse < 0:
            self.pulse = 0
            self.pulse_direction = 1
    
    def _find_path_to_player(self, maze, start, goal):
        open_set = []
        heapq.heappush(open_set, (0 + self._heuristic(start, goal), 0, start, [start]))
        visited = set()
        
        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            if current == goal:
                return path
            
            visited.add(current)
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                neighbor = (current[0]+dx, current[1]+dy)
                if (0 <= neighbor[0] < maze.width and
                    0 <= neighbor[1] < maze.height and
                    maze.grid[neighbor[1]][neighbor[0]] == 0 and
                    neighbor not in visited):
                    heapq.heappush(open_set, (
                        g+1 + self._heuristic(neighbor, goal),
                        g+1,
                        neighbor,
                        path + [neighbor]
                    ))
        return [start]
    
    def _heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def freeze(self, duration):
        self.frozen = True
        self.freeze_timer = duration
    
    def draw(self, screen, offset_x=0, offset_y=0):
        screen_x = int(self.x * CELL_SIZE + CELL_SIZE // 2) + offset_x
        screen_y = int(self.y * CELL_SIZE + CELL_SIZE // 2) + offset_y
        
        size = int(CELL_SIZE // 2 - 2 + self.pulse * 4)
        
        if self.frozen:
            color = pygame.Color(100, 100, 255)
        else:
            color = pygame.Color(*MONSTER_COLOR)
        
        # Draw pulsating glow
        glow_size = size + 6
        glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
        glow_color = (color.r, color.g, color.b, 100)
        pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
        screen.blit(glow_surf, (screen_x - glow_size, screen_y - glow_size))
        
        # Draw enhanced monster body
        pygame.draw.circle(screen, color, (screen_x, screen_y), size)
        
        # Draw monster details
        eye_size = size // 3
        eye_offset = size // 2
        
        # Draw main eyes
        for x_offset in [-eye_offset, eye_offset]:
            # Eye socket (darker color)
            socket_color = (color.r//2, color.g//2, color.b//2)
            pygame.draw.circle(screen, socket_color,
                             (screen_x + x_offset, screen_y - eye_offset), eye_size + 2)
            
            # Eye white
            pygame.draw.circle(screen, (255, 255, 255),
                             (screen_x + x_offset, screen_y - eye_offset), eye_size)
            
            # Pupil (follows player direction)
            pupil_offset = 2 if self.facing == 'right' else -2
            pygame.draw.circle(screen, (255, 0, 0),  # Red pupils for menacing look
                             (screen_x + x_offset + pupil_offset, screen_y - eye_offset), eye_size//2)
        
        # Draw "teeth" when not frozen
        if not self.frozen:
            teeth_color = (255, 255, 255)
            teeth_width = 3
            teeth_height = 6
            teeth_count = 4
            teeth_gap = size // (teeth_count + 1)
            
            for i in range(teeth_count):
                tooth_x = screen_x - size + (i + 1) * teeth_gap
                pygame.draw.polygon(screen, teeth_color, [
                    (tooth_x, screen_y + size//2),
                    (tooth_x + teeth_width, screen_y + size//2),
                    (tooth_x + teeth_width//2, screen_y + size//2 + teeth_height)
                ])
        
        # Draw "horns" or spikes
        horn_color = (color.r//2, color.g//2, color.b//2)
        horn_points = [
            [(screen_x - size, screen_y - size), (screen_x - size + 8, screen_y - size - 8), (screen_x - size + 16, screen_y - size)],
            [(screen_x + size - 16, screen_y - size), (screen_x + size - 8, screen_y - size - 8), (screen_x + size, screen_y - size)]
        ]
        for points in horn_points:
            pygame.draw.polygon(screen, horn_color, points)
        
        # Add animation effect when moving
        if abs(self.x - self.target_x) > 0.01 or abs(self.y - self.target_y) > 0.01:
            # Draw energy particles
            particle_color = (255, 100, 100) if not self.frozen else (100, 100, 255)
            for i in range(4):
                offset = (self.animation_frame + i) * 5
                particle_x = screen_x - size - offset if self.facing == 'right' else screen_x + size + offset
                particle_y = screen_y + (i - 1.5) * 4
                pygame.draw.circle(screen, particle_color, (particle_x, particle_y), 2) 