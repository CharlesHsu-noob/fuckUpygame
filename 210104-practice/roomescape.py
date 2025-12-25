import pygame as pg
import math
import sys
import os

pg.init()

# ----------------- 參數修正 -----------------
WIDTH, HEIGHT = 1920,1080

# 依照您的圖片，中間是 16x12 的格子
COLS = 16
ROWS = 12

# 調整格子大小以符合 1080p 畫面中的棋盤比例
# 12格 * 80px = 960px，剩下 120px 給上下邊框，看起來剛好
GRID_SIZE = 79

# --- 關鍵修正：計算偏移量 (讓格子置中) ---
# 這會算出棋盤格左上角在螢幕的哪個像素點
OFFSET_X = 330
OFFSET_Y = 66

FPS = 60
PLAYER_SPEED = 300 # 速度加快

# 顏色
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
DARK_GRAY = (160, 160, 160)
GREEN = (80, 200, 120)
RED = (220, 50, 50)
BLUE = (60, 140, 220)
YELLOW = (235, 210, 80)

font = pg.font.SysFont("Microsoft JhengHei", 32)

screen = pg.display.set_mode((WIDTH, HEIGHT)) # 若要全螢幕可加 pg.FULLSCREEN
pg.display.set_caption("Bob")

clock = pg.time.Clock()

# --- 載入背景 ---

bg_img = pg.image.load(os.path.join('picture', 'labg_b.png')).convert()
bg_img = pg.transform.scale(bg_img, (WIDTH, HEIGHT))


# --- 載入圖片資源 (通用縮放邏輯) ---
def load_and_scale(path, scale_factor, rotate=0):
    try:
        img = pg.image.load(os.path.join('picture', path)).convert_alpha()
    except:
        s = pg.Surface((GRID_SIZE, GRID_SIZE), pg.SRCALPHA)
        s.fill((255, 0, 255, 128)) # 紫色方塊代表缺圖
        img = s
    
    target_size = int(GRID_SIZE * scale_factor)
    img = pg.transform.scale(img, (target_size, target_size))
    if rotate:
        img = pg.transform.rotate(img, rotate)
    return img

laser_emitter_img = load_and_scale('lab_laser_top.png', 1.5, -18)
mirror_hold_image = load_and_scale('lab_mirror_whole.png', 0.6)
mirror_base_image = pg.image.load(os.path.join('picture', 'lab_mirror_tile.png')).convert_alpha()
mirror_base_image = pg.transform.scale(mirror_base_image, (GRID_SIZE, GRID_SIZE))

# 鏡子處理

img_original = pg.image.load(os.path.join('picture', 'lab_mirror_b.png')).convert_alpha()
img_original = pg.transform.scale(img_original, (GRID_SIZE, GRID_SIZE))

mirror_images = {
    45: img_original,
    135: pg.transform.rotate(img_original, 90)
}

# ----------------- 資料結構 (修正座標邏輯) -----------------
class Tile:
    def __init__(self, col, row, can_place=True):
        self.col = col
        self.row = row
        self.can_place = can_place
        self.mirror = None

    @property
    def center(self):
        # 中心點 = 偏移量 + 格子位置 + 半格
        return (
            OFFSET_X + self.col * GRID_SIZE + GRID_SIZE // 2,
            OFFSET_Y + self.row * GRID_SIZE + GRID_SIZE // 2
        )

    @property
    def rect(self):
        # 矩形 = 偏移量 + 格子位置
        return pg.Rect(OFFSET_X + self.col * GRID_SIZE, 
                       OFFSET_Y + self.row * GRID_SIZE, 
                       GRID_SIZE, GRID_SIZE)

class Mirror:
    def __init__(self, angle_deg=45):
        self.angle = angle_deg

    def get_image(self):
        return mirror_images.get(self.angle)
    
    def get_base_image(self):
        return mirror_base_image

    def endpoints(self, center):
        cx, cy = center
        half = GRID_SIZE * 0.45
        a = math.radians(self.angle)
        dx = math.cos(a) * half
        dy = math.sin(a) * half
        return ((cx - dx, cy - dy), (cx + dx, cy + dy))

