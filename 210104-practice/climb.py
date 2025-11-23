import pygame as pg
import random
import sys

# --- 初始化 ---
pg.init()
WIDTH, HEIGHT = 400, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
FPS = 60

# --- 顏色 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
BLUE = (0, 100, 255)
GREEN = (34, 139, 34)

# --- 玩家設定 ---
player_radius = 12
player_x = WIDTH // 2
player_y = HEIGHT - 100
player_vx = 0
player_vy = 0
MOVE_SPEED = 5
JUMP_SPEED = -12
GRAVITY = 0.5

# --- 岩點設定 ---
platforms = []
PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 15

# --- 地面平台 ---
ground = pg.Rect(0, HEIGHT - 20, WIDTH, 20)
platforms.append(ground)

# --- 生成初始岩點 ---
for i in range(7):
    x = random.randint(0, WIDTH - PLATFORM_WIDTH)
    y = HEIGHT - 100 - i * 80
    platforms.append(pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT))

# --- 遊戲主循環 ---
running = True
while running:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # --- 玩家控制 ---
    keys = pg.key.get_pressed()
    player_vx = 0
    if keys[pg.K_LEFT]:
        player_vx = -MOVE_SPEED
    if keys[pg.K_RIGHT]:
        player_vx = MOVE_SPEED
    if keys[pg.K_SPACE]:
        # 只有在站在岩點上才可以跳
        for plat in platforms:
            if plat.collidepoint(player_x, player_y + player_radius + 1):
                player_vy = JUMP_SPEED
                break

    # --- 水平移動與左右碰撞 ---
    player_x += player_vx
    player_rect = pg.Rect(player_x - player_radius, player_y - player_radius, player_radius*2, player_radius*2)
    for plat in platforms:
        if player_rect.colliderect(plat):
            if player_vx > 0:
                player_x = plat.left - player_radius*2
            elif player_vx < 0:
                player_x = plat.right

    # --- 垂直移動與上下碰撞 ---
    player_vy += GRAVITY
    player_y += player_vy
    player_rect = pg.Rect(player_x - player_radius, player_y - player_radius, player_radius*2, player_radius*2)
    for plat in platforms:
        if player_rect.colliderect(plat):
            if player_vy > 0:  # 往下落
                player_y = plat.top - player_radius
                player_vy = 0
            elif player_vy < 0:  # 往上跳
                player_y = plat.bottom + player_radius
                player_vy = 0

    # --- 地圖向上滾動 ---
    if player_y < HEIGHT // 3:
        scroll = HEIGHT // 3 - player_y
        player_y = HEIGHT // 3
        for i in range(len(platforms)):
            platforms[i].y += scroll
        # 生成新的岩點
        while platforms[-1].y > 0:
            x = random.randint(0, WIDTH - PLATFORM_WIDTH)
            y = platforms[-1].y - random.randint(60, 120)
            platforms.append(pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT))

    # --- 移除掉出畫面的岩點（不移除地面）---
    platforms = [plat for plat in platforms if plat.y < HEIGHT or plat == ground]

    # --- 邊界檢查 ---
    if player_x - player_radius < 0:
        player_x = player_radius
    if player_x + player_radius > WIDTH:
        player_x = WIDTH - player_radius

    # --- 畫面繪製 ---
    screen.fill(BLACK)
    for plat in platforms:
        color = GREEN if plat == ground else BROWN
        pg.draw.rect(screen, color, plat)
    pg.draw.circle(screen, BLUE, (int(player_x), int(player_y)), player_radius)
    pg.display.flip()

pg.quit()
sys.exit()
