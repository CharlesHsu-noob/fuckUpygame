import pygame as pg
import sys, os
import json

pg.init()

# --- 為了跨平台相容性而進行的路徑設定 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)

screeninfo = pg.display.Info()
w, h = screeninfo.current_w, screeninfo.current_h - 80
screen = pg.display.set_mode((w, h))
pg.display.set_caption("object_practice")

bg = pg.Surface(screen.get_size())
bg = bg.convert()

# 視窗背景
main_screen = pg.image.load(os.path.join(base_dir, "picture", "back_ground", "main_screen.webp"))
main_screen.convert()
mainMenuBg = pg.transform.scale(main_screen.convert_alpha(), (w, h))

def main_menu():
    screen.blit(mainMenuBg, (0, 0))

# 字體
font = pg.font.SysFont(None, 36)

# 玩家資料與存檔檔案
player_data = {"score": 0, "level": 1}
save_file = "save.json"

# ===== 存檔 / 讀檔 =====
def load_game():
    try:
        with open(save_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"score": 0, "level": 1}

# ===== 按鈕類別 =====
class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.rect = pg.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.color_normal = (100, 200, 100)
        self.color_hover = (150, 250, 150)
        self.color_click = (50, 150, 50)
        self.is_pressed = False

    def draw(self, screen):
        mouse_pos = pg.mouse.get_pos()
        if self.is_pressed:
            color = self.color_click
        elif self.rect.collidepoint(mouse_pos):
            color = self.color_hover
        else:
            color = self.color_normal
        pg.draw.rect(screen, color, self.rect, border_radius=10)
        text_surface = font.render(self.text, True, (0,0,0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.is_pressed = True
        elif event.type == pg.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.callback()
            self.is_pressed = False

# ===== 頁面狀態 =====
current_page = "main"  # main 或 credits

# ===== 功能 =====
def on_load():
    global player_data
    player_data = load_game()
    print("讀取成功：", player_data)

def show_credits():
    global current_page
    current_page = "credits"

def go_back():
    global current_page
    current_page = "main"

# ===== 建立按鈕 =====
load_button = Button("loading", 200, 100, 200, 60, on_load)
credits_button = Button("credits", 200, 200, 200, 60, show_credits)
back_button = Button("return", 200, 300, 200, 60, go_back)

# ===== 名單 =====
credits_list = ["Leo", "Daniel", "Dylan", "Charles"]

# ===== 遊戲迴圈 =====
running = True
while running:
    screen.fill((220, 220, 220))
    main_menu()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if current_page == "main":
            load_button.handle_event(event)
            credits_button.handle_event(event)
        elif current_page == "credits":
            back_button.handle_event(event)

    if current_page == "main":
        # 顯示玩家資料
        info = font.render(f"Score: {player_data['score']}  Level: {player_data['level']}", True, (0,0,0))
        screen.blit(info, (150, 50))
        # 畫按鈕
        load_button.draw(screen)
        credits_button.draw(screen)
    elif current_page == "credits":
        # 顯示名單
        for i, name in enumerate(credits_list):
            text_surface = font.render(name, True, (0,0,0))
            screen.blit(text_surface, (250, 50 + i*40))
        back_button.draw(screen)

    pg.display.flip()

pg.quit()
sys.exit()