import pygame
import random
import math
import os
from QTE_MLBmode import play_qte 
from QTE_DBDmode import play_dbd_qte 

# ==========================================
# ★★★ 【初始化與全螢幕設定】 ★★★
# ==========================================
pygame.init()
pygame.mixer.init() 

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Fight Prototype")
clock = pygame.time.Clock()

# ==========================================
# ★★★ 【參數設定區】 ★★★
# ==========================================

# 敵人設定
SNAKE_CONFIG = {"hp": 80, "scale": 0.38, "pos_x": 0.25, "pos_y": 0.55}
OWL_CONFIG   = {"hp": 60, "scale": 0.40, "pos_x": 0.5, "pos_y": 0.45}
FOX_CONFIG   = {"hp": 100, "scale": 0.28, "pos_x": 0.75, "pos_y": 0.45}

BASE_ENEMY_DMG = 8
HP_BAR_OFFSET_Y = -20

# Select 圖示位置調整變數
SELECT_OFFSET_X = 0
SELECT_OFFSET_Y = 230 

# ==========================================
# ★★★ 【資源路徑與圖片載入】 ★★★
# ==========================================
current_path = os.path.dirname(__file__) 

def load_img(sub_path, alpha=True):
    path = os.path.join(current_path, sub_path)
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()
    return None

# ★★★ 新增：音效載入函式 ★★★
def load_sfx(filename):
    path = os.path.join(current_path, "voice", filename)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None

# BGM 載入
bgm_path = os.path.join(current_path, "voice", "battle.ogg")
try:
    if os.path.exists(bgm_path):
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.5) 
        pygame.mixer.music.play(-1)       
        print(f"BGM Loaded: {bgm_path}")
    else:
        print(f"Warning: BGM not found at {bgm_path}")
except Exception as e:
    print(f"Error loading BGM: {e}")

bg_raw = load_img("photo/forest_battle.png", False)
bg_img = pygame.transform.scale(bg_raw, (int(WIDTH * 1.05), int(HEIGHT * 1.05))) if bg_raw else pygame.Surface((WIDTH, HEIGHT))
bite_raw = load_img("photo/bite.png")
def_icon_raw = load_img("photo/def_up.png")

# 選怪游標
select_raw = load_img("photo/select.png")
select_img = None
if select_raw:
    s_h = int(HEIGHT * 0.2)
    s_w = int(select_raw.get_width() * (s_h / select_raw.get_height()))
    select_img = pygame.transform.scale(select_raw, (s_w, s_h))

# ==========================================
# ★★★ 【字體定義】 ★★★
# ==========================================
font = pygame.font.SysFont(None, int(HEIGHT * 0.045))
option_font = pygame.font.SysFont(None, int(HEIGHT * 0.045))
result_font = pygame.font.SysFont(None, int(HEIGHT * 0.15)) 
name_font = pygame.font.SysFont(None, int(HEIGHT * 0.1))   
stats_font = pygame.font.SysFont(None, int(HEIGHT * 0.075)) 
enemy_hp_font = pygame.font.SysFont(None, int(HEIGHT * 0.025))

