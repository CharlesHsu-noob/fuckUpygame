import pygame as pg
import math
import sys
import os

pg.init()

# ----------------- 參數 -----------------
GRID_SIZE = 79
COLS = 16
ROWS = 6
WIDTH, HEIGHT = 1920,1080
FPS = 60
PLAYER_SPEED = 300 # 平滑移動速度（px/sec）
OFFSET_X = 330
OFFSET_Y = 460
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
overlay_font = pg.font.SysFont("Microsoft JhengHei", 96)

screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Bob")

clock = pg.time.Clock()
# --- 載入背景 ---
bg_img = pg.image.load(os.path.join('picture', 'labb_g.png')).convert()
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

# --- 雷射發射器圖片 ---
# 修改這部分，確保我們有「乾淨」的原始圖片
laser_emitter_base_blue = pg.image.load(os.path.join('picture', 'lab_laser_top_2.png')).convert_alpha()
laser_emitter_base_blue = pg.transform.scale(laser_emitter_base_blue, (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)))

laser_emitter_base_red = pg.image.load(os.path.join('picture', 'lab_laser_top_3.png')).convert_alpha()
laser_emitter_base_red = pg.transform.scale(laser_emitter_base_red, (int(GRID_SIZE * 1.5), int(GRID_SIZE * 1.5)))

# --- 玩家手持鏡子圖片 ---
mirror_hold_image = pg.image.load(os.path.join('picture', 'lab_mirror_whole.png')).convert_alpha()
mirror_hold_image = pg.transform.scale(mirror_hold_image,(int(GRID_SIZE * 0.6), int(GRID_SIZE * 0.6)))

# --- 角色站立圖片 ---
stand_img = pg.image.load(os.path.join('picture', 'stand.png')).convert_alpha()
stand_img = pg.transform.scale(stand_img, (int(GRID_SIZE * 1.3), int(GRID_SIZE * 1.5)))

# --- 載入鏡子的底圖 ---
mirror_base_image = pg.image.load(os.path.join('picture', 'lab_mirror_tile.png')).convert_alpha()
mirror_base_image = pg.transform.scale(mirror_base_image, (GRID_SIZE, GRID_SIZE))  # 縮放到底圖大小

# --- 修正後的圖片載入與處理（單圖旋轉） ---
mirror_images = {}

# 載入原始圖片 (假設它是 45 度角圖案)
img_original = pg.image.load(os.path.join('picture', 'lab_mirror_b.png')).convert_alpha()
img_original = pg.transform.scale(img_original, (GRID_SIZE, GRID_SIZE))

# 45 度圖片：使用原始圖片
img_45 = img_original

# 135 度圖片：將 45 度圖片旋轉 90 度 (逆時針) 
# 這樣 / 圖案就會變成 \ 圖案
img_135 = pg.transform.rotate(img_original, 90) 
    
# 將旋轉後的圖片儲存在字典中
mirror_images = {
    45: img_45,
    135: img_135
}

# ----------------- 載入音效 -----------------
try:
    # 嘗試載入受傷音效
    hit_sound = pg.mixer.Sound(os.path.join('sean', 'battle', 'voice', 'snake_d.ogg'))
except:
    try:
        # 如果失敗，嘗試往上一層找 (針對不同執行目錄)
        hit_sound = pg.mixer.Sound(os.path.join('..', 'sean', 'battle', 'voice', 'snake_d.ogg'))
    except:
        print("Warning: snake_d.ogg not found")
        hit_sound = None

# ----------------- 新增：旋轉控制參數 -----------------
turret_angle = 0.0       # 目前角度 (0度 = 水平向右)
turret_speed = 30.0      # 旋轉速度 (每秒轉動的度數)
turret_direction = 1     # 1 表示向下轉，-1 表示向上轉
cycle_start_time = pg.time.get_ticks() # 循環計時起點

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
        # 這是決定反射行為的數學線段，不受繪圖方式影響
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
grid[0][3].mirror = Mirror(45)

player = Player(1, 1)

