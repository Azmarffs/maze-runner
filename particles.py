import pygame
import random
import math
from config import PARTICLE_COLORS

class Particle:
    def __init__(self, x, y, lifetime):
        self.x = x
        self.y = y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = random.choice(PARTICLE_COLORS)
        self.speed = random.uniform(50, 150)
        self.angle = random.uniform(0, 2 * math.pi)
        self.size = random.uniform(2, 4)
        self.alpha = 255  # Initialize alpha value
        
        # Calculate velocity components
        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed
        
        # Add some gravity effect
        self.gravity = random.uniform(50, 100)
    
    def update(self, dt):
        self.lifetime -= dt
        self.vy += self.gravity * dt
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Fade out based on lifetime
        self.alpha = int((self.lifetime / self.max_lifetime) * 255)
    
    def draw(self, screen):
        if self.lifetime <= 0:
            return
        
        # Create surface for particle with alpha
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), 
                                        pygame.SRCALPHA)
        
        # Draw particle with fade
        color_with_alpha = (*self.color, self.alpha)
        pygame.draw.circle(particle_surface, color_with_alpha,
                         (int(self.size), int(self.size)), self.size)
        
        # Draw glow effect
        glow_size = self.size * 2
        glow_surface = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), 
                                    pygame.SRCALPHA)
        glow_alpha = int(self.alpha * 0.5)
        pygame.draw.circle(glow_surface, (*self.color, glow_alpha),
                         (int(glow_size), int(glow_size)), glow_size)
        
        # Blit both surfaces to screen
        screen.blit(glow_surface, 
                   (int(self.x - glow_size), int(self.y - glow_size)))
        screen.blit(particle_surface, 
                   (int(self.x - self.size), int(self.y - self.size)))

class ParticleSystem:
    def __init__(self, x, y, count, lifetime):
        self.particles = []
        for _ in range(count):
            self.particles.append(Particle(x, y, lifetime))
    
    def update(self, dt):
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
    
    def is_finished(self):
        return len(self.particles) == 0