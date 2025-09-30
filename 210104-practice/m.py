import pygame
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("雷射反射模擬")
clock = pygame.time.Clock()

# 顏色
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# 入口、出口
entrance = pygame.Rect(50, 50, 20, 20)
exit_rect = pygame.Rect(WIDTH-70, HEIGHT-70, 20, 20)

# 鏡子
mirror = pygame.Rect(WIDTH//2, HEIGHT//2, 150, 5)
mirror_speed = 5

# 雷射
laser_active = False
laser_start = [entrance.centerx, entrance.centery]
laser_end = laser_start.copy()
laser_angle = 45  # 往右下45度
laser_dir = [math.cos(math.radians(laser_angle)), math.sin(math.radians(laser_angle))]

# 按鈕
button = pygame.Rect(50, HEIGHT-50, 100, 30)

running = True
while running:
    screen.fill(BLACK)
    
    # --- 畫入口、出口、鏡子、按鈕 ---
    pygame.draw.rect(screen, BLUE, entrance)
    pygame.draw.rect(screen, GREEN if exit_rect.collidepoint(laser_end) else RED, exit_rect)
    pygame.draw.rect(screen, GRAY, mirror)
    pygame.draw.rect(screen, WHITE, button)
    
    font = pygame.font.SysFont(None, 24)
    screen.blit(font.render("開始", True, BLACK), (button.x + 20, button.y + 5))
    
    # --- 鏡子移動（按開始前可移動） ---
    keys = pygame.key.get_pressed()
    if not laser_active:
        if keys[pygame.K_LEFT] and mirror.x > 0:
            mirror.x -= mirror_speed
        if keys[pygame.K_RIGHT] and mirror.x + mirror.width < WIDTH:
            mirror.x += mirror_speed
    
    # --- 雷射運動 ---
    if laser_active:
        # 先預設雷射射到鏡子碰撞
        # 簡單處理：水平鏡子，只改變垂直方向
        if mirror.collidepoint(laser_end):
            laser_dir[1] *= -1  # 垂直方向反向
        
        # 更新雷射末端
        laser_end[0] += laser_dir[0] * 10
        laser_end[1] += laser_dir[1] * 10

    # 畫雷射光
    pygame.draw.line(screen, RED, laser_start, laser_end, 2)
    
    # --- 事件處理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button.collidepoint(event.pos) and not laser_active:
                # 按下開始鍵
                laser_active = True
                laser_start = [entrance.centerx, entrance.centery]
                laser_end = laser_start.copy()
                laser_dir = [math.cos(math.radians(45)), math.sin(math.radians(45))]  # 45度射出
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
