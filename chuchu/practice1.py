import os, sys
import pygame as pg

# === 初始化 ===
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
sys.path.insert(0, base_dir)
from XddObjects import buttonObject, Slider

pg.init()
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Pause Background Centered")
clock = pg.time.Clock()

# ===== 音量 Slider =====
w, h = WIDTH, HEIGHT
volume = 0.5
pg.mixer.init()
pg.mixer.music.set_volume(volume)
slider = Slider(400, h//2, 400, 20, init_val=volume)
credits_font = pg.font.SysFont(None, 48)

# === 暫停按鈕 ===
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
bg_size = (int(background.get_width() * 0.4),
           int(background.get_height() * 0.5))
background = pg.transform.scale(background, bg_size)
bg_rect = background.get_rect(center=(WIDTH // 2, HEIGHT // 2))

paused = False
font = pg.font.Font(None, 60)

# === 主迴圈 ===
while True:
    clock.tick(30)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        # 滑桿事件只在暫停時生效
        if paused:
            slider.handle_event(event)

    buttons.update()

    if pause_btn.ispress:
        paused = not paused

    # --- 繪製遊戲畫面 ---
    screen.fill((120, 180, 240))
    buttons.draw(screen)

    # --- 暫停畫面 ---
    if paused:
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(background, bg_rect)

        slider.draw(screen)
        volume = slider.get_value()
        pg.mixer.music.set_volume(volume)

        vol_text = font.render(f"Volume: {int(volume*100)}%", True, (0,0,0))
        screen.blit(vol_text, (w//2 - vol_text.get_width()//2, h//2 + 50))

    pg.display.flip()

