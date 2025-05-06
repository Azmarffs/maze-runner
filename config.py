import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Maze Runner - Escape from AI"

# Game constants
FPS = 60
CELL_SIZE = 32
WALL_THICKNESS = 3

# Maze dimensions (must be odd numbers)
MAZE_WIDTH = 25
MAZE_HEIGHT = 17

# Game timing
MONSTER_MOVE_DELAY = 0.5
POWERUP_DURATION = 5

# Enhanced color palette
BACKGROUND_COLOR = (8, 12, 28)  # Deeper blue for atmosphere
WALL_COLOR = (0, 180, 255)  # Brighter neon blue
PATH_COLOR = (15, 20, 35)  # Darker path for contrast
PLAYER_COLOR = (0, 255, 150)  # Vibrant cyan
MONSTER_COLOR = (255, 30, 60)  # Brighter red
EXIT_COLOR = (255, 100, 255)  # Bright magenta
FOG_COLOR = (0, 0, 0, 180)
UI_TEXT_COLOR = (220, 230, 255)
SPEED_POWERUP_COLOR = (255, 220, 0)  # Golden yellow
FREEZE_POWERUP_COLOR = (100, 200, 255)  # Ice blue

# Particle effects
PARTICLE_COLORS = [
    (0, 255, 255),  # Cyan
    (0, 200, 255),  # Light blue
    (100, 255, 200),  # Mint
    (200, 255, 100),  # Light green
    (255, 100, 255),  # Pink
    (255, 150, 50),  # Orange
]

# Enhanced player settings
PLAYER_SPEED = 15
PLAYER_VISION_RADIUS = 4
PLAYER_TRAIL_LENGTH = 5
PLAYER_GLOW_INTENSITY = 0.8

# Enhanced monster settings
MONSTER_COUNT = 2
MONSTER_BASE_SPEED = 3
MONSTER_GLOW_INTENSITY = 0.6
MONSTER_TRAIL_LENGTH = 4

# Power-up settings
POWERUP_COUNT = 4
POWERUP_SIZE = 18
POWERUP_PULSE_SPEED = 2
POWERUP_GLOW_INTENSITY = 0.7

# Visual effects
WALL_PULSE_SPEED = 1.5
WALL_GLOW_INTENSITY = 0.5
FOG_FADE_SPEED = 2.0
PARTICLE_COUNT = 15  # Reduced for better performance
PARTICLE_LIFETIME = 0.8

# Game states
STATE_TITLE = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_WIN = 3
STATE_PAUSED = 4
STATE_MENU = 10
STATE_HOW_TO_PLAY = 11

# Key bindings
MOVE_UP = pygame.K_w, pygame.K_UP
MOVE_DOWN = pygame.K_s, pygame.K_DOWN
MOVE_LEFT = pygame.K_a, pygame.K_LEFT
MOVE_RIGHT = pygame.K_d, pygame.K_RIGHT
PAUSE_KEY = pygame.K_p
RESTART_KEY = pygame.K_r

# Animation timings
TRANSITION_DURATION = 0.3
EFFECT_DURATION = 0.5
PULSE_DURATION = 1.0

# Storm settings
STORM_MIN_INTERVAL = 8  # seconds
STORM_MAX_INTERVAL = 15
STORM_DURATION = 8  # seconds
