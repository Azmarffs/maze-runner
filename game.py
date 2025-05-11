import pygame
import random
import time
import sys
from maze import Maze
from player import Player
from monster import Monster
from powerups import PowerUp, SpeedPowerUp, FreezePowerUp
from particles import ParticleSystem
from config import *
import math


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.game_state = STATE_TITLE
        self.menu_state = STATE_MENU
        self.storm_active = False
        self.storm_warning = False
        self.storm_timer = 0
        self.storm_warning_timer = 0
        self.next_storm_time = random.uniform(STORM_MIN_INTERVAL, STORM_MAX_INTERVAL)
        if not pygame.mixer.get_init():
            print("Warning: Mixer not initialized")
        if not pygame.mixer.get_init() or not pygame.mixer.get_init()[0]:
            print("Warning: No sound device available")
        print(f"MP3 supported: {pygame.mixer.get_init()}")
        # Enhanced fonts with larger sizes
        pygame.font.init()
        self.title_font = pygame.font.SysFont("Verdana", 92, bold=True)
        self.menu_font = pygame.font.SysFont("Verdana", 42)
        self.font = pygame.font.SysFont("Verdana", 32)
        self.small_font = pygame.font.SysFont("Verdana", 24)

        # Menu options and animations
        self.menu_options = ["Start Game", "How to Play", "Exit"]
        self.selected_option = 0
        self.menu_animations = {
            "title_offset": 0,
            "title_glow": 0,
            "option_scales": [1.0] * len(self.menu_options),
            "background_offset": 0,
            "particle_timer": 0,
        }

        # Initialize sound system first
        pygame.mixer.init(44100, -16, 2, 2048)
        self.init_sounds()

        # Initialize particle systems
        self.particle_systems = []
        self.menu_particles = []
        self.init_menu_particles()

        # Initialize visual effects
        self.transition_alpha = 0
        self.effect_timer = 0
        self.pulse_value = 0
        self.pulse_direction = 1

        # Initialize game elements
        self.new_game()

        # Maze background for menu
        self.menu_maze_lines = self.generate_menu_maze_lines()

        # Cache terminal fonts for UI
        self.term_font = pygame.font.SysFont("Consolas", 20, bold=True)
        self.term_font_big = pygame.font.SysFont("Consolas", 48, bold=True)
        self.term_font_med = pygame.font.SysFont("Consolas", 32, bold=True)
        self.term_font_small = pygame.font.SysFont("Consolas", 28, bold=True)

    def init_menu_particles(self):
        self.menu_particles = []
        for _ in range(40):
            self.menu_particles.append(
                {
                    "x": random.randint(0, self.screen_width),
                    "y": random.randint(0, self.screen_height),
                    "speed": random.uniform(30, 80),
                    "size": random.uniform(2, 6),
                    "color": random.choice(PARTICLE_COLORS),
                    "alpha": random.randint(50, 200),
                    "direction": random.uniform(-0.5, 0.5),
                }
            )

    def generate_menu_maze_lines(self):
        lines = []
        cell_size = 80
        for x in range(0, self.screen_width + cell_size, cell_size):
            for y in range(0, self.screen_height + cell_size, cell_size):
                if random.random() < 0.7:
                    lines.append(
                        {
                            "start": (x, y),
                            "end": (
                                (x + cell_size, y)
                                if random.random() < 0.5
                                else (x, y + cell_size)
                            ),
                            "alpha": random.randint(30, 80),
                            "width": random.randint(1, 3),
                        }
                    )
        return lines

    def draw_main_menu(self):
        # Fill background with dark color
        self.screen.fill((0, 10, 0))  # Darker green for more atmosphere

        # Draw animated maze lines in background
        for line in self.menu_maze_lines:
            color = (0, line["alpha"], 0)
            pygame.draw.line(
                self.screen, color, line["start"], line["end"], line["width"]
            )

        # Update and draw particles
        current_time = time.time()
        for particle in self.menu_particles:
            # Update position with smooth wave motion
            particle["x"] += (
                math.sin(current_time + particle["y"] * 0.01) * particle["direction"]
            )
            particle["y"] = (
                particle["y"] - particle["speed"] * 0.016
            ) % self.screen_height

            # Draw particle with glow effect
            glow_radius = particle["size"] * 3
            glow_surface = pygame.Surface(
                (glow_radius * 2, glow_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                glow_surface,
                (*particle["color"][:3], particle["alpha"] // 3),
                (glow_radius, glow_radius),
                glow_radius,
            )
            self.screen.blit(
                glow_surface, (particle["x"] - glow_radius, particle["y"] - glow_radius)
            )

            # Draw core particle
            pygame.draw.circle(
                self.screen,
                (*particle["color"][:3], particle["alpha"]),
                (int(particle["x"]), int(particle["y"])),
                particle["size"],
            )

        # Animate title
        self.menu_animations["title_glow"] = (
            self.menu_animations["title_glow"] + 0.02
        ) % (2 * math.pi)
        glow_intensity = abs(math.sin(self.menu_animations["title_glow"]))

        # Draw main title with dramatic glow effect
        title_text = "MAZE RUNNER"
        title_shadow_color = (0, int(40 * glow_intensity), 0)
        title_color = (
            0,
            int(200 + 55 * glow_intensity),
            int(100 + 155 * glow_intensity),
        )

        # Draw multiple layers of shadow for depth
        for offset in range(3, 0, -1):
            title_surface = self.title_font.render(title_text, True, title_shadow_color)
            self.screen.blit(
                title_surface,
                (
                    self.screen_width // 2 - title_surface.get_width() // 2 + offset,
                    120 + offset,
                ),
            )

        # Draw main title
        title_surface = self.title_font.render(title_text, True, title_color)
        self.screen.blit(
            title_surface,
            (self.screen_width // 2 - title_surface.get_width() // 2, 120),
        )

        # Draw subtitle with pulsing effect
        subtitle_color = (
            0,
            int(150 + 105 * glow_intensity),
            int(200 + 55 * glow_intensity),
        )
        subtitle = self.menu_font.render("Escape from AI", True, subtitle_color)
        subtitle_pos = (self.screen_width // 2 - subtitle.get_width() // 2, 220)
        self.screen.blit(subtitle, subtitle_pos)

        # Draw menu options with enhanced hover effects
        for i, option in enumerate(self.menu_options):
            # Update hover scale with smooth animation
            target_scale = 1.2 if i == self.selected_option else 1.0
            self.menu_animations["option_scales"][i] += (
                target_scale - self.menu_animations["option_scales"][i]
            ) * 0.2

            # Calculate colors based on selection
            if i == self.selected_option:
                base_color = (0, 255, 200)
                glow_color = (0, 200, 150, 100)
            else:
                base_color = (0, 150, 100)
                glow_color = (0, 100, 50, 50)

            # Apply pulsing effect to selected option
            if i == self.selected_option:
                color_pulse = abs(math.sin(time.time() * 4)) * 55
                base_color = tuple(min(255, c + color_pulse) for c in base_color)

            # Render text with current scale
            text = self.menu_font.render(option, True, base_color)
            scaled_size = (
                int(text.get_width() * self.menu_animations["option_scales"][i]),
                int(text.get_height() * self.menu_animations["option_scales"][i]),
            )
            text = pygame.transform.smoothscale(text, scaled_size)

            # Position text
            pos_x = self.screen_width // 2 - text.get_width() // 2
            pos_y = 350 + i * 80

            # Draw glow effect
            if i == self.selected_option:
                glow_surf = pygame.Surface(
                    (text.get_width() + 40, text.get_height() + 20), pygame.SRCALPHA
                )
                for size in range(20, 0, -5):
                    pygame.draw.rect(
                        glow_surf,
                        (*glow_color[:3], glow_color[3] // size),
                        (
                            size,
                            size,
                            text.get_width() + 40 - size * 2,
                            text.get_height() + 20 - size * 2,
                        ),
                        border_radius=10,
                    )
                self.screen.blit(glow_surf, (pos_x - 20, pos_y - 10))

            # Draw text with shadow
            shadow = self.menu_font.render(option, True, (0, 40, 20))
            shadow = pygame.transform.smoothscale(shadow, scaled_size)
            self.screen.blit(shadow, (pos_x + 2, pos_y + 2))
            self.screen.blit(text, (pos_x, pos_y))

    def init_sounds(self):
        try:
            pygame.mixer.init()
            self.sounds = {
                "move": pygame.mixer.Sound("move.wav"),
                "powerup": pygame.mixer.Sound("powerup.wav"),
                "win": pygame.mixer.Sound("win.wav"),
                "game_over": pygame.mixer.Sound("game_over.mp3"),
            }

            # Set volumes
            for sound in self.sounds.values():
                sound.set_volume(0.4)
        except Exception as e:
            print(f"Warning: Sound initialization failed: {e}")
            self.sounds = {}

    def new_game(self):
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.player = Player(*self.maze.start_pos)
        self.monsters = []

        # Create monsters with varied behaviors
        for i in range(MONSTER_COUNT):
            while True:
                x = random.randint(0, MAZE_WIDTH - 1)
                y = random.randint(0, MAZE_HEIGHT - 1)
                if (
                    self.maze.grid[y][x] == 0
                    and abs(x - self.maze.start_pos[0])
                    + abs(y - self.maze.start_pos[1])
                    > 10
                ):
                    self.monsters.append(Monster(x, y, i))
                    break

        # Create power-ups with enhanced visuals
        self.powerups = []
        for i, pos in enumerate(self.maze.powerup_positions):
            if i % 2 == 0:
                self.powerups.append(SpeedPowerUp(*pos))
            else:
                self.powerups.append(FreezePowerUp(*pos))

        # Reset timers and effects
        self.last_time = pygame.time.get_ticks() / 1000.0
        self.game_time = 0
        self.effect_timer = 0
        self.particle_systems = []

        if self.game_state != STATE_TITLE:
            self.game_state = STATE_PLAYING

    def handle_event(self, event):
        if self.menu_state == STATE_MENU:
            if event.type == pygame.KEYDOWN:
                # Menu navigation with arrow keys
                if event.key in [pygame.K_UP, pygame.K_w]:
                    self.selected_option = (self.selected_option - 1) % len(
                        self.menu_options
                    )
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.selected_option = (self.selected_option + 1) % len(
                        self.menu_options
                    )
                # Menu selection
                elif event.key == pygame.K_RETURN:
                    if self.selected_option == 0:  # Start Game
                        self.menu_state = STATE_PLAYING
                        self.game_state = STATE_PLAYING
                        self.new_game()
                    elif self.selected_option == 1:  # How to Play
                        self.menu_state = STATE_HOW_TO_PLAY
                    elif self.selected_option == 2:  # Exit
                        pygame.quit()
                        sys.exit()
                return
        if self.menu_state == STATE_HOW_TO_PLAY:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.menu_state = STATE_MENU
            return
        if event.type == pygame.KEYDOWN:
            if self.game_state == STATE_TITLE:
                self.game_state = STATE_PLAYING
                self.add_transition_effect()
                return

            if (
                self.game_state in [STATE_GAME_OVER, STATE_WIN]
                and event.key == RESTART_KEY
            ):
                self.new_game()
                self.add_transition_effect()
                return

            if event.key == PAUSE_KEY:
                if self.game_state == STATE_PLAYING:
                    self.game_state = STATE_PAUSED
                elif self.game_state == STATE_PAUSED:
                    self.game_state = STATE_PLAYING
                self.add_transition_effect()
                return

    def update(self):
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - self.last_time
        self.last_time = current_time

        # Update visual effects
        self.update_effects(dt)

        if self.game_state != STATE_PLAYING:
            return

        self.game_time += dt

        # --- Continuous movement logic ---
        keys = pygame.key.get_pressed()
        # Only allow new movement if player is at target (not in between cells)
        if (
            abs(self.player.x - self.player.target_x) < 0.01
            and abs(self.player.y - self.player.target_y) < 0.01
        ):
            move_made = False
            if any(keys[k] for k in MOVE_UP) and self.maze.is_valid_move(
                self.player.target_x, self.player.target_y - 1
            ):
                self.player.target_y -= 1
                self.player.facing = "up" if hasattr(self.player, "facing") else "right"
                move_made = True
            elif any(keys[k] for k in MOVE_DOWN) and self.maze.is_valid_move(
                self.player.target_x, self.player.target_y + 1
            ):
                self.player.target_y += 1
                self.player.facing = (
                    "down" if hasattr(self.player, "facing") else "right"
                )
                move_made = True
            elif any(keys[k] for k in MOVE_LEFT) and self.maze.is_valid_move(
                self.player.target_x - 1, self.player.target_y
            ):
                self.player.target_x -= 1
                self.player.facing = "left"
                move_made = True
            elif any(keys[k] for k in MOVE_RIGHT) and self.maze.is_valid_move(
                self.player.target_x + 1, self.player.target_y
            ):
                self.player.target_x += 1
                self.player.facing = "right"
                move_made = True
            if move_made and "move" in self.sounds:
                self.sounds["move"].play()
                self.add_movement_particles(
                    (self.player.x, self.player.y),
                    (self.player.target_x, self.player.target_y),
                )

        self.player.update(dt)

        # --- Shield timer update ---
        if hasattr(self.player, "shield") and self.player.shield:
            self.player.shield_timer -= dt
            if self.player.shield_timer <= 0:
                self.player.shield = False
                self.player.shield_timer = 0

        # Update monsters and check collisions
        for monster in self.monsters:
            monster.update(dt, self.player, self.maze)
            if (
                int(monster.x) == int(self.player.x)
                and int(monster.y) == int(self.player.y)
                and not monster.frozen
            ):
                # --- Shield logic: if player has shield, consume it instead of health ---
                if hasattr(self.player, "shield") and self.player.shield:
                    self.player.shield = False
                    self.player.shield_timer = 0
                    self.add_powerup_effect((int(self.player.x), int(self.player.y)))
                elif self.player.health > 0:
                    is_dead = self.player.take_damage()
                    if is_dead:
                        self.game_state = STATE_GAME_OVER
                        if "game_over" in self.sounds:
                            self.sounds["game_over"].play()
                        self.add_game_over_effect()
                else:
                    self.game_state = STATE_GAME_OVER
                    if "game_over" in self.sounds:
                        self.sounds["game_over"].play()
                    self.add_game_over_effect()

        # Update power-ups and check collection
        player_pos = (int(self.player.x), int(self.player.y))
        for powerup in self.powerups[:]:
            if (int(powerup.x), int(powerup.y)) == player_pos:
                if isinstance(powerup, SpeedPowerUp):
                    self.player.apply_speed_boost(POWERUP_DURATION)
                elif isinstance(powerup, FreezePowerUp):
                    self.player.shield = True
                    self.player.shield_timer = 10.0
                self.powerups.remove(powerup)
                if "powerup" in self.sounds:
                    self.sounds["powerup"].play()
                self.add_powerup_effect(player_pos)

        # Check win condition
        ex, ey = self.maze.exit_pos
        # Use rounding to allow for float imprecision
        if round(self.player.x) == ex and round(self.player.y) == ey:
            self.game_state = STATE_WIN
            if "win" in self.sounds:
                self.sounds["win"].play()
            self.add_win_effect()

        # Update particle systems
        for system in self.particle_systems[:]:
            system.update(dt)
            if system.is_finished():
                self.particle_systems.remove(system)

        # --- Storm logic ---
        print(
            # f"[Storm Debug] storm_active={self.storm_active}, storm_warning={self.storm_warning}, next_storm_time={self.next_storm_time:.2f}, storm_timer={self.storm_timer:.2f}, storm_warning_timer={self.storm_warning_timer:.2f}"
        )
        if not self.storm_active and not self.storm_warning:
            self.next_storm_time -= dt
            if self.next_storm_time <= 3:
                # print("[Storm Debug] Storm warning triggered!")
                self.storm_warning = True
                self.storm_warning_timer = 3
        elif self.storm_warning:
            self.storm_warning_timer -= dt
            if self.storm_warning_timer <= 0:
                # print("[Storm Debug] Storm active!")
                self.storm_warning = False
                self.storm_active = True
                self.storm_timer = STORM_DURATION
        elif self.storm_active:
            self.storm_timer -= dt
            if self.storm_timer <= 0:
                # print("[Storm Debug] Storm ended!")
                self.storm_active = False
                self.next_storm_time = random.uniform(
                    STORM_MIN_INTERVAL, STORM_MAX_INTERVAL
                )

    def update_effects(self, dt):
        # Update pulse effect
        self.pulse_value += dt * WALL_PULSE_SPEED * self.pulse_direction
        if self.pulse_value >= 1:
            self.pulse_value = 1
            self.pulse_direction = -1
        elif self.pulse_value <= 0:
            self.pulse_value = 0
            self.pulse_direction = 1

        # Update transition effect
        if self.transition_alpha > 0:
            self.transition_alpha = max(
                0, self.transition_alpha - dt * 255 / TRANSITION_DURATION
            )

        # Update effect timer
        if self.effect_timer > 0:
            self.effect_timer = max(0, self.effect_timer - dt)

    def add_transition_effect(self):
        self.transition_alpha = 255
        self.effect_timer = EFFECT_DURATION

    def add_movement_particles(self, old_pos, new_pos):
        x = (old_pos[0] + new_pos[0]) / 2 * CELL_SIZE
        y = (old_pos[1] + new_pos[1]) / 2 * CELL_SIZE
        self.particle_systems.append(
            ParticleSystem(x, y, PARTICLE_COUNT, PARTICLE_LIFETIME)
        )

    def add_powerup_effect(self, pos):
        x = pos[0] * CELL_SIZE
        y = pos[1] * CELL_SIZE
        self.particle_systems.append(
            ParticleSystem(x, y, PARTICLE_COUNT * 2, PARTICLE_LIFETIME * 1.5)
        )
        self.effect_timer = EFFECT_DURATION

    def add_game_over_effect(self):
        self.effect_timer = EFFECT_DURATION * 2
        center_x = self.screen_width / 2
        center_y = self.screen_height / 2
        self.particle_systems.append(
            ParticleSystem(
                center_x, center_y, PARTICLE_COUNT * 3, PARTICLE_LIFETIME * 2
            )
        )

    def add_win_effect(self):
        self.effect_timer = EFFECT_DURATION * 2
        for i in range(4):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            self.particle_systems.append(
                ParticleSystem(x, y, PARTICLE_COUNT * 2, PARTICLE_LIFETIME * 1.5)
            )

    def draw(self):
        if self.menu_state == STATE_MENU:
            self.draw_main_menu()
            return
        if self.menu_state == STATE_HOW_TO_PLAY:
            self.draw_how_to_play()
            return
        if self.game_state == STATE_GAME_OVER:
            self.draw_game_over_screen()
        elif self.game_state == STATE_WIN:
            self.draw_maze_and_entities()
            # --- Terminal-style win message overlay ---
            overlay = pygame.Surface(
                (self.screen_width, self.screen_height), pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            term_font = pygame.font.SysFont("Consolas", 48, bold=True)
            win_text = term_font.render("YOU ESCAPED!", True, (0, 255, 80))
            win_rect = win_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 - 40)
            )
            self.screen.blit(win_text, win_rect)
            time_font = pygame.font.SysFont("Consolas", 32, bold=True)
            time_text = time_font.render(
                f"Time: {int(self.game_time)} seconds", True, (0, 255, 80)
            )
            time_rect = time_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 10)
            )
            self.screen.blit(time_text, time_rect)
            prompt_font = pygame.font.SysFont("Consolas", 28, bold=True)
            prompt_text = prompt_font.render(
                "Press R to play again", True, (255, 255, 80)
            )
            prompt_rect = prompt_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 60)
            )
            self.screen.blit(prompt_text, prompt_rect)
        elif self.game_state == STATE_PAUSED:
            self.draw_maze_and_entities()
            self.draw_pause_overlay()
        else:
            self.draw_maze_and_entities()
            # Draw storm darkening overlay if storm is active and only in STATE_PLAYING
            if self.storm_active:
                overlay = pygame.Surface(
                    (self.screen_width, self.screen_height), pygame.SRCALPHA
                )
                overlay.fill((0, 0, 0, 255))  # Pitch black
                # Torch effect with smooth non-linear gradient
                torch_radius = int(2.5 * CELL_SIZE)
                torch_soft_edge = int(1.2 * CELL_SIZE)
                px = int(
                    self.player.x * CELL_SIZE
                    + (self.screen_width - MAZE_WIDTH * CELL_SIZE) // 2
                    + CELL_SIZE // 2
                )
                py = int(
                    self.player.y * CELL_SIZE
                    + (self.screen_height - MAZE_HEIGHT * CELL_SIZE) // 2
                    + CELL_SIZE // 2
                )
                for r in range(torch_radius + torch_soft_edge, 0, -1):
                    # Use a non-linear fade for realism (ease-in)
                    if r > torch_radius:
                        t = (r - torch_radius) / torch_soft_edge
                        alpha = int(255 * (t**2))  # quadratic fade
                    else:
                        alpha = 0
                    pygame.draw.circle(overlay, (0, 0, 0, alpha), (px, py), r)
                self.screen.blit(overlay, (0, 0))

                # CRT grain and scanlines effect
                crt_overlay = pygame.Surface(
                    (self.screen_width, self.screen_height), pygame.SRCALPHA
                )
                # Scanlines
                for y in range(0, self.screen_height, 3):
                    pygame.draw.line(
                        crt_overlay, (0, 40, 0, 32), (0, y), (self.screen_width, y)
                    )
                # Grain/noise
                import random

                for _ in range(self.screen_width * self.screen_height // 80):
                    x = random.randint(0, self.screen_width - 1)
                    y = random.randint(0, self.screen_height - 1)
                    g = random.randint(32, 96)
                    crt_overlay.set_at((x, y), (0, g, 0, random.randint(16, 48)))
                self.screen.blit(
                    crt_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD
                )

        # Draw transition effect
        if self.transition_alpha > 0:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(self.transition_alpha)
            self.screen.blit(overlay, (0, 0))

    def draw_maze_and_entities(self):
        # Calculate offset to center maze
        offset_x = (self.screen_width - MAZE_WIDTH * CELL_SIZE) // 2
        offset_y = (self.screen_height - MAZE_HEIGHT * CELL_SIZE) // 2

        # Draw maze walls as CRT background color (dark)
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if self.maze.grid[y][x] == 1:
                    rect = pygame.Rect(
                        x * CELL_SIZE + offset_x,
                        y * CELL_SIZE + offset_y,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(self.screen, CRT_BACKGROUND_COLOR, rect)

        # Animate grid glow
        grid_glow = 80 + int(
            80 * (0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.002))
        )
        path_color = (80, 255, 80)  # Neon green for path
        path_thickness = 28
        border_color = (0, 40, 0)  # Dark green border
        border_thickness = path_thickness + 8
        corner_radius = CELL_SIZE // 2
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if self.maze.grid[y][x] == 0:
                    cx = x * CELL_SIZE + offset_x + CELL_SIZE // 2
                    cy = y * CELL_SIZE + offset_y + CELL_SIZE // 2
                    # Draw lines to all open neighbors (right and down only to avoid duplicates)
                    for dx, dy in [(1, 0), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if (
                            0 <= nx < MAZE_WIDTH
                            and 0 <= ny < MAZE_HEIGHT
                            and self.maze.grid[ny][nx] == 0
                        ):
                            ncx = nx * CELL_SIZE + offset_x + CELL_SIZE // 2
                            ncy = ny * CELL_SIZE + offset_y + CELL_SIZE // 2
                            # Draw border first
                            pygame.draw.line(
                                self.screen,
                                border_color,
                                (cx, cy),
                                (ncx, ncy),
                                border_thickness,
                            )
                            # Draw path on top
                            pygame.draw.line(
                                self.screen,
                                path_color,
                                (cx, cy),
                                (ncx, ncy),
                                path_thickness,
                            )
                    # Draw rounded corners (arc) if both right and down are open
                    if (
                        x + 1 < MAZE_WIDTH
                        and y + 1 < MAZE_HEIGHT
                        and self.maze.grid[y][x + 1] == 0
                        and self.maze.grid[y + 1][x] == 0
                        and self.maze.grid[y + 1][x + 1] == 0
                    ):
                        rect = pygame.Rect(cx, cy, corner_radius * 2, corner_radius * 2)
                        # Border arc
                        pygame.draw.arc(
                            self.screen,
                            border_color,
                            rect,
                            math.pi,
                            1.5 * math.pi,
                            border_thickness,
                        )
                        # Path arc
                        pygame.draw.arc(
                            self.screen,
                            path_color,
                            rect,
                            math.pi,
                            1.5 * math.pi,
                            path_thickness,
                        )
        # Draw exit as animated glowing portal
        ex, ey = self.maze.exit_pos
        exit_cx = ex * CELL_SIZE + offset_x + CELL_SIZE // 2
        exit_cy = ey * CELL_SIZE + offset_y + CELL_SIZE // 2
        portal_radius = 22
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.005)
        # Outer glow
        for i in range(6, 0, -1):
            alpha = int(max(0, min(255, 60 * pulse * i)))
            r = int(0)
            g = int(max(0, min(255, 255 - i * 30)))
            b = int(max(0, min(255, 180 + i * 10)))
            color = (r, g, b, alpha)
            surf = pygame.Surface(
                (portal_radius * 2 + 16, portal_radius * 2 + 16), pygame.SRCALPHA
            )
            pygame.draw.circle(
                surf,
                color,
                (portal_radius + 8, portal_radius + 8),
                portal_radius + i * 2,
            )
            self.screen.blit(
                surf,
                (exit_cx - portal_radius - 8, exit_cy - portal_radius - 8),
                special_flags=pygame.BLEND_RGBA_ADD,
            )
        # Main portal ring
        pygame.draw.circle(
            self.screen, (0, 255, 180), (exit_cx, exit_cy), portal_radius, 4
        )
        # Bright center
        pygame.draw.circle(self.screen, (180, 255, 255), (exit_cx, exit_cy), 12)
        # Animated sparkles
        for i in range(8):
            angle = math.radians(i * 45 + (pygame.time.get_ticks() * 0.1) % 360)
            sx = int(exit_cx + math.cos(angle) * (portal_radius - 4))
            sy = int(exit_cy + math.sin(angle) * (portal_radius - 4))
            pygame.draw.circle(self.screen, (255, 255, 255), (sx, sy), 2)
        # Draw powerups on top of maze
        for powerup in self.powerups:
            powerup.draw(self.screen, offset_x, offset_y)

        # Draw monsters and player as before
        for system in self.particle_systems:
            system.draw(self.screen)
        for monster in self.monsters:
            monster.draw(self.screen, offset_x, offset_y)
        self.player.draw(self.screen, offset_x, offset_y)

        # Draw UI (pass shake_x, shake_y)
        self.draw_ui()

    def draw_ui(self, shake_x=0, shake_y=0):
        # --- Console/Terminal styled health bar at bottom left ---
        bar_width = 220
        bar_height = 18
        margin = 24
        bar_x = margin + shake_x
        bar_y = self.screen_height - bar_height - margin + shake_y

        # Draw background (black, like a terminal)
        pygame.draw.rect(
            self.screen,
            (8, 24, 8),
            (bar_x, bar_y, bar_width, bar_height),
            border_radius=0,
        )
        # Draw health fill (single rect, green)
        health_width = int((bar_width - 2) * self.player.health / 100)
        if health_width > 0:
            pygame.draw.rect(
                self.screen,
                (0, 255, 80),
                (bar_x + 1, bar_y + 1, health_width, bar_height - 2),
                border_radius=0,
            )

        # Draw time as terminal text at bottom left
        time_str = f"TIME: {int(self.game_time)}s"
        time_text = self.term_font.render(time_str, True, (0, 255, 80))
        self.screen.blit(time_text, (bar_x, bar_y + bar_height + 6))

        # Draw power-up status as terminal text
        if self.player.speed_boost:
            boost_str = f"SPEED BOOST: {int(self.player.speed_boost_timer)}s"
            boost_text = self.term_font.render(boost_str, True, (255, 255, 0))
            self.screen.blit(boost_text, (bar_x, bar_y + bar_height + 32))

        # Draw shield status as a large, clear label with timer and icon
        if hasattr(self.player, "shield") and self.player.shield:
            shield_bg_rect = pygame.Rect(bar_x, bar_y - 48, 220, 40)
            pygame.draw.rect(self.screen, (8, 24, 32), shield_bg_rect, border_radius=8)
            pygame.draw.rect(
                self.screen, (0, 200, 255), shield_bg_rect, 2, border_radius=8
            )
            shield_str = f"SHIELD {int(self.player.shield_timer)}s"
            shield_font = pygame.font.SysFont("Consolas", 28, bold=True)
            shield_text = shield_font.render(shield_str, True, (0, 200, 255))
            # Draw a shield icon (blue with white border)
            shield_icon_x = bar_x + 24
            shield_icon_y = bar_y - 28
            pygame.draw.circle(
                self.screen, (0, 200, 255), (shield_icon_x, shield_icon_y), 16
            )
            pygame.draw.circle(
                self.screen, (255, 255, 255), (shield_icon_x, shield_icon_y), 16, 3
            )
            # Draw a simple shield shape overlay
            pygame.draw.polygon(
                self.screen,
                (0, 120, 200),
                [
                    (shield_icon_x, shield_icon_y - 10),
                    (shield_icon_x - 10, shield_icon_y),
                    (shield_icon_x, shield_icon_y + 14),
                    (shield_icon_x + 10, shield_icon_y),
                ],
            )
            self.screen.blit(shield_text, (bar_x + 48, bar_y - 42))

        # Storm warning/active as terminal text at bottom center
        if self.storm_warning:
            warning_str = "A DARK STORM IS COMING!"
            warning_text = self.term_font_small.render(warning_str, True, (255, 80, 80))
            self.screen.blit(
                warning_text,
                (
                    self.screen_width // 2 - warning_text.get_width() // 2,
                    self.screen_height - 80,
                ),
            )
        if self.storm_active:
            storm_str = "DARK STORM!"
            storm_text = self.term_font_med.render(storm_str, True, (255, 255, 80))
            self.screen.blit(
                storm_text,
                (
                    self.screen_width // 2 - storm_text.get_width() // 2,
                    self.screen_height - 48,
                ),
            )

    def draw_title_screen(self):
        # Draw animated background
        self.screen.fill(CRT_BACKGROUND_COLOR)

        # Draw particle effects
        if random.random() < 0.05:
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            self.particle_systems.append(
                ParticleSystem(x, y, PARTICLE_COUNT, PARTICLE_LIFETIME)
            )

        for system in self.particle_systems:
            system.draw(self.screen)

        # Draw title with glow effect
        title_text = self.title_font.render("MAZE RUNNER", True, (0, 200, 255))
        glow = int(self.pulse_value * 64)
        title_glow = self.title_font.render(
            "MAZE RUNNER",
            True,
            (min(255, 0 + glow), min(255, 200 + glow), min(255, 255 + glow)),
        )

        subtitle_text = self.font.render("Escape from AI", True, (200, 0, 255))
        subtitle_glow = self.font.render(
            "Escape from AI", True, (min(255, 200 + glow), 0, min(255, 255 + glow))
        )

        title_rect = title_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 50)
        )
        subtitle_rect = subtitle_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )

        self.screen.blit(title_glow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_glow, (subtitle_rect.x + 2, subtitle_rect.y + 2))
        self.screen.blit(subtitle_text, subtitle_rect)

        # Draw instructions with pulse effect
        alpha = int(128 + 127 * self.pulse_value)
        instructions_text = self.font.render(
            "Press any key to start", True, UI_TEXT_COLOR
        )
        instructions_text.set_alpha(alpha)

        controls_text = self.small_font.render(
            "Use WASD or Arrow Keys to move", True, UI_TEXT_COLOR
        )
        controls_text.set_alpha(alpha)

        instructions_rect = instructions_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 100)
        )
        controls_rect = controls_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 150)
        )

        self.screen.blit(instructions_text, instructions_rect)
        self.screen.blit(controls_text, controls_rect)

    def draw_game_over_screen(self):
        self.draw_maze_and_entities()

        # Create dark overlay with particles
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Draw game over text with terminal style
        term_font = pygame.font.SysFont("Consolas", 48, bold=True)
        died_text = term_font.render("YOU DIED!", True, (255, 80, 80))
        died_rect = died_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 40)
        )
        self.screen.blit(died_text, died_rect)
        prompt_font = pygame.font.SysFont("Consolas", 28, bold=True)
        prompt_text = prompt_font.render("Press R to restart", True, (255, 255, 80))
        prompt_rect = prompt_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 40)
        )
        self.screen.blit(prompt_text, prompt_rect)

    def draw_pause_overlay(self):
        # Create pause overlay with blur effect
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        # Draw pause text with glow
        pause_text = self.title_font.render("PAUSED", True, UI_TEXT_COLOR)
        glow = int(self.pulse_value * 64)
        pause_glow = self.title_font.render(
            "PAUSED",
            True,
            (
                min(255, UI_TEXT_COLOR[0] + glow),
                min(255, UI_TEXT_COLOR[1] + glow),
                min(255, UI_TEXT_COLOR[2] + glow),
            ),
        )

        continue_text = self.font.render("Press P to continue", True, UI_TEXT_COLOR)

        pause_rect = pause_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 40)
        )
        continue_rect = continue_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 40)
        )

        self.screen.blit(pause_glow, (pause_rect.x + 2, pause_rect.y + 2))
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(continue_text, continue_rect)

    def draw_how_to_play(self):
        self.screen.fill(CRT_BACKGROUND_COLOR)
        lines = [
            "Escape the maze before the monster catches you!",
            "Use WASD or Arrow Keys to move.",
            "Collect power-ups to help you survive.",
            "Beware of random dark storms that limit your vision!",
            "Press ESC to return to menu.",
        ]
        for i, line in enumerate(lines):
            text = self.font.render(line, True, (220, 220, 220))
            self.screen.blit(
                text, (self.screen_width // 2 - text.get_width() // 2, 150 + i * 40)
            )
