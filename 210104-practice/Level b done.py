import pygame as pg
import math
import sys
import os

pg.init()

# ----------------- 參數 -----------------
GRID_SIZE = 79
COLS = 16
ROWS = 12
WIDTH, HEIGHT = 1920, 1080
FPS = 60
PLAYER_SPEED = 300  # 平滑移動速度（px/sec）
OFFSET_X = 330
OFFSET_Y = 66
# 動畫速度控制 (毫秒 ms)
ANIMATION_DELAY = 150 

# 顏色
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (200, 200, 200)
DARK_GRAY = (160, 160, 160)
GREEN = (80, 200, 120)
RED = (220, 50, 50)
BLUE = (60, 140, 220)
YELLOW = (235, 210, 80)

font = pg.font.SysFont("Microsoft JhengHei", 18)

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Bob")

clock = pg.time.Clock()

# --- 載入背景 ---
try:
    bg_img = pg.image.load(os.path.join('picture', 'labg_b.png')).convert()
    bg_img = pg.transform.scale(bg_img, (WIDTH, HEIGHT))
except:
    bg_img = pg.Surface((WIDTH, HEIGHT))
    bg_img.fill(WHITE)

# --- 雷射發射器圖片 ---
try:
    laser_emitter1_img = pg.image.load(os.path.join('picture', 'lab_laser_top.png')).convert_alpha()
    laser_emitter1_img = pg.transform.scale(laser_emitter1_img, (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)))
    laser_emitter_img = pg.transform.rotate(laser_emitter1_img, -18)
except:
    laser_emitter_img = pg.Surface((GRID_SIZE, GRID_SIZE))
    laser_emitter_img.fill(RED)

# --- 玩家手持鏡子圖片 ---
try:
    mirror_hold_image = pg.image.load(os.path.join('picture', 'lab_mirror_whole.png')).convert_alpha()
