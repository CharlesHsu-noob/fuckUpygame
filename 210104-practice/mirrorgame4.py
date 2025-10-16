import pygame as pg
import math
import os, sys

# --- 路徑設定 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
sys.path.insert(0, base_dir)

pg.init()

# --- 視窗設定 ---
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("雷射反射遊戲")

# --- 顏色定義 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY  = (150, 150, 150)

# --- 插入 flashlight 圖 ---
flashlight_path = os.path.join(base_dir, "picture", "flashlight.png")
flashlight_img = pg.image.load(flashlight_path).convert_alpha()
flashlight_img = pg.transform.scale(flashlight_img, (60, 60))

# --- 遊戲區塊 ---
exit_rect = pg.Rect(WIDTH-90, 50, 60, 60)          # 出口
obstacle_rect = pg.Rect(WIDTH-110, 130, 100, 20)  # 原本障礙物
obstacle_rect2 = pg.Rect(500, 150, 70, 70)       # 新增障礙物

# --- 鏡子設定 ---
mirror_length = 120
mirror_thickness = 6
mirror1 = {"x": 280, "y": HEIGHT//2, "angle": 0}
mirror2 = {"x": WIDTH//2, "y": 100, "angle": 0}

# --- 狀態變數 ---
started = False
won = False
failed = False
laser_path = []
show_instructions = True

# --- 雷射光發射座標 (固定) ---
laser_x, laser_y = 80, 50

# --- 字型 ---
font = pg.font.SysFont("Microsoft JhengHei", 36)
small_font = pg.font.SysFont("Microsoft JhengHei", 24)

# --- 按鈕 ---
start_button = pg.Rect(50, HEIGHT-80, 120, 50)
restart_button = pg.Rect(200, HEIGHT-80, 175, 50)
play_button = pg.Rect(WIDTH//2 - 100, HEIGHT - 120, 165, 60)

# --- 畫鏡子 ---
def draw_mirror(mirror):
    angle_rad = math.radians(mirror["angle"])
    dx = math.cos(angle_rad) * mirror_length / 2
    dy = math.sin(angle_rad) * mirror_length / 2
    p1 = (mirror["x"] - dx, mirror["y"] - dy)
    p2 = (mirror["x"] + dx, mirror["y"] + dy)
    pg.draw.line(screen, BLACK, p1, p2, mirror_thickness)
    return p1, p2

# --- 反射公式 ---
def reflect_vector(vx, vy, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    nx, ny = -dy, dx
    length = math.hypot(nx, ny)
    if length == 0:
        return vx, vy
    nx, ny = nx / length, ny / length
    dot = vx * nx + vy * ny
    rx = vx - 2 * dot * nx
    ry = vy - 2 * dot * ny
    return rx, ry

# --- 雷射反射 ---
def draw_laser():
    global won, failed
    if not started:
        return
    laser_path.clear()
    x, y = laser_x, laser_y
    dx, dy = 5, 5
    won = False
    failed = False
    for _ in range(2000):
        x += dx
        y += dy
        laser_path.append((x, y))

        if exit_rect.collidepoint(x, y):
            won = True
            return
        # 加入第二個障礙物判定
        if obstacle_rect.collidepoint(x, y) or obstacle_rect2.collidepoint(x, y):
            failed = True
            return

        for m in [mirror1, mirror2]:
            p1, p2 = get_mirror_points(m)
            if point_near_line((x, y), p1, p2, 5):
                dx, dy = reflect_vector(dx, dy, *p1, *p2)

        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            failed = True
            return

# --- 幫助函式 ---
def get_mirror_points(mirror):
    angle_rad = math.radians(mirror["angle"])
    dx = math.cos(angle_rad) * mirror_length / 2
    dy = math.sin(angle_rad) * mirror_length / 2
    return (mirror["x"] - dx, mirror["y"] - dy), (mirror["x"] + dx, mirror["y"] + dy)

def point_near_line(point, p1, p2, threshold):
    px, py = point
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0:
        return False
    t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    nearest_x = x1 + t*dx
    nearest_y = y1 + t*dy
    dist = math.hypot(px - nearest_x, py - nearest_y)
    return dist < threshold

# --- 說明畫面 ---
def draw_instructions():
    screen.fill(WHITE)
    title = font.render("遊戲規則", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

    rules = [
        "光線會由手電筒發出，",
        "目標是要碰到右下角綠色正方形，",
        "射到障礙物就失敗！",
        "下方鏡子：方向鍵 ↑↓旋轉，←→左右移動",
        "上方鏡子：W/S旋轉，A/D左右移動",
        "調整好角度後，按下 start 開始發射雷射"
    ]
    for i, text in enumerate(rules):
        line = small_font.render(text, True, BLACK)
        screen.blit(line, (80, 160 + i * 40))

    pg.draw.rect(screen, (180, 180, 180), play_button)
    play_text = font.render("開始遊戲", True, BLACK)
    screen.blit(play_text, (play_button.x + 10, play_button.y +7))

    pg.display.flip()

# --- 主迴圈 ---
clock = pg.time.Clock()
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if show_instructions:
            if event.type == pg.MOUSEBUTTONDOWN and play_button.collidepoint(event.pos):
                show_instructions = False
            continue

        if event.type == pg.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                if not started:
                    started = True
                    won = False
                    failed = False
                    draw_laser()
            if restart_button.collidepoint(event.pos):
                started = False
                won = False
                failed = False
                laser_path.clear()

    if show_instructions:
        draw_instructions()
        clock.tick(60)
        continue

    # --- 鏡子控制 ---
    keys = pg.key.get_pressed()
    if not started:
        if keys[pg.K_UP]:
            mirror1["angle"] -= 1
        if keys[pg.K_DOWN]:
            mirror1["angle"] += 1
        if keys[pg.K_LEFT]:
            mirror1["x"] -= 3
        if keys[pg.K_RIGHT]:
            mirror1["x"] += 3

        if keys[pg.K_w]:
            mirror2["angle"] -= 1
        if keys[pg.K_s]:
            mirror2["angle"] += 1
        if keys[pg.K_a]:
            mirror2["x"] -= 3
        if keys[pg.K_d]:
            mirror2["x"] += 3

        for m in [mirror1, mirror2]:
            m["x"] = max(60, min(WIDTH - 60, m["x"]))
            m["y"] = max(60, min(HEIGHT - 60, m["y"]))

    # --- 畫面更新 ---
    screen.fill(WHITE)

    # 🔦 手電筒放在固定雷射座標
    flashlight_rect = flashlight_img.get_rect(center=(laser_x, laser_y))
    screen.blit(flashlight_img, flashlight_rect)

    pg.draw.rect(screen, GREEN, exit_rect)
    pg.draw.rect(screen, GRAY, obstacle_rect)
    pg.draw.rect(screen, GRAY, obstacle_rect2)  # 畫第二個障礙物
    draw_mirror(mirror1)
    draw_mirror(mirror2)

    if started and len(laser_path) > 1:
        pg.draw.lines(screen, RED, False, laser_path, 2)

    # --- 按鈕 ---
    pg.draw.rect(screen, (200,200,200), start_button)
    pg.draw.rect(screen, (200,200,200), restart_button)
    screen.blit(font.render("start", True, BLACK), (start_button.x+20, start_button.y))
    screen.blit(font.render("try again", True, BLACK), (restart_button.x+20, restart_button.y))

    # --- 結果顯示 ---
    if won:
        screen.blit(font.render("success!", True, RED), (WIDTH-200, HEIGHT-100))
    elif failed:
        screen.blit(font.render("fail!", True, BLACK), (WIDTH-200, HEIGHT-100))

    pg.display.flip()
    clock.tick(60)

pg.quit()
sys.exit()
