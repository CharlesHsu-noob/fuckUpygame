import os, sys, json, time, random
import pygame as pg
from datetime import datetime

# ==========================================
# === 1. 初始化與視窗設定 ===
# ==========================================
pg.init()
pg.key.set_repeat(300, 30)

info = pg.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF)
pg.display.set_caption("Milk Tea Save System - U Photo Only")
clock = pg.time.Clock()

# --- 2. 縮放核心 (勿動) ---
BASE_W, BASE_H = 800, 600
UI_SCALE_X = WIDTH / BASE_W
UI_SCALE_Y = HEIGHT / BASE_H
FONT_SCALE = min(UI_SCALE_X, UI_SCALE_Y)

def s_x(val): return int(val * UI_SCALE_X)
def s_y(val): return int(val * UI_SCALE_Y)
def s_rect(x, y, w, h): return pg.Rect(s_x(x), s_y(y), s_x(w), s_y(h))

# ==========================================
# === 3. 資源載入 ===
# ==========================================
# 設定路徑：向上找一層以確保能讀到 picture 資料夾
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir) 

# 如果腳本直接放在根目錄，則 base_dir 設為 script_dir
if not os.path.exists(os.path.join(base_dir, "picture")):
    base_dir = script_dir

SAVE_DIR = "saves"
if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)

# 載入字體
try:
    font_path = os.path.join(base_dir, "font", "NotoSansTC-VariableFont_wght.ttf")
    font_big = pg.font.Font(font_path, int(50 * FONT_SCALE))
    font_mid = pg.font.Font(font_path, int(25 * FONT_SCALE))
    font_small = pg.font.Font(font_path, int(15 * FONT_SCALE))
    font_tiny = pg.font.Font(font_path, int(10 * FONT_SCALE))
except:
    font_big = pg.font.SysFont("arial", int(50 * FONT_SCALE))
    font_mid = pg.font.SysFont("arial", int(25 * FONT_SCALE))
    font_small = pg.font.SysFont("arial", int(15 * FONT_SCALE))
    font_tiny = pg.font.SysFont("arial", int(10 * FONT_SCALE))

