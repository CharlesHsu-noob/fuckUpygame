import pygame as pg
import sys, os, json

# --- 初始化 pygame ---
pg.init()

# --- 路徑設定（跨平台相容）---
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)

# --- 視窗設定 ---
screeninfo = pg.display.Info()
w, h = screeninfo.current_w, screeninfo.current_h - 80  # 避免被工作列遮住
screen = pg.display.set_mode((w, h))
pg.display.set_caption("object_practice")

# --- 背景設定 ---
bg = pg.Surface(screen.get_size()).convert()
main_screen = pg.image.load(os.path.join(base_dir, "picture", "map.png")).convert_alpha()
mainMenuBg = pg.transform.scale(main_screen, (w, h))

# --- 載入角色圖片 ---
# 假設這三張圖原本「面向左邊」
walk_left = pg.image.load(os.path.join(base_dir, "picture", "leftfoot.png")).convert_alpha()
walk_stand = pg.image.load(os.path.join(base_dir, "picture", "stand.png")).convert_alpha()
walk_right = pg.image.load(os.path.join(base_dir, "picture", "rightfoot.png")).convert_alpha()

# --- 縮放角色大小（可依實際圖片調整）---
walk_left = pg.transform.scale(walk_left, (45, 75))
walk_stand = pg.transform.scale(walk_stand, (45, 75))
walk_right = pg.transform.scale(walk_right, (45, 75))

# --- 動畫順序：左 → 站 → 右 → 站 → 左 ---
walk_cycle = [walk_left, walk_stand, walk_right, walk_stand]

# --- 角色初始狀態 ---
frame_index = 0
frame_delay = 150  # 每幀延遲時間（毫秒）
last_update = pg.time.get_ticks()

player_x, player_y = w // 2 - 75, h // 2 - 125
player_speed = 1
facing_right = False  # 初始朝向左
is_walking = False

clock = pg.time.Clock()
running = True

# --- 主迴圈 ---
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    keys = pg.key.get_pressed()
    is_walking = False
    dx, dy = 0, 0

    # --- 移動控制 ---
    if keys[pg.K_RIGHT]:
        dx = player_speed
        facing_right = True
        is_walking = True
    elif keys[pg.K_LEFT]:
        dx = -player_speed
        facing_right = False
        is_walking = True
    if keys[pg.K_UP]:
        dy = -player_speed
        is_walking = True
    elif keys[pg.K_DOWN]:
        dy = player_speed
        is_walking = True

    player_x += dx
    player_y += dy

    # --- 邊界限制（防止走出螢幕）---
    player_x = max(0, min(player_x, w - 45))
    player_y = max(0, min(player_y, h - 75))

    # --- 動畫更新 ---
    now = pg.time.get_ticks()
    if is_walking:
        if now - last_update > frame_delay:
            frame_index = (frame_index + 1) % len(walk_cycle)
            last_update = now
    else:
        frame_index = 1  # 停止時顯示站姿

    current_image = walk_cycle[frame_index]

    # --- 根據方向翻轉圖片 ---
    # ⚠️ 假設圖片原本是「朝左」的，如果原圖是朝右，就把這個 if 改成 if not facing_right
    if facing_right:
        current_image = pg.transform.flip(current_image, True, False)

    # --- 畫面更新 ---
    screen.blit(mainMenuBg, (0, 0))
    screen.blit(current_image, (player_x, player_y))
    pg.display.flip()

    clock.tick(60)
# --- 結束程式 ---
pg.quit()
sys.exit()
