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
exit_rect = pg.Rect(WIDTH-90, 300, 60, 60)          # 出口

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
selected_mirror = 1  # 1 代表鏡子1，2 代表鏡子2

# --- 雷射光發射座標 ---
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

        for m in [mirror1, mirror2]:
            p1, p2 = get_mirror_points(m)
            if point_near_line((x, y), p1, p2, 5):
                dx, dy = reflect_vector(dx, dy, *p1, *p2)

        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            failed = True
            return

# --- 說明畫面 ---
def draw_instructions():
    screen.fill(WHITE)
    title = font.render("遊戲規則", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

    rules = [
        "光線會由手電筒發出，",
        "目標是要碰到右下角綠色正方形，",
        "← →：選擇鏡子",
        "A / D：左右移動鏡子",
        "調整好位置後，按下 start 開始發射雷射"
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

    keys = pg.key.get_pressed()
    if not started:
        # 鏡子選擇（左右鍵）
        if keys[pg.K_LEFT]:
            selected_mirror = 1
        elif keys[pg.K_RIGHT]:
            selected_mirror = 2

        # 取得目前控制的鏡子
        current = mirror1 if selected_mirror == 1 else mirror2

        # A/D 控制左右移動
        if keys[pg.K_a]:
            current["x"] -= 3
        if keys[pg.K_d]:
            current["x"] += 3

        # 限制邊界
        current["x"] = max(60, min(WIDTH - 60, current["x"]))
        current["y"] = max(60, min(HEIGHT - 60, current["y"]))

    # --- 畫面更新 ---
    screen.fill(WHITE)
    flashlight_rect = flashlight_img.get_rect(center=(laser_x, laser_y))
    screen.blit(flashlight_img, flashlight_rect)
    pg.draw.rect(screen, GREEN, exit_rect)

    # --- 畫鏡子 ---
    p1, p2 = draw_mirror(mirror1)
    p3, p4 = draw_mirror(mirror2)

    # 畫選取提示
    selected = mirror1 if selected_mirror == 1 else mirror2
    pg.draw.circle(screen, RED, (int(selected["x"]), int(selected["y"])), 10, 2)

    # --- 畫雷射 ---
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
