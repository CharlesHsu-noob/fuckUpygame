import pygame as pg
import sys, os

# ================= 初始化 =================
pg.init()

# --- 世界大小 ---
WORLD_WIDTH, WORLD_HEIGHT = 400, 600

# --- 視窗 ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080
screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Climbing Game")

clock = pg.time.Clock()
FPS = 60

# --- 世界畫面 ---
world_surface = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT))

# --- 等比例縮放 ---
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

# ================= 背景 =================
bg_img_raw = pg.image.load(os.path.join("picture", "forest_e.png")).convert()
bg_img_full = pg.transform.scale(bg_img_raw, (2000, 3500))  # 原尺寸，不縮放到視窗

# ================= Camera =================
camera_y = 0
CAMERA_ANCHOR_Y = WORLD_HEIGHT * 0.4
CAMERA_LERP = 0.15

# ================= 玩家 =================
player_img = pg.image.load(os.path.join("picture", "stand.png")).convert_alpha()
player_img = pg.transform.scale(player_img, (48, 64))
PLAYER_WIDTH = 16
PLAYER_HEIGHT = 64
player_x = WORLD_WIDTH - 100
player_y = WORLD_HEIGHT
player_vx = 0
player_vy = 0
MOVE_SPEED = 2
JUMP_SPEED = -11
GRAVITY = 0.6
jump_pressed = False
COYOTE_TIME = 0.12
time_since_ground = 0
JUMP_COOLDOWN = 750
last_jump_time = -750

# ================= 平台 =================
PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 15
platform_positions = [
    (0, 580),(80, 580),(160, 580),(240, 580),(320, 580),(400, 580),
    (50, 490),(350, 490),(200, 440),(120, 360),(20, 270),
    (150, 180),(300, 180),(200, 90),(150, 0),
    (50, -80),(120, -160),(260, -230),(300, -300),
]
platforms = [pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT) for x, y in platform_positions]
ground = platforms[:6]
rock_img = pg.image.load(os.path.join("picture", "forest_rock.png")).convert_alpha()
rock_img = pg.transform.scale(rock_img, (PLATFORM_WIDTH, PLATFORM_HEIGHT))

# ================= 判斷是否站在平台 =================
def is_on_platform(px, py):
    rect = pg.Rect(px - PLAYER_WIDTH//2, py - PLAYER_HEIGHT,
                   PLAYER_WIDTH, PLAYER_HEIGHT)
    return any(rect.colliderect(p) for p in platforms)

# ================= 遊戲主迴圈 =================
running = True
while running:
    dt = clock.tick(FPS) / 1000
    now = pg.time.get_ticks()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYUP and event.key == pg.K_SPACE:
            jump_pressed = False

    # ---------- 玩家操作 ----------
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
        if now - last_jump_time > JUMP_COOLDOWN:
            player_vy = JUMP_SPEED
            jump_pressed = True
            time_since_ground = COYOTE_TIME + 1
            last_jump_time = now

    # ---------- 水平移動 ----------
    player_x += player_vx
    rect = pg.Rect(player_x - PLAYER_WIDTH//2, player_y - PLAYER_HEIGHT,
                   PLAYER_WIDTH, PLAYER_HEIGHT)
    for p in platforms:
        if rect.colliderect(p):
            if player_vx > 0:
                player_x = p.left - PLAYER_WIDTH//2
            elif player_vx < 0:
                player_x = p.right + PLAYER_WIDTH//2

    # ---------- 垂直移動 ----------
    player_vy += GRAVITY
    player_y += player_vy
    rect = pg.Rect(player_x - PLAYER_WIDTH//2, player_y - PLAYER_HEIGHT,
                   PLAYER_WIDTH, PLAYER_HEIGHT)
    for p in platforms:
        if rect.colliderect(p):
            if player_vy > 0:
                player_y = p.top
                player_vy = 0
                time_since_ground = 0
            elif player_vy < 0:
                player_y = p.bottom + PLAYER_HEIGHT
                player_vy = 0

    # ---------- 邊界 ----------
    player_x = max(PLAYER_WIDTH//2,
                   min(WORLD_WIDTH - PLAYER_WIDTH//2, player_x))

    # ---------- Camera 平滑跟隨 ----------
    camera_target_y = player_y - CAMERA_ANCHOR_Y
    camera_y += (camera_target_y - camera_y) * CAMERA_LERP
    camera_y = round(camera_y)

    # ================= 繪製世界 =================
    world_surface.fill(BLACK)

    # 中景背景（世界層視差）
    bg_world_speed = 0.6
    bg_world_y = -camera_y * bg_world_speed
    y = bg_world_y
    while y < WORLD_HEIGHT:
        world_surface.blit(bg_img_full, (-800, y))
        y += 3500

    # 平台
    for p in platforms:
        draw = p.move(0, -camera_y)
        if p in ground:
            pg.draw.rect(world_surface, GREEN, draw)
        else:
            world_surface.blit(rock_img, draw.topleft)

    # 玩家
    world_surface.blit(player_img,
                       (player_x - PLAYER_WIDTH//2 - 15,
                        player_y - PLAYER_HEIGHT - camera_y + 5))

    # ================= 顯示 =================
    scaled_surface = pg.transform.smoothscale(world_surface,
                                              (scaled_width, scaled_height))

    # 遠景背景（前景視差）
    bg_far_speed = 0.3
    bg_far_y = -camera_y * bg_far_speed
    bg_x = (WINDOW_WIDTH - 2000) // 2
    y = bg_far_y
    while y < WINDOW_HEIGHT:
        screen.blit(bg_img_full, (bg_x, y))
        y += 3500

    # 畫世界
    screen.blit(scaled_surface, (offset_x, offset_y))
    pg.display.flip()

pg.quit()
sys.exit()
