import pygame as pg
import sys

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

# --- 遊戲區塊 ---
entry_rect = pg.Rect(50, 50, 40, 40)    # 左上角入口
exit_rect = pg.Rect(WIDTH-90, HEIGHT-300, 60, 60)  # 右下角出口(勝利區)

# --- 鏡子 ---
mirror_rect = pg.Rect(WIDTH//2 - 50, HEIGHT//2, 100, 10)   # 鏡子 1
mirror2_rect = pg.Rect(WIDTH//2 - 50, 100, 100, 10)        # 鏡子 2

# --- 狀態變數 ---
started = False    # 是否按下開始
won = False        # 是否成功過關
failed = False     # 是否失敗
laser_path = []    # 雷射路徑紀錄

# --- 字型 ---
font = pg.font.SysFont(None, 48)

# --- 按鈕 ---
start_button = pg.Rect(50, HEIGHT-80, 120, 50)
restart_button = pg.Rect(200, HEIGHT-80, 170, 50)

# --- 畫雷射函式 ---
def draw_laser():
    global won, failed
    if not started:
        return
    laser_path.clear()
    won = False
    failed = False
    # 初始位置與方向（右下）
    x, y = entry_rect.center
    dx, dy = 5, 5
    for _ in range(500):  # 限制最多反射次數
        x += dx
        y += dy
        laser_path.append((x, y))
        # 進入出口 → 勝利
        if exit_rect.collidepoint(x, y):
            won = True
            return
        # 碰到鏡子反射（簡化：只做上下反射）
        if mirror_rect.collidepoint(x, y) or mirror2_rect.collidepoint(x, y):
            dy = -dy
        # 出界 → 失敗
        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            failed = True
            return

# --- 主迴圈 ---
clock = pg.time.Clock()
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        # 滑鼠事件：按下按鈕
        if event.type == pg.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                if not started:   # 按下開始才啟動雷射
                    started = True
                    won = False
                    failed = False
                    draw_laser()
            if restart_button.collidepoint(event.pos):  # 重新開始
                started = False
                won = False
                failed = False
                laser_path.clear()

    # --- 鍵盤控制鏡子 (只能在還沒開始前移動) ---
    if not started:
        keys = pg.key.get_pressed()
        # 鏡子 1：← → 控制
        if keys[pg.K_LEFT] and mirror_rect.left > 0:
            mirror_rect.x -= 5
        if keys[pg.K_RIGHT] and mirror_rect.right < WIDTH:
            mirror_rect.x += 5
        # 鏡子 2：A D 控制
        if keys[pg.K_a] and mirror2_rect.left > 0:
            mirror2_rect.x -= 5
        if keys[pg.K_d] and mirror2_rect.right < WIDTH:
            mirror2_rect.x += 5

    # --- 畫面更新 ---
    screen.fill(WHITE)

    # 畫入口與出口
    pg.draw.rect(screen, BLUE, entry_rect)   # 入口
    pg.draw.rect(screen, GREEN, exit_rect)   # 出口(勝利區)

    # 畫鏡子
    pg.draw.rect(screen, BLACK, mirror_rect)
    pg.draw.rect(screen, BLACK, mirror2_rect)

    # 畫雷射路徑
    if started:
        if len(laser_path) > 1:
            pg.draw.lines(screen, RED, False, laser_path, 2)

    # 畫按鈕
    pg.draw.rect(screen, (200, 200, 200), start_button)
    pg.draw.rect(screen, (200, 200, 200), restart_button)
    screen.blit(font.render("start", True, BLACK), (start_button.x+20, start_button.y+10))
    screen.blit(font.render("try again", True, BLACK), (restart_button.x+20, restart_button.y+10))

    # 顯示結果訊息
    if won:
        text = font.render("success!", True, RED)
        screen.blit(text, (WIDTH-200, HEIGHT-100))
    elif failed:
        text = font.render("fail!", True, BLACK)
        screen.blit(text, (WIDTH-200, HEIGHT-100))

    pg.display.flip()
    clock.tick(60)

pg.quit()
sys.exit()
