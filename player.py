import pygame
from config import (
    CELL_SIZE,
    PLAYER_COLOR,
    PLAYER_SPEED,
    MOVE_UP,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
)
import math
import os


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
        self.facing = "right"
        self.moving = False
        self.state = "idle"  # 'idle' or 'walk'
        self.direction = "down"  # 'up', 'down', 'left', 'right'
        self.health = 2  # Player can take 2 hits

        # Animation variables
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.12  # seconds per frame

        # Load all sprite frames
        self.sprites = {
            "up": {
                "idle": [
                    pygame.image.load(
                        os.path.join("assets", "elf_back_idle", "elf_back_idle.png")
                    ).convert_alpha()
                ],
                "walk": [
                    pygame.image.load(
                        os.path.join("assets", "elf_back_walk", f"elf_back_walk{i}.png")
                    ).convert_alpha()
                    for i in range(1, 9)
                ],
            },
            "down": {
                "idle": [
                    pygame.image.load(
                        os.path.join("assets", "elf_front_idle", "elf_front_idle.png")
                    ).convert_alpha()
                ],
                "walk": [
                    pygame.image.load(
                        os.path.join(
                            "assets", "elf_front_walk", f"elf_front_walk{i}.png"
                        )
                    ).convert_alpha()
                    for i in range(1, 9)
                ],
            },
            "right": {
                "idle": [
                    pygame.image.load(
                        os.path.join("assets", "elf_side01_idle", "elf_side01_idle.png")
                    ).convert_alpha()
                ],
                "walk": [
                    pygame.image.load(
                        os.path.join(
                            "assets", "elf_side01_walk", f"elf_side01_walk{i}.png"
                        )
                    ).convert_alpha()
                    for i in range(1, 9)
                ],
            },
            "left": {
                "idle": [
                    pygame.image.load(
                        os.path.join("assets", "elf_side02_idle", "elf_side02_idle.png")
                    ).convert_alpha()
                ],
                "walk": [
                    pygame.image.load(
                        os.path.join(
                            "assets", "elf_side02_walk", f"elf_side02_walk{i}.png"
                        )
                    ).convert_alpha()
                    for i in range(1, 9)
                ],
            },
        }

    def handle_event(self, event, maze):
        if event.type == pygame.KEYDOWN:
            move_speed = self.speed * 2 if self.speed_boost else self.speed
            moved = False
            if event.key in MOVE_UP and maze.is_valid_move(
                self.target_x, self.target_y - 1
            ):
                self.target_y -= 1
                self.facing = "up"
                moved = True
            elif event.key in MOVE_DOWN and maze.is_valid_move(
                self.target_x, self.target_y + 1
            ):
                self.target_y += 1
                self.facing = "down"
                moved = True
            elif event.key in MOVE_LEFT and maze.is_valid_move(
                self.target_x - 1, self.target_y
            ):
                self.target_x -= 1
                self.facing = "left"
                moved = True
            elif event.key in MOVE_RIGHT and maze.is_valid_move(
                self.target_x + 1, self.target_y
            ):
                self.target_x += 1
                self.facing = "right"
                moved = True
            if moved:
                self.direction = self.facing

    def update(self, dt):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        interp_speed = self.speed * (2 if self.speed_boost else 1) * dt
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            move = min(interp_speed, dist)
            self.x += (dx / dist) * move
            self.y += (dy / dist) * move
            self.moving = True
            # Update facing based on movement direction
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.facing = "right"
                    self.direction = "right"
                elif dx < 0:
                    self.facing = "left"
                    self.direction = "left"
            else:
                if dy > 0:
                    self.facing = "down"
                    self.direction = "down"
                elif dy < 0:
                    self.facing = "up"
                    self.direction = "up"
        else:
            self.x = self.target_x
            self.y = self.target_y
            self.moving = False

        # Update speed boost
        if self.speed_boost:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost = False

        # Update animation
        if self.moving:
            self.state = "walk"
            self.animation_timer += dt
            frames = self.sprites[self.direction]["walk"]
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % len(frames)
        else:
            self.state = "idle"
            self.animation_frame = 0
            self.animation_timer = 0

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
        # Draw sprite at 1.5x size
        frames = self.sprites[self.direction][self.state]
        frame = frames[self.animation_frame % len(frames)]
        scale = 1.5
        new_size = (int(frame.get_width() * scale), int(frame.get_height() * scale))
        frame_scaled = pygame.transform.smoothscale(frame, new_size)
        frame_rect = frame_scaled.get_rect(center=(screen_x, screen_y))
        screen.blit(frame_scaled, frame_rect)

        # # Draw glow
        # glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        # pygame.draw.circle(
        #     glow_surf,
        #     (0, 255, 0, 80),
        #     (self.radius * 2, self.radius * 2),
        #     self.radius + 8,
        # )
        # screen.blit(glow_surf, (screen_x - self.radius * 2, screen_y - self.radius * 2))

        # # Draw eye
        # eye_x = int(screen_x + self.radius // 2 * math.cos(math.radians(-45)))
        # eye_y = int(screen_y - self.radius // 2)
        # pygame.draw.circle(screen, (0, 255, 0), (eye_x, eye_y), 3)

        # Draw speed lines when moving
        # if abs(self.x - self.target_x) > 0.01 or abs(self.y - self.target_y) > 0.01:
        #     speed_line_offset = 15 if self.facing == "right" else -15
        #     for i in range(3):
        #         start_pos = (screen_x - speed_line_offset + i * 5, screen_y - 5)
        #         end_pos = (screen_x - speed_line_offset + i * 5, screen_y + 5)
        #         pygame.draw.line(screen, color, start_pos, end_pos, 1)

    def take_damage(self):
        self.health = max(0, self.health - 1)
