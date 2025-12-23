import pygame
import random
import math
import os
from QTE_MLBmode import play_qte 
from QTE_DBDmode import play_dbd_qte 

pygame.init()

# ==========================================
# ★★★ 【全螢幕設定】 ★★★
# ==========================================
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Fight Prototype")
clock = pygame.time.Clock()

# --- 【資源路徑設定】 ---
current_path = os.path.dirname(__file__) 

def load_img(sub_path, alpha=True):
    path = os.path.join(current_path, sub_path)
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()
    return None

# --- 【圖片載入】 ---
bg_raw = load_img("photo/forest_battle.png", False)
bg_img = pygame.transform.scale(bg_raw, (int(WIDTH * 1.05), int(HEIGHT * 1.05))) if bg_raw else pygame.Surface((WIDTH, HEIGHT))

fox_raw = load_img("photo/forest_fox.png")
fox_img = None
if fox_raw:
    f_h = int(HEIGHT * 0.35)
    f_w = int(fox_raw.get_width() * (f_h / fox_raw.get_height()))
    fox_img = pygame.transform.scale(fox_raw, (f_w, f_h))

bite_raw = load_img("photo/bite.png")

# ==========================================
# ★★★ 【視覺特效：紅框濾鏡】 ★★★
# ==========================================
def create_blood_vignette(w, h):
    grad_w, grad_h = w // 10, h // 10
    grad_surf = pygame.Surface((grad_w, grad_h), pygame.SRCALPHA)
    
    for y in range(grad_h):
        for x in range(grad_w):
            dx = abs(x - grad_w/2) / (grad_w/2)
            dy = abs(y - grad_h/2) / (grad_h/2)
            dist = max(dx, dy) 
            
            if dist > 0.5: 
                alpha = int(255 * ((dist - 0.5) / 0.5))
                alpha = min(220, alpha)
                grad_surf.set_at((x, y), (255, 0, 0, alpha))
            else:
                grad_surf.set_at((x, y), (0, 0, 0, 0))
                
    return pygame.transform.smoothscale(grad_surf, (w, h))

blood_vignette_img = create_blood_vignette(WIDTH, HEIGHT)

# 受傷特效狀態管理
impact_state = {
    "active": False,
    "max_alpha": 0,    
    "current_alpha": 0,
    "shake_amp": 0,    
    "duration": 0,     
    "timer": 0
}

# ==========================================
# ★★★ 【UI設定】 ★★★
# ==========================================
P_HP_X, P_HP_Y, P_HP_W, P_HP_H = 0.725, 0.615, 0.2, 0.025
E_HP_X, E_HP_Y, E_HP_W, E_HP_H = 0.40, 0.1, 0.2, 0.025
OPT_X, OPT_Y, OPT_GAP, OPT_COL_GAP = 0.31, 0.66, 0.10, 0.22
OPT_COLOR, OPT_FONT_SIZE = (0, 0, 0), 0.045
DEF_IMG_X, DEF_IMG_Y, DEF_IMG_SIZE, DEF_NUM_X_OFF = 0.24, 0.58, 0.05, 0.0001
BITE_X, BITE_Y, BITE_FINAL_SIZE = 0.16, 0.73, 0.3 

# 預縮放防禦圖片
def_icon_raw = load_img("photo/def_up.png")
def_icon_img = None
if def_icon_raw:
    di_h = int(HEIGHT * DEF_IMG_SIZE)
    di_w = int(def_icon_raw.get_width() * (di_h / def_icon_raw.get_height()))
    def_icon_img = pygame.transform.scale(def_icon_raw, (di_w, di_h))

# --- 遊戲數據 (保留原樣) ---
PLAYER_HP = 100
PLAYER_MAX_HP = 100
ENEMY_HP = 100
ENEMY_MAX_HP = 100
MAX_ENERGY = 10
player_energy = MAX_ENERGY

# ★★★ 遊戲狀態變數 ★★★
game_over = False
victory = False

