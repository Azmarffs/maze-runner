import pygame
import heapq
from config import CELL_SIZE, MONSTER_COLOR, MONSTER_MOVE_DELAY, MONSTER_BASE_SPEED
import math


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
        self.facing = "right"

        # Animation variables
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.12  # seconds per frame
        # Load spritesheet
        self.spritesheet = pygame.image.load(
            "assets/enemy_spritesheet.png"
        ).convert_alpha()
        self.frames = []
        self.frame_size = self.spritesheet.get_height() // 5  # 5 columns
        for i in range(5):  # 5 columns
            # Add 1-pixel margin to avoid clipping
            rect = pygame.Rect(
                i * self.frame_size + 1, 1, self.frame_size - 2, self.frame_size - 2
            )
            self.frames.append(self.spritesheet.subsurface(rect))

    def update(self, dt, player, maze):
        if self.frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0:
                self.frozen = False

        if self.frozen:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y

        # Track facing direction
        if abs(dx) > abs(dy):
            if dx > 0:
                self.facing = "right"
            elif dx < 0:
                self.facing = "left"
        else:
            if dy > 0:
                self.facing = "down"
            elif dy < 0:
                self.facing = "up"

        # Use a fixed interpolation speed for smooth movement
        interp_speed = self.speed * dt
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            move = min(interp_speed, dist)
            self.x += (dx / dist) * move
            self.y += (dy / dist) * move
        else:
            self.x = self.target_x
            self.y = self.target_y

        # Update animation
        self.animation_timer += dt
        if self.animation_timer > self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.frames)

        self.move_timer -= dt
        if self.move_timer <= 0:
            self.move_timer = MONSTER_MOVE_DELAY

            if not self.frozen:
                player_x = int(player.x + 0.5)
                player_y = int(player.y + 0.5)

                self.path = self._find_path_to_player(
                    maze, (int(self.x), int(self.y)), (player_x, player_y)
                )

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
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if (
                    0 <= neighbor[0] < maze.width
                    and 0 <= neighbor[1] < maze.height
                    and maze.grid[neighbor[1]][neighbor[0]] == 0
                    and neighbor not in visited
                ):
                    heapq.heappush(
                        open_set,
                        (
                            g + 1 + self._heuristic(neighbor, goal),
                            g + 1,
                            neighbor,
                            path + [neighbor],
                        ),
                    )
        return [start]

    def _heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def freeze(self, duration):
        self.frozen = True
        self.freeze_timer = duration

    def draw(self, screen, offset_x=0, offset_y=0):
        screen_x = int(self.x * CELL_SIZE + CELL_SIZE // 2) + offset_x
        # Raise the sprite a bit higher in the grid
        screen_y = (
            int(self.y * CELL_SIZE + CELL_SIZE // 2 - self.frame_size // 4) + offset_y
        )
        # Draw current animation frame
        frame = self.frames[self.animation_frame]
        # Flip or rotate based on facing
        if self.facing == "left":
            frame = pygame.transform.flip(frame, True, False)
        elif self.facing == "up":
            frame = pygame.transform.rotate(frame, 90)
        elif self.facing == "down":
            frame = pygame.transform.rotate(frame, -90)
        frame_rect = frame.get_rect(center=(screen_x, screen_y))
        screen.blit(frame, frame_rect)

        # Add animation effect when moving (energy particles)
        # if abs(self.x - self.target_x) > 0.01 or abs(self.y - self.target_y) > 0.01:
        #     particle_color = (255, 100, 100) if not self.frozen else (100, 100, 255)
        #     for i in range(4):
        #         offset = (self.animation_frame + i) * 5
        #         particle_x = (
        #             screen_x - 20 - offset
        #             if self.facing == "right"
        #             else screen_x + 20 + offset
        #         )
        #         particle_y = screen_y + (i - 1.5) * 4
        #         pygame.draw.circle(screen, particle_color, (particle_x, particle_y), 2)
