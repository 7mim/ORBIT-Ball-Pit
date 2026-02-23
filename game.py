import sys
import pygame
import random
import math
import os

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

orb_images = []
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
balls = []
cube = None
spawn_count = 0
CUBE_DROP_INDEX = random.randint(35, 45)
last_spawn = pygame.time.get_ticks()
next_spawn_delay = random.randint(0, 2000)
held_ball = None
prev_mouse_pos = (0, 0)


