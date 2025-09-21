import pygame as pg
import sys, os, json

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
main_screen = pg.image.load(os.path.join(base_dir, "picture", "back_ground", "formal_main_screen.webp"))
main_screen.convert()
mainMenuBg = pg.transform.scale(main_screen.convert_alpha(), (w, h))

def main_menu():
    screen.blit(mainMenuBg, (0, 0))

# 初始化 mixer
pg.mixer.init()

# 載入音樂
pg.mixer.music.load(os.path.join(base_dir, "voice", "soundtrack", "red_sun_in_the_sky.wav"))

# 播放音樂（-1 代表無限循環）
pg.mixer.music.play(-1)

# 字體
font = pg.font.SysFont(None, 36)
credits_font = pg.font.SysFont(None, 48)

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

# ===== Slider 類別 =====
class Slider:
    def __init__(self, x, y, w, h, min_val=0, max_val=1, init_val=0.5):
        self.rect = pg.Rect(x, y, w, h)       # 背景條
        self.min_val = min_val
        self.max_val = max_val
        self.value = init_val
        self.handle_radius = 12
        self.dragging = False

    def draw(self, screen):
        # 畫底條
        pg.draw.rect(screen, (180,180,180), self.rect, border_radius=5)
        # 畫已填滿的部分
        fill_w = int(self.rect.w * self.value)
        pg.draw.rect(screen, (100,200,100), (self.rect.x, self.rect.y, fill_w, self.rect.h), border_radius=5)
        # 畫滑塊
        handle_x = self.rect.x + fill_w
        handle_y = self.rect.y + self.rect.h//2
        pg.draw.circle(screen, (50,150,50), (handle_x, handle_y), self.handle_radius)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pg.MOUSEMOTION:
            if self.dragging:
                rel_x = event.pos[0] - self.rect.x
                self.value = max(0, min(1, rel_x / self.rect.w))

    def get_value(self):
        return self.value

# ===== 頁面狀態 =====
current_page = "main"  # main / credits / game / settings

# ===== 功能 =====
def on_load():
    global player_data
    player_data = load_game()
    print("讀取成功：", player_data)

def show_credits():
    global current_page, credits_y
    current_page = "credits"
    credits_y = h  # 重新設定滾動起點

def go_back():
    global current_page
    current_page = "main"

def start_game():
    global current_page
    current_page = "game"

def exit_game():
    pg.quit()
    sys.exit()

def open_settings():
    global current_page
    current_page = "settings"

# ===== 建立按鈕 =====
load_button = Button("loading", 775, 440, 100, 60, on_load)
credits_button = Button("credits", 1120, 500, 100, 60, show_credits)
back_button = Button("return", 50, h - 100, 120, 60, go_back)

start_button = Button("Start Game", 1000, 270, 150, 60, start_game)
exit_button = Button("Exit", 50, 500, 100, 60, exit_game)
settings_button = Button("Settings", 350, 400, 120, 60, open_settings)

# ===== 名單 =====
credits_list = ["Bob", "Daniel", "Dylan", "Charles", "Sean"]

# ===== Credits 滾動參數 =====
credits_y = h
scroll_speed = 1  # 滾動速度 (越大越快)

# ===== 音量 Slider =====
volume = 0.5
pg.mixer.music.set_volume(volume)
slider = Slider(400, h//2, 400, 20, init_val=volume)

# ===== 遊戲迴圈 =====
running = True
clock = pg.time.Clock()

# --- 遊戲畫面背景 ---
game_bg = pg.image.load(os.path.join(base_dir, "picture", "back_ground", "main_menu_bg.png"))
game_bg = pg.transform.scale(game_bg, (w, h))

while running:
    screen.fill((220, 220, 220))
    main_menu()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if current_page == "main":
            load_button.handle_event(event)
            credits_button.handle_event(event)
            start_button.handle_event(event)
            exit_button.handle_event(event)
            settings_button.handle_event(event)
        elif current_page == "credits":
            back_button.handle_event(event)
        elif current_page == "game":
            back_button.handle_event(event)
        elif current_page == "settings":
            back_button.handle_event(event)
            slider.handle_event(event)

    if current_page == "main":
        info = font.render(f"Score: {player_data['score']}  Level: {player_data['level']}", True, (0,0,0))
        screen.blit(info, (150, 50))
        load_button.draw(screen)
        credits_button.draw(screen)
        start_button.draw(screen)
        exit_button.draw(screen)
        settings_button.draw(screen)

    elif current_page == "credits":
        overlay = pg.Surface((w, h))
        overlay.set_alpha(180)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (0, 0))

        for i, name in enumerate(credits_list):
            text_surface = credits_font.render(name, True, (0,0,0))
            screen.blit(text_surface, (w//2 - text_surface.get_width()//2, credits_y + i*60))

        credits_y -= scroll_speed
        if credits_y + len(credits_list)*60 < 0:
            credits_y = h

        back_button.draw(screen)

    elif current_page == "game":
        # 顯示新背景圖
        screen.blit(game_bg, (0, 0))
        back_button.draw(screen)

    elif current_page == "settings":
        overlay = pg.Surface((w, h))       # 建立一個和畫面一樣大的 Surface
        overlay.set_alpha(180)             # 設定透明度 (0=完全透明, 255=不透明)
        overlay.fill((255, 255, 255))      # 填滿白色
        screen.blit(overlay, (0, 0))       # 貼到畫面上
        settings_text = credits_font.render("Settings", True, (0,0,0))
        screen.blit(settings_text, (w//2 - settings_text.get_width()//2, h//2 - 100))

        slider.draw(screen)
        volume = slider.get_value()
        pg.mixer.music.set_volume(volume)

        vol_text = font.render(f"Volume: {int(volume*100)}%", True, (0,0,0))
        screen.blit(vol_text, (w//2 - vol_text.get_width()//2, h//2 + 50))

        back_button.draw(screen)

    pg.display.flip()
    clock.tick(60)

pg.quit()
sys.exit()
