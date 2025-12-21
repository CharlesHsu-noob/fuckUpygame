import pygame as pg
import sys
import os

# --- 初始化 ---
pg.init()
WIDTH, HEIGHT = 1920, 1080
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
FPS = 60

# --- 顏色 ---
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (0, 100, 255)

# --- 玩家圖片 ---
player_img = pg.image.load(os.path.join("picture", "stand.png")).convert_alpha()
SCALE_FACTOR = 4.8  # 從 400x600 -> 1920x1080 的比例

PLAYER_WIDTH = int(48 * SCALE_FACTOR)
PLAYER_HEIGHT = int(64 * SCALE_FACTOR)
player_img = pg.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))

# --- 玩家設定 ---
player_x = WIDTH // 2
player_y = HEIGHT - int(150 * SCALE_FACTOR)
player_vx = 0
player_vy = 0
MOVE_SPEED = 2 * SCALE_FACTOR
JUMP_SPEED = -11 * SCALE_FACTOR
GRAVITY = 0.6 * SCALE_FACTOR

# 跳躍控制
jump_pressed = False
COYOTE_TIME = 0.12  # 土狼時間，0.12秒
time_since_ground = 0  # 離開平台時間

# --- 平台設定 ---
PLATFORM_WIDTH = int(80 * SCALE_FACTOR)
PLATFORM_HEIGHT = int(15 * SCALE_FACTOR)

platform_positions = [
    (0, 580*SCALE_FACTOR),(80*SCALE_FACTOR, 580*SCALE_FACTOR),(160*SCALE_FACTOR, 580*SCALE_FACTOR),
    (240*SCALE_FACTOR, 580*SCALE_FACTOR),(320*SCALE_FACTOR, 580*SCALE_FACTOR),(400*SCALE_FACTOR, 580*SCALE_FACTOR),  # 地面
    (50*SCALE_FACTOR, 490*SCALE_FACTOR),
    (350*SCALE_FACTOR, 490*SCALE_FACTOR),
    (200*SCALE_FACTOR, 420*SCALE_FACTOR),
    (120*SCALE_FACTOR, 360*SCALE_FACTOR),
    (20*SCALE_FACTOR, 270*SCALE_FACTOR),
    (150*SCALE_FACTOR, 180*SCALE_FACTOR),
    (300*SCALE_FACTOR, 180*SCALE_FACTOR),
    (200*SCALE_FACTOR, 90*SCALE_FACTOR),
    (150*SCALE_FACTOR, 0),
    (50*SCALE_FACTOR, -80*SCALE_FACTOR),
    (120*SCALE_FACTOR, -160*SCALE_FACTOR),
    (260*SCALE_FACTOR, -230*SCALE_FACTOR),
    (300*SCALE_FACTOR, -300*SCALE_FACTOR),
]

platforms = [pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT) for x, y in platform_positions]
ground = platforms[:6]  # 前 6 個是地面

# --- 載入圖片 ---
rock_img = pg.image.load(os.path.join("picture", "forest_rock.png")).convert_alpha()
rock_img = pg.transform.scale(rock_img, (PLATFORM_WIDTH, PLATFORM_HEIGHT))

# --- 判斷角色是否站在平台上 ---
def is_on_platform(px, py):
    feet_y = py 
    for plat in platforms:
        if plat.collidepoint(px, feet_y):
            return True
    return False

# --- 捲動設定 ---
SCROLL_UP_TRIGGER_Y = HEIGHT * 0.35
SCROLL_DOWN_TRIGGER_Y = HEIGHT * 0.60
scroll_offset = 0

# --- 遊戲主循環 ---
running = True
while running:
    dt = clock.tick(FPS) / 1000  # delta time，秒
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYUP and event.key == pg.K_SPACE:
            jump_pressed = False

    # --- 控制 ---
    keys = pg.key.get_pressed()
    player_vx = 0
    if keys[pg.K_LEFT]:
        player_vx = -MOVE_SPEED
    if keys[pg.K_RIGHT]:
        player_vx = MOVE_SPEED

    # --- 土狼時間判定 ---
    if is_on_platform(player_x, player_y):
        time_since_ground = 0
    else:
        time_since_ground += dt

    # --- 跳躍 ---
    if keys[pg.K_SPACE] and not jump_pressed and time_since_ground <= COYOTE_TIME:
        player_vy = JUMP_SPEED
        jump_pressed = True

    # --- 水平移動 ---
    player_x += player_vx

    player_rect = pg.Rect(
        player_x - PLAYER_WIDTH // 2,
        player_y - PLAYER_HEIGHT,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )

    for plat in platforms:
        if player_rect.colliderect(plat):
            if player_vx > 0:
                player_x = plat.left - PLAYER_WIDTH // 2
            elif player_vx < 0:
                player_x = plat.right + PLAYER_WIDTH // 2

    # --- 垂直移動 ---
    player_vy += GRAVITY
    player_y += player_vy

    player_rect = pg.Rect(
        player_x - PLAYER_WIDTH // 2,
        player_y - PLAYER_HEIGHT,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )

    for plat in platforms:
        if player_rect.colliderect(plat):
            if player_vy > 0:  # 往下掉，踩到平台
                player_y = plat.top
                player_vy = 0
                time_since_ground = 0 # 落地後重置土狼時間
            elif player_vy < 0:
                player_y = plat.bottom + PLAYER_HEIGHT
                player_vy = 0

    # --- 邊界 ---
    player_x = max(
        PLAYER_WIDTH // 2,
        min(WIDTH - PLAYER_WIDTH // 2, player_x)
    )

    # --- 捲動（往上） ---
    if player_y < SCROLL_UP_TRIGGER_Y and player_vy < 0:
        scroll_amount = SCROLL_UP_TRIGGER_Y - player_y
        player_y += scroll_amount
        scroll_offset += scroll_amount
        for plat in platforms:
            plat.y += scroll_amount

    # --- 捲動（往下） ---
    if player_y > SCROLL_DOWN_TRIGGER_Y and player_vy > 0:
        scroll_amount = player_y - SCROLL_DOWN_TRIGGER_Y
        lowest_ground_y = 580 * SCALE_FACTOR
        if platforms[0].y - scroll_amount < lowest_ground_y:
            scroll_amount = platforms[0].y - lowest_ground_y
        player_y -= scroll_amount
        for plat in platforms:
            plat.y -= scroll_amount
        scroll_offset -= scroll_amount

    # --- 繪製 ---
    screen.fill(BLACK)
    for plat in platforms:
        if plat in ground:
            pg.draw.rect(screen, GREEN, plat)
        else:
            screen.blit(rock_img, (plat.x, plat.y))
    screen.blit(
        player_img,
        (player_x - PLAYER_WIDTH // 2, player_y - PLAYER_HEIGHT)
    )

    pg.display.flip()

pg.quit()
