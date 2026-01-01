import pygame as pg
import sys
import os

# ================= 初始化 =================
pg.init()

# --- 世界大小（邏輯用，不變） ---
WORLD_WIDTH, WORLD_HEIGHT = 1350, 600

# --- 實際視窗大小 ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1080
screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Climbing Game")

clock = pg.time.Clock()
FPS = 60

# --- 虛擬畫面（所有遊戲內容畫在這） ---
world_surface = pg.Surface((WORLD_WIDTH, WORLD_HEIGHT), pg.SRCALPHA)

# --- 等比例縮放計算 ---
scale_x = WINDOW_WIDTH / WORLD_WIDTH
scale_y = WINDOW_HEIGHT / WORLD_HEIGHT
SCALE = min(scale_x, scale_y)

scaled_width = int(WORLD_WIDTH * SCALE)
scaled_height = int(WORLD_HEIGHT * SCALE)
offset_x = (WINDOW_WIDTH - scaled_width) // 2
offset_y = (WINDOW_HEIGHT - scaled_height) // 2


# ================= 顏色 =================
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BLUE = (0, 100, 255)
RED = (255, 0, 0) # 除錯用紅色

# 請確保你的圖片路徑正確，若無圖片可先註解掉 image.load 改用 fill
bg_img_raw = pg.image.load(os.path.join("picture", "forest_e.png")).convert()
bg_img_full = pg.transform.scale(bg_img_raw, (2000, 3500))

# ================= 玩家圖片 =================
player_img = pg.image.load(os.path.join("picture", "stand.png")).convert_alpha()
PLAYER_WIDTH = 48
PLAYER_HEIGHT = 64
player_img = pg.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
# 這裡原本有重設 PLAYER_WIDTH，稍微修正邏輯保留圖片寬度
# PLAYER_WIDTH = 16 (原始代碼這行會讓圖片與碰撞箱大小不一致，暫時保留你的設定)
PLAYER_WIDTH = 16 
char_half_w=24

# ================= 玩家設定 =================
class char(pg.sprite.Sprite):
    def __init__(self,image:pg.surface.Surface,player_x,player_y):
        super().__init__()
        self.image=image
        self.rect=self.image.get_rect(center=(player_x,player_y))

player_x = 1350
player_y = 300 # 玩家初始位置
bg_scroll_anchor_y = 300 # 背景捲動基準點
BG_SCROLL_ANCHOR_INITIAL = bg_scroll_anchor_y
player_vx = 0
player_vy = 0
char_u=char(player_img,player_x,player_y)
MOVE_SPEED = 2
JUMP_SPEED = -11
GRAVITY = 0.6

# 跳躍控制
jump_pressed = False
COYOTE_TIME = 0.12
time_since_ground = 0

# --- 跳躍冷卻設定 ---
JUMP_COOLDOWN = 750  # 毫秒 
last_jump_time = -750 

# ================= 平台設定 =================
class platOb(pg.sprite.Sprite):
    def __init__(self,image:pg.surface.Surface,pos:tuple[int,int]):
        super().__init__()
        self.image=image
        self.rect=self.image.get_rect(center=pos)
PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 15

platform_positions = [
    (-60, 322),(20, 322),(100, 322),(180, 322),(260, 322),(340, 322),(420, 322),
    (500, 322),(580, 322),(660, 322),(740, 322),(820, 322),(900, 322),(980, 322),
    (1060, 322),(1140, 322),(1220, 322),(1300, 322),
    (550, 240),(850, 230),(650, 160),(700, 90),(630, 10),
    (550, -80),(620, -160),(760, -230),(800, -300),(750, -380),
    (700, -450),(620, -530),(550, -590),(500, -640),(450, -693),(370, -693),(290, -693),(210, -693),(130, -693),(50, -693),(-30, -693)
]

# 定義要隱藏的岩石座標
hidden_rock_coords = [
    (290, -693), (210, -693), (130, -693), (50, -693), (-30, -693)
]

platforms = [pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT) for x, y in platform_positions]
ground = platforms[:18]

rock_img = pg.image.load(os.path.join("picture", "forest_rock.png")).convert_alpha()
rock_img = pg.transform.scale(rock_img, (PLATFORM_WIDTH, PLATFORM_HEIGHT))

platform_object=[]
for pos in platform_positions:
    wall=platOb(rock_img,pos)
    platform_object.append(wall)

# ================= [新增] 左側隱形牆壁設定 =================
# x = -100 (在最左邊平台 -60 的更左邊)
# y = -5000 (設很高，確保往上跳也擋得住)
# w = 40 (厚度)
# h = 6000 (高度，確保覆蓋整個遊戲垂直範圍)
debug_wall = pg.Rect(320, 100, 40, 6000)

# 將牆壁加入 platforms 列表，這樣它就會自動擁有碰撞和捲動功能
platforms.append(debug_wall)
# ========================================================


# ================= 判斷是否站在平台 =================
offset_for_plat_x=48
def is_on_platform(px, py):
    for plat in platforms:
        if plat.colliderect(px, py,PLAYER_WIDTH,PLAYER_HEIGHT):
            return True
    return False

# ================= 捲動設定 =================
SCROLL_UP_TRIGGER_Y = WORLD_HEIGHT * 0.35
SCROLL_DOWN_TRIGGER_Y = 250 

