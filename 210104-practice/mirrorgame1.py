import pygame as pg
import sys
import os

# ================= 初始化 =================
pg.init()

# --- 世界大小（邏輯用，不變） ---
WORLD_WIDTH, WORLD_HEIGHT = 400, 600

# --- 實際視窗大小 ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080
screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Climbing Game")

clock = pg.time.Clock()
FPS = 60

# --- 虛擬畫面（所有遊戲內容畫在這） ---
world_surface = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT))

# --- 等比例縮放計算 ---
scale_x = WINDOW_WIDTH / WORLD_WIDTH
scale_y = WINDOW_HEIGHT / WORLD_HEIGHT
SCALE = min(scale_x, scale_y)

scaled_width = int(WORLD_WIDTH * SCALE)
scaled_height = int(WORLD_HEIGHT * SCALE)
offset_x = (WINDOW_WIDTH - scaled_width) // 2
offset_y = (WINDOW_HEIGHT - scaled_height) // 2

# ================= 顏色 =================
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (0, 100, 255)

# ================= 玩家圖片 =================
player_img = pg.image.load(os.path.join("picture", "stand.png")).convert_alpha()
PLAYER_WIDTH = 48
PLAYER_HEIGHT = 64
player_img = pg.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))

# ================= 玩家設定 =================
player_x = WORLD_WIDTH
player_y = WORLD_HEIGHT
player_vx = 0
player_vy = 0

MOVE_SPEED = 2
JUMP_SPEED = -11
GRAVITY = 0.6

# 跳躍控制
jump_pressed = False
COYOTE_TIME = 0.12
time_since_ground = 0

# ================= 平台設定 =================
PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 15

platform_positions = [
    (0, 580),(80, 580),(160, 580),(240, 580),(320, 580),(400, 580),
    (50, 490),(350, 490),(200, 420),(120, 360),(20, 270),
    (150, 180),(300, 180),(200, 90),(150, 0),
    (50, -80),(120, -160),(260, -230),(300, -300),
]

platforms = [pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT) for x, y in platform_positions]
ground = platforms[:6]

rock_img = pg.image.load(os.path.join("picture", "forest_rock.png")).convert_alpha()
rock_img = pg.transform.scale(rock_img, (PLATFORM_WIDTH, PLATFORM_HEIGHT))

# ================= 判斷是否站在平台 =================
def is_on_platform(px, py):
    for plat in platforms:
        if plat.collidepoint(px, py):
            return True
    return False

# ================= 捲動設定 =================
SCROLL_UP_TRIGGER_Y = WORLD_HEIGHT * 0.35
SCROLL_DOWN_TRIGGER_Y = WORLD_HEIGHT * 0.60

# ================= 遊戲主迴圈 =================
running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYUP and event.key == pg.K_SPACE:
            jump_pressed = False

    # ---------- 操作 ----------
    keys = pg.key.get_pressed()
    player_vx = 0
    if keys[pg.K_LEFT]:
        player_vx = -MOVE_SPEED
    if keys[pg.K_RIGHT]:
        player_vx = MOVE_SPEED

    # ---------- 土狼時間 ----------
    if is_on_platform(player_x, player_y):
        time_since_ground = 0
    else:
        time_since_ground += dt

    # ---------- 跳躍 ----------
    if keys[pg.K_SPACE] and not jump_pressed and time_since_ground <= COYOTE_TIME:
        player_vy = JUMP_SPEED
        jump_pressed = True

    # ---------- 水平移動 ----------
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

    # ---------- 垂直移動 ----------
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
            if player_vy > 0:
                player_y = plat.top
                player_vy = 0
                time_since_ground = 0
            elif player_vy < 0:
                player_y = plat.bottom + PLAYER_HEIGHT
                player_vy = 0

    # ---------- 邊界 ----------
    player_x = max(
        PLAYER_WIDTH // 2,
        min(WORLD_WIDTH - PLAYER_WIDTH // 2, player_x)
    )

    # ---------- 向上捲動 ----------
    if player_y < SCROLL_UP_TRIGGER_Y and player_vy < 0:
        scroll = SCROLL_UP_TRIGGER_Y - player_y
        player_y += scroll
        for plat in platforms:
            plat.y += scroll

    # ---------- 向下捲動（有限速版） ----------
    if player_y > SCROLL_DOWN_TRIGGER_Y and player_vy > 0:
        raw_scroll = player_y - SCROLL_DOWN_TRIGGER_Y

        # 限制每幀最大捲動量，避免瞬移
        MAX_SCROLL = 6
        scroll = min(raw_scroll, MAX_SCROLL)

        # 避免把地面拉過頭
        lowest_ground_y = 485
        if platforms[0].y - scroll < lowest_ground_y:
            scroll = platforms[0].y - lowest_ground_y

        if scroll > 0:
            player_y -= scroll
            for plat in platforms:
                plat.y -= scroll

    # ================= 繪製（畫在 world_surface） =================
    world_surface.fill(BLACK)

    for plat in platforms:
        if plat in ground:
            pg.draw.rect(world_surface, GREEN, plat)
        else:
            world_surface.blit(rock_img, plat.topleft)

    world_surface.blit(
        player_img,
        (player_x - PLAYER_WIDTH // 2, player_y - PLAYER_HEIGHT)
    )

    # ================= 縮放顯示 =================
    scaled_surface = pg.transform.smoothscale(
        world_surface,
        (scaled_width, scaled_height)
    )

    screen.fill(BLACK)
    screen.blit(scaled_surface, (offset_x, offset_y))
    pg.display.flip()

pg.quit()
sys.exit()
