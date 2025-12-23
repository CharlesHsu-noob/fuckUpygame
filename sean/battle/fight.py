import pygame
import random
import math
import time
import os
from QTE_MLBmode import play_qte 
from QTE_DBDmode import play_dbd_qte 

pygame.init()

# --- 【全螢幕設定】 ---
screen_info = pygame.display.Info()
WIDTH = screen_info.current_w
HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Fight Prototype")
clock = pygame.time.Clock()

# --- 【背景圖片載入】 ---
current_path = os.path.dirname(__file__) 
possible_paths = [
    os.path.join(current_path, "photo", "forest_battle.png"),
    os.path.join(current_path, "forest_battle.png")
]
bg_img = None
for path in possible_paths:
    if os.path.exists(path):
        try:
            raw_img = pygame.image.load(path).convert()
            bg_img = pygame.transform.scale(raw_img, (WIDTH, HEIGHT))
            break
        except:
            pass

if bg_img is None:
    bg_img = pygame.Surface((WIDTH, HEIGHT))
    bg_img.fill((30, 30, 30))

# ==========================================
# ★★★ 【可調整變數區 (UI設定)】 ★★★
# ==========================================

# 1. 玩家血條 (Player HP)
# 數值皆為螢幕比例 (0.0 ~ 1.0)
P_HP_X = 0.715    # 左邊距離
P_HP_Y = 0.63  # 上邊距離
P_HP_W = 0.2     # 寬度
P_HP_H = 0.025   # 高度

# 2. 敵人血條 (Enemy HP)
E_HP_X = 0.78    # 左邊距離
E_HP_Y = 0.025   # 上邊距離
E_HP_W = 0.2     # 寬度
E_HP_H = 0.025   # 高度

# 3. 選項選單 (Options)
OPT_X = 0.33   # 選單起始 X 位置
OPT_Y = 0.68    # 選單起始 Y 位置
OPT_GAP = 0.10   # 選項的垂直間距 (行距)
OPT_COLOR = (0, 0, 0) # ★ 字體顏色：黑色

# ==========================================

# --- 遊戲數據 ---
PLAYER_HP = 100
PLAYER_MAX_HP = 100
ENEMY_HP = 100
ENEMY_MAX_HP = 100
MAX_ENERGY = 10
player_energy = MAX_ENERGY

font = pygame.font.SysFont(None, int(HEIGHT * 0.025))
option_font = pygame.font.SysFont(None, int(HEIGHT * 0.025))
damage_font = pygame.font.SysFont(None, int(HEIGHT * 0.04))

options = ["Normal Attack", "Special Attack", "Defend", "End this round"]
energy_cost = [3, 5, 4, 0]
selected_option = None
pending_action = False
temp_energy = player_energy
damage_texts = []
energy_recover_queue = []
energy_recover_timer = [0] * MAX_ENERGY
shield_turns = 0
pending_energy_recover = 0
ENERGY_DELAY = 0.1
recover_timer = 0

