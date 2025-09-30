import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("雙球")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)   
RED = (255, 0, 0)   
BLACK = (0, 0, 0)

# WASD
x1, y1 = 200, 300
vx1, vy1 = 0, 0
size1 = 15
speed1 = 5
friction = 0.6
pressed_keys = []

# 反彈 + 追蹤
x2, y2 = 600, 300
size2 = 20
follow_accel = 0.005  # 追蹤a
max_speed = 10    # MAX V
vx2, vy2 = max_speed, max_speed

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

    # WASD
    if pressed_keys:
        key = pressed_keys[-1]
        if key == pygame.K_w:
            vx1, vy1 = 0, -speed1
        elif key == pygame.K_s:
            vx1, vy1 = 0, speed1
        elif key == pygame.K_a:
            vx1, vy1 = -speed1, 0
        elif key == pygame.K_d:
            vx1, vy1 = speed1, 0
    else:
        vx1 *= friction
        vy1 *= friction

    x1 += vx1
    y1 += vy1

    if x1 - size1 < 0:
        x1 = size1
        vx1 = 0
    if x1 + size1 > WIDTH:
        x1 = WIDTH - size1
        vx1 = 0
    if y1 - size1 < 0:
        y1 = size1
        vy1 = 0
    if y1 + size1 > HEIGHT:
        y1 = HEIGHT - size1
        vy1 = 0

    # 向量
    dx = x1 - x2
    dy = y1 - y2

    vx2 += dx * follow_accel
    vy2 += dy * follow_accel

    # limit V
    speed = (vx2**2 + vy2**2)**0.5
    if speed > max_speed:
        factor = max_speed / speed
        vx2 *= factor
        vy2 *= factor

    x2 += vx2
    y2 += vy2

    if x2 - size2 < 0 or x2 + size2 > WIDTH:
        vx2 = -vx2
    if y2 - size2 < 0 or y2 + size2 > HEIGHT:
        vy2 = -vy2

    # 畫面更新
    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (int(x1), int(y1)), size1)
    pygame.draw.circle(screen, RED, (int(x2), int(y2)), size2)

    display_keys = [pygame.key.name(k) for k in pressed_keys]
    keys_text = font.render(f"Pressed keys: {display_keys}", True, BLACK)
    screen.blit(keys_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)
