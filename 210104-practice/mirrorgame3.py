import pygame as pg
import sys
import math

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
BLUE  = (0, 0, 255)
GRAY  = (150, 150, 150)

# --- 遊戲區塊 ---
entry_rect = pg.Rect(50, 50, 40, 40)                # 左上角入口
exit_rect = pg.Rect(WIDTH-90, HEIGHT-90, 60, 60)    # 右下角出口(勝利區)

# 🧱 新增：障礙物（出口上方）
obstacle_rect = pg.Rect(WIDTH-90, HEIGHT-170, 60, 20)

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

# --- 字型 ---
font = pg.font.SysFont(None, 48)

# --- 按鈕 ---
start_button = pg.Rect(50, HEIGHT-80, 120, 50)
restart_button = pg.Rect(200, HEIGHT-80, 170, 50)

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
    x, y = entry_rect.center
    dx, dy = 5, 5
    won = False
    failed = False
    for _ in range(2000):
        x += dx
        y += dy
        laser_path.append((x, y))

        # --- 勝利判定 ---
        if exit_rect.collidepoint(x, y):
            won = True
            return

        # --- 碰到障礙物則失敗 ---
        if obstacle_rect.collidepoint(x, y):
            failed = True
            return

        # --- 碰鏡子反射 ---
        for m in [mirror1, mirror2]:
            p1, p2 = get_mirror_points(m)
            if point_near_line((x, y), p1, p2, 5):
                dx, dy = reflect_vector(dx, dy, *p1, *p2)

        # --- 出界失敗 ---
        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            failed = True
            return

# --- 幫助函式 ---
def get_mirror_points(mirror):
    angle_rad = math.radians(mirror["angle"])
    dx = math.cos(angle_rad) * mirror_length / 2
    dy = math.sin(angle_rad) * mirror_length / 2
    p1 = (mirror["x"] - dx, mirror["y"] - dy)
    p2 = (mirror["x"] + dx, mirror["y"] + dy)
    return p1, p2

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

# --- 主迴圈 ---
clock = pg.time.Clock()
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
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

    # --- 鏡子控制 ---
    keys = pg.key.get_pressed()
    if not started:
        # 鏡子1：↑↓ 旋轉，←→ 移動
        if keys[pg.K_UP]:
            mirror1["angle"] -= 1
        if keys[pg.K_DOWN]:
            mirror1["angle"] += 1
        if keys[pg.K_LEFT]:
            mirror1["x"] -= 3
        if keys[pg.K_RIGHT]:
            mirror1["x"] += 3

        # 鏡子2：W/S 旋轉，A/D 移動
        if keys[pg.K_w]:
            mirror2["angle"] -= 1
        if keys[pg.K_s]:
            mirror2["angle"] += 1
        if keys[pg.K_a]:
            mirror2["x"] -= 3
        if keys[pg.K_d]:
            mirror2["x"] += 3

        # 限制鏡子不出界
        for m in [mirror1, mirror2]:
            m["x"] = max(60, min(WIDTH - 60, m["x"]))
            m["y"] = max(60, min(HEIGHT - 60, m["y"]))

    # --- 畫面更新 ---
    screen.fill(WHITE)
    pg.draw.rect(screen, BLUE, entry_rect)       # 入口
    pg.draw.rect(screen, GREEN, exit_rect)       # 出口
    pg.draw.rect(screen, GRAY, obstacle_rect)    # 障礙物
    draw_mirror(mirror1)
    draw_mirror(mirror2)
    if started and len(laser_path) > 1:
        pg.draw.lines(screen, RED, False, laser_path, 2)

    # --- 按鈕 ---
    pg.draw.rect(screen, (200,200,200), start_button)
    pg.draw.rect(screen, (200,200,200), restart_button)
    screen.blit(font.render("start", True, BLACK), (start_button.x+20, start_button.y+10))
    screen.blit(font.render("try again", True, BLACK), (restart_button.x+20, restart_button.y+10))

    # --- 結果顯示 ---
    if won:
        screen.blit(font.render("success!", True, RED), (WIDTH-200, HEIGHT-100))
    elif failed:
        screen.blit(font.render("fail!", True, BLACK), (WIDTH-200, HEIGHT-100))

    pg.display.flip()
    clock.tick(60)

pg.quit()
sys.exit()
