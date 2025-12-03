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

selected_box = None

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
font_big = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 50)
font_mid = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 25)
font_small = pg.font.Font("C:\\Windows\\Fonts\\msjh.ttc", 15)

# --- 第一頁 UI ---
continue_text = font_mid.render("繼續遊戲", True, (132, 132, 132))
continue_rect = continue_text.get_rect(center=(210, 210))
exit_text = font_mid.render("退出遊戲", True, (132, 132, 132))
exit_rect = exit_text.get_rect(center=(210, 450))
back_text = font_mid.render("返回遊戲", True, (132,132,132))
back_rect = back_text.get_rect(center=(210, 380))

paused = False
mouse_click = False

# === 翻頁控制 ===
current_page = 1   # 1 = 第一頁, 2 = 第二頁
fade_alpha = 255
fade_speed = 15
is_flipping = False
fading_out = False
fading_in = False
ui_interactive = True

# === 左右翻頁三角形 ===
left_rect = pg.Rect(20, HEIGHT//2 - 25, 50, 50)
right_rect = pg.Rect(WIDTH - 70, HEIGHT//2 - 25, 50, 50)

def draw_flip_buttons(surface, mouse_pos):
    color = (160,160,160) if left_rect.collidepoint(mouse_pos) else (132,132,132)
    pg.draw.polygon(surface, color, [(left_rect.right, left_rect.top),
                                     (left_rect.right, left_rect.bottom),
                                     (left_rect.left, left_rect.centery)])
    color = (160,160,160) if right_rect.collidepoint(mouse_pos) else (132,132,132)
    pg.draw.polygon(surface, color, [(right_rect.left, right_rect.top),
                                     (right_rect.left, right_rect.bottom),
                                     (right_rect.right, right_rect.centery)])

# === 第一頁：角色 ===
box_w, box_h = 60, 110
left_page_x1 = bg_rect.centerx - bg_rect.width//2 + 40 
top_y = bg_rect.top + 100  
boxes_chars = []
for i in range(5):
    x = left_page_x1 + i * box_w
    boxes_chars.append(pg.Rect(x, top_y, box_w, box_h))

# === 第二頁：物品欄 ===
box2_w, box2_h = 200, 50
x2 = bg_rect.centerx + bg_rect.width//10

boxes_items = []
start_y = bg_rect.top + 230

for i in range(5):
    y = start_y + i * box2_h
    boxes_items.append(pg.Rect(x2, y, box2_w, box2_h))

# 框框對應的細節資訊
boxes_info = [
    {"name": "角色A", "desc": "力量型角色，攻擊高，防禦中", "value": 50},
    {"name": "角色B", "desc": "速度型角色，攻擊中，速度快", "value": 40},
    {"name": "角色C", "desc": "防禦型角色，攻擊低，防禦高", "value": 60},
    {"name": "角色D", "desc": "平衡型角色，攻擊防禦均衡", "value": 55},
    {"name": "角色E", "desc": "魔法型角色，攻擊特殊技能強", "value": 45},
]

boxes_items_info = [
    {"name": "道具A", "desc": "回復少量生命", "value": 5},
    {"name": "道具B", "desc": "增加速度", "value": 3},
    {"name": "道具C", "desc": "防禦提升", "value": 2},
    {"name": "道具D", "desc": "特殊技能卷軸", "value": 1},
    {"name": "道具E", "desc": "魔法回復藥水", "value": 4},
]

def draw_page2(surface, mouse_pos, selected_char, selected_item):
    # --- 畫角色框框 ---
    for i, rect in enumerate(boxes_chars):
        if selected_char == i:
            color = (220, 220, 220)
        elif rect.collidepoint(mouse_pos):
            color = (170, 170, 170)
        else:
            color = (132, 132, 132)
        pg.draw.rect(surface, color, rect, width=3)

    # --- 畫物品框框 ---
    for i, rect in enumerate(boxes_items):
        if selected_item == i:
            color = (220, 220, 220)
        elif rect.collidepoint(mouse_pos):
            color = (170, 170, 170)
        else:
            color = (132, 132, 132)
        pg.draw.rect(surface, color, rect, width=3)

    # 左下角色資訊框
    info_panel_w = bg_rect.width // 2 - 100
    info_panel_h = 160
    right_h = 120
    info_panel_x = bg_rect.left + 60
    info_panel_y = bg_rect.bottom - info_panel_h - 100
    info_panel_rect = pg.Rect(info_panel_x, info_panel_y, info_panel_w, info_panel_h)
    pg.draw.rect(surface, (132,132,132), info_panel_rect, width=3)

    # 顯示角色資訊
    if selected_char is not None:
        info = boxes_info[selected_char]
        name_text = font_mid.render(info["name"], True, (132,132,132))
        desc_text = font_small.render(info["desc"], True, (132,132,132))
        value_text = font_small.render(f"數值: {info['value']}", True, (132,132,132))
        surface.blit(name_text, (info_panel_x + 15, info_panel_y + 10))
        surface.blit(desc_text, (info_panel_x + 15, info_panel_y + 50))
        surface.blit(value_text, (info_panel_x + 15, info_panel_y + 80))
    else:
        hint_text = font_small.render("選擇上方角色以查看詳細資訊", True, (132,132,132))
        surface.blit(hint_text, (info_panel_x + 15, info_panel_y + 10))

    # 右上物品資訊框
    info2_x = bg_rect.left + 420
    info2_y = bg_rect.top + 100
    info2_rect = pg.Rect(info2_x, info2_y, info_panel_w, right_h)
    pg.draw.rect(surface, (132,132,132), info2_rect, width=3)

    # 顯示物品資訊
    if selected_item is not None:
        info = boxes_items_info[selected_item]  # 你需要建立對應物品資訊列表
        name_text = font_mid.render(info["name"], True, (132,132,132))
        desc_text = font_small.render(info["desc"], True, (132,132,132))
        surface.blit(name_text, (info2_x + 15, info2_y + 10))
        surface.blit(desc_text, (info2_x + 15, info2_y + 50))
    else:
        hint_text = font_small.render("選擇下方物品以查看詳細資訊", True, (132,132,132))
        surface.blit(hint_text, (info2_x + 15, info2_y + 10))

# ----------------------------------------------------------
# === 主迴圈 ===
selected_char = None
selected_item = None

while True:
    clock.tick(30)
    mouse_pos = pg.mouse.get_pos()
    mouse_click = False

    # --- 事件處理 ---
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True
        # Slider 只在第一頁可操作
        if paused and ui_interactive and current_page == 1:
            slider.handle_event(event)

    # 暫停按鈕
    buttons.update()
    if pause_btn.ispress and not is_flipping:
        paused = not paused

    # --- 左右翻頁與選框點擊 ---
    if paused and not is_flipping and mouse_click:
        if current_page == 2:
            # 角色選取
            for i, rect in enumerate(boxes_chars):
                if rect.collidepoint(mouse_pos):
                    selected_char = i
                    break
            else:
                # 物品選取
                for i, rect in enumerate(boxes_items):
                    if rect.collidepoint(mouse_pos):
                        selected_item = i
                        break
        # 翻頁按鈕
        if left_rect.collidepoint(mouse_pos) or right_rect.collidepoint(mouse_pos):
            fading_out = True
            is_flipping = True
            ui_interactive = False
            fade_alpha = 255

    # --- 遊戲背景 ---
    screen.fill((120, 180, 240))
    buttons.draw(screen)

    # --- 暫停畫面 ---
    if paused:
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        screen.blit(background, bg_rect)
        pause_layer = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)

        # 翻頁動畫
        if fading_out:
            temp = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            if current_page == 1:
                # 第一頁內容
                temp.blit(font_big.render("遊戲名稱", True, (132,132,132)), (110,100))
                slider.draw(temp)
                temp.blit(continue_text, continue_rect)
                temp.blit(exit_text, exit_rect)
            else:
                draw_page2(temp, mouse_pos, selected_char, selected_item)
            temp.set_alpha(fade_alpha)
            pause_layer.blit(temp, (0,0))
            fade_alpha -= 15
            if fade_alpha <= 0:
                fade_alpha = 0
                fading_out = False
                fading_in = True
                # 翻頁完成後更新頁碼
                current_page = 2 if current_page == 1 else 1

        elif fading_in:
            temp = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            if current_page == 1:
                temp.blit(font_big.render("遊戲名稱", True, (132,132,132)), (110,100))
                slider.draw(temp)
                temp.blit(continue_text, continue_rect)
                temp.blit(exit_text, exit_rect)
            else:
                draw_page2(temp, mouse_pos, selected_char, selected_item)
            temp.set_alpha(fade_alpha)
            pause_layer.blit(temp, (0,0))
            fade_alpha += 15
            if fade_alpha >= 255:
                fade_alpha = 255
                fading_in = False
                is_flipping = False
                ui_interactive = True

        # --- 正常顯示 ---
        elif not is_flipping:
            if current_page == 1:
                pause_layer.blit(font_big.render("遊戲名稱", True, (132,132,132)), (110,100))
                slider.draw(pause_layer)
                volume = slider.get_value()
                pg.mixer.music.set_volume(volume)
                vol = font_small.render(f"音樂音量: {int(volume*100)}%", True, (132,132,132))
                pause_layer.blit(vol, (160,260))
                # 繼續遊戲
                if continue_rect.collidepoint(mouse_pos):
                    c = font_mid.render("繼續遊戲", True, (160,160,160))
                    if mouse_click: paused = False
                else:
                    c = font_mid.render("繼續遊戲", True, (132,132,132))
                pause_layer.blit(c, continue_rect)
                # 退出遊戲
                if exit_rect.collidepoint(mouse_pos):
                    e = font_mid.render("退出遊戲", True, (160,160,160))
                    if mouse_click: pg.quit(); sys.exit()
                else:
                    e = font_mid.render("退出遊戲", True, (132,132,132))
                pause_layer.blit(e, exit_rect)
            else:
                draw_page2(pause_layer, mouse_pos, selected_char, selected_item)

        # 翻頁按鈕
        draw_flip_buttons(pause_layer, mouse_pos)
        screen.blit(pause_layer, (0,0))

    pg.display.flip()
