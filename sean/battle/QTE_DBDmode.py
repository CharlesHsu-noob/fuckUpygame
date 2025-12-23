import pygame, math, random, time, sys

def play_dbd_qte(screen, WIDTH, HEIGHT, draw_bg_func=None):
    # --- 1. 計算縮放比例 (配合全螢幕) ---
    ORIG_W, ORIG_H = 500, 400
    scale_x = WIDTH / ORIG_W
    scale_y = HEIGHT / ORIG_H
    # 圓形物體使用 "最小邊" 的比例，確保是正圓形，不會被拉成橢圓
    scale_r = min(scale_x, scale_y) 

    # --- 2. 應用縮放後的參數 ---
    # 圓心位置 (垂直位置稍微偏移)
    center_offset_y = int(30 * scale_y)
    C = (WIDTH // 2, HEIGHT // 2 + center_offset_y)
    
    # 半徑與線條粗細
    R = int(80 * scale_r)
    width_circle_stroke = max(1, int(8 * scale_r))
    width_arc_stroke = max(1, int(16 * scale_r))
    width_pointer = max(1, int(4 * scale_r))
    
    # 字體大小與位置偏移
    font_size = int(28 * scale_r)
    text_y_offset = int(120 * scale_y)

    # --- 初始化物件 ---
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", font_size, bold=True)
    
    results = []
    current_step = 0
    total_steps = 4
    
    pointer_angle = 0.0      
    base_angle = 0.0         
    pointer_speed = 5.0      
    direction = 1            
    traveled_angle = 0.0     
    
    perfect_range = 0.15     
    
    def get_safe_angle(b_angle, d):
        offset = random.uniform(1.57, 4.71)
        return (b_angle + offset * d) % (2 * math.pi)

    center_angle = get_safe_angle(base_angle, direction)
    
    running = True
    finish_time = 0
    last_time = time.time()

    pygame.event.clear(pygame.KEYDOWN)

    while running:
        now = time.time()
        dt = now - last_time
        last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            # 支援 ESC 退出 (雖然通常 QTE 不給退，但全螢幕模式下為了安全起見)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                results = ["MISS"] * total_steps # 強制失敗

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if current_step < total_steps:
                    diff = abs(pointer_angle - center_angle)
                    if diff > math.pi: diff = 2 * math.pi - diff
                    results.append("PERFECT" if diff <= perfect_range else "MISS")
                    
                    base_angle = pointer_angle
                    current_step += 1
                    if current_step >= total_steps:
                        finish_time = time.time()
                    else:
                        direction *= -1
                        center_angle = get_safe_angle(base_angle, direction)
                        traveled_angle = 0.0

        if current_step < total_steps:
            move = pointer_speed * dt
            pointer_angle = (pointer_angle + move * direction) % (2 * math.pi)
            traveled_angle += move
            if traveled_angle >= 2 * math.pi:
                results.append("MISS")
                base_angle = pointer_angle
                current_step += 1
                if current_step >= total_steps:
                    finish_time = time.time()
                else:
                    direction *= -1
                    center_angle = get_safe_angle(base_angle, direction)
                    traveled_angle = 0.0
        else:
            if now - finish_time > 0.5:
                running = False

        # --- 渲染 ---
        # 如果有傳入背景繪圖函數，就呼叫它 (讓能量動畫在背景繼續跑)
        if draw_bg_func:
            draw_bg_func(dt)
        else:
            screen.fill((0, 0, 0))

        # QTE 介面覆蓋 (半透明黑底)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 10, 200))
        screen.blit(overlay, (0,0))
        
        # 繪製外框圓圈
        pygame.draw.circle(screen, (60, 60, 60), C, R, width_circle_stroke)
        
        if current_step < total_steps:
            # 繪製判定區 (白色弧線)
            start_a = -(center_angle + perfect_range)
            stop_a = -(center_angle - perfect_range)
            # 使用 Rect 定義弧線位置: (left, top, width, height)
            pygame.draw.arc(screen, (255, 255, 255), (C[0]-R, C[1]-R, 2*R, 2*R), start_a, stop_a, width_arc_stroke)
            
            # 繪製指針
            p_x = C[0] + R * math.cos(pointer_angle)
            p_y = C[1] + R * math.sin(pointer_angle)
            pygame.draw.line(screen, (255, 50, 50), C, (p_x, p_y), width_pointer)
            
        hits = results.count("PERFECT")
        txt = font.render(f"DEFENDING: {hits} / {current_step}", True, (0, 255, 255))
        # 文字置中顯示
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - text_y_offset))
        
        pygame.display.flip()
        clock.tick(60)

    return results