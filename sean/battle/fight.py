import pygame
from QTE_MLBmode import play_qte  # QTE 函式不要自動 quit Pygame

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
font = pygame.font.SysFont(None, 18)       # 血條文字
option_font = pygame.font.SysFont(None, 18)  # 技能選項文字

# --- 選項 ---
options = ["Normal Attack", "Special Attack", "Defend"]
selected_option = None
pending_action = False  # 是否選擇技能但尚未按空白鍵

# --- 能量需求 ---
energy_cost = [3, 5, 4]  # 普通攻擊、特殊攻擊、防禦
temp_energy = player_energy  # 暫時顯示能量

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # 選擇技能
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

            # 執行技能
            elif event.key == pygame.K_SPACE and pending_action:
                if selected_option is not None:
                    cost = energy_cost[selected_option]
                    if player_energy >= cost:
                        player_energy -= cost
                        # 執行技能效果
                        if selected_option == 0:
                            print("Used Normal Attack!")
                        elif selected_option == 1:
                            print("Used Special Attack! Launching QTE...")
                            result = play_qte()
                            print("QTE Result:", result)
                        elif selected_option == 2:
                            print("Used Defend!")
                    else:
                        print("Not enough energy!")
                pending_action = False
                temp_energy = player_energy

    # --- 背景 ---
    screen.fill((0, 0, 0))

    # --- 玩家血條 (左上) ---
    pygame.draw.rect(screen, (255, 0, 0), (10, 10, 100, 10))  # 底色
    pygame.draw.rect(screen, (0, 255, 0), (10, 10, 100 * (PLAYER_HP / PLAYER_MAX_HP), 10))  # 當前血量
    hp_text = font.render(f"HP: {PLAYER_HP}/{PLAYER_MAX_HP}", True, (255, 255, 255))
    screen.blit(hp_text, (10, 22))

    # --- 敵人血條 (右上) ---
    pygame.draw.rect(screen, (100, 0, 0), (WIDTH - 110, 10, 100, 10))  # 底色
    pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 110, 10, 100 * (ENEMY_HP / ENEMY_MAX_HP), 10))  # 當前血量
    enemy_text = font.render(f"HP: {ENEMY_HP}/{ENEMY_MAX_HP}", True, (255, 255, 255))
    screen.blit(enemy_text, (WIDTH - 110, 22))

    # --- 選項顯示 ---
    start_x = 50
    start_y = HEIGHT // 2
    spacing = 25
    for i, option in enumerate(options):
        option_text = option_font.render(f"{i+1}. {option}", True, (255, 255, 255))
        screen.blit(option_text, (start_x, start_y + i * spacing))
        # 框住選中的
        if selected_option == i:
            pygame.draw.rect(screen, (255, 255, 0),
                             (start_x - 5, start_y + i * spacing - 2,
                              option_text.get_width() + 10, option_text.get_height() + 4), 1)

    # --- 能量條 (下方菱形，直的，每個從左到右排列) ---
    energy_start_x = 50
    energy_start_y = HEIGHT - 50
    energy_spacing = 20
    for i in range(MAX_ENERGY):
        # 判斷是否要填充
        if i < temp_energy:
            color = (0, 255, 255)  # 實心
            fill = True
        else:
            color = (0, 255, 255)  # 邊框顏色
            fill = False

        # 直的菱形，每個菱形中心在水平上排列
        points = [
            (energy_start_x + i * energy_spacing, energy_start_y),           # 左
            (energy_start_x + i * energy_spacing + 5, energy_start_y - 10),  # 上
            (energy_start_x + i * energy_spacing + 10, energy_start_y),      # 右
            (energy_start_x + i * energy_spacing + 5, energy_start_y + 10)   # 下
        ]
        if fill:
            pygame.draw.polygon(screen, color, points)
        else:
            pygame.draw.polygon(screen, color, points, 1)  # 空心

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
