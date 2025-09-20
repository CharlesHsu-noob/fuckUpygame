import pygame, math, time, random
pygame.init()

WIDTH, HEIGHT = 500, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

C = (250, 350)  
R = 100  

num = random.randint(165, 330)
pointer_angle = math.radians(180)
pointer_speed = math.radians(150)
direction = -1

center_angle = math.radians(135)
perfect_range = math.radians(5)
great_range = math.radians(15)

start_time = time.time()
a = math.radians(70)

font = pygame.font.SysFont(None, 48)
result = ""
puss_time = 0
waiting = False
animation = True
pre_start = time.time()

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False

        if not animation:
            if not waiting and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                gap = (pointer_angle - center_angle + math.pi) % (2*math.pi) - math.pi
                if abs(gap) <= perfect_range:
                    result = "PERFECT"
                elif abs(gap) <= great_range:
                    result = "GREAT"
                else:
                    result = "MISS"

                waiting = True
                puss_time = time.time()

            elif waiting and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
                pointer_angle = 0.0
                direction = 1
                result = ""
                num = random.randint(165, 330)
                center_angle = math.radians(135)
                start_time = time.time()
                pointer_speed = math.radians(100)
                animation = True
                direction = -1
                pre_start = time.time()
                pointer_angle = math.radians(180)
                pointer_speed = math.radians(150)

    if animation:  
        pointer_angle += pointer_speed * dt * direction
        if pointer_angle < math.radians(1):
            animation = False
            start_time = time.time()
            pointer_angle = 0.0
            pointer_speed = math.radians(50)
            direction = 1

    elif not waiting:  
        pointer_speed = pointer_speed + a * (time.time() - start_time)
        pointer_angle += pointer_speed * dt * direction
        if pointer_angle > math.radians(179):
            pointer_angle = math.radians(180)
            result = "MISS"
            waiting = True

    
    screen.fill((30, 30, 30))
    pygame.draw.arc(screen, (200, 200, 200), (C[0]-R, C[1]-R, 2*R, 2*R), 0, math.pi, 5)

    if not animation:

        pygame.draw.arc(screen, (0, 0, 255), (C[0]-R, C[1]-R, 2*R, 2*R),
                    center_angle - great_range, center_angle + great_range, 10)

        pygame.draw.arc(screen, (0, 255, 0), (C[0]-R, C[1]-R, 2*R, 2*R),
                    center_angle - perfect_range, center_angle + perfect_range, 10)
        
    if animation and pointer_angle < center_angle + great_range and pointer_angle > center_angle - great_range:

        pygame.draw.arc(screen, (0, 0, 255), (C[0]-R, C[1]-R, 2*R, 2*R),
                    pointer_angle, center_angle + great_range, 10)
    elif animation and pointer_angle < center_angle + great_range:
        pygame.draw.arc(screen, (0, 0, 255), (C[0]-R, C[1]-R, 2*R, 2*R),
                    center_angle - great_range, center_angle + great_range, 10)
        
    if animation and pointer_angle < center_angle + perfect_range and pointer_angle > center_angle - perfect_range:

        pygame.draw.arc(screen, (0, 255, 0), (C[0]-R, C[1]-R, 2*R, 2*R),
                    pointer_angle, center_angle + perfect_range, 10)
    elif animation and pointer_angle < center_angle + perfect_range:
        pygame.draw.arc(screen, (0, 255, 0), (C[0]-R, C[1]-R, 2*R, 2*R),
                    center_angle - perfect_range, center_angle + perfect_range, 10)
        
    pointer_x = C[0] + R * math.cos(pointer_angle)
    pointer_y = C[1] - R * math.sin(pointer_angle)
    pygame.draw.line(screen, (255, 0, 0), C, (pointer_x, pointer_y), 5)

    if result:
        text_surf = font.render(result, True, (255, 255, 255))
        screen.blit(text_surf, (C[0]-text_surf.get_width()/2, C[1]-R-60))

    pygame.display.flip()
