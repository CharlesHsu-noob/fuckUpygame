import pygame as pg
import sys
import os

# ================= 初始化 =================
pg.init()

# --- 世界大小（邏輯用，不變） ---
WORLD_WIDTH, WORLD_HEIGHT = 500, 600

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

bg_img_raw = pg.image.load(os.path.join("picture", "forest_e.png")).convert()
bg_img_full = pg.transform.scale(bg_img_raw, (2000, 3500))

# ================= 玩家圖片 =================
player_img = pg.image.load(os.path.join("picture", "stand.png")).convert_alpha()
PLAYER_WIDTH = 48
PLAYER_HEIGHT = 64
player_img = pg.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
PLAYER_WIDTH = 16
char_half_w=24

# ================= 玩家設定 =================
class char(pg.sprite.Sprite):
    def __init__(self,image:pg.surface,player_x,player_y):
        super().__init__()
        self.image=image
        self.rect=self.image.get_rect(center=(player_x,player_y))
player_x = 450
player_y = 300 # 玩家初始位置
bg_scroll_anchor_y = 300 # 背景捲動基準點 (與初始位置相同，讓一開始背景位置正確)
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

# --- 新增：跳躍冷卻設定 ---
JUMP_COOLDOWN = 750  # 毫秒 
last_jump_time = -750 # 設為負數是為了讓遊戲一開始就能馬上跳

# ================= 平台設定 =================
class platOb(pg.sprite.Sprite):
    def __init__(self,image:pg.surface,pos:tuple[int,int]):
        super().__init__()
        self.image=image
        self.rect=self.image.get_rect(center=pos)
PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 15

platform_positions = [
    (0, 322),(80, 322),(160, 322),(240, 322),(320, 322),(400, 322),(480, 322),
    (50, 240),(350, 230),(150, 160),(200, 90),(130, 10),
    (50, -80),(120, -160),(260, -230),(300, -300),(250, -380),
    (200, -450),(120, -530),(50, -590),(0, -640),
]

platforms = [pg.Rect(x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT) for x, y in platform_positions]
ground = platforms[:7]

rock_img = pg.image.load(os.path.join("picture", "forest_rock.png")).convert_alpha()
rock_img = pg.transform.scale(rock_img, (PLATFORM_WIDTH, PLATFORM_HEIGHT))

platform_object=[]
for pos in platform_positions:
    wall=platOb(rock_img,pos)
    platform_object.append(wall)
# ================= 判斷是否站在平台 =================
offset_for_plat_x=48
def is_on_platform(px, py):
    for plat in platforms:
        #abs_x=abs(px-plat[0])
        if plat.colliderect(px, py,PLAYER_WIDTH,PLAYER_HEIGHT):
            return True
    return False

# ================= 捲動設定 =================
SCROLL_UP_TRIGGER_Y = WORLD_HEIGHT * 0.35
SCROLL_DOWN_TRIGGER_Y = WORLD_HEIGHT * 0.6

# ================= 遊戲主迴圈 =================
running = True
while running:
    dt = clock.tick(FPS) / 1000
    
    # 取得目前時間 (毫秒)
    current_time = pg.time.get_ticks()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYUP and event.key == pg.K_SPACE:
            jump_pressed = False

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

    # ---------- 跳躍 (修改處) ----------
    # 判斷條件增加： (目前時間 - 上次跳躍時間) 必須大於 冷卻時間
    if keys[pg.K_SPACE] and not jump_pressed and time_since_ground <= COYOTE_TIME:
        if current_time - last_jump_time > JUMP_COOLDOWN: 
            player_vy = JUMP_SPEED
            jump_pressed = True
            time_since_ground = COYOTE_TIME + 1 # 清除土狼時間
            last_jump_time = current_time       # 更新上次跳躍時間

    # ---------- 水平移動 ----------
    player_x += player_vx
    player_rect = pg.Rect(
        player_x - PLAYER_WIDTH // 2,
        player_y - PLAYER_HEIGHT,
        PLAYER_WIDTH,
        PLAYER_HEIGHT
    )
    
    for i in range(len(platforms)):
        plat=platforms[i]
        plat_sprite=platform_object[i]
        #if pg.sprite.collide_rect(char_u,plat_sprite):
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
        PLAYER_WIDTH // 2,
        min(WORLD_WIDTH - PLAYER_WIDTH // 2, player_x)
    )

    # ---------- 向上捲動 (鏡頭跟隨) ----------
    if player_y < SCROLL_UP_TRIGGER_Y:
        scroll = SCROLL_UP_TRIGGER_Y - player_y
        player_y += scroll
        # 修正：所有平台一起移動，石頭位置改變
        for plat in platforms:
            plat.y += scroll
        
        # 修正：背景捲動基準點也要跟著移動，確保背景與玩家同步
        bg_scroll_anchor_y += scroll

    # ---------- 向下捲動 (鏡頭跟隨，限制最低高度) ----------
    INITIAL_GROUND_Y = 322
    INITIAL_PLAYER_Y = 315
    if player_y > SCROLL_DOWN_TRIGGER_Y:
        raw_scroll = player_y - SCROLL_DOWN_TRIGGER_Y
        MAX_SCROLL = 15
        scroll = min(raw_scroll, MAX_SCROLL)

        # 1️⃣ 限制地面不能低於初始地面
        if platforms[0].y - scroll < INITIAL_GROUND_Y:
            scroll = platforms[0].y - INITIAL_GROUND_Y

        # 2️⃣ 限制玩家不能低於初始畫面高度
        if player_y - scroll > INITIAL_PLAYER_Y:
            scroll = player_y - INITIAL_PLAYER_Y

        # 3️⃣ 若已無法再捲動，直接歸位
        if scroll > 0:
            player_y -= scroll
            for plat in platforms:
                plat.y -= scroll

            bg_scroll_anchor_y -= scroll
            bg_scroll_anchor_y = max(bg_scroll_anchor_y, BG_SCROLL_ANCHOR_INITIAL)


    # ================= 繪製（畫在 world_surface） =================
    world_surface.fill((0, 0, 0, 0))

    for plat in platforms:
        if plat in ground:
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

    # 計算背景位置
    # 當 player_y = bg_scroll_anchor_y 時，顯示背景底部 (bg_start_y)
    # 背景高度 3500, 螢幕高度 1080 -> y = 1080 - 3500 = -2420
    # 玩家往上跳 (player_y 變小)，背景向下捲 (bg_y 變大)
    bg_scroll_speed = 2.0
    bg_start_y = 1080 - 3500
    bg_y = bg_start_y + (bg_scroll_anchor_y - player_y) * bg_scroll_speed
    
    # 限制背景不要跑出範圍 (上方不能露出黑邊，下方不能露出黑邊)
    if bg_y > 0: bg_y = 0
    if bg_y < 1080 - 3500: bg_y = 1080 - 3500

    # 置中繪製
    bg_x = (WINDOW_WIDTH - 2000) // 2
    screen.blit(bg_img_full, (bg_x, bg_y))

    screen.blit(scaled_surface, (offset_x, offset_y))
    pg.display.flip()
    #update class 
    char_u.rect=char_u.image.get_rect(center=(player_x,player_y))
    
pg.quit()
sys.exit()