# ==========================================
# ★★★ 【類別：敵人】 ★★★
# ==========================================
class Enemy:
    def __init__(self, name, img_name, config):
        self.name = name
        self.max_hp = config["hp"]
        self.hp = self.max_hp
        self.buffer_hp = self.max_hp
        self.buffer_timer = 0
        
        # ★★★ 新增：載入個別音效 (Attack & Damage) ★★★
        # name.lower() 會把 "Snake" 變成 "snake"，對應檔名 snake_a.ogg / snake_d.ogg
        self.snd_attack = load_sfx(f"{name.lower()}_a.ogg")
        self.snd_damage = load_sfx(f"{name.lower()}_d.ogg")

        raw = load_img(f"photo/{img_name}")
        if raw:
            h = int(HEIGHT * config["scale"])
            w = int(raw.get_width() * (h / raw.get_height()))
            self.image = pygame.transform.scale(raw, (w, h))
        else:
            h = int(HEIGHT * config["scale"])
            self.image = pygame.Surface((h, h)); self.image.fill((100, 100, 100))
            
        self.rect = self.image.get_rect()
        self.rect.centerx = int(WIDTH * config["pos_x"])
        self.rect.bottom = int(HEIGHT * config["pos_y"])
        self.is_dead = False

    def take_damage(self, amount):
        if self.is_dead: return
        
        self.hp = max(0, self.hp - amount)
        self.buffer_timer = 0.5 
        
        # ★★★ 新增：播放受擊音效 ★★★
        if self.snd_damage:
            self.snd_damage.play()

        if self.hp <= 0: self.is_dead = True

    def update(self, dt):
        if self.buffer_hp > self.hp:
            if self.buffer_timer > 0: self.buffer_timer -= dt
            else: self.buffer_hp = max(self.hp, self.buffer_hp - 60 * dt)
        
    def draw(self, surface, shake_x, shake_y):
        draw_pos = (self.rect.x + shake_x, self.rect.y + shake_y)
        if self.is_dead:
            img_copy = self.image.copy(); img_copy.set_alpha(80) 
            surface.blit(img_copy, draw_pos)
        else:
            surface.blit(self.image, draw_pos)
            self.draw_hp_bar(surface, shake_x, shake_y)

    def draw_hp_bar(self, surface, sx, sy):
        bar_w = self.rect.width
        bar_h = int(HEIGHT * 0.015) 
        bar_x = self.rect.x + sx
        bar_y = self.rect.top - bar_h - HP_BAR_OFFSET_Y + sy
        pygame.draw.rect(surface, (80, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        if self.max_hp > 0:
            buff_w = bar_w * (self.buffer_hp / self.max_hp)
            pygame.draw.rect(surface, (255, 255, 0), (bar_x, bar_y, buff_w, bar_h))
            hp_w = bar_w * (self.hp / self.max_hp)
            pygame.draw.rect(surface, (234, 150, 183), (bar_x, bar_y, hp_w, bar_h))
        pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_w, bar_h), 1)
        hp_text = f"HP: {int(self.hp)}/{self.max_hp}"
        text_surf = enemy_hp_font.render(hp_text, True, (255, 255, 255))
        text_x = bar_x + (bar_w - text_surf.get_width()) // 2
        text_y = bar_y + bar_h + 2 
        surface.blit(enemy_hp_font.render(hp_text, True, (0, 0, 0)), (text_x + 1, text_y + 1))
        surface.blit(text_surf, (text_x, text_y))

enemies = []
def init_enemies():
    global enemies; enemies = []
    enemies.append(Enemy("Snake", "forest_snake.png", SNAKE_CONFIG))
    enemies.append(Enemy("Owl", "forest_owl.png", OWL_CONFIG))
    enemies.append(Enemy("Fox", "forest_fox.png", FOX_CONFIG))
init_enemies()

# ==========================================
# ★★★ 【UI 與 遊戲變數】 ★★★
# ==========================================
P_HP_X, P_HP_Y, P_HP_W, P_HP_H = 0.725, 0.615, 0.2, 0.025
OPT_X, OPT_Y, OPT_GAP, OPT_COL_GAP = 0.31, 0.66, 0.10, 0.22
OPT_COLOR = (0, 0, 0)
DEF_IMG_X, DEF_IMG_Y, DEF_IMG_SIZE, DEF_NUM_X_OFF = 0.24, 0.58, 0.05, 0.0001
BITE_X, BITE_Y, BITE_FINAL_SIZE = 0.14, 0.73, 0.3 

PLAYER_NAME = "Mortis"; NAME_X, NAME_Y = 0.086, 0.877; TEXT_COLOR_GRAY = (220, 220, 220) 
PLAYER_STATS = {"ATK": 17, "CRT": 25, "DEF": 25, "INT": 23}
STATS_X, STATS_Y = 0.725, 0.73; STATS_SPACING = 0.06 

def_icon_img = None
if def_icon_raw:
    di_h = int(HEIGHT * DEF_IMG_SIZE)
    di_w = int(def_icon_raw.get_width() * (di_h / def_icon_raw.get_height()))
    def_icon_img = pygame.transform.scale(def_icon_raw, (di_w, di_h))

