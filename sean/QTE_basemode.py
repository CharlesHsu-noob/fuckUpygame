import pygame, math, time,random
pygame.init()

WIDTH, HEIGHT = 500, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

C = (250, 300)
R = 100
num=random.randint(30,150)
pointer_angle = 0.0
pointer_speed = math.radians(180)
direction = 1

center_angle = math.radians(num)
perfect_range = math.radians(10)
great_range = math.radians(30)

font = pygame.font.SysFont(None, 48)
result = ""
puss_time = 0
waiting = False

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False
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

    if not waiting:
        pointer_angle += pointer_speed * dt * direction
        if pointer_angle > math.pi:
            pointer_angle = math.pi
            direction = -1
        elif pointer_angle < 0:
            pointer_angle = 0
            direction = 1

    if waiting and time.time() - puss_time >= 1.0:
        waiting = False
        pointer_angle = 0.0
        direction = 1
        result = ""
        num=random.randint(30,150)
        center_angle = math.radians(num)

    screen.fill((30, 30, 30))


    pygame.draw.arc(screen, (200, 200, 200), (C[0]-R, C[1]-R, 2*R, 2*R), 0, math.pi, 5)

   
    pygame.draw.arc(screen, (0, 0, 255), (C[0]-R, C[1]-R, 2*R, 2*R),
                    center_angle - great_range, center_angle + great_range, 10)

    pygame.draw.arc(screen, (0, 255, 0), (C[0]-R, C[1]-R, 2*R, 2*R),
                    center_angle - perfect_range, center_angle + perfect_range, 10)

    pointer_x = C[0] + R * math.cos(pointer_angle)
    pointer_y = C[1] - R * math.sin(pointer_angle)
    pygame.draw.line(screen, (255, 0, 0), C, (pointer_x, pointer_y), 5)

    if result:
        text_surf = font.render(result, True, (255, 255, 255))
        screen.blit(text_surf, (C[0]-text_surf.get_width()/2, C[1]-R-60))

    pygame.display.flip()
