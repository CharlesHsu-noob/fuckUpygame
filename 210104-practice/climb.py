import pygame as pg
import sys
import os

# --- 初始化 ---
pg.init()
WIDTH, HEIGHT = 400, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
FPS = 60

# --- 顏色 ---
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (0, 100, 255)

# --- 玩家設定 ---
player_radius = 12
player_x = WIDTH // 2
player_y = HEIGHT - 150
player_vx = 0
player_vy = 0
MOVE_SPEED = 3
JUMP_SPEED = -12
GRAVITY = 0.5

# 跳躍控制
jump_pressed = False
COYOTE_TIME = 0.12  # 土狼時間，0.12秒
time_since_ground = 0  # 離開平台時間

# --- 平台設定 ---
PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 15

platform_positions = [
    (0, 580),(80, 580),(160, 580),(240, 580),(320, 580),(400, 580),  # 地面
    (50, 470),
    (350, 470),
    (200, 400),
    (120, 290),
    (20, 220),
    (150, 150),
    (300, 100),
    (200, 0),
    (150, -50),
    (0, -120),
    (120, -230),
    (260, -300),
    (300, -380),
]

platforms = [pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT) for x, y in platform_positions]
ground = platforms[:6]  # 前 6 個是地面

# --- 載入圖片 ---
rock_img = pg.image.load(os.path.join("picture", "forest_rock.png")).convert_alpha()
rock_img = pg.transform.scale(rock_img, (PLATFORM_WIDTH, PLATFORM_HEIGHT))

# --- 判斷角色是否站在平台上 ---
def is_on_platform(px, py):
    feet_y = py + player_radius + 3
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
    player_rect = pg.Rect(player_x - player_radius, player_y - player_radius,
                          player_radius * 2, player_radius * 2)

    for plat in platforms:
        if player_rect.colliderect(plat):
            if player_vx > 0:
                player_x = plat.left - player_radius * 2
            elif player_vx < 0:
                player_x = plat.right

    # --- 垂直移動 ---
    player_vy += GRAVITY
    player_y += player_vy
    player_rect = pg.Rect(player_x - player_radius, player_y - player_radius,
                          player_radius*2, player_radius*2)

    for plat in platforms:
        if player_rect.colliderect(plat):
            if player_vy > 0:
                player_y = plat.top - player_radius
                player_vy = 0
                time_since_ground = 0  # 落地後重置土狼時間
            elif player_vy < 0:
                player_y = plat.bottom + player_radius
                player_vy = 0

    # --- 邊界 ---
    if player_x - player_radius < 0:
        player_x = player_radius
    if player_x + player_radius > WIDTH:
        player_x = WIDTH - player_radius

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
        lowest_ground_y = 580
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
    pg.draw.circle(screen, BLUE, (int(player_x), int(player_y)), player_radius)

    pg.display.flip()

pg.quit()
sys.exit()
