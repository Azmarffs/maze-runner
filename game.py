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

        # Enhanced fonts
        pygame.font.init()
        self.title_font = pygame.font.SysFont("Verdana", 48, bold=True)
        self.font = pygame.font.SysFont("Verdana", 24)
        self.small_font = pygame.font.SysFont("Verdana", 16)

        # Initialize particle systems
        self.particle_systems = []

        # Initialize visual effects
        self.transition_alpha = 0
        self.effect_timer = 0
        self.pulse_value = 0
        self.pulse_direction = 1

        # Initialize game elements
        self.init_sounds()
        self.new_game()

    def init_sounds(self):
        try:
            pygame.mixer.init()
            self.sounds = {
                "move": pygame.mixer.Sound("move.wav"),
                "powerup": pygame.mixer.Sound("powerup.wav"),
                "win": pygame.mixer.Sound("win.wav"),
                "lose": pygame.mixer.Sound("lose.wav"),
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
                if event.key == pygame.K_RETURN:
                    self.menu_state = STATE_TITLE
                elif event.key == pygame.K_h:
                    self.menu_state = STATE_HOW_TO_PLAY
                elif event.key == pygame.K_q:
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
        # No player movement here!

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

        # Update monsters and check collisions
        for monster in self.monsters:
            monster.update(dt, self.player, self.maze)
            if int(monster.x) == int(self.player.x) and int(monster.y) == int(
                self.player.y
            ):
                self.game_state = STATE_GAME_OVER
                if "lose" in self.sounds:
                    self.sounds["lose"].play()
                self.add_game_over_effect()

        # Update power-ups and check collection
        player_pos = (int(self.player.x), int(self.player.y))
        for powerup in self.powerups[:]:
            if (int(powerup.x), int(powerup.y)) == player_pos:
                if isinstance(powerup, SpeedPowerUp):
                    self.player.apply_speed_boost(POWERUP_DURATION)
                else:
                    for monster in self.monsters:
                        monster.freeze(POWERUP_DURATION)
                self.powerups.remove(powerup)
                if "powerup" in self.sounds:
                    self.sounds["powerup"].play()
                self.add_powerup_effect(player_pos)

        # Check win condition
        if player_pos == self.maze.exit_pos:
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
            f"[Storm Debug] storm_active={self.storm_active}, storm_warning={self.storm_warning}, next_storm_time={self.next_storm_time:.2f}, storm_timer={self.storm_timer:.2f}, storm_warning_timer={self.storm_warning_timer:.2f}"
        )
        if not self.storm_active and not self.storm_warning:
            self.next_storm_time -= dt
            if self.next_storm_time <= 3:
                print("[Storm Debug] Storm warning triggered!")
                self.storm_warning = True
                self.storm_warning_timer = 3
        elif self.storm_warning:
            self.storm_warning_timer -= dt
            if self.storm_warning_timer <= 0:
                print("[Storm Debug] Storm active!")
                self.storm_warning = False
                self.storm_active = True
                self.storm_timer = STORM_DURATION
        elif self.storm_active:
            self.storm_timer -= dt
            if self.storm_timer <= 0:
                print("[Storm Debug] Storm ended!")
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
        if self.game_state == STATE_TITLE:
            self.draw_title_screen()
        elif self.game_state == STATE_GAME_OVER:
            self.draw_game_over_screen()
        elif self.game_state == STATE_WIN:
            self.draw_win_screen()
        elif self.game_state == STATE_PAUSED:
            self.draw_maze_and_entities()
            self.draw_pause_overlay()
        else:
            self.draw_maze_and_entities()

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

        # Create fog of war surface
        fog_surface = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        fog_surface.fill(FOG_COLOR)

        # Draw maze with enhanced effects
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                rect = pygame.Rect(
                    x * CELL_SIZE + offset_x,
                    y * CELL_SIZE + offset_y,
                    CELL_SIZE,
                    CELL_SIZE,
                )

                if self.maze.grid[y][x] == 1:
                    # Wall with glow effect
                    glow = int(self.pulse_value * WALL_GLOW_INTENSITY * 255)
                    color = (
                        min(255, WALL_COLOR[0] + glow),
                        min(255, WALL_COLOR[1] + glow),
                        min(255, WALL_COLOR[2] + glow),
                    )
                    pygame.draw.rect(self.screen, color, rect)

                    # Add inner shadow
                    shadow_rect = rect.inflate(-4, -4)
                    pygame.draw.rect(
                        self.screen,
                        (color[0] // 2, color[1] // 2, color[2] // 2),
                        shadow_rect,
                    )
                else:
                    # Path with subtle grid
                    pygame.draw.rect(self.screen, PATH_COLOR, rect)
                    pygame.draw.rect(
                        self.screen,
                        (PATH_COLOR[0] + 10, PATH_COLOR[1] + 10, PATH_COLOR[2] + 10),
                        rect,
                        1,
                    )

                    # Draw exit
                    if (x, y) == self.maze.exit_pos:
                        exit_rect = rect.inflate(-8, -8)
                        glow = int(self.pulse_value * 64)
                        exit_color = (
                            min(255, EXIT_COLOR[0] + glow),
                            min(255, EXIT_COLOR[1] + glow),
                            min(255, EXIT_COLOR[2] + glow),
                        )
                        pygame.draw.rect(
                            self.screen, exit_color, exit_rect, border_radius=8
                        )

                        if CELL_SIZE >= 30:
                            exit_text = self.small_font.render(
                                "EXIT", True, (255, 255, 255)
                            )
                            text_rect = exit_text.get_rect(center=rect.center)
                            self.screen.blit(exit_text, text_rect)

        # Draw power-ups with enhanced effects
        for powerup in self.powerups:
            powerup.draw(self.screen, offset_x, offset_y)

        # Draw particle systems
        for system in self.particle_systems:
            system.draw(self.screen)

        # Draw monsters with enhanced effects
        for monster in self.monsters:
            monster.draw(self.screen, offset_x, offset_y)

        # Draw player with enhanced effects
        self.player.draw(self.screen, offset_x, offset_y)

        # --- Flashlight fog of war ---
        player_screen_x = int(self.player.x * CELL_SIZE + CELL_SIZE // 2) + offset_x
        player_screen_y = int(self.player.y * CELL_SIZE + CELL_SIZE // 2) + offset_y
        fog_surface = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        if self.storm_active:
            # Pitch black everywhere except a torch radius around the player, with soft edge and flicker
            fog_surface.fill((0, 0, 0, 255))
            torch_radius = int(CELL_SIZE * 3.5)
            flicker = random.randint(-8, 8)
            gradient_radius = torch_radius + flicker

            # Create a white radial gradient for the torch
            flashlight_surface = pygame.Surface(
                (gradient_radius * 2, gradient_radius * 2), pygame.SRCALPHA
            )
            for r in range(gradient_radius, 0, -1):
                alpha = int(255 * (1 - r / gradient_radius) ** 2)
                pygame.draw.circle(
                    flashlight_surface,
                    (255, 255, 255, alpha),
                    (gradient_radius, gradient_radius),
                    r,
                )
            # The center is fully white, edge fades to transparent

            # Subtract the gradient from the black fog to make a visible torch
            fog_surface.blit(
                flashlight_surface,
                (player_screen_x - gradient_radius, player_screen_y - gradient_radius),
                special_flags=pygame.BLEND_RGBA_SUB,
            )

            # Add subtle noise overlay
            noise = pygame.Surface(
                (self.screen_width, self.screen_height), pygame.SRCALPHA
            )
            for _ in range(300):
                x = random.randint(0, self.screen_width - 1)
                y = random.randint(0, self.screen_height - 1)
                a = random.randint(10, 30)
                pygame.draw.circle(noise, (0, 0, 0, a), (x, y), 1)
            fog_surface.blit(noise, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            self.screen.blit(fog_surface, (0, 0))
        else:
            # Normal flashlight effect
            visibility_radius = int(PLAYER_VISION_RADIUS * CELL_SIZE)
            flashlight_strength = 255
            fog_surface.fill((0, 0, 0, 0))
            for r in range(visibility_radius, 0, -1):
                alpha = int(flashlight_strength * (r / visibility_radius))
                pygame.draw.circle(
                    fog_surface, (0, 0, 0, alpha), (player_screen_x, player_screen_y), r
                )
            # Subtle noise/texture overlay to maze at all times
            noise = pygame.Surface(
                (self.screen_width, self.screen_height), pygame.SRCALPHA
            )
            for _ in range(200):
                x = random.randint(0, self.screen_width - 1)
                y = random.randint(0, self.screen_height - 1)
                a = random.randint(5, 15)
                pygame.draw.circle(noise, (0, 0, 0, a), (x, y), 1)
            fog_surface.blit(noise, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            self.screen.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        # Draw UI
        # Fog/mist particles and screen shake if monster is near
        shake_x = shake_y = 0
        min_dist = (
            min(
                ((monster.x - self.player.x) ** 2 + (monster.y - self.player.y) ** 2)
                ** 0.5
                for monster in self.monsters
            )
            if self.monsters
            else 99
        )
        if min_dist < 5:
            # import random

            shake_x = random.randint(-6, 6)
            shake_y = random.randint(-6, 6)
            # Draw fog/mist particles
            mist_surface = pygame.Surface(
                (self.screen_width, self.screen_height), pygame.SRCALPHA
            )
            for _ in range(30):
                mx = random.randint(0, self.screen_width - 1)
                my = random.randint(0, self.screen_height - 1)
                r = random.randint(10, 30)
                a = random.randint(10, 40)
                pygame.draw.circle(mist_surface, (180, 180, 200, a), (mx, my), r)
            self.screen.blit(mist_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        # Apply screen shake by shifting the whole screen (simulate by offsetting UI)
        self.draw_ui(shake_x, shake_y)

    def draw_ui(self, shake_x=0, shake_y=0):
        # Draw time with shadow
        time_text = self.font.render(
            f"Time: {int(self.game_time)}", True, UI_TEXT_COLOR
        )
        shadow_text = self.font.render(f"Time: {int(self.game_time)}", True, (0, 0, 0))
        self.screen.blit(shadow_text, (22 + shake_x, 22 + shake_y))
        self.screen.blit(time_text, (20 + shake_x, 20 + shake_y))

        # Draw power-up status with effects
        if self.player.speed_boost:
            boost_text = self.font.render(
                f"Speed Boost: {int(self.player.speed_boost_timer)}s",
                True,
                SPEED_POWERUP_COLOR,
            )
            glow = int(self.pulse_value * 64)
            boost_color = (
                min(255, SPEED_POWERUP_COLOR[0] + glow),
                min(255, SPEED_POWERUP_COLOR[1] + glow),
                min(255, SPEED_POWERUP_COLOR[2] + glow),
            )
            boost_glow = self.font.render(
                f"Speed Boost: {int(self.player.speed_boost_timer)}s", True, boost_color
            )
            self.screen.blit(boost_glow, (22 + shake_x, 62 + shake_y))
            self.screen.blit(boost_text, (20 + shake_x, 60 + shake_y))

        # Improved storm warning and storm active text
        if self.storm_warning:
            big_font = pygame.font.SysFont("Verdana", 44, bold=True)
            warning_text = big_font.render(
                "A dark storm is coming!", True, (255, 80, 80)
            )
            glow = pygame.font.SysFont("Verdana", 44, bold=True).render(
                "A dark storm is coming!", True, (255, 0, 0)
            )
            self.screen.blit(
                glow, (self.screen_width // 2 - glow.get_width() // 2 + 2, 62 + 2)
            )
            self.screen.blit(
                warning_text,
                (self.screen_width // 2 - warning_text.get_width() // 2, 60),
            )
        if self.storm_active:
            big_font = pygame.font.SysFont("Verdana", 54, bold=True)
            storm_text = big_font.render("DARK STORM!", True, (255, 255, 80))
            glow = big_font.render("DARK STORM!", True, (255, 0, 0))
            self.screen.blit(
                glow, (self.screen_width // 2 - glow.get_width() // 2 + 3, 93 + 3)
            )
            self.screen.blit(
                storm_text, (self.screen_width // 2 - storm_text.get_width() // 2, 90)
            )

    def draw_title_screen(self):
        # Draw animated background
        self.screen.fill(BACKGROUND_COLOR)

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

        # Draw game over text with glow
        game_over_text = self.title_font.render("GAME OVER", True, (255, 50, 50))
        glow = int(self.pulse_value * 64)
        game_over_glow = self.title_font.render(
            "GAME OVER",
            True,
            (min(255, 255 + glow), min(255, 50 + glow), min(255, 50 + glow)),
        )

        restart_text = self.font.render("Press R to restart", True, UI_TEXT_COLOR)

        game_over_rect = game_over_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 40)
        )
        restart_rect = restart_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 40)
        )

        self.screen.blit(game_over_glow, (game_over_rect.x + 2, game_over_rect.y + 2))
        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw_win_screen(self):
        self.draw_maze_and_entities()

        # Create victory overlay with particles
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Draw victory text with effects
        win_text = self.title_font.render("YOU ESCAPED!", True, (50, 255, 50))
        glow = int(self.pulse_value * 64)
        win_glow = self.title_font.render(
            "YOU ESCAPED!",
            True,
            (min(255, 50 + glow), min(255, 255 + glow), min(255, 50 + glow)),
        )

        time_text = self.font.render(
            f"Time: {int(self.game_time)} seconds", True, UI_TEXT_COLOR
        )
        restart_text = self.font.render("Press R to play again", True, UI_TEXT_COLOR)

        win_rect = win_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 60)
        )
        time_rect = time_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )
        restart_rect = restart_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 60)
        )

        self.screen.blit(win_glow, (win_rect.x + 2, win_rect.y + 2))
        self.screen.blit(win_text, win_rect)
        self.screen.blit(time_text, time_rect)
        self.screen.blit(restart_text, restart_rect)

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

    def draw_main_menu(self):
        self.screen.fill((10, 10, 20))
        title = self.title_font.render("MAZE RUNNER", True, (255, 255, 255))
        self.screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 120))
        start = self.font.render("Press ENTER to Start", True, (200, 200, 200))
        howto = self.font.render("Press H for How to Play", True, (200, 200, 200))
        quit_ = self.font.render("Press Q to Quit", True, (200, 200, 200))
        self.screen.blit(start, (self.screen_width // 2 - start.get_width() // 2, 250))
        self.screen.blit(howto, (self.screen_width // 2 - howto.get_width() // 2, 300))
        self.screen.blit(quit_, (self.screen_width // 2 - quit_.get_width() // 2, 350))

    def draw_how_to_play(self):
        self.screen.fill((10, 10, 20))
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
