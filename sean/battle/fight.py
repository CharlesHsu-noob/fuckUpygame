import pygame
import random
import math
import time
from QTE_MLBmode import play_qte  # MLB QTE 保留
from QTE_DBDmode import play_dbd_qte     # 修正為函數呼叫

pygame.init()

# --- 視窗 ---
WIDTH, HEIGHT = 500, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fight Prototype")
clock = pygame.time.Clock()

# --- 血量設定 ---
PLAYER_HP = 100
PLAYER_MAX_HP = 100
ENEMY_HP = 100
ENEMY_MAX_HP = 100

# --- 能量設定 ---
MAX_ENERGY = 10
player_energy = MAX_ENERGY

# --- 字型 ---
font = pygame.font.SysFont(None, 18)
option_font = pygame.font.SysFont(None, 18)
damage_font = pygame.font.SysFont(None, 24)

# --- 選項 ---
options = ["Normal Attack", "Special Attack", "Defend", "End this round"]
energy_cost = [3, 5, 4, 0]
selected_option = None
pending_action = False
temp_energy = player_energy

# --- 動畫列表 ---
damage_texts = []
energy_recover_queue = []
energy_recover_timer = [0] * MAX_ENERGY

# --- Defend ---
shield_turns = 0
pending_energy_recover = 0  # 延後回復能量格數

# --- 能量格動畫 ---
ENERGY_DELAY = 0.1
recover_timer = 0

