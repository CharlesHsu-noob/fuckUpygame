import os, sys
import pygame as pg

# === 初始化 ===
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
sys.path.insert(0, base_dir)

from XddObjects import buttonObject

pg.init()
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Pause Background Centered")
clock = pg.time.Clock()

# === 按鈕 ===
pause_btn = buttonObject(
    [os.path.join(base_dir,"picture","chuchutest","1.png"),
     os.path.join(base_dir,"picture","chuchutest","2.png"),
     os.path.join(base_dir,"picture","chuchutest","未命名.png")],
    center=(60, 30), size=(100, 50)
)
buttons = pg.sprite.Group(pause_btn)

# === 暫停背景圖 ===
bg_path = os.path.join(base_dir, "picture", "chuchutest", "book1.png")
background = pg.image.load(bg_path).convert_alpha()

# 調整暫停背景大小
bg_size = (int(background.get_width() * 0.4),
           int(background.get_height() * 0.5))
background = pg.transform.scale(background, bg_size)

# 計算置中位置
bg_rect = background.get_rect(center=(WIDTH // 2, HEIGHT // 2))

paused = False
font = pg.font.Font(None, 80)

while True:
    clock.tick(30)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    buttons.update()

    if pause_btn.ispress:
        paused = not paused

    # --- 繪製 ---
    screen.fill((120, 180, 240))  # 模擬遊戲畫面
    buttons.draw(screen)

    if paused:
        # 半透明黑幕
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # 顯示置中的暫停背景
        screen.blit(background, bg_rect)

    pg.display.flip()