font = pygame.font.SysFont(None, int(HEIGHT * OPT_FONT_SIZE))
option_font = pygame.font.SysFont(None, int(HEIGHT * OPT_FONT_SIZE))
damage_font = pygame.font.SysFont(None, int(HEIGHT * 0.04))
result_font = pygame.font.SysFont(None, int(HEIGHT * 0.15)) 

options = ["Normal Attack", "Special Attack", "Defend", "End this round"]
energy_cost = [3, 5, 4, 0]
selected_option = None
pending_action = False
damage_texts = []
energy_recover_queue = []
energy_recover_timer = [0] * MAX_ENERGY
shield_turns = 0
recover_timer = 0
ENERGY_DELAY = 0.1
pending_energy_recover = 0 

# 敵人攻擊流程控制
pending_enemy_attack = False 
enemy_attack_timer = 0       
pending_damage_value = 0
pending_impact_level = 0      

# 特效變數
bite_anim = {"active": False, "timer": 0}
fox_pos_x = 0
fox_pos_y = 0

# 彩帶特效
confetti_particles = []
CONFETTI_COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
    (0, 255, 255), (255, 0, 255), (255, 165, 0), (255, 192, 203), 
    (173, 216, 230), (238, 130, 238)
]

def trigger_bite():
    bite_anim["active"] = True
    bite_anim["timer"] = 0

def trigger_impact(level):
    """觸發受傷瞬間特效"""
    impact_state["active"] = True
    impact_state["timer"] = 0
    
    if level == 3: # 重傷
        impact_state["max_alpha"] = 255
        impact_state["shake_amp"] = 30
        impact_state["duration"] = 1.0      
    elif level == 2: # 中傷
        impact_state["max_alpha"] = 160
        impact_state["shake_amp"] = 15
        impact_state["duration"] = 0.6
    else: # 輕傷
        impact_state["max_alpha"] = 60
        impact_state["shake_amp"] = 5
        impact_state["duration"] = 0.3
    
    impact_state["current_alpha"] = impact_state["max_alpha"]

