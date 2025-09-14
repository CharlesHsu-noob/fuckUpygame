import pygame

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# 載入原始圖片
original_ship_image = pygame.image.load("picture/sybau/sybau1.png").convert_alpha()
rect = original_ship_image.get_rect(center=(400, 300))

# 旋轉和縮放的參數
current_angle = 0
current_scale = 1.0
scale_direction = -0.01

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # 更新旋轉和縮放參數
    current_angle += 1
    current_scale += scale_direction
    
    # 當圖片縮放到一定程度後反向放大
    if current_scale <= 0.5 or current_scale >= 1.0:
        scale_direction *= -1

    # 使用 rotozoom 函式
    rotated_and_scaled_image = pygame.transform.rotozoom(
        original_ship_image,
        current_angle,
        current_scale
    )
    
    # 獲取新圖片的 rect，並將中心點設為與舊圖片相同
    new_rect = rotated_and_scaled_image.get_rect(center=rect.center)
    
    # 繪製畫面
    screen.fill((0, 0, 0))
    screen.blit(rotated_and_scaled_image, new_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()