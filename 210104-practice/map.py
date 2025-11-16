# mirror_grid_game.py
import pygame as pg
import math
import sys

pg.init()

# ----------------- 參數 -----------------
GRID_SIZE = 48
COLS = 16
ROWS = 12
WIDTH, HEIGHT = GRID_SIZE * COLS, GRID_SIZE * ROWS
FPS = 60

# 顏色
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
DARK_GRAY = (160, 160, 160)
GREEN = (80, 200, 120)
RED = (220, 50, 50)
BLUE = (60, 140, 220)
YELLOW = (235, 210, 80)

font = pg.font.SysFont("Microsoft JhengHei", 16)

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Bob")

clock = pg.time.Clock()

# ----------------- 資料結構 -----------------
class Tile:
    def __init__(self, col, row, can_place=True):
        self.col = col
        self.row = row
        self.can_place = can_place
        self.mirror = None

    @property
    def center(self):
        return (self.col * GRID_SIZE + GRID_SIZE // 2,
                self.row * GRID_SIZE + GRID_SIZE // 2)

    @property
    def rect(self):
        return pg.Rect(self.col * GRID_SIZE, self.row * GRID_SIZE, GRID_SIZE, GRID_SIZE)

class Mirror:
    def __init__(self, angle_deg=45):
        self.angle = angle_deg

    def endpoints(self, center):
        cx, cy = center
        half = GRID_SIZE * 0.45
        a = math.radians(self.angle)
        dx = math.cos(a) * half
        dy = math.sin(a) * half
        p1 = (cx - dx, cy - dy)
        p2 = (cx + dx, cy + dy)
        return p1, p2

class Player:
    def __init__(self, col=1, row=1):
        self.col = col
        self.row = row
        self.holding = None
        self.adjust_mode = False

    @property
    def pos(self):
        return (self.col * GRID_SIZE + GRID_SIZE//2,
                self.row * GRID_SIZE + GRID_SIZE//2)

# ----------------- 建地圖 -----------------
grid = [[Tile(c, r) for r in range(ROWS)] for c in range(COLS)]

# 示範鏡子
grid[5][5].mirror = Mirror(45)
grid[11][4].mirror = Mirror(135)

player = Player(1, 1)

# 雷射來源
laser_source = (GRID_SIZE//2, GRID_SIZE//2)
laser_direction = (1.0, 0.3)

# 終點格
goal_tile = grid[COLS-2][ROWS-2]

# ----------------- 助手函式 -----------------
def draw_grid():
    for c in range(COLS):
        for r in range(ROWS):
            rect = grid[c][r].rect
            pg.draw.rect(screen, WHITE, rect)
            if grid[c][r].can_place:
                pg.draw.rect(screen, (235, 245, 255), rect)
            pg.draw.rect(screen, GRAY, rect, 1)

def draw_shadow_mirrors(last_mirrors):
    if not last_mirrors:
        return
    s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    for c, r, ang in last_mirrors:
        if 0 <= c < COLS and 0 <= r < ROWS:
            t = grid[c][r]
            m = Mirror(ang)
            p1, p2 = m.endpoints(t.center)
            pg.draw.line(s, (255, 255, 100, 80), p1, p2, 6)
            pg.draw.line(s, (255, 255, 180, 80), p1, p2, 2)
    screen.blit(s, (0, 0))

def draw_shadow_laser(last_laser_path):
    if len(last_laser_path) < 2:
        return
    s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    pg.draw.lines(s, (255, 0, 0, 80), False, last_laser_path, 3)
    screen.blit(s, (0, 0))

def draw_tiles_contents():
    for c in range(COLS):
        for r in range(ROWS):
            t = grid[c][r]
            if t.can_place:
                pg.draw.rect(screen, DARK_GRAY, t.rect, 2)
            if t.mirror:
                p1, p2 = t.mirror.endpoints(t.center)
                pg.draw.line(screen, BLACK, p1, p2, 6)
                pg.draw.line(screen, YELLOW, p1, p2, 2)
    # 終點格
    pg.draw.rect(screen, GREEN, goal_tile.rect)

def draw_player():
    x, y = player.pos
    radius = GRID_SIZE//3
    pg.draw.circle(screen, BLUE, (x, y), radius)
    if player.holding:
        mirror = player.holding
        a = mirror.angle
        half = GRID_SIZE * 0.28
        a_rad = math.radians(a)
        dx = math.cos(a_rad) * half
        dy = math.sin(a_rad) * half
        p1 = (x - dx, y - dy)
        p2 = (x + dx, y + dy)
        pg.draw.line(screen, BLACK, p1, p2, 5)
        pg.draw.line(screen, YELLOW, p1, p2, 2)

def point_near_line(point, p1, p2, threshold):
    px, py = point
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return False
    t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    nearest_x = x1 + t*dx
    nearest_y = y1 + t*dy
    dist = math.hypot(px - nearest_x, py - nearest_y)
    return dist <= threshold

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

def fire_laser_and_get_path():
    path = []
    max_steps = 3000
    step_size = 4.0
    x, y = float(laser_source[0]), float(laser_source[1])
    vx, vy = laser_direction
    mag = math.hypot(vx, vy)
    if mag == 0:
        return path, False
    vx, vy = vx/mag * step_size, vy/mag * step_size

    reflections = 0
    reached_goal = False

    for _ in range(max_steps):
        x += vx
        y += vy
        path.append((x, y))

        if goal_tile.rect.collidepoint(int(x), int(y)):
            reached_goal = True
            break

        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            break

        c = int(x // GRID_SIZE)
        r = int(y // GRID_SIZE)
        hit = False
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                cc = c + dc
                rr = r + dr
                if 0 <= cc < COLS and 0 <= rr < ROWS:
                    t = grid[cc][rr]
                    if t.mirror:
                        p1, p2 = t.mirror.endpoints(t.center)
                        if point_near_line((x, y), p1, p2, threshold=6):
                            vx, vy = reflect_vector(vx, vy, *p1, *p2)
                            reflections += 1
                            if reflections > 30:
                                return path, reached_goal
                            x += vx * 0.5
                            y += vy * 0.5
                            path.append((x, y))
                            hit = True
                            break
            if hit:
                break
    return path, reached_goal

def draw_laser_path(path):
    if len(path) < 2:
        return
    pg.draw.lines(screen, RED, False, path, 3)
    pg.draw.circle(screen, RED, (int(laser_source[0]), int(laser_source[1])), 6)

def tile_at(col, row):
    if 0 <= col < COLS and 0 <= row < ROWS:
        return grid[col][row]
    return None

# ----------------- 主 loop -----------------
laser_path_cache = []
laser_reached_goal = False

# 殘影資料
last_laser_path = []
last_mirrors = []  # list of (col, row, angle)

running = True
while running:
    dt = clock.tick(FPS)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:
            # R reset
            if event.key == pg.K_r:
                for c in range(COLS):
                    for r in range(ROWS):
                        grid[c][r].mirror = None
                grid[5][5].mirror = Mirror(45)
                grid[11][4].mirror = Mirror(135)
                player.holding = None
                player.adjust_mode = False
                laser_path_cache = []
                laser_reached_goal = False
                last_laser_path = []
                last_mirrors = []

            # F fire laser
            if event.key == pg.K_f:
                # 儲存當前鏡子狀態為殘影
                last_mirrors = [(c, r, grid[c][r].mirror.angle)
                                for c in range(COLS) for r in range(ROWS)
                                if grid[c][r].mirror]

                # 計算新的雷射
                laser_path_cache, laser_reached_goal = fire_laser_and_get_path()

                # 儲存殘影路徑
                last_laser_path = laser_path_cache[:]

            # E interact
            if event.key == pg.K_e:
                t = tile_at(player.col, player.row)
                if player.adjust_mode:
                    if t and t.can_place and t.mirror is None and player.holding:
                        t.mirror = player.holding
                        player.holding = None
                        player.adjust_mode = False
                        laser_path_cache = []
                        laser_reached_goal = False
                else:
                    if player.holding is None and t and t.mirror:
                        player.holding = t.mirror
                        t.mirror = None
                        laser_path_cache = []
                        laser_reached_goal = False
                    elif player.holding and t and t.can_place and t.mirror is None:
                        player.adjust_mode = True
                        laser_path_cache = []
                        laser_reached_goal = False

            # Q cancel adjust
            if event.key == pg.K_q and player.adjust_mode:
                player.adjust_mode = False
                laser_path_cache = []

            # 角度切換 (在調整模式中)
            if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                if player.adjust_mode and player.holding:
                    player.holding.angle = 135 if player.holding.angle == 45 else 45
                    laser_path_cache = []

            # 玩家移動 (移動時也清除雷射)
            if not player.adjust_mode:
                moved = False
                if event.key == pg.K_LEFT:
                    player.col = max(0, player.col - 1)
                    moved = True
                elif event.key == pg.K_RIGHT:
                    player.col = min(COLS - 1, player.col + 1)
                    moved = True
                elif event.key == pg.K_UP:
                    player.row = max(0, player.row - 1)
                    moved = True
                elif event.key == pg.K_DOWN:
                    player.row = min(ROWS - 1, player.row + 1)
                    moved = True
                if moved:
                    laser_path_cache = []
                    laser_reached_goal = False

    # ======== 畫畫面 ========
    screen.fill(WHITE)

    draw_grid()

    # 畫殘影：先畫殘影雷射和殘影鏡子（較淡）
    draw_shadow_laser(last_laser_path)
    draw_shadow_mirrors(last_mirrors)

    draw_tiles_contents()
    draw_player()

    # 玩家提示文字
    cur_tile = tile_at(player.col, player.row)
    if cur_tile and cur_tile.mirror:
        text = font.render("按E撿起鏡子", True, BLACK)
        screen.blit(text, (30, 30))
    elif player.holding and cur_tile and cur_tile.can_place and cur_tile.mirror is None and not player.adjust_mode:
        text = font.render("按E可調整鏡子角度", True, BLACK)
        screen.blit(text, (30, 30))

    # 調整模式預覽
    if player.adjust_mode and player.holding:
        center = cur_tile.center
        p1, p2 = player.holding.endpoints(center)
        pg.draw.line(screen, BLACK, p1, p2, 6)
        pg.draw.line(screen, YELLOW, p1, p2, 2)
        hint = font.render("調整模式: 方向鍵=旋轉, E=確認, Q=取消", True, BLACK)
        screen.blit(hint, (300, HEIGHT - 30))
        a_text = font.render(f"角度: {player.holding.angle}°", True, BLACK)
        screen.blit(a_text, (WIDTH - 160, HEIGHT - 30))

    # ===== 顯示發射方向提示線（當前未發射時） =====
    if not laser_path_cache:
        lx, ly = laser_source
        vx, vy = laser_direction
        mag = math.hypot(vx, vy)
        if mag != 0:
            nx, ny = vx / mag, vy / mag
            tip_len = 30
            end_pos = (lx + nx * tip_len, ly + ny * tip_len)
            pg.draw.line(screen, (180, 60, 60), laser_source, end_pos, 4)
        pg.draw.circle(screen, RED, laser_source, 5)
        info = font.render("按F發射雷射光", True, BLACK)
        screen.blit(info, (WIDTH - 220, 10))

    # 畫雷射
    if laser_path_cache:
        draw_laser_path(laser_path_cache)
        msg = "成功!" if laser_reached_goal else "失敗!"
        color = GREEN if laser_reached_goal else RED
        screen.blit(font.render(msg, True, color), (WIDTH-100, 30))

    # 底部 legend
    legend = [
        "方向鍵: 移動 / 轉動鏡子 (在調整模式)",
        "E: 撿起 / 放置",
        "Q: 取消調整模式",
        "F: 發射雷射",
        "R: 重新開始"
    ]
    for i, s in enumerate(legend):
        screen.blit(font.render(s, True, BLACK), (10, HEIGHT - 110 + i*18))

    pg.display.flip()

pg.quit()
sys.exit()
