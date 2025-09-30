import pygame
import sys
import os
pygame.init()

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("顯示圖片")


water = pygame.image.load(os.path.join(base_dir, "picture", "pet", "water.png")).convert_alpha()
water = pygame.transform.scale(water, (200, 200))

fire = pygame.image.load(os.path.join(base_dir, "picture", "pet", "fire.png")).convert_alpha()
fire = pygame.transform.scale(fire, (240, 180))

seed = pygame.image.load(os.path.join(base_dir, "picture", "pet", "seed.png")).convert_alpha()
seed = pygame.transform.scale(seed, (200, 200))

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))
    screen.blit(water, (0, 0))
    screen.blit(fire, (0, 200))
    screen.blit(seed, (0, 400))
    
    pygame.display.flip()
    clock.tick(60)
