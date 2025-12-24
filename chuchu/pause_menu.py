import os, sys
import pygame as pg
import json
import time
import random
from datetime import datetime

# === 初始化 ===
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
sys.path.insert(0, base_dir)

pg.init()
pg.key.set_repeat(300, 30)

WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Milk Tea Save System - Rune Update")
clock = pg.time.Clock()

# ==========================================
# === 🎨 奶茶色系與 Style ===
# ==========================================
GLOBAL_RADIUS = 6
C_THEME       = (191, 164, 139)   
C_TEXT_DARK   = (90, 74, 66)      
C_TEXT_LIGHT  = (166, 138, 118)   
C_BG_PAPER    = (250, 248, 245)   
C_BG_OVERLAY  = (242, 235, 225)   
C_WHITE       = (255, 255, 255)   
C_ALERT       = (214, 132, 115)   
C_SELECTED    = (141, 114, 89)    
C_HP_BAR      = (167, 191, 139)

# ==========================================
# === 📐 介面佈局配置 ===
# ==========================================
PADDING_SMALL = 10
BTN_H         = 40  

# --- Page 1 ---
P1_MENU_CENTER_X = 210
P1_BTN_W         = 140
P1_CONTINUE_Y    = 210
P1_EXIT_Y        = 460
P1_SLIDER_X      = 110
P1_SLIDER_MUSIC_Y= 290
P1_SLIDER_SFX_Y  = 360
P1_SLIDER_W      = 200
P1_SAVE_PANEL_X  = 460
P1_SAVE_PANEL_Y  = 110
P1_SLOT_W        = 240
P1_SLOT_H        = 80
P1_SLOT_GAP      = 10
P1_ACTION_BTN_W  = 100
P1_BTN_SAVE_X    = P1_SAVE_PANEL_X + 10
P1_BTN_LOAD_X    = P1_SAVE_PANEL_X + 130
P1_BTN_ACTION_Y  = P1_SAVE_PANEL_Y + 320

# --- Page 2 ---
P2_CHAR_COUNT    = 5
P2_CHAR_W        = 55
P2_CHAR_H        = 110
P2_CHAR_GAP      = 8
P2_CHAR_START_Y  = 160
P2_ITEM_COUNT    = 3
P2_ITEM_W        = 220
P2_ITEM_H        = 45
P2_ITEM_GAP      = 10
P2_ITEM_START_Y  = 160
P2_DESC_H        = 150
P2_DESC_BOTTOM_M = 70

