import pygame as pg
import sys, os

# ---------------- 初始化 ----------------
pg.init()
WIDTH, HEIGHT = 1920, 1080
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("圖片上下滾動")
clock = pg.time.Clock()
FPS = 60

# ---------------- 載入圖片 ----------------
bg_img_raw = pg.image.load(os.path.join("picture", "forest_e.png")).convert()
bg_img_full = pg.transform.scale(bg_img_raw, (2000, 3500))
img_rect = bg_img_full.get_rect()
img_rect.topleft = (0, 0)  # 初始位置從畫面頂部開始

# 滾動速度
scroll_speed = 5

# ---------------- 主迴圈 ----------------
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # 按鍵偵測
    keys = pg.key.get_pressed()
    if keys[pg.K_UP]:
        img_rect.y += scroll_speed  # 按上，畫面往下看，圖片向下
    if keys[pg.K_DOWN]:
        img_rect.y -= scroll_speed  # 按下，畫面往上看，圖片向上

    # 邊界檢查（圖片大於視窗）
    if img_rect.top > 0:
        img_rect.top = 0
    if img_rect.bottom < HEIGHT:
        img_rect.bottom = HEIGHT

    # 畫面更新
    screen.fill((0, 0, 0))
    screen.blit(bg_img_full, img_rect)
    pg.display.flip()
    clock.tick(FPS)

pg.quit()
sys.exit()