# 雷射來源：修正為相對 Grid 的位置 + Offset
laser_source = (OFFSET_X + GRID_SIZE//2 +10, OFFSET_Y + GRID_SIZE//2)
laser_direction = (1.0, 0.3)

emitter_hitbox_w = int(GRID_SIZE * 0.6)
emitter_hitbox_h = int(GRID_SIZE * 0.6)

# ----------------- 助手函式 -----------------
# 修改後的函式，增加 img 參數
def draw_laser_emitter(base_img, angle):
    # 使用 -angle 因為 Pygame 旋轉方向是逆時針，我們需要順時針(向下)轉
    # 這裡的 base_img 必須是原始沒轉過的圖
    rotated_img = pg.transform.rotate(base_img, -angle)
    rect = rotated_img.get_rect(center=laser_source)
    screen.blit(rotated_img, rect.topleft)

def draw_grid():
    # 畫個外框幫助除錯，確認格子有沒有對齊背景
    board_rect = pg.Rect(OFFSET_X, OFFSET_Y, COLS*GRID_SIZE, ROWS*GRID_SIZE)
    pg.draw.rect(screen, BLACK, board_rect, 3) 
    for c in range(COLS):
        for r in range(ROWS):
            t = grid[c][r]

            # ❌ 移除實心白色方塊
            # pg.draw.rect(screen, WHITE, t.rect)

            # （可選）可放置區塊用半透明顏色顯示
            if t.can_place:
                pass  # 什麼都不畫，背景自然透出

            # ✅ 只畫格線（邊框）
            pg.draw.rect(screen, GRAY, t.rect, 1)


def draw_shadow_mirrors(last_mirrors):
    if not last_mirrors:
        return
    s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    for c, r, ang in last_mirrors:
        if 0 <= c < COLS and 0 <= r < ROWS:
            t = grid[c][r]
            
            img = mirror_images.get(ang)
            if img:
                shadow_img = img.copy()
                shadow_img.set_alpha(80) 
                s.blit(shadow_img, t.rect.topleft) # 使用 rect.topleft 自動包含 offset
            else:
                # 圖片載入失敗時的回退
                m = Mirror(ang)
                p1, p2 = m.endpoints(t.center)
                pg.draw.line(s, (255, 255, 100, 80), p1, p2, 6)
                
    screen.blit(s, (0, 0))

def draw_shadow_laser(last_laser_path):
    if len(last_laser_path) < 2:
        return
    s = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    pg.draw.lines(s, (255, 0, 0, 80), False, last_laser_path, 3)
    screen.blit(s, (0, 0))

# 修改繪製鏡子的函數
def draw_tiles_contents():
    for c in range(COLS):
        for r in range(ROWS):
            t = grid[c][r]
            if t.can_place:
                pg.draw.rect(screen, DARK_GRAY, t.rect, 2)
                
            if t.mirror:
                # 先繪製鏡子的底圖
                base_img = t.mirror.get_base_image()
                if base_img:
                    screen.blit(base_img, t.rect.topleft)
                
                # 然後繪製鏡子本身
                img = t.mirror.get_image()
                if img :
                    screen.blit(img, t.rect.topleft)
                else:
                    # 如果沒有底圖，就繪製鏡子的反射線（回退）
                    p1, p2 = t.mirror.endpoints(t.center)
                    pg.draw.line(screen, BLACK, p1, p2, 6)
                    pg.draw.line(screen, YELLOW, p1, p2, 2)

    pass

def draw_player():
    x, y = player.pos
    radius = GRID_SIZE // 3

    img = stand_img
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect.topleft)

    if player.holding:
        # 複製手持鏡子圖片，避免影響原圖
        holding_img = mirror_hold_image.copy()

        # 玩家手持鏡子角度是 45，就旋轉 90 度
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
    if dx == 0 and dy == 0:
        return False
    t = ((px-x1)*dx + (py-y1)*dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    nx = x1 + t * dx
    ny = y1 + t * dy
    return math.hypot(px-nx, py-ny) <= threshold

def reflect_vector(vx, vy, x1, y1, x2, y2):
    # 計算線段法向量並進行反射
    dx, dy = x2-x1, y2-y1
    nx, ny = -dy, dx # 法向量 (垂直於線段)
    l = math.hypot(nx, ny)
    if l == 0:
        return vx, vy
    nx, ny = nx/l, ny/l
    dot = vx*nx + vy*ny
    # 反射公式
    return (vx - 2*dot*nx, vy - 2*dot*ny)

def fire_laser_and_get_path():
    path = []
    max_steps = 6000
    step_size = 5.0

    lx, ly = float(laser_source[0]), float(laser_source[1])
    vx, vy = laser_direction
    mag = math.hypot(vx, vy)
    if mag == 0:
        return path, 0
    ux, uy = vx/mag, vy/mag
    start_offset = max(emitter_hitbox_w, emitter_hitbox_h) * 0.5 + 8
    x, y = lx + ux * start_offset, ly + uy * start_offset
    vx, vy = ux * step_size, uy * step_size

    reflections = 0

    # 優化邊界檢查 (只在畫面內運算)
    screen_rect = pg.Rect(0, 0, WIDTH, HEIGHT)

    for _ in range(max_steps):
        x += vx
        y += vy
        path.append((x, y))

        pass

        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            break

        # 座標轉 Grid
        c = int((x - OFFSET_X) // GRID_SIZE)
        r = int((y - OFFSET_Y) // GRID_SIZE)
        hit = False
        
        # 檢查周圍九宮格的鏡子
        for dc in (-1, 0, 1):
            for dr in (-1, 0, 1):
                cc = c + dc
                rr = r + dr
                if 0 <= cc < COLS and 0 <= rr < ROWS:
                    t = grid[cc][rr]
                    if t.mirror:
                        # 使用 Mirror 物件的 endpoints 來獲取數學線段
                        p1, p2 = t.mirror.endpoints(t.center)
                        
                        # 判斷雷射是否靠近這條線段（碰撞檢測）
                        if point_near_line((x, y), p1, p2, 8):
                            # 使用 reflect_vector 函式計算反射
                            vx, vy = reflect_vector(vx, vy, *p1, *p2)
                            
                            reflections += 1
                            if reflections > 40:
                                return path, reflections
                            
                            # 稍微移動雷射，防止立即再次碰撞
                            x += vx*0.6
                            y += vy*0.6
                            path.append((x, y))
                            hit = True
                            break
            if hit:
                break

    return path, reflections

def draw_laser_path(path):
    if len(path) < 2:
        return
    pg.draw.lines(screen, RED, False, path, 5)
    # 注意：這裡移除 draw_laser_emitter() 的呼叫，統一在主迴圈繪製

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
last_fire_time = 0
fire_check_pending = False
freeze_active = False
player_max_hp = 100
player_hp = 100
damage_applied_for_shot = False
game_over = False
last_reflections_count = 0

# 新增：循環計時器的起始時間
cycle_start_time = pg.time.get_ticks()

running = True
while running:
    dt = clock.tick(FPS)
    now = pg.time.get_ticks()
    elapsed = now - cycle_start_time
    # 計算目前循環經過的毫秒數
    current_time = pg.time.get_ticks()
    elapsed_time = current_time - cycle_start_time

    # 判斷目前的砲台狀態與是否發射
    current_base_img = laser_emitter_base_blue

    # --- 時間參數設定 ---
    PHASE_BLUE = 5000       # 藍色追蹤時間 (5秒)
    PHASE_RED = 1000        # 紅色鎖定時間 (1秒)
    TOTAL_CYCLE = PHASE_BLUE + PHASE_RED # 總週期 6.0秒
    FREEZE_DURATION = 500   # 發射前定身時間 (0.5秒)

    # --- A. 追蹤玩家瞄準 ---
    # 只有在藍色階段才追蹤 (紅燈時鎖定角度)
    if elapsed_time < PHASE_BLUE:
        dx_track = player.x - laser_source[0]
        dy_track = player.y - laser_source[1]
        turret_angle = math.degrees(math.atan2(dy_track, dx_track))

    rad = math.radians(turret_angle)
    laser_direction = (math.cos(rad), math.sin(rad))

    # 定身判定
    freeze_active = (elapsed_time >= (TOTAL_CYCLE - FREEZE_DURATION) and elapsed_time < TOTAL_CYCLE)

    if elapsed_time < PHASE_BLUE:
        current_base_img = laser_emitter_base_blue
    elif elapsed_time < TOTAL_CYCLE:
        current_base_img = laser_emitter_base_red
    elif elapsed_time >= TOTAL_CYCLE:
        # 1. 執行發射運算
        last_mirrors = [
            (c, r, grid[c][r].mirror.angle)
            for c in range(COLS)
            for r in range(ROWS)
            if grid[c][r].mirror
        ]
        laser_path_cache, last_reflections_count = fire_laser_and_get_path()
        last_laser_path = laser_path_cache[:]
        last_fire_time = current_time
        fire_check_pending = True
        r_hit = GRID_SIZE // 3
        if not damage_applied_for_shot:
            for (px, py) in laser_path_cache:
                if math.hypot(px - player.x, py - player.y) <= r_hit:
                    player_hp = max(0, player_hp - 25)
                    damage_applied_for_shot = True
                    if hit_sound:
                        hit_sound.play()
                    break
        if player_hp <= 0:
            game_over = True
        # 2. 重置計時器
        cycle_start_time = current_time
        current_base_img = laser_emitter_base_blue
        freeze_active = False
        damage_applied_for_shot = False

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
                grid[0][5].mirror = Mirror(45)
                grid[0][4].mirror = Mirror(45) 
                grid[0][3].mirror = Mirror(45)
                player.holding = None
                player.adjust_mode = False
                laser_path_cache = []
                laser_reached_goal = False
                last_laser_path = []
                last_mirrors = []
                # 重設時也要重置循環時間
                cycle_start_time = pg.time.get_ticks()

            # -------- (原本的 F 鍵發射雷射已移除) --------

            # -------- E 互動（撿/放/調整）--------
            if event.key == pg.K_e:
                t = tile_at_pixel(player.x, player.y)
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

    #     平滑移動
    if not player.adjust_mode and not freeze_active and not game_over:
        keys = pg.key.get_pressed()
        dx = dy = 0
        if keys[pg.K_LEFT]: dx -= 1
        if keys[pg.K_RIGHT]: dx += 1
        if keys[pg.K_UP]: dy -= 1
        if keys[pg.K_DOWN]: dy += 1

        if dx or dy:
            laser_path_cache = []
            laser_reached_goal = False
            l = math.hypot(dx, dy)
            if l != 0:
                dx /= l
                dy /= l
            player.x += dx * PLAYER_SPEED * (dt / 1000)
            player.y += dy * PLAYER_SPEED * (dt / 1000)

            min_x =0 #OFFSET_X + GRID_SIZE//2
            max_x =screen.get_width() #OFFSET_X + COLS*GRID_SIZE - GRID_SIZE//2
            min_y = 100#OFFSET_Y + GRID_SIZE//2
            max_y = screen.get_height()-130#OFFSET_Y + ROWS*GRID_SIZE - GRID_SIZE//2
            player.x = max(min_x, min(max_x, player.x))
            player.y = max(min_y, min(max_y, player.y))
            player.update_logic_position()

    if fire_check_pending and (pg.time.get_ticks() - last_fire_time) >= 500:
        cx, cy = laser_source
        hitbox = pg.Rect(cx - emitter_hitbox_w // 2, cy - emitter_hitbox_h // 2, emitter_hitbox_w, emitter_hitbox_h)
        hit = False
        for (px, py) in laser_path_cache:
            if hitbox.collidepoint(int(px), int(py)):
                hit = True
                break
        laser_reached_goal = (hit and last_reflections_count >= 3)
        fire_check_pending = False
    # ================== 畫畫面 ==================
    screen.fill(BLACK)
    screen.blit(bg_img, (0, 0))
    draw_grid()
    draw_shadow_laser(last_laser_path)
    draw_shadow_mirrors(last_mirrors)
    draw_tiles_contents()
    draw_player()
    bar_w = 200
    bar_h = 20
    bx, by = 20, 20
    pg.draw.rect(screen, (60, 60, 60), (bx, by, bar_w, bar_h))
    fill_w = int(bar_w * (player_hp / player_max_hp))
    pg.draw.rect(screen, (200, 50, 50), (bx, by, fill_w, bar_h))
    screen.blit(font.render(f"HP: {player_hp}/{player_max_hp}", True, BLACK), (bx + 210, by))

    # 瞄準提示線 (隨砲台轉動)
    if not laser_path_cache:
        lx, ly = laser_source
        dx, dy = laser_direction
        m = math.hypot(dx, dy)
        if m != 0:
            ux, uy = dx/m, dy/m
            start_offset = max(emitter_hitbox_w, emitter_hitbox_h) * 0.5 + 8
            sx, sy = lx + ux * start_offset, ly + uy * start_offset
            end_p = (sx + ux * 60, sy + uy * 60)
            pg.draw.line(screen, (200, 50, 50), (sx, sy), end_p, 3)

    draw_laser_emitter(current_base_img, turret_angle)
    cx, cy = laser_source
    hitbox = pg.Rect(cx - emitter_hitbox_w // 2, cy - emitter_hitbox_h // 2, emitter_hitbox_w, emitter_hitbox_h)
    # 顯示砲台判定範圍（DEBUG）
    #pg.draw.rect(screen, (0, 255, 0), hitbox, 2)

    # 互動提示
    cur_tile = tile_at_pixel(player.x, player.y)
    if cur_tile and cur_tile.mirror:
        screen.blit(font.render("按E撿起鏡子", True, BLACK), (30, 45))
    elif player.holding and cur_tile and cur_tile.can_place and cur_tile.mirror is None and not player.adjust_mode:
        screen.blit(font.render("按E可調整鏡子角度", True, BLACK), (30, 45))

    # 調整模式預覽
    if player.adjust_mode and player.holding:
        center = cur_tile.center
        img = player.holding.get_image()
        if img:
            screen.blit(img, cur_tile.rect.topleft)
        else:
            p1, p2 = player.holding.endpoints(center)
            pg.draw.line(screen, BLACK, p1, p2, 6)
            pg.draw.line(screen, YELLOW, p1, p2, 2)
        screen.blit(font.render("調整模式: 方向鍵=旋轉, E=確認, Q=取消", True, BLACK), (300, HEIGHT - 30))
        screen.blit(font.render(f"角度: {player.holding.angle}°", True, BLACK), (WIDTH - 160, HEIGHT - 30))

    # 未發射的雷射提示線
    if not laser_path_cache:
        lx, ly = laser_source
        vx, vy = laser_direction
        mag = math.hypot(vx, vy)
        if mag != 0:
            nx, ny = vx/mag, vy/mag
            start_offset = max(emitter_hitbox_w, emitter_hitbox_h) * 0.5 + 8
            sx, sy = lx + nx * start_offset, ly + ny * start_offset
            tip_len = 40
            end_pos = (sx + nx*tip_len, sy + ny*tip_len)
            pg.draw.line(screen, (180,60,60), (sx, sy), end_pos, 4)

    if game_over:
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        t = overlay_font.render("失敗", True, RED)
        tr = t.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(t, tr.topleft)
    
    # 顯示倒數計時資訊 (可選)
    time_left = max(0, 6000 - elapsed_time) / 1000
    timer_color = RED if elapsed_time >= 5000 else BLACK
    screen.blit(font.render(f"下次發射: {time_left:.1f}秒", True, timer_color), (WIDTH - 220, 10))

    # 畫雷射路徑
    if laser_path_cache:
        draw_laser_path(laser_path_cache)
        if laser_reached_goal and not game_over:
            overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            t = overlay_font.render("成功!", True, GREEN)
            tr = t.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(t, tr.topleft)

    # 下方 legend (移除 F 的說明)
    legend = [
        "方向鍵: 移動 / 轉動鏡子 (調整模式)",
        "E: 撿起 / 放置",
        "Q: 取消調整",
        "R: 重新開始 (重置計時)"
        "                      要利用到三個鏡子才算通關!!!"
    ]
    for i, s in enumerate(legend):
        screen.blit(font.render(s, True, RED), (10, HEIGHT - 110 + i*18))

    pg.display.flip()

pg.quit()
sys.exit()
