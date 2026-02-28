import pygame
import random
import math
import os
import sys

def get_resource_path(relative_path):
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
orb_folder = get_resource_path("assets")

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

balls = []
cube = None

spawn_count = 0
CUBE_DROP_INDEX = random.randint(35, 45)

last_spawn = pygame.time.get_ticks()
next_spawn_delay = random.randint(0, 2000)

held_ball = None
prev_mouse_pos = (0, 0)


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
        self.color = (
            random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255),
        )

        if USE_IMAGES:
            self.orb_image = random.choice(orb_images)
            self.base_image = pygame.transform.smoothscale(
                self.orb_image, (r * 2, r * 2)
            )
        else:
            self.base_image = None

    def update(self):
        if self.held:
            return

        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        if abs(self.vx) > 0.5:
            self.angular_velocity = -self.vx / self.r * 0.5
        else:
            self.angular_velocity *= 0.9

        if abs(self.angular_velocity) > 0.15:
            self.angular_velocity = 0.15 if self.angular_velocity > 0 else -0.15

        if abs(self.angular_velocity) < 0.01:
            self.angular_velocity = 0

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
            if abs(self.vy) < 0.4:
                self.vy = 0
            self.vx *= 0.98

    def draw(self):
        if USE_IMAGES and self.base_image:
            rotated_image = pygame.transform.rotozoom(
                self.base_image,
                math.degrees(self.angle),
                1.0
            )
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, rect)
        else:
            pygame.draw.circle(
                screen, self.color, (int(self.x), int(self.y)), self.r
            )


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
            self.base_image = pygame.transform.smoothscale(
                cube_image, (size, size)
            )
        else:
            self.base_image = None

    def update(self):
        if self.held:
            return

        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        if abs(self.vx) > 0.5:
            self.angular_velocity = -self.vx / self.r * 0.5
        else:
            self.angular_velocity *= 0.9

        if abs(self.angular_velocity) > 0.15:
            self.angular_velocity = 0.15 if self.angular_velocity > 0 else -0.15

        if abs(self.angular_velocity) < 0.01:
            self.angular_velocity = 0

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
            if abs(self.vy) < 0.4:
                self.vy = 0
            self.vx *= 0.98

    def draw(self):
        if self.base_image:
            rotated_image = pygame.transform.rotozoom(
                self.base_image,
                math.degrees(self.angle),
                1.0
            )
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, rect)
        else:
            half = self.size // 2
            points = [
                (self.x - half, self.y - half),
                (self.x + half, self.y - half),
                (self.x + half, self.y + half),
                (self.x - half, self.y + half)
            ]
            pygame.draw.polygon(screen, self.color, points)


def resolve_collision(a, b):
    if a.held or b.held:
        return

    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)
    min_dist = a.r + b.r

    if dist == 0:
        angle = random.random() * 2 * math.pi
        dx = math.cos(angle)
        dy = math.sin(angle)
        dist = 0.1

    if dist >= min_dist:
        return

    overlap = (min_dist - dist) * 0.5
    nx