class Player:
    def __init__(self, col=1, row=1):
        self.col = col
        self.row = row
        # 初始像素位置也要加上 OFFSET
        self.x = OFFSET_X + col * GRID_SIZE + GRID_SIZE//2
        self.y = OFFSET_Y + row * GRID_SIZE + GRID_SIZE//2
        self.holding = None
        self.adjust_mode = False

    @property
    def pos(self):
        return (int(self.x), int(self.y))

    def update_logic_position(self):
        # 反推邏輯座標時，要減去 OFFSET
        self.col = int((self.x - OFFSET_X) // GRID_SIZE)
        self.row = int((self.y - OFFSET_Y) // GRID_SIZE)

# ----------------- 建地圖 -----------------
grid = [[Tile(c, r) for r in range(ROWS)] for c in range(COLS)]

# 示範鏡子
grid[0][5].mirror = Mirror(45)
grid[0][4].mirror = Mirror(45) 

player = Player(1, 1)

# 雷射來源：修正為相對 Grid 的位置 + Offset
laser_source = (OFFSET_X + GRID_SIZE//2, OFFSET_Y + GRID_SIZE//2)
laser_direction = (1.0, 0.3)

goal_tile = grid[COLS-2][ROWS-2]

# ----------------- 助手函式 -----------------
def draw_laser_emitter():
    lx, ly = laser_source
    w = laser_emitter_img.get_width()
    h = laser_emitter_img.get_height()
    screen.blit(laser_emitter_img, (lx - w // 2, ly - h // 2))

def draw_grid():
    # 畫個外框幫助除錯，確認格子有沒有對齊背景
    board_rect = pg.Rect(OFFSET_X, OFFSET_Y, COLS*GRID_SIZE, ROWS*GRID_SIZE)
    pg.draw.rect(screen, BLACK, board_rect, 3) 
    
    for c in range(COLS):
        for r in range(ROWS):
            t = grid[c][r]
            # 淡淡的格線
            pg.draw.rect(screen, (100, 100, 100), t.rect, 1)

def draw_shadow_mirrors(last_mirrors):
    if not last_mirrors: return
    s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    for c, r, ang in last_mirrors:
        if 0 <= c < COLS and 0 <= r < ROWS:
            t = grid[c][r]
            img = mirror_images.get(ang)
            if img:
                shadow_img = img.copy()
                shadow_img.set_alpha(80) 
                s.blit(shadow_img, t.rect.topleft) # 使用 rect.topleft 自動包含 offset
    screen.blit(s, (0, 0))

def draw_shadow_laser(last_laser_path):
    if len(last_laser_path) < 2: return
    s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    pg.draw.lines(s, (255, 0, 0, 80), False, last_laser_path, 3)
    screen.blit(s, (0, 0))

def draw_tiles_contents():
    for c in range(COLS):
        for r in range(ROWS):
            t = grid[c][r]
            if t.can_place:
                # 滑鼠懸停效果 (可選)
                if t.rect.collidepoint(pg.mouse.get_pos()):
                    pg.draw.rect(screen, (255, 255, 255), t.rect, 2)

            if t.mirror:
                base = t.mirror.get_base_image()
                if base: screen.blit(base, t.rect.topleft)
                
                img = t.mirror.get_image()
                if img: screen.blit(img, t.rect.topleft)

    pg.draw.rect(screen, GREEN, goal_tile.rect, 4) # 終點框

def draw_player():
    x, y = player.pos
    radius = GRID_SIZE // 3
    pg.draw.circle(screen, BLUE, (x, y), radius)

    if player.holding:
        holding_img = mirror_hold_image.copy()
        if player.holding.angle == 45:
            holding_img = pg.transform.rotate(holding_img, 90)
        draw_x = x - holding_img.get_width() // 2
        draw_y = y - holding_img.get_height() - radius + 20
        screen.blit(holding_img, (draw_x, draw_y))

def point_near_line(point, p1, p2, threshold):
    px, py = point
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0: return False
    t = ((px-x1)*dx + (py-y1)*dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    return math.hypot(px-(x1+t*dx), py-(y1+t*dy)) <= threshold

def reflect_vector(vx, vy, x1, y1, x2, y2):
    dx, dy = x2-x1, y2-y1
    nx, ny = -dy, dx 
    l = math.hypot(nx, ny)
    if l == 0: return vx, vy
    nx, ny = nx/l, ny/l
    dot = vx*nx + vy*ny
    return (vx - 2*dot*nx, vy - 2*dot*ny)

def fire_laser_and_get_path():
    path = []
    max_steps = 6000 
    step_size = 5.0 # 稍微加快計算

    x, y = float(laser_source[0]), float(laser_source[1])
    vx, vy = laser_direction
    mag = math.hypot(vx, vy)
    if mag == 0: return path, False
    vx, vy = vx/mag * step_size, vy/mag * step_size

    reflections = 0
    reached_goal = False

    # 優化邊界檢查 (只在畫面內運算)
    screen_rect = pg.Rect(0, 0, WIDTH, HEIGHT)

    for _ in range(max_steps):
        x += vx
        y += vy
        path.append((x, y))

        if goal_tile.rect.collidepoint(int(x), int(y)):
            reached_goal = True
            break
        
        if not screen_rect.collidepoint(int(x), int(y)):
            break

        # 座標轉 Grid
        c = int((x - OFFSET_X) // GRID_SIZE)
        r = int((y - OFFSET_Y) // GRID_SIZE)
        
        hit = False
        # 檢查周圍 3x3 區域
        fordc = -1; 
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                cc, rr = c + dc, r + dr
                if 0 <= cc < COLS and 0 <= rr < ROWS:
                    t = grid[cc][rr]
                    if t.mirror:
                        p1, p2 = t.mirror.endpoints(t.center)
                        if point_near_line((x, y), p1, p2, 8): # 碰撞閾值稍微加大
                            vx, vy = reflect_vector(vx, vy, *p1, *p2)
                            reflections += 1
                            if reflections > 40: return path, reached_goal
                            x += vx*0.6 # 防沾黏
                            y += vy*0.6
                            path.append((x, y))
                            hit = True
                            break
            if hit: break
    return path, reached_goal

def tile_at_pixel(px, py):
    # 將像素座標轉換為網格座標
    c = int((px - OFFSET_X) // GRID_SIZE)
    r = int((py - OFFSET_Y) // GRID_SIZE)
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

    for event in pg.event.get():
        if event.type == pg.QUIT: running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE: running = False
            
            # --- 互動邏輯 ---
            if event.key == pg.K_r: # Reset
                for c in range(COLS):
                    for r in range(ROWS): grid[c][r].mirror = None
                grid[0][5].mirror = Mirror(45)
                player.holding = None
                laser_path_cache = []
            
            if event.key == pg.K_f: # Fire
                last_mirrors = [(c, r, grid[c][r].mirror.angle) for c in range(COLS) for r in range(ROWS) if grid[c][r].mirror]
                laser_path_cache, laser_reached_goal = fire_laser_and_get_path()
                last_laser_path = laser_path_cache[:]

            if event.key == pg.K_e: # Interact
                t = tile_at_pixel(player.x, player.y) # 使用修正後的查找函數
                if player.adjust_mode:
                    if t and t.can_place and t.mirror is None and player.holding:
                        t.mirror = player.holding
                        player.holding = None
                        player.adjust_mode = False
                        laser_path_cache = []
                else:
                    if player.holding is None and t and t.mirror:
                        player.holding = t.mirror
                        t.mirror = None
                        laser_path_cache = []
                    elif player.holding and t and t.can_place and t.mirror is None:
                        player.adjust_mode = True
                        laser_path_cache = []

            if event.key == pg.K_q and player.adjust_mode:
                player.adjust_mode = False

            if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                if player.adjust_mode and player.holding:
                    player.holding.angle = 135 if player.holding.angle == 45 else 45
                    laser_path_cache = []

    # --- 移動邏輯 ---
    if not player.adjust_mode:
        keys = pg.key.get_pressed()
        dx, dy = 0, 0
        if keys[pg.K_LEFT]: dx = -1
        if keys[pg.K_RIGHT]: dx = 1
        if keys[pg.K_UP]: dy = -1
        if keys[pg.K_DOWN]: dy = 1
        
        if dx or dy:
            laser_path_cache = []
            mag = math.hypot(dx, dy)
            dx, dy = dx/mag, dy/mag
            player.x += dx * PLAYER_SPEED * (dt/1000)
            player.y += dy * PLAYER_SPEED * (dt/1000)
            
            # 限制玩家移動範圍 (加上 OFFSET)
            min_x = OFFSET_X + GRID_SIZE//2
            max_x = OFFSET_X + COLS*GRID_SIZE - GRID_SIZE//2
            min_y = OFFSET_Y + GRID_SIZE//2
            max_y = OFFSET_Y + ROWS*GRID_SIZE - GRID_SIZE//2
            
            player.x = max(min_x, min(max_x, player.x))
            player.y = max(min_y, min(max_y, player.y))
            player.update_logic_position()

    # --- 繪圖 ---
    screen.fill(BLACK) # 背景設黑，以免圖片沒覆蓋到的地方變白
    screen.blit(bg_img, (0, 0))
    
    draw_grid() # 畫格線 (除錯用，確認對齊)
    draw_shadow_laser(last_laser_path)
    draw_shadow_mirrors(last_mirrors)
    draw_tiles_contents()
    draw_player()

    # --- UI 繪製 (位置動態調整) ---
    ui_y_base = HEIGHT - 100
    if player.adjust_mode:
        screen.blit(font.render("調整模式", True, RED), (WIDTH//2 - 50, ui_y_base))
    
    if not laser_path_cache:
        lx, ly = laser_source
        vx, vy = laser_direction
        end_pos = (lx + vx*40, ly + vy*40)
        pg.draw.line(screen, RED, laser_source, end_pos, 4)
        draw_laser_emitter()

    pg.display.flip()

pg.quit()
sys.exit()