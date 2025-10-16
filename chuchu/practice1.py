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
volume = 0.5
pg.mixer.init()
pg.mixer.music.set_volume(volume)
slider = Slider(
    110, 300, 200, 5,
    init_val=volume,
    bg_color=(132, 132, 132),
    fill_color=(132, 132, 132),
    handle_color=(132, 132, 132)
)

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

# === 字體 ===
font_big = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 50)   # 遊戲名稱
font_mid = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 25)   #繼續遊戲
font_small = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 15) # 音量

# --- 繼續遊戲 ---
continue_text = font_mid.render("繼續遊戲", True, (132, 132, 132))
continue_rect = continue_text.get_rect(center=(210, 210)) 
# --- 退出遊戲 ---
exit_text = font_mid.render("退出遊戲", True, (132, 132, 132))
exit_rect = exit_text.get_rect(center=(210, 450)) 

paused = False

# === 主迴圈 ===
while True:
    clock.tick(30)
    mouse_pos = pg.mouse.get_pos()
    mouse_click = False

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True
        if paused:
            slider.handle_event(event)

    buttons.update()
    if pause_btn.ispress:
        paused = not paused

    # --- 遊戲畫面 ---
    screen.fill((120, 180, 240))
    buttons.draw(screen)

    # --- 暫停畫面 ---
    if paused:
        # 半透明黑幕
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 背景圖
        screen.blit(background, bg_rect)

        # 暫停標題
        pause_title = font_big.render("遊戲名稱", True, (132, 132, 132))
        screen.blit(pause_title,(110, 100))

        # 音量滑桿
        slider.draw(screen)
        volume = slider.get_value()
        pg.mixer.music.set_volume(volume)
        vol_text = font_small.render(f"音樂音量: {int(volume*100)}%", True, (132, 132, 132))
        screen.blit(vol_text, (160, 260))

        # 繼續遊戲文字按鈕（滑鼠 hover 變色）
        if continue_rect.collidepoint(mouse_pos):
            continue_text = font_mid.render("繼續遊戲", True, (160, 160, 160))
            if mouse_click:
                paused = False
        else:
            continue_text = font_mid.render("繼續遊戲", True, (132, 132, 132))
        screen.blit(continue_text, continue_rect)

        # 退出遊戲文字按鈕 hover / 點擊
        if exit_rect.collidepoint(pg.mouse.get_pos()):
            exit_text = font_mid.render("退出遊戲", True, (160, 160, 160))
            if pg.mouse.get_pressed()[0]:
                pg.quit()
                sys.exit()
        else:
            exit_text =font_mid.render("退出遊戲", True, (132, 132, 132))
        screen.blit(exit_text, exit_rect)

    pg.display.flip()