except:
    mirror_hold_image = pg.Surface((GRID_SIZE//2, GRID_SIZE//2))
    mirror_hold_image.fill(YELLOW)
mirror_hold_image = pg.transform.scale(mirror_hold_image, (int(GRID_SIZE * 0.6), int(GRID_SIZE * 0.6)))

# --- 載入鏡子的底圖 ---
try:
    mirror_base_image = pg.image.load(os.path.join('picture', 'lab_mirror_tile.png')).convert_alpha()
    mirror_base_image = pg.transform.scale(mirror_base_image, (GRID_SIZE, GRID_SIZE))
except:
    mirror_base_image = None

# --- 鏡子圖片載入與處理 ---
mirror_images = {}
try:
    img_original = pg.image.load(os.path.join('picture', 'lab_mirror_b.png')).convert_alpha()
    img_original = pg.transform.scale(img_original, (GRID_SIZE, GRID_SIZE))
    mirror_images = {
        45: img_original,
        135: pg.transform.rotate(img_original, 90)
    }
except:
    pass

# --- 終點圖片與通過圖片 ---
try:
    goal_img_raw = pg.image.load(os.path.join('picture', 'lab_detector.png')).convert_alpha()
    try:
        content_rect = goal_img_raw.get_bounding_rect(min_alpha=1)
        goal_img_cropped = goal_img_raw.subsurface(content_rect).copy()
    except:
        goal_img_cropped = goal_img_raw
    goal_img = pg.transform.smoothscale(goal_img_cropped, (GRID_SIZE, GRID_SIZE))
except:
    goal_img = None
try:
    goal_pass_raw = pg.image.load(os.path.join('picture', 'lab_detector_pass.png')).convert_alpha()
    try:
        content_rect2 = goal_pass_raw.get_bounding_rect(min_alpha=1)
        goal_pass_cropped = goal_pass_raw.subsurface(content_rect2).copy()
    except:
        goal_pass_cropped = goal_pass_raw
    goal_img_pass = pg.transform.smoothscale(goal_pass_cropped, (GRID_SIZE, GRID_SIZE))
except:
    goal_img_pass = None

# ==========================================
# 載入玩家圖片序列並等比例縮放
# ==========================================
player_images = []
image_files = ["u_stand.png", "u_s_l.png", "u_s_r.png"]
img_path_base = os.path.join("picture", "chuchutest")

# 設定目標高度：大約兩格 (1.9倍)
PLAYER_TARGET_HEIGHT = int(GRID_SIZE * 1.9)

for f_name in image_files:
    try:
        full_path = os.path.join(img_path_base, f_name)
        original = pg.image.load(full_path).convert_alpha()

        # 計算等比例縮放
        old_w, old_h = original.get_size()
        if old_h > 0:
            scale_factor = PLAYER_TARGET_HEIGHT / old_h
            new_w = int(old_w * scale_factor)
            
            scaled_img = pg.transform.smoothscale(original, (new_w, PLAYER_TARGET_HEIGHT))
            player_images.append(scaled_img)
            print(f"已載入並縮放: {f_name} -> {new_w}x{PLAYER_TARGET_HEIGHT}")
        else:
            player_images.append(original)

    except Exception as e:
        print(f"無法載入 {f_name}: {e}")
        fallback = pg.Surface((PLAYER_TARGET_HEIGHT//2, PLAYER_TARGET_HEIGHT), pg.SRCALPHA)
        pg.draw.rect(fallback, (0, 255, 255), (0,0,PLAYER_TARGET_HEIGHT//2, PLAYER_TARGET_HEIGHT))
        player_images.append(fallback)

if not player_images:
    fallback = pg.Surface((GRID_SIZE, GRID_SIZE*2), pg.SRCALPHA)
    pg.draw.rect(fallback, (0, 255, 255), (0,0,GRID_SIZE, GRID_SIZE*2))
    player_images = [fallback, fallback, fallback]


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
            OFFSET_X + self.col * GRID_SIZE + GRID_SIZE // 2,
            OFFSET_Y + self.row * GRID_SIZE + GRID_SIZE // 2
        )

    @property
    def rect(self):
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
        self.x = OFFSET_X + col * GRID_SIZE + GRID_SIZE//2
        self.y = OFFSET_Y + row * GRID_SIZE + GRID_SIZE//2
        self.holding = None
        self.adjust_mode = False
        
        self.facing_right = True
        self.is_moving = False
        self.anim_index = 0
        self.anim_timer = 0

    @property
    def pos(self):
        return (int(self.x), int(self.y))
    
    # [新增] 手部判定座標
    @property
    def hand_pos(self):
        # 1. 取得圖片高度
        h = PLAYER_TARGET_HEIGHT
        
        # 2. 圖片繪製的頂部 Y 座標 (draw_y) = self.y - h // 2
        # 3. 手部在圖片中的位置 = 頂部 + 65% 高度
        hand_y = (self.y - h // 2) + (h * 0.65)
        
        # X 軸保持中心，Y 軸使用手部位置
        return (int(self.x), int(hand_y))

    def update_logic_position(self):
        self.col = int((self.x - OFFSET_X) // GRID_SIZE)
        self.row = int((self.y - OFFSET_Y) // GRID_SIZE)

# ----------------- 建地圖 -----------------
grid = [[Tile(c, r) for r in range(ROWS)] for c in range(COLS)]

grid[0][5].mirror = Mirror(45)
grid[0][4].mirror = Mirror(45) 

player = Player(1, 1)

laser_source = (OFFSET_X + GRID_SIZE//2, OFFSET_Y + GRID_SIZE//2)
laser_direction = (1.0, 0.3)
goal_tile = grid[COLS-2][ROWS-2]
goal_passed = False

# ----------------- 助手函式 -----------------
def draw_laser_emitter():
    lx, ly = laser_source
    w = laser_emitter_img.get_width()
    h = laser_emitter_img.get_height()
    screen.blit(laser_emitter_img, (lx - w // 2, ly - h // 2))

def draw_grid():
    board_rect = pg.Rect(OFFSET_X, OFFSET_Y, COLS*GRID_SIZE, ROWS*GRID_SIZE)
    pg.draw.rect(screen, BLACK, board_rect, 3) 
    for c in range(COLS):
        for r in range(ROWS):
            t = grid[c][r]
            pg.draw.rect(screen, GRAY, t.rect, 1)

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
                s.blit(shadow_img, t.rect.topleft)
            else:
                m = Mirror(ang)
                p1, p2 = m.endpoints(t.center)
                pg.draw.line(s, (255, 255, 100, 80), p1, p2, 6)
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
                pg.draw.rect(screen, DARK_GRAY, t.rect, 2)
            if t.mirror:
                base_img = t.mirror.get_base_image()
                if base_img: screen.blit(base_img, t.rect.topleft)
                img = t.mirror.get_image()
                if img: screen.blit(img, t.rect.topleft)
                else:
                    p1, p2 = t.mirror.endpoints(t.center)
                    pg.draw.line(screen, BLACK, p1, p2, 6)
                    pg.draw.line(screen, YELLOW, p1, p2, 2)
    pg.draw.rect(screen, GREEN, goal_tile.rect, 4)
    if goal_img:
        img_to_draw = goal_img_pass if goal_passed and goal_img_pass else goal_img
        screen.blit(img_to_draw, goal_tile.rect.topleft)

def draw_player():
    x, y = player.pos 

    idx = player.anim_index % len(player_images)
    base_img = player_images[idx]

    if player.facing_right:
        current_img = pg.transform.flip(base_img, True, False)
    else:
        current_img = base_img

    w, h = current_img.get_width(), current_img.get_height()
    draw_x = x - w // 2
    draw_y = y - h // 2
    
    screen.blit(current_img, (draw_x, draw_y))

    if player.holding:
        holding_img = mirror_hold_image.copy()
        if player.holding.angle == 45:
            holding_img = pg.transform.rotate(holding_img, 90)
        
        m_w = holding_img.get_width()
        m_h = holding_img.get_height()
        
        m_draw_x = x - m_w // 2
        
        # 視覺繪製也是使用相同的邏輯：頂部 + 65% 高度
        hand_offset_y = int(h * 0.65) 
        m_draw_y = draw_y + hand_offset_y - m_h // 2

        screen.blit(holding_img, (m_draw_x, m_draw_y))

def point_near_line(point, p1, p2, threshold):
    px, py = point
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0: return False
    t = ((px-x1)*dx + (py-y1)*dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    nx = x1 + t * dx
    ny = y1 + t * dy
    return math.hypot(px-nx, py-ny) <= threshold

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
    step_size = 5.0
    x, y = float(laser_source[0]), float(laser_source[1])
    vx, vy = laser_direction
    mag = math.hypot(vx, vy)
    if mag == 0: return path, False
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
        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT: break
        
        c = int((x - OFFSET_X) // GRID_SIZE)
        r = int((y - OFFSET_Y) // GRID_SIZE)
        hit = False
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                cc, rr = c + dc, r + dr
                if 0 <= cc < COLS and 0 <= rr < ROWS:
                    t = grid[cc][rr]
                    if t.mirror:
                        p1, p2 = t.mirror.endpoints(t.center)
                        if point_near_line((x, y), p1, p2, 8):
                            vx, vy = reflect_vector(vx, vy, *p1, *p2)
                            reflections += 1
                            if reflections > 40: return path, reached_goal
                            x += vx*0.6
                            y += vy*0.6
                            path.append((x, y))
                            hit = True
                            break
            if hit: break
    return path, reached_goal

def draw_laser_path(path):
    if len(path) < 2: return
    pg.draw.lines(screen, RED, False, path, 5)
    draw_laser_emitter()

def tile_at_pixel(px, py):
    c = int((px - OFFSET_X) // GRID_SIZE)
    r = int((py - OFFSET_Y) // GRID_SIZE)
    if 0 <= c < COLS and 0 <= r < ROWS: return grid[c][r]
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
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_r: # Reset
                for c in range(COLS):
                    for r in range(ROWS):
                        grid[c][r].mirror = None
                grid[0][5].mirror = Mirror(45)
                grid[0][4].mirror = Mirror(45) 
                player.holding = None
                player.adjust_mode = False
                laser_path_cache = []
                laser_reached_goal = False
                last_laser_path = []
                player.anim_index = 0
                player.is_moving = False
                player.facing_right = True
                goal_passed = False

            if event.key == pg.K_f: # Fire
                last_mirrors = [(c,r,grid[c][r].mirror.angle) for c in range(COLS) for r in range(ROWS) if grid[c][r].mirror]
                laser_path_cache, laser_reached_goal = fire_laser_and_get_path()
                last_laser_path = laser_path_cache[:]
                if laser_reached_goal:
                    goal_passed = True

            if event.key == pg.K_e: # Interact
                # [修改] 使用 hand_pos 進行判定
                t = tile_at_pixel(*player.hand_pos)
                
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
                        player.is_moving = False
                        player.anim_index = 0

            if event.key == pg.K_q and player.adjust_mode:
                player.adjust_mode = False
                laser_path_cache = []

            if event.key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                if player.adjust_mode and player.holding:
                    player.holding.angle = 135 if player.holding.angle == 45 else 45
                    laser_path_cache = []

    player.is_moving = False

    if not player.adjust_mode:
        keys = pg.key.get_pressed()
        dx = dy = 0

        if keys[pg.K_LEFT]:
            dx -= 1
            player.facing_right = False
        if keys[pg.K_RIGHT]:
            dx += 1
            player.facing_right = True
        if keys[pg.K_UP]:
            dy -= 1
        if keys[pg.K_DOWN]:
            dy += 1

        if dx or dy:
            player.is_moving = True 
            laser_path_cache = []
            laser_reached_goal = False
            l = math.hypot(dx, dy)
            if l != 0:
                dx, dy = dx/l, dy/l
            player.x += dx * PLAYER_SPEED * (dt / 1000)
            player.y += dy * PLAYER_SPEED * (dt / 1000)

            min_x = 0#OFFSET_X + GRID_SIZE//2
            max_x = screen.get_width()#OFFSET_X + COLS*GRID_SIZE - GRID_SIZE//2
            min_y = OFFSET_Y + GRID_SIZE//2
            max_y = OFFSET_Y + ROWS*GRID_SIZE - GRID_SIZE//2
            player.x = max(min_x, min(max_x, player.x))
            player.y = max(min_y, min(max_y, player.y))
            player.update_logic_position()

    if player.is_moving:
        player.anim_timer += dt
        if player.anim_timer >= ANIMATION_DELAY:
            player.anim_timer = 0
            player.anim_index += 1
            if player.anim_index > 2:
                player.anim_index = 1
    else:
        player.anim_index = 0
        player.anim_timer = 0

    screen.fill(BLACK)
    screen.blit(bg_img, (0, 0))
    draw_grid()
    draw_shadow_laser(last_laser_path)
    draw_shadow_mirrors(last_mirrors)
    draw_tiles_contents()
    draw_player() 

    # [修改] UI 提示也根據手的位置顯示
    cur_tile = tile_at_pixel(*player.hand_pos)
    
    if cur_tile and cur_tile.mirror:
        screen.blit(font.render("按E撿起鏡子", True, BLACK), (30, 30))
    elif player.holding and cur_tile and cur_tile.can_place and cur_tile.mirror is None and not player.adjust_mode:
        screen.blit(font.render("按E可調整鏡子角度", True, BLACK), (30, 30))

    if player.adjust_mode and player.holding:
        img = player.holding.get_image()
        # 在調整模式下，鏡子會顯示在手部判定到的格子
        target_rect = cur_tile.rect if cur_tile else pg.Rect(0,0,0,0)
        
        if img: screen.blit(img, target_rect.topleft)
        else:
            p1, p2 = player.holding.endpoints(cur_tile.center)
            pg.draw.line(screen, BLACK, p1, p2, 6)
            pg.draw.line(screen, YELLOW, p1, p2, 2)
        screen.blit(font.render("調整模式: 方向鍵=旋轉, E=確認, Q=取消", True, BLACK), (300, HEIGHT - 30))
        screen.blit(font.render(f"角度: {player.holding.angle}°", True, BLACK), (WIDTH - 160, HEIGHT - 30))

    if not laser_path_cache:
        lx, ly = laser_source
        vx, vy = laser_direction
        mag = math.hypot(vx, vy)
        if mag != 0:
            nx, ny = vx/mag, vy/mag
            pg.draw.line(screen, (180,60,60), laser_source, (lx+nx*40, ly+ny*40), 4)
        draw_laser_emitter()
        screen.blit(font.render("按F發射雷射光", True, BLACK), (WIDTH - 220, 10))

    if laser_path_cache:
        draw_laser_path(laser_path_cache)
        msg = "成功!" if laser_reached_goal else "失敗!"
        color = GREEN if laser_reached_goal else RED
        screen.blit(font.render(msg, True, color), (WIDTH - 100, 30))

    legend = ["方向鍵: 移動", "E: 撿起/放置", "Q: 取消調整", "F: 發射雷射", "R: 重設"]
    for i, s in enumerate(legend):
        screen.blit(font.render(s, True, BLACK), (10, HEIGHT - 110 + i*18))

    pg.display.flip()

pg.quit()
sys.exit()
