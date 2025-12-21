import pygame, math, random, time, sys

def play_dbd_qte(screen, WIDTH, HEIGHT):
    # --- 初始化參數 ---
    C = (WIDTH // 2, HEIGHT // 2 + 30)
    R = 80
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 28, bold=True)
    
    results = []
    current_step = 0
    total_steps = 4
    
    pointer_angle = 0.0      # 指針當前位置
    base_angle = 0.0         # 動態基準點
    pointer_speed = 5.0      # 指針轉動速度
    direction = 1            # 1為順時針，-1為逆時針
    traveled_angle = 0.0     # 紀錄從基準點開始轉了多少
    
    perfect_range = 0.15     # 判定格寬度一半
    
    def get_safe_angle(b_angle, d):
        """
        強制目標生成在基準點的對向區域 (90度 ~ 270度)。
        這樣指針至少要轉過 1/4 圈才會碰到判定格。
        """
        # 1.57 弧度 = 90度, 4.71 弧度 = 270度
        offset = random.uniform(1.57, 4.71)
        return (b_angle + offset * d) % (2 * math.pi)

    # 第一次初始化：以 0 度為基準生成在對面
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if current_step < total_steps:
                    # 判定邏輯
                    diff = abs(pointer_angle - center_angle)
                    if diff > math.pi: diff = 2 * math.pi - diff
                    results.append("PERFECT" if diff <= perfect_range else "MISS")
                    
                    # 更新基準點並換向生成
                    base_angle = pointer_angle
                    current_step += 1
                    
                    if current_step >= total_steps:
                        finish_time = time.time()
                    else:
                        direction *= -1 # 每次按完換方向
                        center_angle = get_safe_angle(base_angle, direction)
                        traveled_angle = 0.0

        # 指針移動
        if current_step < total_steps:
            move = pointer_speed * dt
            pointer_angle = (pointer_angle + move * direction) % (2 * math.pi)
            traveled_angle += move
            
            # 轉滿一圈 (360度) 沒按視為 MISS
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
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 10, 220))
        screen.blit(overlay, (0,0))
        
        pygame.draw.circle(screen, (60, 60, 60), C, R, 8)
        
        if current_step < total_steps:
            # 判定格
            start_a = -(center_angle + perfect_range)
            stop_a = -(center_angle - perfect_range)
            pygame.draw.arc(screen, (255, 255, 255), 
                            (C[0]-R, C[1]-R, 2*R, 2*R), 
                            start_a, stop_a, 16)
            
            # 指針 (紅色直線)
            p_x = C[0] + R * math.cos(pointer_angle)
            p_y = C[1] + R * math.sin(pointer_angle)
            pygame.draw.line(screen, (255, 50, 50), C, (p_x, p_y), 4)
            
        hits = results.count("PERFECT")
        txt = font.render(f"DEFENDING: {hits} / {current_step}", True, (0, 255, 255))
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 120))
        
        pygame.display.flip()
        clock.tick(60)

    return results