# ==========================================
# === 🛠️ Slider 類別 ===
# ==========================================
class Slider:
    def __init__(self, x, y, w, h, init_val=0.5, bg_color=(200, 200, 200), fill_color=(150, 150, 150), handle_color=(100, 100, 100)):
        self.rect = pg.Rect(x, y, w, h)
        self.val = max(0.0, min(1.0, init_val))  
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.handle_color = handle_color

    def change_value(self, amount):
        self.val += amount
        self.val = max(0.0, min(1.0, self.val)) 

    def set_value(self, new_val):
        self.val = max(0.0, min(1.0, new_val))

    def get_value(self):
        return self.val

    def draw(self, surface):
        pg.draw.rect(surface, self.bg_color, self.rect, border_radius=self.rect.height//2)
        fill_width = int(self.rect.width * self.val)
        if fill_width > 0:
            fill_rect = pg.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pg.draw.rect(surface, self.fill_color, fill_rect, border_radius=self.rect.height//2)
        handle_x = self.rect.x + fill_width
        handle_y = self.rect.centery
        pg.draw.circle(surface, self.handle_color, (handle_x, handle_y), self.rect.height + 3)

# ==========================================
# === 🔮 盧恩符文資料 (Runes) ===
# ==========================================
# 這裡定義六種符文與其對應的數值代號
RUNES_DATA = [
    {"symbol": "ᛒ", "name": "Berkano", "stat": "HP",  "desc": "成長、孕育、生命延展"},
    {"symbol": "ᛚ", "name": "Laguz",   "stat": "INT", "desc": "流動、循環、回復"},
    {"symbol": "ᛞ", "name": "Dagaz",   "stat": "CRT", "desc": "突破、瞬間轉變"},
    {"symbol": "ᛋ", "name": "Sowilo",  "stat": "ENG", "desc": "太陽、核心能量"}, # ENG = 能量上限
    {"symbol": "ᛏ", "name": "Tiwaz",   "stat": "ATK", "desc": "武勇、正面戰力"},
    {"symbol": "ᛉ", "name": "Algiz",   "stat": "DEF", "desc": "守護、警覺、防護"}
]

# ==========================================
# === 核心資料 (GameData) ===
# ==========================================
SAVE_DIR = "saves"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

CHAR_DEFAULTS = [
    {"name": "U", "desc": "平衡型戰士", "hp": 80, "max_hp": 100},
    {"name": "法師", "desc": "高輸出單位", "hp": 45, "max_hp": 60},
    {"name": "盜賊", "desc": "高速度單位", "hp": 60, "max_hp": 70},
    {"name": "牧師", "desc": "支援型單位", "hp": 50, "max_hp": 60}, 
    {"name": "騎士", "desc": "防禦型單位", "hp": 110, "max_hp": 120}  
]

class GameData:
    def __init__(self):
        self.chapter = 1
        self.money = 100
        self.total_playtime = 0.0
        self._session_start = time.time() 
        self.volume = 0.5      
        self.sfx_volume = 0.5  
        self.party_data = [c.copy() for c in CHAR_DEFAULTS]
        
        # === 新增：升級紀錄變數 ===
        # 這裡只儲存紀錄，不涉及複雜運算
        # 格式範例: {"timestamp": "...", "char": "U", "source": "Berkano", "effect": "HP UP"}
        self.upgrade_log = [] 

    def get_current_playtime(self):
        return self.total_playtime + (time.time() - self._session_start)

    def to_dict(self):
        return {
            "chapter": self.chapter,
            "money": self.money,
            "playtime": self.get_current_playtime(),
            "volume": self.volume,
            "sfx_volume": self.sfx_volume,
            "party_data": self.party_data,
            "upgrade_log": self.upgrade_log, # 存檔包含紀錄
            "timestamp": datetime.now().strftime("%m/%d %H:%M") 
        }

    def load_from_dict(self, data):
        self.chapter = data.get("chapter", 1)
        self.money = data.get("money", 0)
        self.total_playtime = data.get("playtime", 0.0)
        self.volume = data.get("volume", 0.5)
        self.sfx_volume = data.get("sfx_volume", 0.5)
        self.party_data = data.get("party_data", [c.copy() for c in CHAR_DEFAULTS])
        self.upgrade_log = data.get("upgrade_log", [])
        self._session_start = time.time()

game_data = GameData()
save_slots_cache = [None, None, None]
save_msg = ""
save_msg_timer = 0

def refresh_save_slots():
    global save_slots_cache
    for i in range(3):
        filename = os.path.join(SAVE_DIR, f"save_{i}.json")
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    save_slots_cache[i] = json.load(f)
            except:
                save_slots_cache[i] = None
        else:
            save_slots_cache[i] = None

pg.mixer.init()
slider_music = Slider(P1_SLIDER_X, P1_SLIDER_MUSIC_Y, P1_SLIDER_W, 5, init_val=game_data.volume, 
                bg_color=C_TEXT_LIGHT, fill_color=C_THEME, handle_color=C_TEXT_DARK)
slider_sfx = Slider(P1_SLIDER_X, P1_SLIDER_SFX_Y, P1_SLIDER_W, 5, init_val=game_data.sfx_volume, 
                bg_color=C_TEXT_LIGHT, fill_color=C_THEME, handle_color=C_TEXT_DARK)

def save_current_slot(slot_idx):
    filename = os.path.join(SAVE_DIR, f"save_{slot_idx}.json")
    game_data.volume = slider_music.get_value()
    game_data.sfx_volume = slider_sfx.get_value()
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(game_data.to_dict(), f, indent=4)
        refresh_save_slots()
        return "存檔成功"
    except Exception as e:
        return f"錯誤: {e}"

def load_current_slot(slot_idx):
    filename = os.path.join(SAVE_DIR, f"save_{slot_idx}.json")
    if not os.path.exists(filename):
        return "無存檔"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        game_data.load_from_dict(data)
        slider_music.set_value(game_data.volume)
        slider_sfx.set_value(game_data.sfx_volume)
        pg.mixer.music.set_volume(game_data.volume)
        return "讀檔成功"
    except Exception as e:
        return f"錯誤: {e}"

def format_playtime_detailed(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

refresh_save_slots()
pg.mixer.music.set_volume(game_data.volume)

# ==========================================
# === 🖼️ UI 資源與 Rect ===
# ==========================================
class MockBtn(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((100, 50)); self.image.fill(C_THEME)
        self.rect = self.image.get_rect(center=(60, 30))
    def update(self): pass

pause_btn = MockBtn()
buttons = pg.sprite.Group(pause_btn)

try:
    bg_path = os.path.join(base_dir, "picture", "chuchutest", "book1.png")
    background = pg.image.load(bg_path).convert_alpha()
    bg_size = (int(background.get_width() * 0.4), int(background.get_height() * 0.5))
    background = pg.transform.scale(background, bg_size)
    bg_rect = background.get_rect(center=(WIDTH // 2, HEIGHT // 2))
except:
    background = pg.Surface((640, 420)); background.fill(C_BG_PAPER)
    bg_rect = background.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# 字型
font_path = os.path.join(base_dir, "font", "NotoSansTC-VariableFont_wght.ttf")
try:
    font_big = pg.font.Font(font_path, 50)
    font_mid = pg.font.Font(font_path, 25)
    font_small = pg.font.Font(font_path, 15)
except:
    font_big = pg.font.SysFont("arial", 50)
    font_mid = pg.font.SysFont("arial", 25)
    font_small = pg.font.SysFont("arial", 15)

# Rects
continue_rect = pg.Rect(0, 0, P1_BTN_W, BTN_H); continue_rect.center = (P1_MENU_CENTER_X, P1_CONTINUE_Y)
exit_rect = pg.Rect(0, 0, P1_BTN_W, BTN_H); exit_rect.center = (P1_MENU_CENTER_X, P1_EXIT_Y)

slot_rects = []
for i in range(3):
    r = pg.Rect(P1_SAVE_PANEL_X, P1_SAVE_PANEL_Y + 40 + i*(P1_SLOT_H + P1_SLOT_GAP), P1_SLOT_W, P1_SLOT_H)
    slot_rects.append(r)

btn_save_rect = pg.Rect(P1_BTN_SAVE_X, P1_BTN_ACTION_Y, P1_ACTION_BTN_W, BTN_H)
btn_load_rect = pg.Rect(P1_BTN_LOAD_X, P1_BTN_ACTION_Y, P1_ACTION_BTN_W, BTN_H)

page_width = bg_rect.width // 2
left_page_center_x = bg_rect.left + page_width // 2
right_page_center_x = bg_rect.right - page_width // 2
total_chars_width = (P2_CHAR_W * P2_CHAR_COUNT) + (P2_CHAR_GAP * (P2_CHAR_COUNT - 1))
start_char_x = left_page_center_x - (total_chars_width // 2) 

boxes_chars = []
for i in range(P2_CHAR_COUNT): 
    r = pg.Rect(start_char_x + i * (P2_CHAR_W + P2_CHAR_GAP), P2_CHAR_START_Y, P2_CHAR_W, P2_CHAR_H)
    boxes_chars.append(r)

start_item_x = right_page_center_x - (P2_ITEM_W // 2)
boxes_items = []
for i in range(P2_ITEM_COUNT): 
    r = pg.Rect(start_item_x, P2_ITEM_START_Y + i * (P2_ITEM_H + P2_ITEM_GAP), P2_ITEM_W, P2_ITEM_H)
    boxes_items.append(r)

desc_y_pos = bg_rect.bottom - P2_DESC_H - P2_DESC_BOTTOM_M
desc_l_rect = pg.Rect(start_char_x, desc_y_pos, total_chars_width, P2_DESC_H)
desc_r_rect = pg.Rect(start_item_x, desc_y_pos, P2_ITEM_W, P2_DESC_H) 

# 道具清單
ITEM_TYPES = [
    {"name": "能量飲料", "desc": "咕嚕咕嚕\n紀錄：能量+3", "type": "consumable", "effect": "ENG +3"},
    {"name": "堅果棒", "desc": "真香\n紀錄：回復20%血量", "type": "consumable", "effect": "HP +20%"},
    {"name": "空白符文", "desc": "未刻印的石板\n點擊開啟刻印選單", "type": "rune", "effect": "Rune Upgrade"}
]

def create_stacked_inventory():
    raw_items = []
    for _ in range(30):
        raw_items.append(random.choice(ITEM_TYPES))
    stacked = {}
    for item in raw_items:
        name = item["name"]
        if name not in stacked:
            stacked[name] = item.copy()
            stacked[name]["count"] = 0
        stacked[name]["count"] += 1
    return list(stacked.values())

inventory_list = create_stacked_inventory()

# ==========================================
# === 🎮 導航變數與狀態機 ===
# ==========================================
paused = False
current_page = 1
fade_alpha = 255
is_flipping = False
fading_out = False
fading_in = False
ui_interactive = True
nav_cursor = [0, 0] 
active_slot_index = 0 

p2_section = 0 
p2_char_idx = 0
p2_item_idx = 0        

# --- 狀態控制定義 ---
POPUP_NONE = 0
POPUP_RUNE_SELECT = 1   # 選擇符文效果 (6宮格)
POPUP_TARGET_SELECT = 2 # 選擇施放目標 (清單選擇)
POPUP_MSG = 3           # 顯示訊息

popup_state = POPUP_NONE
rune_cursor = 0         # 0~5 (符文游標)
target_cursor = 0       # 0~4 (角色選擇游標)
selected_rune_data = None # 暫存選中的符文
popup_timer = 0         
popup_message = ""

# 觸發物品使用 (Enter)
def trigger_item_usage(item_idx):
    global popup_state, rune_cursor, target_cursor, selected_rune_data
    
    if item_idx >= len(inventory_list): return
    item = inventory_list[item_idx]
    
    if item["type"] == "rune":
        popup_state = POPUP_RUNE_SELECT
        rune_cursor = 0
        selected_rune_data = None
    else:
        # 一般消耗品，直接進選人視窗
        popup_state = POPUP_TARGET_SELECT
        target_cursor = 0
        selected_rune_data = None # 代表這是普通道具

# 確認選擇目標
def confirm_target_selection():
    global popup_state, popup_message, popup_timer, p2_item_idx
    
    # 1. 取得目標角色
    target_char = game_data.party_data[target_cursor]
    
    # 2. 判斷來源 (符文 OR 道具)
    item_idx = p2_item_idx
    if item_idx >= len(inventory_list): return # 防呆

    current_item = inventory_list[item_idx]
    
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "char_name": target_char["name"],
        "source": "",
        "effect": ""
    }

    # === 符文邏輯 ===
    if selected_rune_data: 
        rune = selected_rune_data
        log_entry["source"] = f"Rune: {rune['name']}"
        log_entry["effect"] = f"{rune['stat']} UP"
        popup_message = f"{target_char['name']} 獲得\n[{rune['name']}] 刻印 !"
        
        # 扣除空白符文
        current_item["count"] -= 1

    # === 消耗品邏輯 ===
    else: 
        log_entry["source"] = current_item["name"]
        log_entry["effect"] = current_item["effect"]
        popup_message = f"對 {target_char['name']} 使用了\n{current_item['name']} !"
        
        # 簡單的視覺回饋 (雖然主要邏輯在外部，但這裡演一下)
        if "HP" in current_item["effect"]:
            heal = int(target_char["max_hp"] * 0.2)
            target_char["hp"] = min(target_char["hp"] + heal, target_char["max_hp"])
        
        current_item["count"] -= 1

    # === 共同結尾 ===
    # 紀錄到 GameData 變數
    game_data.upgrade_log.append(log_entry)

    # 移除數量歸零的道具
    if current_item["count"] <= 0:
        inventory_list.pop(item_idx)
        if p2_item_idx >= len(inventory_list):
            p2_item_idx = max(0, len(inventory_list) - 1)
    
    popup_state = POPUP_MSG
    popup_timer = 50

# ==========================================
# === 輸入處理函式 ===
# ==========================================

def handle_input_page1(event):
    global nav_cursor, paused, save_msg, save_msg_timer, active_slot_index, fading_out, is_flipping, ui_interactive, fade_alpha

    col, row = nav_cursor
    # ... (Page 1 輸入邏輯保持不變) ...
    if event.key == pg.K_UP:
        if col == 1 and (row == 3 or row == 4): row = 2
        else: row -= 1
        if row < 0: row = 0 
        nav_cursor[1] = row
            
    elif event.key == pg.K_DOWN:
        max_row = 3 if col == 0 else 4
        row += 1
        if row > max_row: row = max_row
        nav_cursor[1] = row

    elif event.key == pg.K_LEFT:
        if col == 0 and row == 1: slider_music.change_value(-0.01); return 
        if col == 0 and row == 2: slider_sfx.change_value(-0.01); return 
        if col == 1:
            if row == 4: row = 3; nav_cursor = [col, row]; return
            col = 0; 
            if row > 3: row = 3
            nav_cursor = [col, row]

    elif event.key == pg.K_RIGHT:
        if col == 0 and row == 1: slider_music.change_value(0.01); return
        if col == 0 and row == 2: slider_sfx.change_value(0.01); return 
        if col == 0:
            col = 1; nav_cursor = [col, row]
        else:
            if row == 3: row = 4; nav_cursor = [col, row]; return
            fading_out = True; is_flipping = True; ui_interactive = False; fade_alpha = 255

    elif event.key in (pg.K_RETURN, pg.K_z, pg.K_SPACE):
        if col == 0:
            if row == 0: paused = False 
            if row == 3: pg.quit(); sys.exit() 
        elif col == 1:
            if 0 <= row <= 2: active_slot_index = row
            elif row == 3: save_msg = save_current_slot(active_slot_index); save_msg_timer = 60
            elif row == 4: save_msg = load_current_slot(active_slot_index); save_msg_timer = 60

def handle_input_page2(event):
    global p2_section, p2_char_idx, p2_item_idx, fading_out, is_flipping, ui_interactive, fade_alpha
    global popup_state, rune_cursor, selected_rune_data, target_cursor, popup_timer
    
    max_item_idx = max(0, min(len(inventory_list), P2_ITEM_COUNT) - 1)

    # --- 1. 符文選擇視窗 (6宮格) ---
    if popup_state == POPUP_RUNE_SELECT:
        if event.key == pg.K_LEFT:
            if rune_cursor % 2 == 1: rune_cursor -= 1
        elif event.key == pg.K_RIGHT:
            if rune_cursor % 2 == 0: rune_cursor += 1
        elif event.key == pg.K_UP:
            if rune_cursor >= 2: rune_cursor -= 2
        elif event.key == pg.K_DOWN:
            if rune_cursor <= 3: rune_cursor += 2
        elif event.key in (pg.K_RETURN, pg.K_SPACE, pg.K_z):
            selected_rune_data = RUNES_DATA[rune_cursor]
            popup_state = POPUP_TARGET_SELECT # 進選人
            target_cursor = 0 
        elif event.key == pg.K_ESCAPE:
            popup_state = POPUP_NONE
        return

    # --- 2. 目標選擇視窗 (清單) ---
    elif popup_state == POPUP_TARGET_SELECT:
        if event.key == pg.K_UP:
            if target_cursor > 0: target_cursor -= 1
        elif event.key == pg.K_DOWN:
            if target_cursor < len(game_data.party_data) - 1: target_cursor += 1
        elif event.key in (pg.K_RETURN, pg.K_SPACE, pg.K_z):
            confirm_target_selection()
        elif event.key == pg.K_ESCAPE:
            # 如果是符文來的，退回符文選單，否則完全關閉
            if selected_rune_data: popup_state = POPUP_RUNE_SELECT
            else: popup_state = POPUP_NONE
        return

    # --- 3. 訊息顯示 ---
    elif popup_state == POPUP_MSG:
        if event.type == pg.KEYDOWN:
            popup_timer = 0
            popup_state = POPUP_NONE
        return

    # --- 4. 正常頁面導航 ---
    if p2_section == 0: 
        if event.key == pg.K_LEFT:
            if p2_char_idx > 0: p2_char_idx -= 1
            else: fading_out = True; is_flipping = True; ui_interactive = False; fade_alpha = 255
        elif event.key == pg.K_RIGHT:
            if p2_char_idx < len(boxes_chars) - 1: p2_char_idx += 1
            else:
                p2_section = 1
                if inventory_list: p2_item_idx = max(0, min(p2_item_idx, max_item_idx))
                else: p2_section = 0 
    
    elif p2_section == 1: 
        if not inventory_list: 
             if event.key == pg.K_LEFT: p2_section = 0; p2_char_idx = len(boxes_chars) - 1
             return

        if event.key == pg.K_UP:
            if p2_item_idx > 0: p2_item_idx -= 1
        elif event.key == pg.K_DOWN:
            if p2_item_idx < max_item_idx: p2_item_idx += 1
        elif event.key == pg.K_LEFT:
            p2_section = 0
            p2_char_idx = len(boxes_chars) - 1 
        
        # 觸發使用
        elif event.key in (pg.K_RETURN, pg.K_SPACE, pg.K_z):
            trigger_item_usage(p2_item_idx)

# ==========================================
# 繪圖函式 (Page 1 & Common)
# ==========================================

def draw_button(surface, rect, text, is_focused):
    if is_focused:
        pg.draw.rect(surface, C_THEME, rect, border_radius=GLOBAL_RADIUS)
        pg.draw.rect(surface, C_SELECTED, rect, width=3, border_radius=GLOBAL_RADIUS)
        txt_color = C_WHITE
    else:
        pg.draw.rect(surface, C_THEME, rect, width=2, border_radius=GLOBAL_RADIUS)
        txt_color = C_THEME 
    txt_surf = font_mid.render(text, True, txt_color)
    surface.blit(txt_surf, txt_surf.get_rect(center=rect.center))

def draw_page1_right(surface):
    global save_msg_timer
    col, row = nav_cursor
    
    title = font_mid.render("冒險紀錄", True, C_TEXT_DARK)
    surface.blit(title, (P1_SAVE_PANEL_X + 80, P1_SAVE_PANEL_Y))

    for i, rect in enumerate(slot_rects):
        is_hover = (col == 1 and row == i)
        is_active = (i == active_slot_index)
        bg_color = C_BG_PAPER
        border_color = C_SELECTED if is_hover else (C_THEME if is_active else C_TEXT_LIGHT)
        line_width = 3 if (is_hover or is_active) else 1

        pg.draw.rect(surface, bg_color, rect, border_radius=GLOBAL_RADIUS)
        pg.draw.rect(surface, border_color, rect, width=line_width, border_radius=GLOBAL_RADIUS)

        data = save_slots_cache[i]
        px, py = rect.x + 15, rect.y + 12
        
        if data:
            # 1. 顯示存檔編號
            no_surf = font_mid.render(f"No.{i+1}", True, C_TEXT_DARK)
            surface.blit(no_surf, (px, py))
            
            # 2. 顯示現實日期 (右側)
            ts_surf = font_small.render(data.get("timestamp", "--/--"), True, C_TEXT_DARK)
            surface.blit(ts_surf, (rect.right - ts_surf.get_width() - 15, py + 5))
            
            # 3. 顯示遊玩時間 (取代原本的升級紀錄)
            playtime_sec = data.get("playtime", 0.0)
            time_str = format_playtime_detailed(playtime_sec)
            
            # 加上一個時鐘小圖示或文字前綴讓它更清楚
            info_surf = font_small.render(f"Play Time:  {time_str}", True, C_TEXT_LIGHT)
            surface.blit(info_surf, (px, py + 35))
            
        else:
            # 空存檔
            empty_txt = font_mid.render(f"No.{i+1}   ----", True, C_TEXT_LIGHT)
            surface.blit(empty_txt, (px, rect.centery - 12))

    draw_button(surface, btn_save_rect, "存檔", (col == 1 and row == 3))
    draw_button(surface, btn_load_rect, "讀檔", (col == 1 and row == 4))

    if save_msg_timer > 0:
        msg_surf = font_small.render(save_msg, True, C_ALERT)
        msg_rect = msg_surf.get_rect(center=(P1_SAVE_PANEL_X + P1_SLOT_W//2, P1_BTN_ACTION_Y + 55))
        surface.blit(msg_surf, msg_rect)
        save_msg_timer -= 1


def draw_multiline_text(surface, text, x, y, font, color, line_height):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        txt_surf = font.render(line, True, color)
        surface.blit(txt_surf, (x, y + i * line_height))

# ==========================================
# === ✨ 新版 Page 2 與 Popup 繪製 ===
# ==========================================
def draw_page2(surface):
    # --- 1. 左側角色 (背景層) ---
    title_l = font_mid.render("隊伍", True, C_TEXT_DARK)
    surface.blit(title_l, (left_page_center_x - title_l.get_width()//2, boxes_chars[0].top - 40))
    
    for i, rect in enumerate(boxes_chars):
        # 只有在非彈窗狀態下才 highlight 游標
        is_focused = (p2_section == 0 and p2_char_idx == i and popup_state == POPUP_NONE)
        
        color = C_SELECTED if is_focused else C_TEXT_LIGHT
        line_width = 3 if is_focused else 1
        
        pg.draw.rect(surface, C_BG_PAPER, rect, border_radius=GLOBAL_RADIUS)
        pg.draw.rect(surface, color, rect, width=line_width, border_radius=GLOBAL_RADIUS)
        
        char_txt = font_mid.render(chr(65+i), True, C_TEXT_DARK)
        surface.blit(char_txt, char_txt.get_rect(center=(rect.centerx, rect.top + 25)))
        
        char_data = game_data.party_data[i]
        hp_ratio = char_data["hp"] / char_data["max_hp"]
        bar_w, bar_h = 8, 40
        bar_x, bar_y = rect.centerx - 4, rect.bottom - 55
        pg.draw.rect(surface, (200,200,200), (bar_x, bar_y, bar_w, bar_h))
        fill_h = int(bar_h * hp_ratio)
        pg.draw.rect(surface, C_HP_BAR, (bar_x, bar_y + (bar_h - fill_h), bar_w, fill_h))
        
        pg.draw.rect(surface, (*C_THEME, 100), (rect.x+5, rect.y+5, rect.width-10, rect.width-10), 1)

        if is_focused:
             overlay = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
             overlay.fill((*C_THEME, 50))
             surface.blit(overlay, rect)

    # 左側說明
    pg.draw.rect(surface, C_THEME, desc_l_rect, width=2, border_radius=GLOBAL_RADIUS)
    char_info = game_data.party_data[p2_char_idx]
    info_header = f"[ {char_info['name']} ]  HP: {char_info['hp']}/{char_info['max_hp']}"
    surface.blit(font_small.render(info_header, True, C_TEXT_DARK), (desc_l_rect.x+10, desc_l_rect.y+10))
    draw_multiline_text(surface, char_info['desc'], desc_l_rect.x+10, desc_l_rect.y+35, font_small, C_TEXT_LIGHT, 20)

    # --- 2. 右側道具 ---
    visible_count = min(len(inventory_list), P2_ITEM_COUNT)
    title_r = font_mid.render(f"背包 ({p2_item_idx+1}/{visible_count})", True, C_TEXT_DARK)
    surface.blit(title_r, (right_page_center_x - title_r.get_width()//2, boxes_items[0].top - 40))

    for i, rect in enumerate(boxes_items):
        if i >= len(inventory_list):
            pg.draw.rect(surface, (*C_BG_PAPER, 100), rect, border_radius=GLOBAL_RADIUS)
            continue

        is_focused = (p2_section == 1 and p2_item_idx == i and popup_state == POPUP_NONE)
        
        color = C_SELECTED if is_focused else C_TEXT_LIGHT
        line_width = 3 if is_focused else 1
        
        pg.draw.rect(surface, C_BG_PAPER, rect, border_radius=GLOBAL_RADIUS)
        pg.draw.rect(surface, color, rect, width=line_width, border_radius=GLOBAL_RADIUS)
        
        item_info = inventory_list[i]
        txt_surf = font_mid.render(item_info["name"], True, C_TEXT_DARK if is_focused else C_TEXT_LIGHT)
        surface.blit(txt_surf, (rect.x + 15, rect.centery - txt_surf.get_height()//2))
        
        count_surf = font_mid.render(f"x{item_info['count']}", True, C_TEXT_DARK if is_focused else C_ALERT)
        surface.blit(count_surf, (rect.right - count_surf.get_width() - 15, rect.centery - count_surf.get_height()//2))
        
        if is_focused:
             overlay = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
             overlay.fill((*C_THEME, 50))
             surface.blit(overlay, rect)

    # 右側說明
    pg.draw.rect(surface, C_THEME, desc_r_rect, width=2, border_radius=GLOBAL_RADIUS)
    if inventory_list and p2_item_idx < len(inventory_list):
        current_item = inventory_list[p2_item_idx]
        surface.blit(font_small.render(f"[ {current_item['name']} ]", True, C_TEXT_DARK), (desc_r_rect.x+10, desc_r_rect.y+10))
        draw_multiline_text(surface, current_item['desc'], desc_r_rect.x+10, desc_r_rect.y+35, font_small, C_TEXT_LIGHT, 20)

    # --- 3. 彈窗繪製 ---
    if popup_state != POPUP_NONE:
        draw_popup_layer(surface)

def draw_popup_layer(surface):
    global popup_timer, popup_state
    
    # 全螢幕半透明黑底
    mask = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
    mask.fill((0,0,0,140))
    surface.blit(mask, (0,0))

    center_x, center_y = WIDTH // 2, HEIGHT // 2

    # === A. 符文選擇視窗 (6宮格) ===
    if popup_state == POPUP_RUNE_SELECT:
        win_w, win_h = 420, 320
        win_rect = pg.Rect(center_x - win_w//2, center_y - win_h//2, win_w, win_h)
        
        pg.draw.rect(surface, C_BG_PAPER, win_rect, border_radius=10)
        pg.draw.rect(surface, C_THEME, win_rect, width=3, border_radius=10)
        
        title = font_mid.render("選擇刻印符文", True, C_TEXT_DARK)
        surface.blit(title, title.get_rect(center=(center_x, win_rect.top + 30)))
        
        opt_w, opt_h = 180, 55
        start_x = win_rect.centerx - opt_w - 10
        start_y = win_rect.top + 80
        
        for i, rune in enumerate(RUNES_DATA):
            col = i % 2
            row = i // 2
            r_rect = pg.Rect(start_x + col * (opt_w + 20), start_y + row * (opt_h + 15), opt_w, opt_h)
            
            is_sel = (i == rune_cursor)
            bg_c = C_WHITE if is_sel else C_BG_OVERLAY
            bd_c = C_SELECTED if is_sel else C_THEME
            
            pg.draw.rect(surface, bg_c, r_rect, border_radius=5)
            pg.draw.rect(surface, bd_c, r_rect, width=2, border_radius=5)
            
            # 顯示符號 + 英文名
            # 如果 font 不支援符號可能會顯示方框，這裡同時顯示英文確保可讀性
            sym_txt = font_mid.render(f"{rune['symbol']} {rune['name']}", True, bd_c)
            surface.blit(sym_txt, (r_rect.x + 10, r_rect.y + 5))
            
            eff_txt = font_small.render(f"{rune['stat']} UP", True, C_TEXT_LIGHT)
            surface.blit(eff_txt, (r_rect.right - eff_txt.get_width() - 10, r_rect.bottom - 20))
            
            # 如果選中，在下方顯示詳細描述
            if is_sel:
                desc_txt = font_small.render(rune['desc'], True, C_WHITE)
                desc_bg_rect = desc_txt.get_rect(center=(center_x, win_rect.bottom - 25))
                pg.draw.rect(surface, C_SELECTED, desc_bg_rect.inflate(20, 10), border_radius=5)
                surface.blit(desc_txt, desc_bg_rect)

    # === B. 目標選擇視窗 (列表) ===
    elif popup_state == POPUP_TARGET_SELECT:
        win_w, win_h = 300, 300
        win_rect = pg.Rect(center_x - win_w//2, center_y - win_h//2, win_w, win_h)
        
        pg.draw.rect(surface, C_BG_PAPER, win_rect, border_radius=10)
        pg.draw.rect(surface, C_THEME, win_rect, width=3, border_radius=10)
        
        title_str = "選擇對象"
        if selected_rune_data: title_str = f"使用 {selected_rune_data['symbol']} 於..."
            
        title = font_mid.render(title_str, True, C_TEXT_DARK)
        surface.blit(title, title.get_rect(center=(center_x, win_rect.top + 30)))
        
        # 列表
        list_start_y = win_rect.top + 70
        item_h = 40
        for i, char in enumerate(game_data.party_data):
            r_rect = pg.Rect(win_rect.left + 20, list_start_y + i * item_h, win_rect.width - 40, 35)
            is_sel = (i == target_cursor)
            
            if is_sel:
                pg.draw.rect(surface, C_SELECTED, r_rect, border_radius=5)
                txt_c = C_WHITE
            else:
                txt_c = C_TEXT_DARK
                
            name_txt = font_mid.render(char["name"], True, txt_c)
            surface.blit(name_txt, (r_rect.x + 10, r_rect.centery - name_txt.get_height()//2))
            
            stat_txt = font_small.render(f"HP {char['hp']}", True, txt_c)
            surface.blit(stat_txt, (r_rect.right - 60, r_rect.centery - stat_txt.get_height()//2))

    # === C. 訊息視窗 ===
    elif popup_state == POPUP_MSG:
        msg_w, msg_h = 320, 120
        msg_rect = pg.Rect(center_x - msg_w//2, center_y - msg_h//2, msg_w, msg_h)
        
        pg.draw.rect(surface, C_BG_PAPER, msg_rect, border_radius=10)
        pg.draw.rect(surface, C_ALERT, msg_rect, width=2, border_radius=10)
        
        draw_multiline_text(surface, popup_message, msg_rect.x + 20, msg_rect.y + 25, font_mid, C_TEXT_DARK, 30)
        
        popup_timer -= 1
        if popup_timer <= 0:
            popup_state = POPUP_NONE

# ==========================================
# 主迴圈
# ==========================================
while True:
    clock.tick(30)
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit(); sys.exit()
            
        elif event.type == pg.KEYDOWN:
            # 只有在沒有任何彈窗時，ESC 才是暫停/切換
            if event.key == pg.K_ESCAPE and popup_state == POPUP_NONE:
                if paused: paused = False 
                else: 
                    paused = True
                    refresh_save_slots()
                    nav_cursor = [0, 0] 
            
            # 在暫停選單內的操作
            elif paused and ui_interactive:
                if current_page == 1: handle_input_page1(event)
                else: handle_input_page2(event)

    buttons.update() 
    if pg.mouse.get_pressed()[0] and pause_btn.rect.collidepoint(pg.mouse.get_pos()):
         if not paused:
             paused = True; refresh_save_slots(); nav_cursor = [0, 0]
         pg.time.wait(200)

    screen.fill((216, 226, 233)) 
    buttons.draw(screen)

    if paused:
        overlay = pg.Surface((WIDTH, HEIGHT)); overlay.set_alpha(120); overlay.fill((40, 30, 20))
        screen.blit(overlay, (0, 0))
        
        if 'bg_path' not in locals() or not os.path.exists(bg_path):
             pg.draw.rect(screen, C_BG_PAPER, bg_rect, border_radius=10)
        else:
             screen.blit(background, bg_rect)
             
        pause_layer = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)

        def draw_current_content(surf, alpha):
            surf.set_alpha(alpha)
            if current_page == 1:
                # Page 1 繪製 (保持原樣)
                col, row = nav_cursor
                surf.blit(font_big.render("遊戲暫停", True, C_TEXT_DARK), (P1_SLIDER_X, 100))
                draw_button(surf, continue_rect, "繼續遊戲", (col==0 and row==0))
                
                slider_music.draw(surf)
                game_data.volume = slider_music.get_value()
                pg.mixer.music.set_volume(game_data.volume)
                if col == 0 and row == 1:
                    pg.draw.rect(surf, C_ALERT, (P1_SLIDER_X - 5, P1_SLIDER_MUSIC_Y - 5, P1_SLIDER_W + 10, 25), 2, border_radius=5)
                surf.blit(font_small.render(f"音樂: {int(game_data.volume*100)}%", True, C_TEXT_DARK if (col==0 and row==1) else C_TEXT_LIGHT), (P1_SLIDER_X + 50, P1_SLIDER_MUSIC_Y - 30))

                slider_sfx.draw(surf)
                game_data.sfx_volume = slider_sfx.get_value()
                if col == 0 and row == 2:
                      pg.draw.rect(surf, C_ALERT, (P1_SLIDER_X - 5, P1_SLIDER_SFX_Y - 5, P1_SLIDER_W + 10, 25), 2, border_radius=5)
                surf.blit(font_small.render(f"音效: {int(game_data.sfx_volume*100)}%", True, C_TEXT_DARK if (col==0 and row==2) else C_TEXT_LIGHT), (P1_SLIDER_X + 50, P1_SLIDER_SFX_Y - 30))
                
                draw_button(surf, exit_rect, "退出遊戲", (col==0 and row==3))
                draw_page1_right(surf)
            else:
                # Page 2 繪製
                draw_page2(surf)
            
            # 翻頁箭頭
            if current_page == 1:
                pg.draw.polygon(surf, C_SELECTED, [(WIDTH-50, HEIGHT//2), (WIDTH-70, HEIGHT//2-10), (WIDTH-70, HEIGHT//2+10)])
            elif current_page == 2:
                if popup_state == POPUP_NONE:
                    pg.draw.polygon(surf, C_SELECTED, [(50, HEIGHT//2), (70, HEIGHT//2-10), (70, HEIGHT//2+10)])

        if fading_out:
            temp = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            draw_current_content(temp, fade_alpha)
            pause_layer.blit(temp, (0,0))
            fade_alpha -= 30 
            if fade_alpha <= 0: 
                fade_alpha = 0; fading_out = False; fading_in = True
                current_page = 2 if current_page == 1 else 1
                if current_page == 2:
                    p2_section = 0; p2_char_idx = 0
                else:
                    nav_cursor = [1, 0] 

        elif fading_in:
            temp = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            draw_current_content(temp, fade_alpha)
            pause_layer.blit(temp, (0,0))
            fade_alpha += 30
            if fade_alpha >= 255: fade_alpha = 255; fading_in = False; is_flipping = False; ui_interactive = True
        elif not is_flipping:
            draw_current_content(pause_layer, 255)

        screen.blit(pause_layer, (0,0))

    pg.display.flip()