# ================= 遊戲主迴圈 =================
running = True
while running:
    dt = clock.tick(FPS) / 1000
    current_time = pg.time.get_ticks()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            
    # ---------- 操作 ----------
    keys = pg.key.get_pressed()
    player_vx = 0
    if keys[pg.K_LEFT]:
        player_vx = -MOVE_SPEED
    if keys[pg.K_RIGHT]:
        player_vx = MOVE_SPEED

    # ---------- 土狼時間 ----------
    if is_on_platform(player_x, player_y):
        time_since_ground = 0
    else:
        time_since_ground += dt

    # ---------- 跳躍 ----------
    if keys[pg.K_SPACE]:
        if not jump_pressed and time_since_ground <= COYOTE_TIME:
            if current_time - last_jump_time > JUMP_COOLDOWN: 
                player_vy = JUMP_SPEED
                jump_pressed = True
                time_since_ground = COYOTE_TIME + 1 
                last_jump_time = current_time       
    else:
        jump_pressed = False

    # ---------- 水平移動 ----------
    player_x += player_vx
    player_rect = pg.Rect(
        player_x - PLAYER_WIDTH // 2,
        player_y - PLAYER_HEIGHT,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )
    
    # 碰撞檢測 (包含新增的牆壁)
    for i in range(len(platforms)):
        plat = platforms[i]
        if player_rect.colliderect(plat):
            if player_vx > 0:
                player_x = plat.left - PLAYER_WIDTH // 2
            elif player_vx < 0:
                player_x = plat.right + PLAYER_WIDTH // 2

    # ---------- 垂直移動 ----------
    player_vy += GRAVITY
    player_y += player_vy

    player_rect = pg.Rect(
        player_x - PLAYER_WIDTH // 2,
        player_y - PLAYER_HEIGHT,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )

    for plat in platforms:
        if player_rect.colliderect(plat):
            if player_vy > 0:
                player_y = plat.top
                player_vy = 0
                time_since_ground = 0
            elif player_vy < 0:
                player_y = plat.bottom + PLAYER_HEIGHT
                player_vy = 0

    # ---------- 邊界 ----------
    player_x = max(
        PLAYER_WIDTH ,
        min(WORLD_WIDTH - PLAYER_WIDTH // 2, player_x)
    )
    
    # ---------- 向上捲動 ----------
    if player_y < SCROLL_UP_TRIGGER_Y:
        scroll = SCROLL_UP_TRIGGER_Y - player_y
        int_scroll = int(scroll)
        player_y += int_scroll
        for plat in platforms:
            plat.y += int_scroll
        
        new_hidden_coords = []
        for h_coord in hidden_rock_coords:
            new_hidden_coords.append((h_coord[0], h_coord[1] + int_scroll))
        hidden_rock_coords = new_hidden_coords
        
        bg_scroll_anchor_y += int_scroll

    # ---------- 向下捲動 ----------
    INITIAL_GROUND_Y = 322
    if player_y > SCROLL_DOWN_TRIGGER_Y:
        raw_scroll = player_y - SCROLL_DOWN_TRIGGER_Y
        int_scroll = int(raw_scroll)

        if platforms[0].y - int_scroll < INITIAL_GROUND_Y:
            int_scroll = platforms[0].y - INITIAL_GROUND_Y

        if int_scroll > 0:
            player_y -= int_scroll
            for plat in platforms:
                plat.y -= int_scroll
            
            new_hidden_coords = []
            for h_coord in hidden_rock_coords:
                new_hidden_coords.append((h_coord[0], h_coord[1] - int_scroll))
            hidden_rock_coords = new_hidden_coords

            bg_scroll_anchor_y -= int_scroll
            bg_scroll_anchor_y = max(bg_scroll_anchor_y, BG_SCROLL_ANCHOR_INITIAL)


    # ================= 繪製（畫在 world_surface） =================
    world_surface.fill((0, 0, 0, 0))

    for plat in platforms:
        # === [新增] 繪製除錯牆壁 (紅色) ===
        if plat == debug_wall:
            pass # 畫出紅色矩形
        # ================================
        elif plat in ground:
            pass
        elif plat.topleft in hidden_rock_coords:
            pass
        else:
            world_surface.blit(rock_img, plat.topleft)
            
    blit_offset_y=5
    blit_offset_x=15
    world_surface.blit(
        player_img,
        (player_x - PLAYER_WIDTH // 2-blit_offset_x, player_y - PLAYER_HEIGHT+blit_offset_y)
    )

    # ================= 縮放顯示 =================
    scaled_surface = pg.transform.smoothscale(
        world_surface,
        (scaled_width, scaled_height)
    )

    screen.fill(BLACK)

    # 背景繪製
    bg_scroll_speed = 2.0
    bg_start_y = 480 - 3500
    bg_y = bg_start_y + (bg_scroll_anchor_y) * bg_scroll_speed
    
    if bg_y > 0: bg_y = 0
    if bg_y < 1080 - 3500: bg_y = 1080 - 3500

    bg_x = (WINDOW_WIDTH - 2000) // 2
    screen.blit(bg_img_full, (bg_x, bg_y))

    screen.blit(scaled_surface, (offset_x, offset_y))
    pg.display.flip()
    
    char_u.rect=char_u.image.get_rect(center=(player_x,player_y))
    
pg.quit()
sys.exit()