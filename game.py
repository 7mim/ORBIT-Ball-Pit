import pygame
import random
import math
import os

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
orb_folder = "assets"

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
    nx = dx / dist
    ny = dy / dist

    total_mass = a.mass + b.mass
    a.x -= nx * overlap * (b.mass / total_mass)
    a.y -= ny * overlap * (b.mass / total_mass)
    b.x += nx * overlap * (a.mass / total_mass)
    b.y += ny * overlap * (a.mass / total_mass)

    rvx = b.vx - a.vx
    rvy = b.vy - a.vy
    vel_norm = rvx * nx + rvy * ny

    if vel_norm > 0:
        return

    j = -(1 + BOUNCE) * vel_norm
    j /= (1 / a.mass + 1 / b.mass)

    ix = j * nx
    iy = j * ny

    a.vx -= ix / a.mass
    a.vy -= iy / a.mass
    b.vx += ix / b.mass
    b.vy += iy / b.mass

    if abs(a.vx) < 0.01:
        a.vx = 0
    if abs(a.vy) < 0.01:
        a.vy = 0
    if abs(b.vx) < 0.01:
        b.vx = 0
    if abs(b.vy) < 0.01:
        b.vy = 0


def is_screen_full():
    total_area = WIDTH * HEIGHT
    balls_area = sum(math.pi * ball.r * ball.r for ball in balls)
    if cube:
        balls_area += math.pi * cube.r * cube.r
    coverage = balls_area / total_area
    return coverage > COVERAGE_THRESHOLD or len(balls) + (1 if cube else 0) >= MAX_BALLS


def reset_game():
    global balls, cube, last_spawn, next_spawn_delay, held_ball, CUBE_SPAWNED, spawn_count, CUBE_DROP_INDEX
    balls = []
    cube = None
    CUBE_SPAWNED = False
    spawn_count = 0
    CUBE_DROP_INDEX = random.randint(35, 45)
    last_spawn = pygame.time.get_ticks()
    next_spawn_delay = random.randint(0, 2000)
    held_ball = None


running = True
while running:
    clock.tick(60)
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if cube and (mx - cube.x) ** 2 + (my - cube.y) ** 2 <= cube.r ** 2:
                held_ball = cube
                cube.held = True
                cube.vx = cube.vy = 0
                prev_mouse_pos = (mx, my)

            if not held_ball:
                for ball in reversed(balls):
                    if (mx - ball.x) ** 2 + (my - ball.y) ** 2 <= ball.r ** 2:
                        held_ball = ball
                        ball.held = True
                        ball.vx = ball.vy = 0
                        prev_mouse_pos = (mx, my)
                        break

        if event.type == pygame.MOUSEBUTTONUP and held_ball:
            mx, my = pygame.mouse.get_pos()
            dx = mx - prev_mouse_pos[0]
            dy = my - prev_mouse_pos[1]
            held_ball.vx = dx
            held_ball.vy = dy
            held_ball.held = False
            held_ball = None

    if held_ball:
        mx, my = pygame.mouse.get_pos()
        held_ball.x = mx
        held_ball.y = my
        prev_mouse_pos = (mx, my)

    if not is_screen_full():
        now = pygame.time.get_ticks()
        if now - last_spawn >= next_spawn_delay:
            spawn_count += 1
            if spawn_count == CUBE_DROP_INDEX and not CUBE_SPAWNED:
                size = MIN_RADIUS * 2
                x = random.randint(size // 2, WIDTH - size // 2)
                cube = Cube(x, -size // 2, size)
                CUBE_SPAWNED = True
            else:
                r = random.randint(MIN_RADIUS, MAX_RADIUS)
                x = random.randint(r, WIDTH - r)
                balls.append(Ball(x, -r, r))

            last_spawn = now
            next_spawn_delay = random.randint(0, 2000)

    for ball in balls:
        ball.update()
    if cube:
        cube.update()

    all_objects = balls + ([cube] if cube else [])
    for _ in range(3):
        for i in range(len(all_objects)):
            for j in range(i + 1, len(all_objects)):
                resolve_collision(all_objects[i], all_objects[j])

    for ball in balls:
        ball.draw()
    if cube:
        cube.draw()

    pygame.display.flip()

pygame.quit()
