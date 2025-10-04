import pygame

# 初始化 Pygame
pygame.init()

# 設定視窗
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame 字體預覽工具")
clock = pygame.time.Clock()

# 取得所有系統字體列表
font_list = pygame.font.get_fonts()

# 顯示的文字內容
sample_text = "TEST 1234 ,.~! 測試中文"
current_font_index = 0

running = True
while running:
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 偵測按鍵事件
        if event.type == pygame.KEYDOWN:
            # 按下空白鍵，切換到下一個字體
            if event.key == pygame.K_SPACE:
                current_font_index = (current_font_index + 1) % len(font_list)
            # 按下 B 鍵，切換到上一個字體
            elif event.key == pygame.K_b:
                current_font_index = (current_font_index - 1 + len(font_list)) % len(font_list)
            # 按下 Esc 鍵，退出程式
            elif event.key == pygame.K_ESCAPE:
                running = False

    # 清空畫面
    screen.fill((50, 50, 50)) # 深灰色背景

    # 確保字體列表不為空
    if font_list:
        font_name = font_list[current_font_index]
        
        try:
            # 載入字體並設定大小
            font = pygame.font.SysFont(font_name, 60)
            
            # 渲染文字
            text_surface = font.render(sample_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            
            # 渲染字體名稱
            name_font = pygame.font.SysFont(None, 30) # 使用內建字體顯示名稱
            name_surface = name_font.render(font_name, True, (255, 255, 0))
            name_rect = name_surface.get_rect(center=(SCREEN_WIDTH // 2, 50))
            
            # 將文字繪製到畫面上
            screen.blit(text_surface, text_rect)
            screen.blit(name_surface, name_rect)

        except pygame.error:
            # 如果某個字體無法正確渲染，跳過並提示
            error_font = pygame.font.SysFont(None, 30)
            error_surface = error_font.render(f"無法載入字體: {font_name}", True, (255, 0, 0))
            error_rect = error_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(error_surface, error_rect)
            
    else:
        # 如果找不到任何字體
        no_font_text = pygame.font.SysFont(None, 40).render("找不到任何系統字體。", True, (255, 255, 255))
        no_font_rect = no_font_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(no_font_text, no_font_rect)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()