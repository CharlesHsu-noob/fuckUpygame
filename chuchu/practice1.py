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
'''
# === 字體 ===
font_big = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 50)   # 遊戲名稱
font_mid = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 25)   # 繼續/退出
font_small = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 15) # 音量
'''
# === 字體 ===
font_big = pg.font.Font(os.path.join(base_dir,"font","msjh.ttf"),50)   # 遊戲名稱
font_mid = pg.font.Font(os.path.join(base_dir,"font","msjh.ttf"),25)   #繼續遊戲
font_small = pg.font.Font(os.path.join(base_dir,"font","msjh.ttf"),15) # 音量

# --- 繼續遊戲 ---
continue_text = font_mid.render("繼續遊戲", True, (132, 132, 132))
continue_rect = continue_text.get_rect(center=(210, 210)) 
# --- 退出遊戲 ---
exit_text = font_mid.render("退出遊戲", True, (132, 132, 132))
exit_rect = exit_text.get_rect(center=(210, 450)) 

paused = False
prev_pause_state = False
mouse_click = False

# === 淡入淡出控制 ===
fade_alpha = 255
fade_speed = 15
is_flipping = False
fading_out = False
fading_in = False
ui_interactive = True  # 暫停畫面內 UI 是否可以操作（滑桿、文字按鈕）

# === 左右翻頁按鈕（三角形） ===
left_rect = pg.Rect(20, HEIGHT//2 - 25, 50, 50)
right_rect = pg.Rect(WIDTH - 70, HEIGHT//2 - 25, 50, 50)

def draw_flip_buttons(surface, mouse_pos):
    # 左三角形
    color = (160,160,160) if left_rect.collidepoint(mouse_pos) else (132,132,132)
    pg.draw.polygon(surface, color, [
        (left_rect.right, left_rect.top),
        (left_rect.right, left_rect.bottom),
        (left_rect.left, left_rect.centery)
    ])
    # 右三角形
    color = (160,160,160) if right_rect.collidepoint(mouse_pos) else (132,132,132)
    pg.draw.polygon(surface, color, [
        (right_rect.left, right_rect.top),
        (right_rect.left, right_rect.bottom),
        (right_rect.right, right_rect.centery)
    ])

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
        # 滑桿事件只在可操作時
        if paused and ui_interactive:
            slider.handle_event(event)

    # 暫停按鈕始終可按
    buttons.update()
    if pause_btn.ispress and not is_flipping:
        paused = not paused

    # 點擊左右按鈕觸發翻頁
    if paused and not is_flipping and mouse_click:
        if left_rect.collidepoint(mouse_pos) or right_rect.collidepoint(mouse_pos):
            fading_out = True
            is_flipping = True
            ui_interactive = False
            fade_alpha = 255
            # 這裡可以切換頁面索引 current_page +=1 或 -=1

    # --- 遊戲畫面 ---
    screen.fill((120, 180, 240))
    buttons.draw(screen)

    # --- 暫停畫面 ---
    if paused:
        
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        screen.blit(background, bg_rect)

        # 暫停圖層，所有UI淡入淡出都放在這
        pause_layer = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)

        # 遊戲名稱
        title_text = font_big.render("遊戲名稱", True, (132,132,132))
        title_pos = (110, 100)

        # === 第二頁五個互動框 ===
box_color = (132, 132, 132)
hover_color = (195, 140, 121)

# 五個框的中心位置
box_positions = [
    (WIDTH//2 - 180, HEIGHT//2 - 100),
    (WIDTH//2,        HEIGHT//2 - 100),
    (WIDTH//2 + 180, HEIGHT//2 - 100),
    (WIDTH//2 - 90,  HEIGHT//2 + 80),
    (WIDTH//2 + 90,  HEIGHT//2 + 80)
]

# 框大小
box_size = (120, 80)
mouse_pos = pg.mouse.get_pos()
click = pg.mouse.get_pressed()[0]

for pos in box_positions:
    rect = pg.Rect(0, 0, *box_size)
    rect.center = pos

    # 檢查滑鼠 hover
    if rect.collidepoint(mouse_pos):
        color = hover_color
        scale = 1.08  # 放大效果
        scaled_rect = pg.Rect(0, 0, box_size[0]*scale, box_size[1]*scale)
        scaled_rect.center = pos
        pg.draw.rect(screen, color, scaled_rect, border_radius=10)
        # 點擊時可加特效（例如閃爍或音效）
        if click:
            pg.time.delay(100)  # 模擬閃一下
    else:
        pg.draw.rect(screen, box_color, rect, border_radius=10)


        # --- 淡出動畫 ---
        if fading_out:
            temp_layer = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            temp_layer.blit(title_text, title_pos)
            slider.draw(temp_layer)
            temp_layer.blit(continue_text, continue_rect)
            temp_layer.blit(exit_text, exit_rect)
            temp_layer.set_alpha(fade_alpha)
            pause_layer.blit(temp_layer, (0,0))
            fade_alpha -= fade_speed
            if fade_alpha <= 0:
                fade_alpha = 0
                fading_out = False
                fading_in = True

        # --- 淡入動畫 ---
        elif fading_in:
            temp_layer = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            temp_layer.blit(title_text, title_pos)
            slider.draw(temp_layer)
            temp_layer.blit(continue_text, continue_rect)
            temp_layer.blit(exit_text, exit_rect)
            temp_layer.set_alpha(fade_alpha)
            pause_layer.blit(temp_layer, (0,0))
            fade_alpha += fade_speed
            if fade_alpha >= 255:
                fade_alpha = 255
                fading_in = False
                is_flipping = False
                ui_interactive = True

        # --- 正常顯示（無翻頁） ---
        elif not is_flipping:
            pause_layer.blit(title_text, title_pos)
            slider.draw(pause_layer)
            # 繼續遊戲
            if continue_rect.collidepoint(mouse_pos):
                continue_text = font_mid.render("繼續遊戲", True, (160,160,160))
                if mouse_click:
                    paused = False
            else:
                continue_text = font_mid.render("繼續遊戲", True, (132,132,132))
            pause_layer.blit(continue_text, continue_rect)

            # 退出遊戲
            if exit_rect.collidepoint(mouse_pos):
                exit_text = font_mid.render("退出遊戲", True, (160,160,160))
                if mouse_click:
                    pg.quit()
                    sys.exit()
            else:
                exit_text = font_mid.render("退出遊戲", True, (132,132,132))
            pause_layer.blit(exit_text, exit_rect)

        # 音量滑桿
        if ui_interactive:
            slider.draw(pause_layer)
            volume = slider.get_value()
            pg.mixer.music.set_volume(volume)
            vol_text = font_small.render(f"音樂音量: {int(volume*100)}%", True, (132,132,132))
            pause_layer.blit(vol_text, (160,260))

        # 左右翻頁按鈕
        draw_flip_buttons(pause_layer, mouse_pos)
        screen.blit(pause_layer, (0,0))

    prev_pause_state = pause_btn.ispress
    pg.display.flip()