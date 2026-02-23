import sys
import pygame
import random
import math
import os

# --- PYINSTALLER PATH FIX ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Pit")
clock = pygame.time.Clock()

GRAVITY = 0.6
BOUNCE = 0.35
MIN_RADIUS = 35
MAX_RADIUS = 70
MAX_BALLS = 50
COVERAGE_THRESHOLD = 0.85

CUBE_SPAWNED = False
orb_images = []

# --- LOAD ASSETS FROM FOLDER ---
orb_folder = resource_path("assets")

if os.path.exists(orb_folder):
    for filename in os.listdir(orb_folder):
        if filename.endswith(".png") and filename != "cube.png":
            img_path = os.path.join(orb_folder, filename)
            try:
                img = pygame.image.load(img_path).convert_alpha()
                orb_images.append(img)
            except:
                pass

cube_image = None
cube_path = os.path.join(orb_folder, "cube.png")
if os.path.exists(cube_path):
    try:
        cube_image = pygame.image.load(cube_path).convert_alpha()
    except:
        pass

USE_IMAGES = len(orb_images) > 0

class Ball:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r
        self.vx = 0
        self.vy = 0
        self.mass = r * r
        self.held = False
        self.angle = 0
        self.angular_velocity = 0
        self.color = (random.randint(80, 255), random.randint(80, 255), random.randint(80, 255))

        if USE_IMAGES:
            self.orb_image = random.choice(orb_images)
            self.base_image = pygame.transform.smoothscale(self.orb_image, (r * 2, r * 2))
        else:
            self.base_image = None

    def update(self):
        if self.held: return
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        if abs(self.vx) > 0.5:
            self.angular_velocity = -self.vx / self.r * 0.5
        else:
            self.angular_velocity *= 0.9
        self.angle += self.angular_velocity
        if self.x - self.r < 0:
            self.x = self.r
            self.vx *= -BOUNCE
        if self.x + self.r > WIDTH:
            self.x = WIDTH - self.r
            self.vx *= -BOUNCE
        if self.y + self.r > HEIGHT:
            self.y = HEIGHT - self.r
            self.vy *= -BOUNCE
            if abs(self.vy) < 0.4: self.vy = 0
            self.vx *= 0.98

    def draw(self):
        if USE_IMAGES and self.base_image:
            rotated_image = pygame.transform.rotozoom(self.base_image, math.degrees(self.angle), 1.0)
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.r)

class Cube:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.r = size / 2
        self.vx = 0
        self.vy = 0
        self.mass = MIN_RADIUS * MIN_RADIUS
        self.held = False
        self.angle = 0
        self.angular_velocity = 0
        self.color = (255, 200, 50)
        if cube_image:
            self.base_image = pygame.transform.smoothscale(cube_image, (size, size))
        else:
            self.base_image = None

    def update(self):
        if self.held: return
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy
        if abs(self.vx) > 0.5:
            self.angular_velocity = -self.vx / self.r * 0.5
        else:
            self.angular_velocity *= 0.9
        self.angle += self.angular_velocity
        if self.x - self.r < 0:
            self.x = self.r
            self.vx *= -BOUNCE
        if self.x + self.r > WIDTH:
            self.x = WIDTH - self.r
            self.vx *= -BOUNCE
        if self.y + self.r > HEIGHT:
            self.y = HEIGHT - self.r
            self.vy *= -BOUNCE
            if abs(self.vy) < 0.4: self.vy = 0
            self.vx *= 0.98

    def draw(self):
        if self.base_image:
            rotated_image = pygame.transform.rotozoom(self.base_image, math.degrees(self.angle), 1.0)
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, rect)
        else:
            pygame.draw.rect(screen, self.color, (self.x-self.r, self.y-self.r, self.size, self.size))

def resolve_collision(a, b):
    if a.held or b.held: return
    dx, dy = b.x - a.x, b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = a.r + b.r
    if dist < min_dist:
        if dist == 0: dist, dx = 0.1, 0.1
        overlap = (min_dist - dist) * 0.5
        nx, ny = dx / dist, dy / dist
        a.x -= nx * overlap; a.y -= ny * overlap
        b.x += nx * overlap; b.y += ny * overlap
        vel_norm = (b.vx - a.vx) * nx + (b.vy - a.vy) * ny
        if vel_norm < 0:
            j = -(1 + BOUNCE) * vel_norm / (1/a.mass + 1/b.mass)
            a.vx -= (j * nx) / a.mass; a.vy -= (j * ny) / a.mass
            b.vx += (j * nx) / b.mass; b.vy += (j * ny) / b.mass

def is_screen_full():
    balls_area = sum(math.pi * b.r * b.r for b in balls)
    return (balls_area / (WIDTH * HEIGHT)) > COVERAGE_THRESHOLD or len(balls) >= MAX_BALLS

balls = []
cube = None
spawn_count = 0
CUBE_DROP_INDEX = random.randint(35, 45)
last_spawn = pygame.time.get_ticks()
next_spawn_delay = random.randint(0, 2000)
held_ball = None

running = True
while running:
    clock.tick(60)
    screen.fill((0, 0, 0))
    mx, my = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if cube and math.hypot(mx-cube.x, my-cube.y) <= cube.r:
                held_ball = cube
            else:
                for b in reversed(balls):
                    if math.hypot(mx-b.x, my-b.y) <= b.r:
                        held_ball = b; break
            if held_ball: held_ball.held = True
        if event.type == pygame.MOUSEBUTTONUP:
            if held_ball:
                held_ball.held = False
                held_ball.vx, held_ball.vy = pygame.mouse.get_rel()[0]*0.5, pygame.mouse.get_rel()[1]*0.5
                held_ball = None
    
    pygame.mouse.get_rel() # Reset relative motion

    if held_ball:
        held_ball.x, held_ball.y = mx, my
        held_ball.vx = held_ball.vy = 0

    if not is_screen_full() and pygame.time.get_ticks() - last_spawn > next_spawn_delay:
        spawn_count += 1
        new_ball = Ball(random.randint(100, WIDTH-100), -50, random.randint(MIN_RADIUS, MAX_RADIUS))
        balls.append(new_ball)
        if spawn_count == CUBE_DROP_INDEX and not cube:
            cube = Cube(WIDTH//2, -50, 80)
        last_spawn = pygame.time.get_ticks()
        next_spawn_delay = random.randint(500, 1500)

    if cube:
        cube.update(); cube.draw()
        for b in balls: resolve_collision(cube, b)
    for i, b1 in enumerate(balls):
        b1.update(); b1.draw()
        for b2 in balls[i+1:]: resolve_collision(b1, b2)

    pygame.display.flip()

pygame.quit()
