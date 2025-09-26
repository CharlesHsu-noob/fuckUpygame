import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("球")
pressed_keys = []

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

x, y = WIDTH // 2, HEIGHT // 2
size = 10
speed = 5
friction = 0.6

vx, vy = 0, 0

font = pygame.font.Font(None, 30)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                if event.key not in pressed_keys:
                    pressed_keys.append(event.key)
        elif event.type == pygame.KEYUP:
            if event.key in pressed_keys:
                pressed_keys.remove(event.key)

    if pressed_keys:
        key = pressed_keys[-1] 
        if key == pygame.K_w:
            vx, vy = 0, -speed
        elif key == pygame.K_s:
            vx, vy = 0, speed
        elif key == pygame.K_a:
            vx, vy = -speed, 0
        elif key == pygame.K_d:
            vx, vy = speed, 0
    else:
        vx *= friction
        vy *= friction

    x += vx
    y += vy

    # 邊界檢查
    if x - size < 0:
        x = size
        vx = 0
    if x + size > WIDTH:
        x = WIDTH - size
        vx = 0
    if y - size < 0:
        y = size
        vy = 0
    if y + size > HEIGHT:
        y = HEIGHT - size
        vy = 0

    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (int(x), int(y)), size)

    display_keys = [pygame.key.name(k) for k in pressed_keys]  
    keys_text = font.render(f"Pressed keys: {display_keys}", True, BLACK)
    screen.blit(keys_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)