running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # --- 選技能 ---
            if event.key in (pygame.K_1, pygame.K_KP1):
                selected_option = 0
                temp_energy = player_energy - energy_cost[0]
                pending_action = True
            elif event.key in (pygame.K_2, pygame.K_KP2):
                selected_option = 1
                temp_energy = player_energy - energy_cost[1]
                pending_action = True
            elif event.key in (pygame.K_3, pygame.K_KP3):
                selected_option = 2
                temp_energy = player_energy - energy_cost[2]
                pending_action = True
            elif event.key in (pygame.K_4, pygame.K_KP4):
                selected_option = 3
                temp_energy = player_energy
                pending_action = True

            # --- 確認技能 ---
            elif event.key == pygame.K_SPACE and pending_action:
                cost = energy_cost[selected_option]
                if player_energy >= cost:
                    player_energy -= cost

                    # Normal Attack
                    if selected_option == 0:
                        damage = 10
                        ENEMY_HP -= damage
                        ENEMY_HP = max(0, ENEMY_HP)
                        damage_texts.append({
                            'damage': damage,
                            'x': WIDTH - 110 + 50,
                            'y': 10 + 15,
                            'alpha': 255,
                            'timer': 0,
                            'target': 'enemy'
                        })

                    # Special Attack
                    elif selected_option == 1:
                        result = play_qte()
                        if result == "MISS":
                            damage = 10
                        elif result == "GREAT":
                            damage = 15
                        elif result == "PERFECT":
                            damage = 20
                        ENEMY_HP -= damage
                        ENEMY_HP = max(0, ENEMY_HP)
                        damage_texts.append({
                            'damage': damage,
                            'x': WIDTH - 110 + 50,
                            'y': 10 + 15,
                            'alpha': 255,
                            'timer': 0,
                            'target': 'enemy'
                        })

                    # Defend
                    elif selected_option == 2:
                        shield_turns = 3

                    # End this round
                    elif selected_option == 3:
                        enemy_multiplier = random.uniform(0.8, 1.3)
                        enemy_damage = int(20 * enemy_multiplier)

                        if shield_turns > 0:
                            # ★ 僅此處修正呼叫邏輯：改為與 MLB 模式一致的函數呼叫
                            results = play_dbd_qte(screen, WIDTH, HEIGHT)
                            perfect_count = results.count("PERFECT")
                            final_damage = int(enemy_damage * (1 - 0.2 * perfect_count))
                            PLAYER_HP -= final_damage
                            damage_texts.append({
                                'damage': final_damage,
                                'x': 10 + 50,
                                'y': 10 + 15,
                                'alpha': 255,
                                'timer': 0,
                                'target': 'player'
                            })

                            # QTE 完成後回復能量
                            pending_energy_recover = 4
                            shield_turns -= 1

                        else:
                            # 普通扣血
                            PLAYER_HP -= enemy_damage
                            damage_texts.append({
                                'damage': enemy_damage,
                                'x': 10 + 50,
                                'y': 10 + 15,
                                'alpha': 255,
                                'timer': 0,
                                'target': 'player'
                            })

                            # 能量立即回復（逐格動畫）
                            for _ in range(4):
                                if player_energy < MAX_ENERGY:
                                    energy_recover_queue.append(player_energy)
                                    player_energy += 1
                                    energy_recover_timer[energy_recover_queue[-1]] = 0

                selected_option = None
                pending_action = False
                temp_energy = player_energy

    # --- 背景 ---
    screen.fill((0, 0, 0))

    # --- 玩家血條 ---
    pygame.draw.rect(screen, (0, 100, 0), (10, 10, 100, 10))
    pygame.draw.rect(screen, (0, 255, 0), (10, 10, 100 * (PLAYER_HP / PLAYER_MAX_HP), 10))
    screen.blit(font.render(f"HP: {PLAYER_HP}/{PLAYER_MAX_HP}", True, (255, 255, 255)), (10, 22))

    # --- 敵人血條 ---
    pygame.draw.rect(screen, (100, 0, 0), (WIDTH - 110, 10, 100, 10))
    pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 110, 10, 100 * (ENEMY_HP / ENEMY_MAX_HP), 10))
    screen.blit(font.render(f"HP: {ENEMY_HP}/{ENEMY_MAX_HP}", True, (255, 255, 255)), (WIDTH - 110, 22))

    # --- 扣血動畫 ---
    for dmg in damage_texts[:]:
        dmg['y'] -= 30 * dt
        dmg['timer'] += dt
        dmg['alpha'] = max(0, 255 * (1 - dmg['timer'] / 1.0))
        color = (255, 100, 0) if dmg['target'] == 'player' else (255, 255, 0)
        text_surf = damage_font.render(f"-{dmg['damage']}", True, color)
        text_surf.set_alpha(int(dmg['alpha']))
        screen.blit(text_surf, (dmg['x'] - text_surf.get_width() // 2,
                                dmg['y'] - text_surf.get_height() // 2))
        if dmg['timer'] >= 1.0:
            damage_texts.remove(dmg)

    # --- 能量回復動畫（逐格亮起） ---
    for i in range(MAX_ENERGY):
        if energy_recover_timer[i] > 0:
            energy_recover_timer[i] -= dt
            if energy_recover_timer[i] < 0:
                energy_recover_timer[i] = 0

    if pending_energy_recover > 0:
        recover_timer += dt
        if recover_timer >= ENERGY_DELAY:
            idx = MAX_ENERGY - pending_energy_recover
            energy_recover_queue.append(idx)
            player_energy += 1
            energy_recover_timer[idx] = 1.0
            pending_energy_recover -= 1
            recover_timer = 0

    if energy_recover_queue:
        recover_timer += dt
        if recover_timer >= ENERGY_DELAY:
            idx = energy_recover_queue.pop(0)
            energy_recover_timer[idx] = 1.0
            recover_timer = 0

    # --- 選項 & 能量條 ---
    start_x = 50
    start_y = HEIGHT // 2
    spacing = 25
    for i, option in enumerate(options):
        color = (255, 255, 255)
        if selected_option == i and pending_action and player_energy < energy_cost[i]:
            color = (255, 80, 80)
        text = option_font.render(f"{i+1}. {option}", True, color)
        screen.blit(text, (start_x, start_y + i * spacing))

        # 選項框
        if selected_option == i:
            if not pending_action or player_energy >= energy_cost[i]:
                pygame.draw.rect(screen, (255, 255, 0),
                                 (start_x - 5, start_y + i * spacing - 2,
                                  text.get_width() + 10, text.get_height() + 4), 1)

        # 三角形盾牌
        if i == 2 and shield_turns > 0:
            h = text.get_height()
            offset = 5
            shield_points = [
                (start_x + text.get_width() + 5 + offset, start_y + i*spacing),
                (start_x + text.get_width() + 12 + offset, start_y + i*spacing + h),
                (start_x + text.get_width() - 2 + offset, start_y + i*spacing + h)
            ]
            pygame.draw.polygon(screen, (0, 200, 255), shield_points)
            screen.blit(font.render(str(shield_turns), True, (255, 255, 255)),
                        (start_x + text.get_width() + 14 + offset, start_y + i*spacing))

    # --- 能量條 ---
    energy_start_x = 50
    energy_start_y = HEIGHT - 50
    energy_spacing = 20
    for i in range(MAX_ENERGY):
        points = [
            (energy_start_x + i * energy_spacing, energy_start_y),
            (energy_start_x + i * energy_spacing + 5, energy_start_y - 10),
            (energy_start_x + i * energy_spacing + 10, energy_start_y),
            (energy_start_x + i * energy_spacing + 5, energy_start_y + 10)
        ]

        if energy_recover_timer[i] > 0:
            alpha = int(255 * energy_recover_timer[i])
            s = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.polygon(s, (0, 255, 255, alpha), [(0,5),(5,0),(10,5),(5,10)])
            screen.blit(s, (energy_start_x + i*energy_spacing, energy_start_y-5))

        elif pending_action and selected_option is not None:
            cost = energy_cost[selected_option]
            # 填滿能量
            if i < player_energy - cost:
                pygame.draw.polygon(screen, (0, 255, 255), points)
            # 空心表示扣掉的能量
            elif i >= player_energy - cost and i < player_energy:
                pygame.draw.polygon(screen, (0, 255, 255), points, 1)
        else:
            # 正常填滿
            if i < player_energy:
                pygame.draw.polygon(screen, (0, 255, 255), points)

    pygame.display.flip()

pygame.quit()