# 載入背景
try:
    bg_path = os.path.join(base_dir, "picture", "chuchutest", "book1.png")
    raw_bg = pg.image.load(bg_path).convert_alpha()
    scale_ratio = (WIDTH * 0.85) / raw_bg.get_width()
    new_size = (int(raw_bg.get_width() * scale_ratio), int(raw_bg.get_height() * scale_ratio))
    background = pg.transform.smoothscale(raw_bg, new_size)
    bg_rect = background.get_rect(center=(WIDTH // 2, HEIGHT // 2))
except:
    background = pg.Surface((s_x(640), s_y(420))); background.fill((250, 248, 245))
    bg_rect = background.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# ==========================================
# === 4. 物件建構 ===
# ==========================================
class Slider:
    def __init__(self, x, y, w, h, init_val=0.5):
        self.rect = s_rect(x, y, w, h)
        self.val = max(0.0, min(1.0, init_val))
    def change_value(self, amount): self.val = max(0.0, min(1.0, self.val + amount))
    def set_value(self, new_val): self.val = max(0.0, min(1.0, new_val))
    def get_value(self): return self.val
    def draw(self, surface):
        pg.draw.rect(surface, (166, 138, 118), self.rect, border_radius=self.rect.height//2)
        fill_w = int(self.rect.width * self.val)
        if fill_w > 0: 
            pg.draw.rect(surface, (191, 164, 139), (self.rect.x, self.rect.y, fill_w, self.rect.height), border_radius=self.rect.height//2)
        pg.draw.circle(surface, (90, 74, 66), (self.rect.x + fill_w, self.rect.centery), self.rect.height + s_y(3))

class GameData:
    def __init__(self): self.reset()
    def reset(self):
        self.chapter = 1; self.money = 100; self.total_playtime = 0.0
        self._session_start = time.time(); self.volume = 0.5; self.sfx_volume = 0.5
        self.party_data = [
            {"name": "U", "desc": "內向 不擅交流", "hp": 80, "max_hp": 100},
            {"name": "K", "desc": "???", "hp": 45, "max_hp": 60},
            {"name": "W", "desc": "???", "hp": 60, "max_hp": 70},
            {"name": "C", "desc": "???", "hp": 50, "max_hp": 60}, 
            {"name": "O", "desc": "???", "hp": 110, "max_hp": 120}  
        ]
        self.upgrade_log = []
    def get_playtime(self): return self.total_playtime + (time.time() - self._session_start)
    def to_dict(self):
        return {"chapter": self.chapter, "money": self.money, "playtime": self.get_playtime(),
                "volume": self.volume, "sfx_volume": self.sfx_volume, "party_data": self.party_data,
                "upgrade_log": self.upgrade_log, "timestamp": datetime.now().strftime("%m/%d %H:%M")}
    def load_from_dict(self, data):
        self.chapter = data.get("chapter", 1); self.money = data.get("money", 0)
        self.total_playtime = data.get("playtime", 0.0); self.volume = data.get("volume", 0.5)
        self.sfx_volume = data.get("sfx_volume", 0.5); self.party_data = data.get("party_data", self.party_data)
        self.upgrade_log = data.get("upgrade_log", []); self._session_start = time.time()

game_data = GameData()
save_slots_cache = [None] * 3

# --- Page 1 物件 ---
continue_rect = s_rect(0, 0, 140, 40); continue_rect.center = (s_x(225), s_y(210))
exit_rect     = s_rect(0, 0, 140, 40); exit_rect.center = (s_x(225), s_y(440))
slider_music = Slider(130, 290, 200, 5, init_val=game_data.volume)
slider_sfx   = Slider(130, 290 + 70, 200, 5, init_val=game_data.sfx_volume) 
slot_rects = [s_rect(470, 150 + i*(75 + 15), 200, 75) for i in range(3)]
btn_save_rect = s_rect(0, 0, 80, 35)
btn_save_rect.center = (s_x(520), s_y(440))
btn_load_rect = s_rect(0, 0, 80, 35)
btn_load_rect.center = (s_x(620), s_y(440))

# --- Page 2 物件 ---
P2_CHAR_COUNT, P2_ITEM_COUNT = 5, 3
boxes_chars = [pg.Rect(s_x(110 + i * (48 + 5)), s_y(140), s_x(48), s_y(150)) for i in range(P2_CHAR_COUNT)]
boxes_items = [pg.Rect(0, s_y(140 + i * (40 + 12)), s_x(180), s_y(40)) for i in range(P2_ITEM_COUNT)]
for r in boxes_items: r.centerx = s_x(560)
desc_rect_l = pg.Rect(s_x(110), s_y(360), s_x(250), s_y(130))
desc_rect_r = pg.Rect(0, s_y(360), s_x(250), s_y(130))
desc_rect_r.centerx = s_x(560)

# --- 資料定義 ---
RUNES_DATA = [
    {"symbol": "ᛒ", "name": "Berkano", "stat": "HP",  "desc": "成長、孕育"}, {"symbol": "ᛚ", "name": "Laguz",   "stat": "INT", "desc": "流動、循環"},
    {"symbol": "ᛞ", "name": "Dagaz",   "stat": "CRT", "desc": "突破、轉變"}, {"symbol": "ᛋ", "name": "Sowilo",  "stat": "ENG", "desc": "太陽、能量"},
    {"symbol": "ᛏ", "name": "Tiwaz",   "stat": "ATK", "desc": "武勇、戰力"}, {"symbol": "ᛉ", "name": "Algiz",   "stat": "DEF", "desc": "守護、防護"}
]
ITEM_TYPES = [
    {"name": "能量飲料", "desc": "ENG +3", "type": "consumable", "effect": "ENG +3"},
    {"name": "堅果棒", "desc": "回復20%血量", "type": "consumable", "effect": "HP +20%"},
    {"name": "空白符文", "desc": "點擊開啟刻印選單", "type": "rune", "effect": "Rune"}
]
inventory_list = []
for _ in range(20): 
    item = random.choice(ITEM_TYPES).copy()
    found = next((x for x in inventory_list if x["name"] == item["name"]), None)
    if found: found["count"] = found.get("count", 1) + 1
    else: item["count"] = 1; inventory_list.append(item)

# ==========================================
# === 5. 邏輯與繪圖 ===
# ==========================================
paused = False; current_page = 1; nav_cursor = [0, 0] 
fade_alpha = 255; is_flipping = False; fading_out, fading_in = False, False; ui_interactive = True
p2_section = 0; p2_char_idx = 0; p2_item_idx = 0
POPUP_NONE, POPUP_RUNE_SELECT, POPUP_TARGET_SELECT, POPUP_MSG = 0, 1, 2, 3
popup_state = POPUP_NONE; rune_cursor = 0; target_cursor = 0; selected_rune_data = None
popup_message = ""; popup_timer = 0; save_msg = ""; save_msg_timer = 0; active_slot_index = 0

def refresh_save_slots():
    for i in range(3):
        fn = os.path.join(SAVE_DIR, f"save_{i}.json")
        try:
            with open(fn, "r", encoding="utf-8") as f: save_slots_cache[i] = json.load(f)
        except: save_slots_cache[i] = None

def save_current_slot(idx):
    fn = os.path.join(SAVE_DIR, f"save_{idx}.json")
    game_data.volume = slider_music.get_value(); game_data.sfx_volume = slider_sfx.get_value()
    try:
        with open(fn, "w", encoding="utf-8") as f: json.dump(game_data.to_dict(), f, indent=4)
        refresh_save_slots(); return "存檔成功"
    except Exception as e: return f"錯誤: {e}"

def load_current_slot(idx):
    fn = os.path.join(SAVE_DIR, f"save_{idx}.json")
    if not os.path.exists(fn): return "無存檔"
    try:
        with open(fn, "r", encoding="utf-8") as f: data = json.load(f)
        game_data.load_from_dict(data)
        slider_music.set_value(game_data.volume); slider_sfx.set_value(game_data.sfx_volume)
        pg.mixer.music.set_volume(game_data.volume); return "讀檔成功"
    except Exception as e: return f"錯誤: {e}"

def trigger_item_usage(idx):
    global popup_state, rune_cursor, target_cursor, selected_rune_data
    if idx >= len(inventory_list): return
    item = inventory_list[idx]
    if item["type"] == "rune": popup_state, rune_cursor, selected_rune_data = POPUP_RUNE_SELECT, 0, None
    else: popup_state, target_cursor, selected_rune_data = POPUP_TARGET_SELECT, 0, None

def confirm_target_selection():
    global popup_state, popup_message, popup_timer, p2_item_idx
    target = game_data.party_data[target_cursor]; item = inventory_list[p2_item_idx]
    log = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "char": target["name"]}
    if selected_rune_data:
        log["source"], log["effect"] = f"Rune: {selected_rune_data['name']}", f"{selected_rune_data['stat']} UP"
        popup_message = f"{target['name']} 獲得 [{selected_rune_data['name']}] !"
    else:
        log["source"], log["effect"] = item["name"], item["effect"]
        popup_message = f"對 {target['name']} 使用了 {item['name']} !"
        if "HP" in item["effect"]: target["hp"] = min(target["hp"] + int(target["max_hp"]*0.2), target["max_hp"])
    game_data.upgrade_log.append(log)
    item["count"] -= 1
    if item["count"] <= 0:
        inventory_list.pop(p2_item_idx); p2_item_idx = max(0, min(p2_item_idx, len(inventory_list)-1))
    popup_state, popup_timer = POPUP_MSG, 50

def handle_global_input(events):
    global paused, nav_cursor, popup_state
    for event in events:
        if event.type == pg.QUIT: pg.quit(); sys.exit()
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE and popup_state == POPUP_NONE:
            paused = not paused
            if paused: refresh_save_slots(); nav_cursor = [0, 0]

def handle_input_page1(event):
    global nav_cursor, paused, save_msg, save_msg_timer, active_slot_index, fading_out, is_flipping, ui_interactive, fade_alpha
    col, row = nav_cursor
    
    # === 上下鍵邏輯 (修改：切斷存檔與讀檔的上下連結) ===
    if event.key == pg.K_UP:
        if col == 1 and row >= 3: 
            # 如果在「存檔(3)」或「讀檔(4)」，按上都直接跳回 Slot 3 (2)
            # 這樣視覺上比較自然，且不會讓讀檔誤觸存檔
            nav_cursor[1] = 2
        else:
            nav_cursor[1] = max(0, row - 1)

    elif event.key == pg.K_DOWN:
        # 左側選單 max=3, 右側選單現在 max 也限制為 3 (只到存檔)
        # 這樣在「存檔」按「下」時，不會跳到「讀檔」
        max_row = 3 
        
        # 只有當目前還沒到底部時才移動 (如果在 Row 4 讀檔，按下也不動)
        if row < max_row:
            nav_cursor[1] = row + 1

    # === 左鍵邏輯 (維持：讀檔 -> 存檔) ===
    elif event.key == pg.K_LEFT:
        if col == 1:
            if row == 4: # 如果在「讀檔」
                nav_cursor[1] = 3 # 往左回到「存檔」
            else:
                if row == 3: row = 3 
                nav_cursor = [0, min(row, 3)]
        else:
            if row == 1: slider_music.change_value(-0.01)
            elif row == 2: slider_sfx.change_value(-0.01)

    # === 右鍵邏輯 (維持：存檔 -> 讀檔) ===
    elif event.key == pg.K_RIGHT:
        if col == 0: 
            if row == 1: slider_music.change_value(0.01)
            elif row == 2: slider_sfx.change_value(0.01)
            else: nav_cursor = [1, row] 
        else: 
            if row == 3: # 如果在「存檔」
                nav_cursor[1] = 4 # 往右移到「讀檔」
            else:
                # 其他情況 (包含在「讀檔」按鈕時) 才翻頁
                fading_out, is_flipping, ui_interactive, fade_alpha = True, True, False, 255

    # === 確認鍵邏輯 (不變) ===
    elif event.key in (pg.K_RETURN, pg.K_SPACE, pg.K_z):
        if col == 0:
            if row == 0: paused = False
            elif row == 3: pg.quit(); sys.exit()
        elif col == 1:
            if row <= 2: active_slot_index = row
            elif row == 3: save_msg, save_msg_timer = save_current_slot(active_slot_index), 60
            elif row == 4: save_msg, save_msg_timer = load_current_slot(active_slot_index), 60

def handle_input_page2(event):
    global p2_section, p2_char_idx, p2_item_idx, fading_out, is_flipping, ui_interactive, fade_alpha
    global popup_state, rune_cursor, target_cursor, selected_rune_data, popup_timer
    if popup_state == POPUP_RUNE_SELECT:
        if event.key == pg.K_LEFT and rune_cursor % 2 == 1: rune_cursor -= 1
        elif event.key == pg.K_RIGHT and rune_cursor % 2 == 0: rune_cursor += 1
        elif event.key == pg.K_UP and rune_cursor >= 2: rune_cursor -= 2
        elif event.key == pg.K_DOWN and rune_cursor <= 3: rune_cursor += 2
        elif event.key in (pg.K_RETURN, pg.K_SPACE, pg.K_z):
            selected_rune_data = RUNES_DATA[rune_cursor]; popup_state, target_cursor = POPUP_TARGET_SELECT, 0
        elif event.key == pg.K_ESCAPE: popup_state = POPUP_NONE
        return
    elif popup_state == POPUP_TARGET_SELECT:
        if event.key == pg.K_UP: target_cursor = max(0, target_cursor - 1)
        elif event.key == pg.K_DOWN: target_cursor = min(len(game_data.party_data) - 1, target_cursor + 1)
        elif event.key in (pg.K_RETURN, pg.K_z): confirm_target_selection()
        elif event.key == pg.K_ESCAPE: popup_state = POPUP_RUNE_SELECT if selected_rune_data else POPUP_NONE
        return
    elif popup_state == POPUP_MSG:
        if event.type == pg.KEYDOWN: popup_state = POPUP_NONE
        return
    if p2_section == 0: 
        if event.key == pg.K_LEFT:
            if p2_char_idx > 0: p2_char_idx -= 1
            else: fading_out, is_flipping, ui_interactive, fade_alpha = True, True, False, 255 
        elif event.key == pg.K_RIGHT:
            if p2_char_idx < P2_CHAR_COUNT - 1: p2_char_idx += 1
            else: 
                p2_section = 1; p2_item_idx = min(p2_item_idx, max(0, min(len(inventory_list), P2_ITEM_COUNT)-1))
                if not inventory_list: p2_section = 0
    else: 
        if not inventory_list: p2_section = 0; return
        if event.key == pg.K_UP: p2_item_idx = max(0, p2_item_idx - 1)
        elif event.key == pg.K_DOWN: p2_item_idx = min(min(len(inventory_list), P2_ITEM_COUNT)-1, p2_item_idx + 1)
        elif event.key == pg.K_LEFT: p2_section, p2_char_idx = 0, P2_CHAR_COUNT - 1
        elif event.key in (pg.K_RETURN, pg.K_z): trigger_item_usage(p2_item_idx)

def draw_text_multiline(surf, text, x, y, font, color, lh):
    for i, line in enumerate(text.split('\n')):
        s = font.render(line, True, color); surf.blit(s, (x, y + i * lh))

def draw_page1(surf):
    col, row = nav_cursor
    surf.blit(font_big.render("遊戲暫停", True, (90, 74, 66)), (s_x(150), s_y(100)))
    
    c = (141, 114, 89) if col==0 and row==0 else (191, 164, 139)
    pg.draw.rect(surf, (191, 164, 139), continue_rect, 2, s_x(6))
    if col==0 and row==0: pg.draw.rect(surf, (141, 114, 89), continue_rect, 3, s_x(6))
    txt = font_mid.render("繼續遊戲", True, c); surf.blit(txt, txt.get_rect(center=continue_rect.center))

    slider_music.draw(surf); game_data.volume = slider_music.get_value(); pg.mixer.music.set_volume(game_data.volume)
    if col==0 and row==1: pg.draw.rect(surf, (214, 132, 115), slider_music.rect.inflate(10, 20), 2, 5) 
    tc = (90, 74, 66) if col==0 and row==1 else (166, 138, 118)
    surf.blit(font_small.render(f"音樂: {int(game_data.volume*100)}%", True, tc), (s_x(130+50), s_y(290-30)))

    slider_sfx.draw(surf); game_data.sfx_volume = slider_sfx.get_value()
    if col==0 and row==2: pg.draw.rect(surf, (214, 132, 115), slider_sfx.rect.inflate(10, 20), 2, 5)
    tc = (90, 74, 66) if col==0 and row==2 else (166, 138, 118)
    surf.blit(font_small.render(f"音效: {int(game_data.sfx_volume*100)}%", True, tc), (s_x(130+50), s_y(290 + 70 - 30)))

    c = (141, 114, 89) if col==0 and row==3 else (191, 164, 139)
    pg.draw.rect(surf, (191, 164, 139), exit_rect, 2, s_x(6))
    if col==0 and row==3: pg.draw.rect(surf, (141, 114, 89), exit_rect, 3, s_x(6))
    txt = font_mid.render("退出遊戲", True, c); surf.blit(txt, txt.get_rect(center=exit_rect.center))

    surf.blit(font_mid.render("冒險紀錄", True, (90, 74, 66)), (s_x(530), s_y(110)))
    for i, r in enumerate(slot_rects):
        is_sel, is_act = (col==1 and row==i), (i == active_slot_index)
        pg.draw.rect(surf, (250, 248, 245), r, border_radius=s_x(6))
        c_border = (141, 114, 89) if is_sel else ((191, 164, 139) if is_act else (166, 138, 118))
        pg.draw.rect(surf, c_border, r, 3 if is_sel or is_act else 1, s_x(6))
        d = save_slots_cache[i]
        surf.blit(font_mid.render(f"No.{i+1}", True, (90, 74, 66)), (r.x+s_x(10), r.y+s_y(10)))
        if d:
            total_sec = int(d.get('playtime', 0)); mm, ss = divmod(total_sec, 60); hh, mm = divmod(mm, 60)
            surf.blit(font_small.render(d.get("timestamp", ""), True, (90, 74, 66)), (r.right-s_x(90), r.y+s_y(10)))
            surf.blit(font_small.render(f"Time: {hh:02d}:{mm:02d}:{ss:02d}", True, (166, 138, 118)), (r.x+s_x(10), r.bottom-s_y(25)))
        else: surf.blit(font_mid.render("----", True, (166, 138, 118)), (r.centerx-s_x(10), r.centery-s_y(5)))

    for r, t, is_f in [(btn_save_rect, "存檔", col==1 and row==3), (btn_load_rect, "讀檔", col==1 and row==4)]:
        pg.draw.rect(surf, (191, 164, 139), r, 2, s_x(6))
        if is_f: pg.draw.rect(surf, (141, 114, 89), r, 3, s_x(6))
        ts = font_mid.render(t, True, (255, 255, 255) if is_f else (191, 164, 139)); surf.blit(ts, ts.get_rect(center=r.center))

    if save_msg_timer > 0:
        ms = font_small.render(save_msg, True, (214, 132, 115))
        surf.blit(ms, ms.get_rect(center=(s_x(470 + 200//2), btn_save_rect.bottom + s_y(25))))
    
    # Page 1 翻頁箭頭
    pg.draw.polygon(surf, (141, 114, 89), [
        (s_x(710), HEIGHT//2 + s_y(10)), 
        (s_x(690), HEIGHT//2), 
        (s_x(690), HEIGHT//2+s_y(20))
    ])

def draw_page2(surf):
    surf.blit(font_mid.render("角色", True, (90, 74, 66)), (s_x(210), s_y(100)))

    for i, r in enumerate(boxes_chars):
        is_f = (p2_section == 0 and p2_char_idx == i and popup_state == POPUP_NONE)
        pg.draw.rect(surf, (250, 248, 245), r, border_radius=s_x(6))
        pg.draw.rect(surf, (141, 114, 89) if is_f else (166, 138, 118), r, 3 if is_f else 1, s_x(6))
        d = game_data.party_data[i]

        # 1. 名字 (置頂)
        char_txt = font_mid.render(d['name'], True, (90, 74, 66))
        char_rect = char_txt.get_rect(center=(r.centerx, r.y + s_y(20)))
        surf.blit(char_txt, char_rect)

        # 2. 照片區域 (中間，只處理 U 的照片)
        photo_h = s_y(65)
        photo_rect = pg.Rect(0, 0, r.width - s_x(10), photo_h)
        photo_rect.center = (r.centerx, r.centery - s_y(5))
        
        # === 載入圖片 ===
        if d['name'] == "U":
            try:
                # 組成路徑：base_dir/picture/chuchutest/u_stand.png
                img_path = os.path.join(base_dir, "picture", "chuchutest", "u_stand.png")
                if os.path.exists(img_path):
                    img = pg.image.load(img_path).convert_alpha()
                    # 保持比例縮放
                    scale = min(photo_rect.width / img.get_width(), photo_rect.height / img.get_height())
                    new_w = int(img.get_width() * scale)
                    new_h = int(img.get_height() * scale)
                    img = pg.transform.smoothscale(img, (new_w, new_h))
                    # 居中繪製
                    img_draw_rect = img.get_rect(center=photo_rect.center)
                    surf.blit(img, img_draw_rect)
            except:
                pass # 讀取失敗就留白
        else:
            # 其他角色 (K, W, C, O) 什麼都不畫，保持空白
            pass

        # 3. 血條
        hp_ratio = d["hp"] / d["max_hp"]
        bar_w = r.width - s_x(12)
        bar_h = s_y(12)
        bar_bg = pg.Rect(0, 0, bar_w, bar_h)
        bar_bg.midbottom = (r.centerx, r.bottom - s_y(15))
        
        pg.draw.rect(surf, (200, 200, 200), bar_bg, border_radius=3)
        if hp_ratio > 0:
            bar_fill = pg.Rect(bar_bg.x, bar_bg.y, int(bar_w * hp_ratio), bar_h)
            pg.draw.rect(surf, (167, 191, 139), bar_fill, border_radius=3)
        pg.draw.rect(surf, (150, 150, 150), bar_bg, 1, border_radius=3)

        if is_f: ov = pg.Surface(r.size, pg.SRCALPHA); ov.fill((191, 164, 139, 50)); surf.blit(ov, r)

    pg.draw.rect(surf, (191, 164, 139), desc_rect_l, 2, s_x(6))
    cd = game_data.party_data[p2_char_idx]
    surf.blit(font_small.render(f"[ {cd['name']} ]  HP: {cd['hp']}/{cd['max_hp']}", True, (90, 74, 66)), (desc_rect_l.x+s_x(10), desc_rect_l.y+s_y(10)))
    draw_text_multiline(surf, cd['desc'], desc_rect_l.x+s_x(10), desc_rect_l.y+s_y(35), font_small, (166, 138, 118), s_y(20))

    surf.blit(font_mid.render("背包", True, (90, 74, 66)), (s_x(540), s_y(100)))
    
    for i, r in enumerate(boxes_items):
        if i >= len(inventory_list): pg.draw.rect(surf, (250, 248, 245, 100), r, border_radius=s_x(6)); continue
        is_f = (p2_section == 1 and p2_item_idx == i and popup_state == POPUP_NONE)
        pg.draw.rect(surf, (250, 248, 245), r, border_radius=s_x(6))
        pg.draw.rect(surf, (141, 114, 89) if is_f else (166, 138, 118), r, 3 if is_f else 1, s_x(6))
        item = inventory_list[i]
        surf.blit(font_mid.render(item["name"], True, (90, 74, 66) if is_f else (166, 138, 118)), (r.x+s_x(10), r.centery-s_y(15)))
        surf.blit(font_mid.render(f"x{item['count']}", True, (90, 74, 66) if is_f else (214, 132, 115)), (r.right-s_x(35), r.centery-s_y(15)))
        if is_f: ov = pg.Surface(r.size, pg.SRCALPHA); ov.fill((191, 164, 139, 50)); surf.blit(ov, r)

    pg.draw.rect(surf, (191, 164, 139), desc_rect_r, 2, s_x(6))
    if inventory_list and p2_item_idx < len(inventory_list):
        it = inventory_list[p2_item_idx]
        surf.blit(font_small.render(f"[ {it['name']} ]", True, (90, 74, 66)), (desc_rect_r.x+s_x(10), desc_rect_r.y+s_y(10)))
        draw_text_multiline(surf, it['desc'], desc_rect_r.x+s_x(10), desc_rect_r.y+s_y(35), font_small, (166, 138, 118), s_y(20))
    
    if popup_state == POPUP_NONE:
        # Page 2 翻頁箭頭
        pg.draw.polygon(surf, (141, 114, 89), [
            (s_x(90), HEIGHT//2 + s_y(10)), 
            (s_x(110), HEIGHT//2), 
            (s_x(110), HEIGHT//2+s_y(20))
        ])
    if popup_state != POPUP_NONE: draw_popup(surf)

def draw_popup(surf):
    mask = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA); mask.fill((0,0,0,140)); surf.blit(mask, (0,0))
    cx, cy = WIDTH//2, HEIGHT//2
    if popup_state == POPUP_RUNE_SELECT:
        r = s_rect(0,0,420,320); r.center = (cx, cy)
        pg.draw.rect(surf, (250, 248, 245), r, border_radius=10); pg.draw.rect(surf, (191, 164, 139), r, 3, 10)
        t = font_mid.render("選擇刻印符文", True, (90, 74, 66)); surf.blit(t, t.get_rect(center=(cx, r.top+s_y(30))))
        sx, sy = r.centerx - s_x(190), r.top + s_y(80)
        for i, rune in enumerate(RUNES_DATA):
            rr = pg.Rect(sx + (i%2)*s_x(200), sy + (i//2)*s_y(70), s_x(180), s_y(55))
            is_s = (i == rune_cursor)
            pg.draw.rect(surf, (255, 255, 255) if is_s else (242, 235, 225), rr, border_radius=5)
            pg.draw.rect(surf, (141, 114, 89) if is_s else (191, 164, 139), rr, 2, 5)
            surf.blit(font_mid.render(f"{rune['symbol']} {rune['name']}", True, (141, 114, 89) if is_s else (191, 164, 139)), (rr.x+s_x(10), rr.y+s_y(5)))
            surf.blit(font_small.render(f"{rune['stat']} UP", True, (166, 138, 118)), (rr.right-s_x(50), rr.bottom-s_y(20)))
    elif popup_state == POPUP_TARGET_SELECT:
        r = s_rect(0,0,300,300); r.center = (cx, cy)
        pg.draw.rect(surf, (250, 248, 245), r, border_radius=10); pg.draw.rect(surf, (191, 164, 139), r, 3, 10)
        tt = f"使用 {selected_rune_data['symbol']} 於..." if selected_rune_data else "選擇對象"
        t = font_mid.render(tt, True, (90, 74, 66)); surf.blit(t, t.get_rect(center=(cx, r.top+s_y(30))))
        for i, char in enumerate(game_data.party_data):
            tr = pg.Rect(r.left+s_x(20), r.top+s_y(70)+i*s_y(40), r.width-s_x(40), s_y(35))
            if i == target_cursor: pg.draw.rect(surf, (141, 114, 89), tr, border_radius=5)
            c = (255, 255, 255) if i == target_cursor else (90, 74, 66)
            surf.blit(font_mid.render(char["name"], True, c), (tr.x+s_x(10), tr.centery-s_y(15)))
    elif popup_state == POPUP_MSG:
        r = s_rect(0,0,320,120); r.center = (cx, cy)
        pg.draw.rect(surf, (250, 248, 245), r, border_radius=10); pg.draw.rect(surf, (214, 132, 115), r, 2, 10)
        draw_text_multiline(surf, popup_message, r.x+s_x(20), r.y+s_y(25), font_mid, (90, 74, 66), s_y(30))

def run_pause_menu(surface, events):
    global ui_interactive, current_page, fade_alpha, fading_out, fading_in, is_flipping, nav_cursor, p2_section, p2_char_idx
    if ui_interactive:
        for event in events:
            if event.type == pg.KEYDOWN:
                if current_page == 1: handle_input_page1(event)
                else: handle_input_page2(event)

    overlay = pg.Surface((WIDTH, HEIGHT)); overlay.set_alpha(120); overlay.fill((40, 30, 20)); surface.blit(overlay, (0, 0))
    if os.path.exists(bg_path): surface.blit(background, bg_rect)
    else: pg.draw.rect(surface, (250, 248, 245), bg_rect, border_radius=10)

    pause_layer = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    if fading_out:
        pause_layer.set_alpha(fade_alpha)
        if current_page == 1: draw_page1(pause_layer)
        else: draw_page2(pause_layer)
        fade_alpha -= 30
        if fade_alpha <= 0:
            fade_alpha, fading_out, fading_in = 0, False, True
            current_page = 2 if current_page == 1 else 1
            if current_page == 2: p2_section, p2_char_idx = 0, 0
            else: nav_cursor = [1, 0]
    elif fading_in:
        pause_layer.set_alpha(fade_alpha)
        if current_page == 1: draw_page1(pause_layer)
        else: draw_page2(pause_layer)
        fade_alpha += 30
        if fade_alpha >= 255: fade_alpha, fading_in, is_flipping, ui_interactive = 255, False, False, True
    else:
        if current_page == 1: draw_page1(pause_layer)
        else: draw_page2(pause_layer)
    surface.blit(pause_layer, (0, 0))

# --- 主迴圈 ---
refresh_save_slots()
pg.mixer.music.set_volume(game_data.volume)
while True:
    clock.tick(30)
    events = pg.event.get()
    handle_global_input(events)
    screen.fill((216, 226, 233)) 
    if paused: run_pause_menu(screen, events)
    else:
        t = font_big.render("PRESS ESC", True, (100,100,100))
        screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2)))
    pg.display.flip()