# --- 繪圖函數 ---
def draw_scene(dt, is_background=False):
    global recover_timer, player_energy, pending_energy_recover, temp_energy
    
    # 畫背景
    screen.blit(bg_img, (0, 0))

    # --- 繪製玩家血條 (使用上方變數) ---
    px, py, pw, ph = WIDTH * P_HP_X, HEIGHT * P_HP_Y, WIDTH * P_HP_W, HEIGHT * P_HP_H
    pygame.draw.rect(screen, (110, 204, 149), (px, py, pw, ph)) # 底色 (綠色背景)
    pygame.draw.rect(screen, (150, 234, 186), (px, py, pw * (PLAYER_HP / PLAYER_MAX_HP), ph)) # 血量 (綠色)
    # ★ 改成黑色文字 (0, 0, 0)
    screen.blit(font.render(f"HP: {PLAYER_HP}/{PLAYER_MAX_HP}", True, (0, 0, 0)), (px, py + ph * 1.2))

    # --- 繪製敵人血條 (使用上方變數) ---
    ex_bar, ey_bar, ew_bar, eh_bar = WIDTH * E_HP_X, HEIGHT * E_HP_Y, WIDTH * E_HP_W, HEIGHT * E_HP_H
    pygame.draw.rect(screen, (219, 120, 158), (ex_bar, ey_bar, ew_bar, eh_bar)) # 底色 (紅色背景)
    pygame.draw.rect(screen, (234, 150, 183), (ex_bar, ey_bar, ew_bar * (ENEMY_HP / ENEMY_MAX_HP), eh_bar)) # 血量 (紅色)
    # ★ 改成黑色文字 (0, 0, 0)
    screen.blit(font.render(f"HP: {ENEMY_HP}/{ENEMY_MAX_HP}", True, (0, 0, 0)), (ex_bar, ey_bar + eh_bar * 1.2))

    # 扣血動畫
    for dmg in damage_texts[:]:
        dmg['y'] -= 30 * dt
        dmg['timer'] += dt
        dmg['alpha'] = max(0, 255 * (1 - dmg['timer'] / 1.0))
        color = (255, 100, 0) if dmg['target'] == 'player' else (255, 255, 0)
        text_surf = damage_font.render(f"-{dmg['damage']}", True, color)
        text_surf.set_alpha(int(dmg['alpha']))
        screen.blit(text_surf, (dmg['x'] - text_surf.get_width() // 2, dmg['y'] - text_surf.get_height() // 2))
        if dmg['timer'] >= 1.0:
            damage_texts.remove(dmg)

    # 能量計時
    for i in range(MAX_ENERGY):
        if energy_recover_timer[i] > 0:
            energy_recover_timer[i] -= dt
            if energy_recover_timer[i] < 0: energy_recover_timer[i] = 0

    if not is_background:
        if pending_energy_recover > 0:
            recover_timer += dt
            if recover_timer >= ENERGY_DELAY:
                if player_energy < MAX_ENERGY:
                    energy_recover_queue.append(player_energy)
                    player_energy += 1
                pending_energy_recover -= 1
                recover_timer = 0
        if energy_recover_queue:
            recover_timer += dt
            if recover_timer >= ENERGY_DELAY:
                idx = energy_recover_queue.pop(0)
                energy_recover_timer[idx] = 1.0
                recover_timer = 0

    # --- 繪製選項 (修改為 2x2 矩陣) ---
    start_x = WIDTH * OPT_X
    start_y = HEIGHT * OPT_Y
    spacing = HEIGHT * OPT_GAP
    col_spacing = WIDTH * 0.22  # ★ 第二列的水平距離 (可調整)
    
    for i, option in enumerate(options):
        # 計算矩陣位置
        # col: 0 或 1 (代表左或右)
        # row: 0 或 1 (代表上或下)
        col = i % 2 
        row = i // 2
        
        # 計算當前選項的座標
        current_opt_x = start_x + (col * col_spacing)
        current_opt_y = start_y + (row * spacing)

        # 預設為黑色 (OPT_COLOR)，能量不足時變紅
        color = OPT_COLOR 
        if selected_option == i and pending_action and player_energy < energy_cost[i]:
            color = (200, 0, 0) 
            
        text = option_font.render(f"{i+1}. {option}", True, color)
        screen.blit(text, (current_opt_x, current_opt_y))
        
        # 選中時顯示紅點 (位置跟隨新的矩陣座標)
        if selected_option == i:
            if not pending_action or player_energy >= energy_cost[i]:
                pygame.draw.circle(screen, (200, 50, 50), (int(current_opt_x - 10), int(current_opt_y + text.get_height()/2)), 5)

        # 盾牌狀態 (位置跟隨新的矩陣座標)
        if i == 2 and shield_turns > 0:
            h, offset = text.get_height(), 5
            base_x = current_opt_x + text.get_width() + offset
            base_y = current_opt_y
            shield_points = [
                (base_x + 5, base_y),
                (base_x + 12, base_y + h),
                (base_x - 2, base_y + h)
            ]
            pygame.draw.polygon(screen, (0, 100, 200), shield_points)
            # 盾牌數字也保持黑色
            screen.blit(font.render(str(shield_turns), True, OPT_COLOR), (base_x + 14, base_y))


    # --- 能量條 (保留原本位置與邏輯) ---
    ex = WIDTH * 0.33 
    ey = HEIGHT * 0.88
    es = WIDTH * 0.035 
    ew = 8  
    eh = 16

    for i in range(MAX_ENERGY):
        cx = ex + i * es
        points = [
            (cx, ey),            # 下
            (cx + ew, ey - eh),  # 右上
            (cx + 2*ew, ey),     # 上
            (cx + ew, ey + eh)   # 左下
        ]
        
        if energy_recover_timer[i] > 0: 
            alpha = int(255 * energy_recover_timer[i])
            s_w, s_h = ew * 2 + 2, eh * 2 + 2
            s = pygame.Surface((s_w, s_h), pygame.SRCALPHA)
            local_points = [(0, eh), (ew, 0), (ew*2, eh), (ew, eh*2)]
            pygame.draw.polygon(s, (0, 255, 255, alpha), local_points)
            screen.blit(s, (cx, ey - eh))
        elif pending_action and selected_option is not None: 
            cost = energy_cost[selected_option]
            if i < player_energy - cost:
                pygame.draw.polygon(screen, (0, 255, 255), points)
            elif i >= player_energy - cost and i < player_energy:
                pygame.draw.polygon(screen, (0, 255, 255), points, 1) # 空心
        else: 
            if i < player_energy:
                pygame.draw.polygon(screen, (0, 255, 255), points)

# --- 主遊戲迴圈 ---
running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: 
                running = False
            
            if event.key in (pygame.K_1, pygame.K_KP1):
                selected_option, temp_energy, pending_action = 0, player_energy - energy_cost[0], True
            elif event.key in (pygame.K_2, pygame.K_KP2):
                selected_option, temp_energy, pending_action = 1, player_energy - energy_cost[1], True
            elif event.key in (pygame.K_3, pygame.K_KP3):
                selected_option, temp_energy, pending_action = 2, player_energy - energy_cost[2], True
            elif event.key in (pygame.K_4, pygame.K_KP4):
                selected_option, temp_energy, pending_action = 3, player_energy, True

            elif event.key == pygame.K_SPACE and pending_action:
                cost = energy_cost[selected_option]
                if player_energy >= cost:
                    player_energy -= cost
                    
                    if selected_option == 0: 
                        ENEMY_HP = max(0, ENEMY_HP - 10)
                        damage_texts.append({'damage': 10, 'x': WIDTH * 0.88, 'y': HEIGHT * 0.05, 'alpha': 255, 'timer': 0, 'target': 'enemy'})
                    
                    elif selected_option == 1: 
                        result = play_qte(screen, WIDTH, HEIGHT, draw_bg_func=lambda d: draw_scene(d, is_background=True))
                        damage = 10 if result == "MISS" else (15 if result == "GREAT" else 20)
                        ENEMY_HP = max(0, ENEMY_HP - damage)
                        damage_texts.append({'damage': damage, 'x': WIDTH * 0.88, 'y': HEIGHT * 0.05, 'alpha': 255, 'timer': 0, 'target': 'enemy'})
                    
                    elif selected_option == 2: 
                        shield_turns = 3
                    
                    elif selected_option == 3: 
                        enemy_damage = int(20 * random.uniform(0.8, 1.3))
                        if shield_turns > 0:
                            results = play_dbd_qte(screen, WIDTH, HEIGHT, draw_bg_func=lambda d: draw_scene(d, is_background=True))
                            final_dmg = int(enemy_damage * (1 - 0.2 * results.count("PERFECT")))
                            PLAYER_HP -= final_dmg
                            damage_texts.append({'damage': final_dmg, 'x': WIDTH * 0.12, 'y': HEIGHT * 0.05, 'alpha': 255, 'timer': 0, 'target': 'player'})
                            pending_energy_recover = 4
                            shield_turns -= 1 
                        else:
                            PLAYER_HP -= enemy_damage
                            damage_texts.append({'damage': enemy_damage, 'x': WIDTH * 0.12, 'y': HEIGHT * 0.05, 'alpha': 255, 'timer': 0, 'target': 'player'})
                            pending_energy_recover = 4
                            
                selected_option, pending_action, temp_energy = None, False, player_energy

    draw_scene(dt, is_background=False)
    pygame.display.flip()

pygame.quit()