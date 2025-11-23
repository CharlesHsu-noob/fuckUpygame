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

# --- 角色圖片 ---
walk_left = pg.image.load(os.path.join(base_dir, "picture", "leftfoot.png")).convert_alpha()
walk_stand = pg.image.load(os.path.join(base_dir, "picture", "stand.png")).convert_alpha()
walk_right = pg.image.load(os.path.join(base_dir, "picture", "rightfoot.png")).convert_alpha()

walk_left = pg.transform.scale(walk_left, (45, 75))
walk_stand = pg.transform.scale(walk_stand, (45, 75))
walk_right = pg.transform.scale(walk_right, (45, 75))

walk_cycle = [walk_left, walk_stand, walk_right, walk_stand]

# --- 玩家初始 ---
frame_index = 0
frame_delay = 150
last_update = pg.time.get_ticks()

player_x, player_y = 625, 300
player_speed = 1
facing_right = False
is_walking = False

# --- 定義地圖外的碰撞牆（Rect）---
walls = [
    pg.Rect(0, 0, w, 3),          # 上邊界
    pg.Rect(0, h-10, w, 3),     # 下邊界
    pg.Rect(0, 0, 35, h),         # 左邊界
    pg.Rect(w-35, 0, 35, h),   # 右邊界

    # --- 地圖內部不可通行牆 ---
    pg.Rect(0, 268, 600, 107),     
    pg.Rect(525, 552, 780, 80),   
    pg.Rect(525, 500, 75, 120),       
    pg.Rect(1140, 210, 280, 420),
    pg.Rect(730, 290, 175, 100),    
    pg.Rect(905, 340, 250, 50),   
    pg.Rect(525, 0, 75, 145),  
    pg.Rect(600, 0, 105, 100),
    pg.Rect(705, 0, 600, 30),
]

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

    # --- 暫存原位置 ---
    old_x, old_y = player_x, player_y

    # --- 嘗試移動 ---
    player_x += dx
    player_y += dy

    # 建立玩家矩形，用於碰撞判定
    player_rect = pg.Rect(player_x, player_y, 45, 75)

    # --- 與牆壁碰撞檢查 ---
    for wall in walls:
        if player_rect.colliderect(wall):
            player_x, player_y = old_x, old_y  # 撞到就回到原位
            break

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
    if facing_right:
        current_image = pg.transform.flip(current_image, True, False)

    # --- 畫面更新 ---
    screen.blit(mainMenuBg, (0, 0))
    screen.blit(current_image, (player_x, player_y))

    # 🔧（除錯用）可視化碰撞牆：可刪除
    #for wall in walls:
        #pg.draw.rect(screen, (255, 0, 0), wall, 2)

    pg.display.flip()
    clock.tick(60)

# --- 結束程式 ---
pg.quit()
sys.exit()
