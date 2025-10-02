import pygame as pg
import math

pg.init()

# --- 視窗設定 ---
w, h = 800, 600
screen = pg.display.set_mode((w, h))
pg.display.set_caption("雷射反射遊戲")

# --- 顏色 ---
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# --- 入口與出口 ---
entry_rect = pg.Rect(50, 50, 40, 40)  # 左上角
exit_rect = pg.Rect(w - 90, h - 90, 40, 40)  # 右下角

# --- 鏡子 ---
mirror_length = 120
mirror_thickness = 6
mirror_speed = 3   # 移動幅度調小
rotate_speed = 3  # 旋轉速度 (度數)

# 鏡子結構：位置 + 角度
mirror1 = {"x": w // 2, "y": h // 2, "angle": 0}
mirror2 = {"x": w // 2, "y": 100, "angle": 0}

# --- 雷射光 ---
laser_start = (entry_rect.centerx, entry_rect.centery)
laser_dir = (1, 1)  # 固定方向 (右下)
shoot_laser = False

# --- 開始按鈕 ---
font = pg.font.SysFont(None, 40)
button_rect = pg.Rect(w // 2 - 60, h - 60, 120, 40)


def draw_mirror(mirror):
    """畫出旋轉鏡子"""
    angle_rad = math.radians(mirror["angle"])
    dx = math.cos(angle_rad) * mirror_length / 2
    dy = math.sin(angle_rad) * mirror_length / 2

    p1 = (mirror["x"] - dx, mirror["y"] - dy)
    p2 = (mirror["x"] + dx, mirror["y"] + dy)
    pg.draw.line(screen, WHITE, p1, p2, mirror_thickness)
    return p1, p2


def reflect_vector(vx, vy, x1, y1, x2, y2):
    """反射向量計算：利用線段法線"""
    dx, dy = x2 - x1, y2 - y1
    nx, ny = -dy, dx  # 法線向量
    length = math.hypot(nx, ny)
    if length == 0:
        return vx, vy
    nx, ny = nx / length, ny / length

    dot = vx * nx + vy * ny
    rx = vx - 2 * dot * nx
    ry = vy - 2 * dot * ny
    return rx, ry


def clamp_mirror(mirror):
    """防止鏡子超出視窗"""
    half_len = mirror_length // 2
    if mirror["x"] - half_len < 0:
        mirror["x"] = half_len
    if mirror["x"] + half_len > w:
        mirror["x"] = w - half_len


def draw_text(text, pos, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, pos)


running = True
clock = pg.time.Clock()

while running:
    screen.fill((0, 0, 0))

    # --- 繪製入口出口 ---
    pg.draw.rect(screen, GREEN, entry_rect)
    pg.draw.rect(screen, BLUE, exit_rect)

    # --- 繪製鏡子 ---
    m1_p1, m1_p2 = draw_mirror(mirror1)
    m2_p1, m2_p2 = draw_mirror(mirror2)

    # --- 繪製開始按鈕 ---
    pg.draw.rect(screen, (200, 200, 200), button_rect)
    draw_text("start", (button_rect.x + 20, button_rect.y + 5), (0, 0, 0))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                shoot_laser = True

    # --- 鏡子控制 ---
    keys = pg.key.get_pressed()

    # 中間鏡子 ← → (移動)，↑ ↓ (旋轉)
    if keys[pg.K_LEFT]:
        mirror1["x"] -= mirror_speed
    if keys[pg.K_RIGHT]:
        mirror1["x"] += mirror_speed
    if keys[pg.K_UP]:
        mirror1["angle"] -= rotate_speed
    if keys[pg.K_DOWN]:
        mirror1["angle"] += rotate_speed
    clamp_mirror(mirror1)

    # 上排鏡子 A D (移動)，W S (旋轉)
    if keys[pg.K_a]:
        mirror2["x"] -= mirror_speed
    if keys[pg.K_d]:
        mirror2["x"] += mirror_speed
    if keys[pg.K_w]:
        mirror2["angle"] -= rotate_speed
    if keys[pg.K_s]:
        mirror2["angle"] += rotate_speed
    clamp_mirror(mirror2)

    # --- 發射雷射 ---
    if shoot_laser:
        lx, ly = laser_start
        vx, vy = laser_dir

        for _ in range(2000):  # 最多畫 2000 步
            nx, ny = lx + vx, ly + vy
            pg.draw.line(screen, RED, (lx, ly), (nx, ny), 2)
            lx, ly = nx, ny

            # 判斷是否撞到鏡子
            for (p1, p2) in [(m1_p1, m1_p2), (m2_p1, m2_p2)]:
                px, py = lx, ly
                x1, y1 = p1
                x2, y2 = p2
                dx, dy = x2 - x1, y2 - y1
                if dx == dy == 0:
                    continue
                t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
                t = max(0, min(1, t))
                nearest_x = x1 + t * dx
                nearest_y = y1 + t * dy
                dist = math.hypot(px - nearest_x, py - nearest_y)

                if dist < 5:  # 接近線段 → 碰撞
                    vx, vy = reflect_vector(vx, vy, x1, y1, x2, y2)

            if lx < 0 or lx > w or ly < 0 or ly > h:
                break

    pg.display.flip()
    clock.tick(60)

pg.quit()