blood_vignette_img = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
def create_blood_vignette(w, h):
    grad_surf = pygame.Surface((w // 10, h // 10), pygame.SRCALPHA)
    for y in range(h // 10):
        for x in range(w // 10):
            dist = max(abs(x - w//20) / (w//20), abs(y - h//20) / (h//20))
            if dist > 0.5: 
                alpha = min(220, int(255 * ((dist - 0.5) / 0.5)))
                grad_surf.set_at((x, y), (255, 0, 0, alpha))
    return pygame.transform.smoothscale(grad_surf, (w, h))
blood_vignette_img = create_blood_vignette(WIDTH, HEIGHT)

impact_state = {"active": False, "max_alpha": 0, "current_alpha": 0, "shake_amp": 0, "duration": 0, "timer": 0}
PLAYER_HP = 100; PLAYER_MAX_HP = 100; MAX_ENERGY = 10; player_energy = MAX_ENERGY
player_buffer_hp = PLAYER_HP; player_buffer_timer = 0; BUFFER_SPEED = 40; BUFFER_DELAY = 0.5
game_over = False; victory = False
options = ["Normal Attack", "Special Attack", "Defend", "End this round"]
energy_cost = [3, 5, 4, 0]; selected_option = None
energy_recover_queue = []; energy_recover_timer = [0] * MAX_ENERGY
shield_turns = 0; recover_timer = 0; ENERGY_DELAY = 0.1; pending_energy_recover = 0 

enemy_turn_active = False   
enemy_attack_queue = []     
enemy_action_timer = 0      

bite_anim = {"active": False, "timer": 0}
confetti_particles = []
selecting_target = False  
target_skill = None       
current_target_idx = 0    

def trigger_bite(): bite_anim["active"] = True; bite_anim["timer"] = 0
def trigger_impact(level):
    impact_state["active"] = True; impact_state["timer"] = 0
    if level == 3: impact_state["max_alpha"] = 255; impact_state["shake_amp"] = 30; impact_state["duration"] = 1.0
    elif level == 2: impact_state["max_alpha"] = 160; impact_state["shake_amp"] = 15; impact_state["duration"] = 0.6
    else: impact_state["max_alpha"] = 60; impact_state["shake_amp"] = 5; impact_state["duration"] = 0.3
    impact_state["current_alpha"] = impact_state["max_alpha"]

def create_confetti():
    return {'x': random.randint(0, WIDTH), 'y': random.randint(-HEIGHT//2, -10), 'color': random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]), 'speed_y': random.uniform(3, 7)}

def check_victory(): return all(e.is_dead for e in enemies)
def reset_game():
    global PLAYER_HP, player_energy, shield_turns, game_over, victory, selected_option
    global bite_anim, energy_recover_queue, confetti_particles, impact_state
    global player_buffer_hp, player_buffer_timer, selecting_target, target_skill
    global enemy_turn_active, enemy_attack_queue, enemy_action_timer
    
    PLAYER_HP = PLAYER_MAX_HP; player_energy = MAX_ENERGY
    player_buffer_hp = PLAYER_HP; player_buffer_timer = 0
    shield_turns = 0; game_over = False; victory = False
    selected_option = None
    enemy_turn_active = False; enemy_attack_queue = []
    
    bite_anim = {"active": False, "timer": 0}; energy_recover_queue = []
    confetti_particles = []; impact_state["active"] = False
    selecting_target = False; target_skill = None
    init_enemies() 

def draw_scene(dt, is_background=False):
    global recover_timer, player_energy, pending_energy_recover
    global enemy_action_timer, enemy_turn_active, PLAYER_HP, game_over, victory
    global confetti_particles, player_buffer_hp, player_buffer_timer
    
    shake_x, shake_y = 0, 0
    total_shake = 0
    if bite_anim["active"] and bite_anim["timer"] <= 0.35: total_shake += 5
    if impact_state["active"] and impact_state["timer"] < 0.2: total_shake += impact_state["shake_amp"]
    if total_shake > 0:
        shake_x = random.randint(-total_shake, total_shake)
        shake_y = random.randint(-total_shake, total_shake)

    screen.blit(bg_img, (-WIDTH*0.025 + shake_x, -HEIGHT*0.025 + shake_y))

    for enemy in enemies:
        enemy.update(dt)
        enemy.draw(screen, shake_x, shake_y)

    if selecting_target and select_img and not (game_over or victory):
        float_y = math.sin(pygame.time.get_ticks() * 0.01) * 10
        def draw_cursor_on(target):
            cx = target.rect.centerx - select_img.get_width() // 2 + shake_x + SELECT_OFFSET_X
            cy = target.rect.top - select_img.get_height() + float_y + shake_y + SELECT_OFFSET_Y
            screen.blit(select_img, (cx, cy))

        if target_skill == 0:
            if 0 <= current_target_idx < len(enemies):
                target = enemies[current_target_idx]
                if not target.is_dead: draw_cursor_on(target)
        elif target_skill == 1:
            for enemy in enemies:
                if not enemy.is_dead: draw_cursor_on(enemy)

    impact_alpha = 0
    if impact_state["active"]:
        impact_state["timer"] += dt
        if impact_state["timer"] < impact_state["duration"]:
            p = impact_state["timer"] / impact_state["duration"]
            impact_state["current_alpha"] = int(impact_state["max_alpha"] * (1 - p))
            impact_alpha = impact_state["current_alpha"]
        else: impact_state["active"] = False

    low_hp_alpha = 0
    if PLAYER_HP / PLAYER_MAX_HP <= 0.3 and not victory:
        pulse = (math.sin(pygame.time.get_ticks() * 0.003) + 1) * 0.5 
        low_hp_alpha = int(30 + 70 * pulse)

    final_alpha = max(impact_alpha, low_hp_alpha)
    if final_alpha > 0:
        blood_vignette_img.set_alpha(final_alpha)
        screen.blit(blood_vignette_img, (0, 0))

    if player_buffer_hp > PLAYER_HP:
        if player_buffer_timer > 0: player_buffer_timer -= dt
        else: player_buffer_hp = max(PLAYER_HP, player_buffer_hp - BUFFER_SPEED * dt)
    elif player_buffer_hp < PLAYER_HP: player_buffer_hp = PLAYER_HP

    px, py, pw, ph = WIDTH * P_HP_X, HEIGHT * P_HP_Y, WIDTH * P_HP_W, HEIGHT * P_HP_H
    pygame.draw.rect(screen, (110, 204, 149), (px, py, pw, ph)) 
    pygame.draw.rect(screen, (255, 255, 255), (px, py, pw * (player_buffer_hp / PLAYER_MAX_HP), ph)) 
    pygame.draw.rect(screen, (150, 234, 186), (px, py, pw * (PLAYER_HP / PLAYER_MAX_HP), ph)) 
    screen.blit(font.render(f"HP: {int(PLAYER_HP)}/{PLAYER_MAX_HP}", True, (0, 0, 0)), (px, py + ph * 1.2))
    
    name_x, name_y = WIDTH * NAME_X, HEIGHT * NAME_Y
    screen.blit(name_font.render(PLAYER_NAME, True, (0, 0, 0)), (name_x + 4, name_y + 4))
    screen.blit(name_font.render(PLAYER_NAME, True, TEXT_COLOR_GRAY), (name_x, name_y))
    
    stats_sx, stats_sy = WIDTH * STATS_X, HEIGHT * STATS_Y
    for idx, (key, value) in enumerate(PLAYER_STATS.items()):
        s_str = f"{key} {value}"
        cy = stats_sy + (idx * (HEIGHT * STATS_SPACING))
        screen.blit(stats_font.render(s_str, True, (0, 0, 0)), (stats_sx + 2, cy + 2))
        screen.blit(stats_font.render(s_str, True, TEXT_COLOR_GRAY), (stats_sx, cy))

    for i in range(MAX_ENERGY):
        if energy_recover_timer[i] > 0: energy_recover_timer[i] = max(0, energy_recover_timer[i] - dt)

    if not is_background:
        if enemy_turn_active and not victory and not game_over:
            enemy_action_timer += dt
            if enemy_action_timer >= 0.8:
                enemy_action_timer = 0
                if enemy_attack_queue:
                    # ★★★ 修改：取出傷害值與攻擊者，播放該攻擊者的音效 ★★★
                    dmg, attacker = enemy_attack_queue.pop(0)
                    
                    if attacker.snd_attack:
                        attacker.snd_attack.play()
                        
                    trigger_bite()
                    trigger_impact(2) 
                    PLAYER_HP = max(0, PLAYER_HP - dmg)
                    player_buffer_timer = BUFFER_DELAY 
                    if PLAYER_HP <= 0: game_over = True
                else:
                    enemy_turn_active = False
                    pending_energy_recover = 4 

        if not (game_over or victory):
            if pending_energy_recover > 0:
                recover_timer += dt
                if recover_timer >= ENERGY_DELAY:
                    if player_energy < MAX_ENERGY: energy_recover_queue.append(player_energy); player_energy += 1
                    pending_energy_recover -= 1; recover_timer = 0
            if energy_recover_queue:
                recover_timer += dt
                if recover_timer >= ENERGY_DELAY:
                    idx = energy_recover_queue.pop(0); energy_recover_timer[idx] = 1.0; recover_timer = 0

    sx, sy, g_y, g_x = WIDTH * OPT_X, HEIGHT * OPT_Y, HEIGHT * OPT_GAP, WIDTH * OPT_COL_GAP
    for i, option in enumerate(options):
        col, row = i % 2, i // 2
        cx, cy = sx + (col * g_x), sy + (row * g_y)
        is_highlighted = (selected_option == i and not selecting_target) or (selecting_target and target_skill == i)
        if enemy_turn_active: is_highlighted = False
        color = (200, 0, 0) if (is_highlighted and player_energy < energy_cost[i]) else OPT_COLOR
        
        text = option_font.render(f"{i+1}. {option}", True, color)
        screen.blit(text, (cx, cy))
        
        if is_highlighted and player_energy >= energy_cost[i] and not (game_over or victory):
            pygame.draw.circle(screen, (200, 50, 50), (int(cx - 10), int(cy + text.get_height()/2)), 5)

    if shield_turns > 0 and def_icon_img:
        fx, fy = WIDTH * DEF_IMG_X, HEIGHT * DEF_IMG_Y
        screen.blit(def_icon_img, (fx, fy))
        num_t = font.render(str(shield_turns), True, OPT_COLOR)
        screen.blit(num_t, (fx + def_icon_img.get_width() + (WIDTH * DEF_NUM_X_OFF), fy + (def_icon_img.get_height()//2) - (num_t.get_height()//2)))

    if bite_anim["active"]:
        bite_anim["timer"] += dt
        t = bite_anim["timer"]
        dur, hold, fade = 0.15, 0.6, 0.2
        if t <= dur + hold + fade:
            alpha = 255
            if t > dur + hold: alpha = int(255 * (1 - (t - dur - hold)/fade))
            tx, ty = WIDTH * BITE_X, HEIGHT * BITE_Y
            size = int(HEIGHT * BITE_FINAL_SIZE)
            if t <= dur: size = int(size * (3.0 - 2.0 * (t/dur)))
            final_x = tx - size // 2 + shake_x
            final_y = ty - size // 2 + shake_y
            if bite_raw:
                s = pygame.transform.scale(bite_raw, (size, size))
                s.set_alpha(alpha)
                screen.blit(s, (final_x, final_y))
        else: bite_anim["active"] = False

    ex, ey, es, ew, eh = WIDTH * 0.33, HEIGHT * 0.88, WIDTH * 0.035, 8, 16
    for i in range(MAX_ENERGY):
        cx = ex + i * es
        pts = [(cx, ey), (cx + ew, ey - eh), (cx + 2*ew, ey), (cx + ew, ey + eh)]
        current_cost = 0
        if selecting_target and target_skill is not None:
            current_cost = energy_cost[target_skill]
        elif selected_option is not None:
            current_cost = energy_cost[selected_option]

        if energy_recover_timer[i] > 0:
            s = pygame.Surface((ew*2+2, eh*2+2), pygame.SRCALPHA)
            pygame.draw.polygon(s, (0, 255, 255, int(255 * energy_recover_timer[i])), [(0, eh), (ew, 0), (ew*2, eh), (ew, eh*2)])
            screen.blit(s, (cx, ey - eh))
        elif current_cost > 0:
            if i < player_energy - current_cost: pygame.draw.polygon(screen, (0, 255, 255), pts)
            elif i >= player_energy - current_cost and i < player_energy: pygame.draw.polygon(screen, (0, 255, 255), pts, 1)
        else:
            if i < player_energy: pygame.draw.polygon(screen, (0, 255, 255), pts)

    if game_over or victory:
        s = pygame.Surface((WIDTH, HEIGHT)); s.set_alpha(180); s.fill((0, 0, 0))
        screen.blit(s, (0, 0))
        if victory:
            if len(confetti_particles) < 150: confetti_particles.append(create_confetti())
            for p in confetti_particles:
                p['y'] += p['speed_y'] * dt * 60
                pygame.draw.rect(screen, p['color'], (p['x'], p['y'], 10, 10))
            txt = result_font.render("VICTORY", True, (255, 215, 0))
        else:
            txt = result_font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - txt.get_height()))
        res = font.render("Press 'R' to Restart", True, (255, 255, 255))
        screen.blit(res, (WIDTH // 2 - res.get_width() // 2, HEIGHT // 2 + HEIGHT * 0.1))

# --- Loop ---
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
        
        if enemy_turn_active: continue

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: 
                if selecting_target:
                    selecting_target = False 
                    target_skill = None
                    selected_option = None
                else: running = False 

            elif selecting_target:
                if target_skill == 0:
                    change = 0
                    if event.key in (pygame.K_a, pygame.K_LEFT): change = -1
                    elif event.key in (pygame.K_d, pygame.K_RIGHT): change = 1
                    if change != 0:
                        for _ in range(len(enemies)):
                            current_target_idx = (current_target_idx + change) % len(enemies)
                            if not enemies[current_target_idx].is_dead: break 
                
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    cost = energy_cost[target_skill]
                    if player_energy >= cost:
                        player_energy -= cost
                        if target_skill == 0:
                            target = enemies[current_target_idx]
                            if not target.is_dead: target.take_damage(10)
                            if check_victory(): victory = True
                        elif target_skill == 1:
                            res = play_qte(screen, WIDTH, HEIGHT, draw_bg_func=lambda d: draw_scene(d, is_background=True))
                            clock.tick(60)
                            dmg = 10 if res == "MISS" else (15 if res == "GREAT" else 20)
                            for e in enemies:
                                if not e.is_dead: e.take_damage(dmg)
                            if check_victory(): victory = True
                        selecting_target = False; target_skill = None; selected_option = None
            else:
                if event.key in (pygame.K_1, pygame.K_KP1): selected_option = 0
                elif event.key in (pygame.K_2, pygame.K_KP2): selected_option = 1
                elif event.key in (pygame.K_3, pygame.K_KP3): selected_option = 2
                elif event.key in (pygame.K_4, pygame.K_KP4): selected_option = 3

                elif event.key in (pygame.K_w, pygame.K_UP):
                    if selected_option is None: selected_option = 0
                    elif selected_option >= 2: selected_option -= 2 
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    if selected_option is None: selected_option = 0
                    elif selected_option < 2: selected_option += 2 
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    if selected_option is None: selected_option = 0
                    elif selected_option % 2 != 0: selected_option -= 1 
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    if selected_option is None: selected_option = 0
                    elif selected_option % 2 == 0: selected_option += 1 

                elif event.key in (pygame.K_SPACE, pygame.K_RETURN) and selected_option is not None:
                    if selected_option == 0: 
                        if player_energy >= energy_cost[0]:
                            target_skill = 0; selecting_target = True
                            for i, e in enumerate(enemies):
                                if not e.is_dead: current_target_idx = i; break
                    elif selected_option == 1: 
                        if player_energy >= energy_cost[1]: target_skill = 1; selecting_target = True
                    elif selected_option == 2: 
                        if player_energy >= energy_cost[2]:
                            player_energy -= energy_cost[2]; shield_turns = 3; selected_option = None
                    elif selected_option == 3:
                        defense_factor = 1.0
                        if shield_turns > 0:
                            results = play_dbd_qte(screen, WIDTH, HEIGHT, draw_bg_func=lambda d: draw_scene(d, is_background=True))
                            clock.tick(60); perf = results.count("PERFECT")
                            defense_factor = 1.0 - (0.2 * perf) 
                            shield_turns -= 1
                        enemy_attack_queue = []
                        for enemy in enemies:
                            if not enemy.is_dead:
                                raw_dmg = BASE_ENEMY_DMG * random.uniform(0.8, 1.2)
                                final_dmg = int(raw_dmg * defense_factor)
                                # ★★★ 修改：將傷害與攻擊者(Enemy物件)一起存入佇列 ★★★
                                enemy_attack_queue.append((final_dmg, enemy))
                        if enemy_attack_queue:
                            enemy_turn_active = True
                            enemy_action_timer = 0.5 
                        selected_option = None

    draw_scene(dt); pygame.display.flip()
pygame.quit()