def create_confetti():
    return {
        'x': random.randint(0, WIDTH),
        'y': random.randint(-HEIGHT // 2, -10), 
        'color': random.choice(CONFETTI_COLORS),
        'speed_y': random.uniform(3, 7),     
        'sway_freq': random.uniform(0.05, 0.2), 
        'sway_amp': random.uniform(1, 3),    
        'tumble_speed': random.uniform(0.1, 0.3), 
        'tumble_phase': random.uniform(0, math.pi * 2), 
        'width': random.randint(8, 15),      
        'height': random.randint(15, 25),    
        'timer': 0
    }

def reset_game():
    global PLAYER_HP, ENEMY_HP, player_energy, shield_turns, game_over, victory
    global pending_action, selected_option, damage_texts
    global pending_enemy_attack, bite_anim, energy_recover_queue, confetti_particles
    global impact_state
    
    PLAYER_HP = PLAYER_MAX_HP
    ENEMY_HP = ENEMY_MAX_HP
    player_energy = MAX_ENERGY
    shield_turns = 0
    game_over = False
    victory = False
    pending_action = False
    selected_option = None
    damage_texts = []
    pending_enemy_attack = False
    bite_anim = {"active": False, "timer": 0}
    energy_recover_queue = []
    confetti_particles = [] 
    
    impact_state["active"] = False
    impact_state["current_alpha"] = 0

def draw_scene(dt, is_background=False):
    global recover_timer, player_energy, pending_energy_recover, fox_pos_x, fox_pos_y
    global pending_enemy_attack, enemy_attack_timer, pending_damage_value, PLAYER_HP, game_over, victory
    global confetti_particles, pending_impact_level
    
    # 1. 震動計算
    shake_x, shake_y = 0, 0
    base_shake = 0
    if bite_anim["active"] and bite_anim["timer"] <= 0.35:
        base_shake = 5
    
    impact_shake = 0
    if impact_state["active"] and impact_state["timer"] < 0.2:
        impact_shake = impact_state["shake_amp"]

    total_shake = base_shake + impact_shake
    if total_shake > 0:
        shake_x = random.randint(-total_shake, total_shake)
        shake_y = random.randint(-total_shake, total_shake)

    # 2. 繪製背景
    screen.blit(bg_img, (-WIDTH*0.025 + shake_x, -HEIGHT*0.025 + shake_y))

    # --- 狐狸繪製 ---
    ex_bar, ey_bar, ew_bar, eh_bar = WIDTH * E_HP_X, HEIGHT * E_HP_Y, WIDTH * E_HP_W, HEIGHT * E_HP_H
    if fox_img:
        base_fox_x = ex_bar + (ew_bar // 2) - (fox_img.get_width() // 2)
        base_fox_y = ey_bar + eh_bar * 1 
        
        offset_x, offset_y = 0, 0
        if bite_anim["active"]:
            t = bite_anim["timer"]
            attack_duration, hold_duration, fade_duration = 0.15, 0.6, 0.2
            total_time = attack_duration + hold_duration + fade_duration
            lunge_dist_x, lunge_dist_y = WIDTH * 0.05, HEIGHT * 0.03 

            if t <= attack_duration:
                p = t / attack_duration
                offset_x, offset_y = -lunge_dist_x * p, lunge_dist_y * p
            elif t <= (attack_duration + hold_duration):
                offset_x, offset_y = -lunge_dist_x, lunge_dist_y
            elif t <= total_time:
                p = 1.0 - ((t - (attack_duration + hold_duration)) / fade_duration)
                offset_x, offset_y = -lunge_dist_x * p, lunge_dist_y * p

        fox_pos_x = base_fox_x + offset_x + shake_x
        fox_pos_y = base_fox_y + offset_y + shake_y
        screen.blit(fox_img, (fox_pos_x, fox_pos_y))

    # ==========================================
    # ★★★ 紅框特效邏輯 (Impact + Low HP) ★★★
    # ==========================================
    
    # 1. 計算「受傷瞬間」的 Alpha (Impact)
    impact_alpha = 0
    if impact_state["active"]:
        impact_state["timer"] += dt
        if impact_state["timer"] < impact_state["duration"]:
            progress = impact_state["timer"] / impact_state["duration"]
            impact_state["current_alpha"] = int(impact_state["max_alpha"] * (1 - progress))
            impact_alpha = impact_state["current_alpha"]
        else:
            impact_state["active"] = False
            impact_state["current_alpha"] = 0

    # 2. 計算「殘血常駐」的 Alpha (Low HP)
    low_hp_alpha = 0
    if PLAYER_HP / PLAYER_MAX_HP <= 0.3 and not victory: # 血量低於30%且未勝利
        # 使用 Sine 波產生呼吸效果 (範圍約 30 ~ 100 透明度)
        time_ms = pygame.time.get_ticks()
        # math.sin 輸出 -1~1，調整為 0~1 區間
        pulse = (math.sin(time_ms * 0.003) + 1) * 0.5 
        low_hp_alpha = int(30 + 70 * pulse)

    # 3. 取兩者最大值 (確保被打的瞬間會蓋過呼吸燈)
    final_alpha = max(impact_alpha, low_hp_alpha)
            
    if final_alpha > 0:
        blood_vignette_img.set_alpha(final_alpha)
        screen.blit(blood_vignette_img, (0, 0))

    # --- UI 繪製 (血條/文字) ---
    px, py, pw, ph = WIDTH * P_HP_X, HEIGHT * P_HP_Y, WIDTH * P_HP_W, HEIGHT * P_HP_H
    pygame.draw.rect(screen, (110, 204, 149), (px, py, pw, ph)) 
    pygame.draw.rect(screen, (150, 234, 186), (px, py, pw * (PLAYER_HP / PLAYER_MAX_HP), ph)) 
    screen.blit(font.render(f"HP: {PLAYER_HP}/{PLAYER_MAX_HP}", True, (0, 0, 0)), (px, py + ph * 1.2))
    
    pygame.draw.rect(screen, (219, 120, 158), (ex_bar, ey_bar, ew_bar, eh_bar)) 
    pygame.draw.rect(screen, (234, 150, 183), (ex_bar, ey_bar, ew_bar * (ENEMY_HP / ENEMY_MAX_HP), eh_bar)) 
    screen.blit(font.render(f"HP: {ENEMY_HP}/{ENEMY_MAX_HP}", True, (0, 0, 0)), (ex_bar, ey_bar + eh_bar * 1.2))

    # 損血文字
    for dmg in damage_texts[:]:
        dmg['y'] -= 30 * dt; dmg['timer'] += dt
        dmg['alpha'] = max(0, 255 * (1 - dmg['timer'] / 1.0))
        txt = damage_font.render(f"-{dmg['damage']}", True, (255, 100, 0) if dmg['target'] == 'player' else (255, 255, 0))
        txt.set_alpha(int(dmg['alpha']))
        screen.blit(txt, (dmg['x'] - txt.get_width() // 2, dmg['y'] - txt.get_height() // 2))
        if dmg['timer'] >= 1.0: damage_texts.remove(dmg)

    # 能量
    for i in range(MAX_ENERGY):
        if energy_recover_timer[i] > 0:
            energy_recover_timer[i] = max(0, energy_recover_timer[i] - dt)

    if not is_background:
        # 敵人攻擊邏輯
        if pending_enemy_attack and not victory: 
            enemy_attack_timer += dt
            if enemy_attack_timer >= 0.2:
                trigger_bite()
                trigger_impact(pending_impact_level)
                
                actual_damage = pending_damage_value
                PLAYER_HP = max(0, PLAYER_HP - actual_damage)
                damage_texts.append({'damage': actual_damage, 'x': WIDTH * 0.12, 'y': HEIGHT * 0.05, 'alpha': 255, 'timer': 0, 'target': 'player'})
                
                if PLAYER_HP <= 0:
                    game_over = True
                
                pending_energy_recover = 4 
                pending_enemy_attack = False
                enemy_attack_timer = 0

        # 能量回復
        if not (game_over or victory):
            if pending_energy_recover > 0:
                recover_timer += dt
                if recover_timer >= ENERGY_DELAY:
                    if player_energy < MAX_ENERGY:
                        energy_recover_queue.append(player_energy); player_energy += 1
                    pending_energy_recover -= 1; recover_timer = 0
            if energy_recover_queue:
                recover_timer += dt
                if recover_timer >= ENERGY_DELAY:
                    idx = energy_recover_queue.pop(0); energy_recover_timer[idx] = 1.0; recover_timer = 0

    # 選項
    start_x, start_y, spacing_y, spacing_x = WIDTH * OPT_X, HEIGHT * OPT_Y, HEIGHT * OPT_GAP, WIDTH * OPT_COL_GAP
    for i, option in enumerate(options):
        col, row = i % 2, i // 2
        curr_x, curr_y = start_x + (col * spacing_x), start_y + (row * spacing_y)
        color = (200, 0, 0) if (selected_option == i and pending_action and player_energy < energy_cost[i]) else OPT_COLOR
        text = option_font.render(f"{i+1}. {option}", True, color)
        screen.blit(text, (curr_x, curr_y))
        if selected_option == i and (not pending_action or player_energy >= energy_cost[i]) and not (game_over or victory):
            pygame.draw.circle(screen, (200, 50, 50), (int(curr_x - 10), int(curr_y + text.get_height()/2)), 5)

    # 防禦標誌
    if shield_turns > 0 and def_icon_img:
        fx, fy = WIDTH * DEF_IMG_X, HEIGHT * DEF_IMG_Y
        screen.blit(def_icon_img, (fx, fy))
        num_t = font.render(str(shield_turns), True, OPT_COLOR)
        screen.blit(num_t, (fx + def_icon_img.get_width() + (WIDTH * DEF_NUM_X_OFF), fy + (def_icon_img.get_height()//2) - (num_t.get_height()//2)))

    # 咬擊動畫
    if bite_anim["active"]:
        bite_anim["timer"] += dt
        t = bite_anim["timer"]
        attack_duration, hold_duration, fade_duration = 0.15, 0.6, 0.2
        total_time = attack_duration + hold_duration + fade_duration
        tx, ty = WIDTH * BITE_X, HEIGHT * BITE_Y
        
        if bite_raw:
            fw = int(HEIGHT * BITE_FINAL_SIZE * (bite_raw.get_width() / bite_raw.get_height()))
            fh = int(HEIGHT * BITE_FINAL_SIZE)
        else:
            fw, fh = int(HEIGHT * BITE_FINAL_SIZE), int(HEIGHT * BITE_FINAL_SIZE)
        
        start_cx = fox_pos_x + (fox_img.get_width() // 2) if fox_img else WIDTH // 2
        start_cy = fox_pos_y + (fox_img.get_height() // 2) if fox_img else HEIGHT // 2
        alpha = 255
        cw, ch, cx, cy = fw, fh, tx - fw//2, ty - fh//2

        if t <= attack_duration:
            p = t / attack_duration
            start_scale = 3.0; current_scale = start_scale - (start_scale - 1.0) * p 
            cw, ch = int(fw * current_scale), int(fh * current_scale)
            cur_cx = start_cx + (tx - start_cx) * p
            cur_cy = start_cy + (ty - start_cy) * p
            cx, cy = cur_cx - cw // 2, cur_cy - ch // 2
        elif t <= (attack_duration + hold_duration):
            pass
        elif t <= total_time:
            p = (t - (attack_duration + hold_duration)) / fade_duration
            alpha = int(255 * (1 - p))
        else:
            bite_anim["active"] = False
        
        if bite_anim["active"]:
            final_x = cx + shake_x
            final_y = cy + shake_y
            if bite_raw:
                s = pygame.transform.scale(bite_raw, (cw, ch))
                if alpha < 255: s.set_alpha(alpha)
                screen.blit(s, (final_x, final_y))
            else:
                s = pygame.Surface((cw, ch)); s.fill((255, 0, 0)); s.set_alpha(alpha)
                screen.blit(s, (final_x, final_y))

    # 能量條
    ex, ey, es, ew, eh = WIDTH * 0.33, HEIGHT * 0.88, WIDTH * 0.035, 8, 16
    for i in range(MAX_ENERGY):
        cx = ex + i * es
        pts = [(cx, ey), (cx + ew, ey - eh), (cx + 2*ew, ey), (cx + ew, ey + eh)]
        if energy_recover_timer[i] > 0:
            s = pygame.Surface((ew*2+2, eh*2+2), pygame.SRCALPHA)
            pygame.draw.polygon(s, (0, 255, 255, int(255 * energy_recover_timer[i])), [(0, eh), (ew, 0), (ew*2, eh), (ew, eh*2)])
            screen.blit(s, (cx, ey - eh))
        elif pending_action and selected_option is not None:
            cost = energy_cost[selected_option]
            if i < player_energy - cost: pygame.draw.polygon(screen, (0, 255, 255), pts)
            elif i >= player_energy - cost and i < player_energy: pygame.draw.polygon(screen, (0, 255, 255), pts, 1)
        else:
            if i < player_energy: pygame.draw.polygon(screen, (0, 255, 255), pts)

    # 結算
    if game_over or victory:
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(180)
        s.fill((0, 0, 0))
        screen.blit(s, (0, 0))

        if victory:
            if len(confetti_particles) < 150: 
                confetti_particles.append(create_confetti())
            for p in confetti_particles:
                p['timer'] += dt
                p['y'] += p['speed_y'] * dt * 60 
                sway_offset = math.sin(p['timer'] * p['sway_freq'] * 10) * p['sway_amp']
                actual_x = p['x'] + sway_offset
                tumble_scale = abs(math.cos(p['tumble_phase'] + p['timer'] * p['tumble_speed'] * 10))
                draw_height = max(1, int(p['height'] * tumble_scale))
                rect = pygame.Rect(actual_x, p['y'] - draw_height // 2, p['width'], draw_height)
                pygame.draw.rect(screen, p['color'], rect)
            confetti_particles = [p for p in confetti_particles if p['y'] < HEIGHT]

        if victory:
            text_str = "VICTORY"
            text_color = (255, 215, 0)
        else:
            text_str = "GAME OVER"
            text_color = (255, 50, 50)

        main_text = result_font.render(text_str, True, text_color)
        restart_text = font.render("Press 'R' to Restart", True, (255, 255, 255))
        screen.blit(main_text, (WIDTH // 2 - main_text.get_width() // 2, HEIGHT // 2 - main_text.get_height()))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + HEIGHT * 0.1))

# --- 主迴圈 ---
running = True
while running:
    dt = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if game_over or victory:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key == pygame.K_r: reset_game() 
            continue 

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            
            if event.key in (pygame.K_1, pygame.K_KP1): selected_option, pending_action = 0, True
            elif event.key in (pygame.K_2, pygame.K_KP2): selected_option, pending_action = 1, True
            elif event.key in (pygame.K_3, pygame.K_KP3): selected_option, pending_action = 2, True
            elif event.key in (pygame.K_4, pygame.K_KP4): selected_option, pending_action = 3, True
            
            elif event.key == pygame.K_SPACE and pending_action:
                cost = energy_cost[selected_option]
                if player_energy >= cost:
                    player_energy -= cost
                    
                    if selected_option == 0:
                        dmg = 10
                        ENEMY_HP = max(0, ENEMY_HP - dmg)
                        damage_texts.append({'damage': dmg, 'x': WIDTH * 0.88, 'y': HEIGHT * 0.05, 'alpha': 255, 'timer': 0, 'target': 'enemy'})
                        if ENEMY_HP <= 0: victory = True
                    
                    elif selected_option == 1:
                        res = play_qte(screen, WIDTH, HEIGHT, draw_bg_func=lambda d: draw_scene(d, is_background=True))
                        clock.tick(60) 
                        dmg = 10 if res == "MISS" else (15 if res == "GREAT" else 20)
                        ENEMY_HP = max(0, ENEMY_HP - dmg)
                        damage_texts.append({'damage': dmg, 'x': WIDTH * 0.88, 'y': HEIGHT * 0.05, 'alpha': 255, 'timer': 0, 'target': 'enemy'})
                        if ENEMY_HP <= 0: victory = True
                    
                    elif selected_option == 2: shield_turns = 3
                    
                    elif selected_option == 3: # End Round
                        e_dmg = int(20 * random.uniform(0.8, 1.3))
                        final_dmg = e_dmg
                        
                        impact_lvl = 3 # 預設

                        if shield_turns > 0:
                            results = play_dbd_qte(screen, WIDTH, HEIGHT, draw_bg_func=lambda d: draw_scene(d, is_background=True))
                            clock.tick(60) 
                            
                            perfect_count = results.count("PERFECT")
                            final_dmg = int(e_dmg * (1 - 0.2 * perfect_count))
                            shield_turns -= 1

                            if perfect_count >= 3: impact_lvl = 1 
                            elif perfect_count >= 1: impact_lvl = 2 
                            else: impact_lvl = 3
                        
                        pending_damage_value = final_dmg
                        pending_impact_level = impact_lvl 
                        pending_enemy_attack = True 
                        enemy_attack_timer = 0

                selected_option, pending_action = None, False

    draw_scene(dt); pygame.display.flip()
pygame.quit()