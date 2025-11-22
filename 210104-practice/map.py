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
PLAYER_SPEED = 150   # 平滑移動速度（px/sec）

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
        return (
            self.col * GRID_SIZE + GRID_SIZE // 2,
            self.row * GRID_SIZE + GRID_SIZE // 2
        )

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
        return ((cx - dx, cy - dy), (cx + dx, cy + dy))

class Player:
    def __init__(self, col=1, row=1):
        # 真實位置（像素，用來做平滑移動）
        self.x = col * GRID_SIZE + GRID_SIZE//2
        self.y = row * GRID_SIZE + GRID_SIZE//2
        # 格子位置（邏輯互動）
        self.col = col
        self.row = row
        self.holding = None
        self.adjust_mode = False

    @property
    def pos(self):
        return (int(self.x), int(self.y))

    def update_logic_position(self):
        self.col = int(self.x // GRID_SIZE)
        self.row = int(self.y // GRID_SIZE)

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
            t = grid[c][r]
            pg.draw.rect(screen, WHITE, t.rect)
            if t.can_place:
                pg.draw.rect(screen, (235, 245, 255), t.rect)
            pg.draw.rect(screen, GRAY, t.rect, 1)

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
        pg.draw.line(screen, BLACK, (x - dx, y - dy), (x + dx, y + dy), 5)
        pg.draw.line(screen, YELLOW, (x - dx, y - dy), (x + dx, y + dy), 2)

def point_near_line(point, p1, p2, threshold):
    px, py = point
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return False
    t = ((px-x1)*dx + (py-y1)*dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    nx = x1 + t * dx
    ny = y1 + t * dy
    return math.hypot(px-nx, py-ny) <= threshold

def reflect_vector(vx, vy, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1
    nx, ny = -dy, dx
    l = math.hypot(nx, ny)
    if l == 0:
        return vx, vy
    nx, ny = nx/l, ny/l
    dot = vx*nx + vy*ny
    return (vx - 2*dot*nx, vy - 2*dot*ny)

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
                        if point_near_line((x, y), p1, p2, 6):
                            vx, vy = reflect_vector(vx, vy, *p1, *p2)
                            reflections += 1
                            if reflections > 30:
                                return path, reached_goal
                            x += vx*0.5
                            y += vy*0.5
                            path.append((x, y))
                            hit = True
                            break
            if hit:
                break

    return path, reached_goal

def draw_laser_path(path):
    if len(path) < 2:
        return
    pg.draw.lines(screen, RED, False, path, 5)
    pg.draw.circle(screen, RED, laser_source, 6)

def tile_at(c, r):
    if 0 <= c < COLS and 0 <= r < ROWS:
        return grid[c][r]
    return None

# ----------------- 主 loop -----------------
laser_path_cache = []
laser_reached_goal = False
last_laser_path = []
last_mirrors = []

running = True
while running:
    dt = clock.tick(FPS)

    # ----------------- 事件 -----------------
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.KEYDOWN:

            # -------- R 重設 --------
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

            # -------- F 發射雷射 --------
            if event.key == pg.K_f:
                last_mirrors = [
                    (c, r, grid[c][r].mirror.angle)
                    for c in range(COLS)
                    for r in range(ROWS)
                    if grid[c][r].mirror
                ]
                laser_path_cache, laser_reached_goal = fire_laser_and_get_path()
                last_laser_path = laser_path_cache[:]

            # -------- E 互動（撿/放/調整）--------
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

            # -------- Q 取消調整 --------
            if event.key == pg.K_q and player.adjust_mode:
                player.adjust_mode = False
                laser_path_cache = []

            # -------- 調整鏡子角度 --------
            if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                if player.adjust_mode and player.holding:
                    player.holding.angle = 135 if player.holding.angle == 45 else 45
                    laser_path_cache = []

    # ----------------------------------------------------
    #     平滑移動：方向鍵持續推動 (dt 做時間修正)
    # ----------------------------------------------------
    if not player.adjust_mode:
        keys = pg.key.get_pressed()
        dx = dy = 0

        if keys[pg.K_LEFT]:
            dx -= 1
        if keys[pg.K_RIGHT]:
            dx += 1
        if keys[pg.K_UP]:
            dy -= 1
        if keys[pg.K_DOWN]:
            dy += 1

        if dx or dy:
            laser_path_cache = []
            laser_reached_goal = False

            # 正規化方向
            l = math.hypot(dx, dy)
            if l != 0:
                dx /= l
                dy /= l

            # 更新像素位置
            player.x += dx * PLAYER_SPEED * (dt / 1000)
            player.y += dy * PLAYER_SPEED * (dt / 1000)

            # 限制邊界
            player.x = max(GRID_SIZE//2, min(WIDTH - GRID_SIZE//2, player.x))
            player.y = max(GRID_SIZE//2, min(HEIGHT - GRID_SIZE//2, player.y))

            # 更新邏輯格
            player.update_logic_position()

    # ================== 畫畫面 ==================
    screen.fill(WHITE)
    draw_grid()
    draw_shadow_laser(last_laser_path)
    draw_shadow_mirrors(last_mirrors)
    draw_tiles_contents()
    draw_player()

    # 互動提示
    cur_tile = tile_at(player.col, player.row)
    if cur_tile and cur_tile.mirror:
        screen.blit(font.render("按E撿起鏡子", True, BLACK), (30, 30))
    elif player.holding and cur_tile and cur_tile.can_place and cur_tile.mirror is None and not player.adjust_mode:
        screen.blit(font.render("按E可調整鏡子角度", True, BLACK), (30, 30))

    # 調整模式預覽
    if player.adjust_mode and player.holding:
        center = cur_tile.center
        p1, p2 = player.holding.endpoints(center)
        pg.draw.line(screen, BLACK, p1, p2, 6)
        pg.draw.line(screen, YELLOW, p1, p2, 2)
        screen.blit(font.render("調整模式: 方向鍵=旋轉, E=確認, Q=取消", True, BLACK),
                    (300, HEIGHT - 30))
        screen.blit(font.render(f"角度: {player.holding.angle}°", True, BLACK),
                    (WIDTH - 160, HEIGHT - 30))

    # 未發射的雷射提示線
    if not laser_path_cache:
        lx, ly = laser_source
        vx, vy = laser_direction
        mag = math.hypot(vx, vy)
        if mag != 0:
            nx, ny = vx/mag, vy/mag
            tip_len = 30
            end_pos = (lx + nx*tip_len, ly + ny*tip_len)
            pg.draw.line(screen, (180,60,60), laser_source, end_pos, 4)

        pg.draw.circle(screen, RED, laser_source, 5)
        screen.blit(font.render("按F發射雷射光", True, BLACK),
                    (WIDTH - 220, 10))

    # 畫雷射
    if laser_path_cache:
        draw_laser_path(laser_path_cache)
        msg = "成功!" if laser_reached_goal else "失敗!"
        color = GREEN if laser_reached_goal else RED
        screen.blit(font.render(msg, True, color), (WIDTH - 100, 30))

    # 下方 legend
    legend = [
        "方向鍵: 移動 / 轉動鏡子 (調整模式)",
        "E: 撿起 / 放置",
        "Q: 取消調整",
        "F: 發射雷射",
        "R: 重新開始"
    ]
    for i, s in enumerate(legend):
        screen.blit(font.render(s, True, BLACK), (10, HEIGHT - 110 + i*18))

    pg.display.flip()

pg.quit()
sys.exit()
