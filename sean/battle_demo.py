import pygame
import sys,os

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
#將父目錄路徑添加到 Python 的搜尋路徑中
#sys.path.insert(0, ...) 將路徑添加到清單的最前面
sys.path.insert(0, base_dir)
import XddObjects as xo

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("雙球")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)   
RED = (255, 0, 0)   
BLACK = (0, 0, 0)

# WASD
x1, y1 = 200, 300
vx1, vy1 = 0, 0
size1 = 15
speed1 = 5
friction = 0.6
pressed_keys = []
x, y = WIDTH // 2, HEIGHT // 2
size = 10
speed = 5



default_friction = 0.6

friction_rail_path=os.path.join(base_dir,"picture","sound_slider","slider_rail.png")
friction_twist_path=os.path.join(base_dir,"picture","sound_slider","slider_twist.png")
friction_rail=xo.sliderRailObject(friction_rail_path,(WIDTH//2,70),(300,10))
friction_twist=xo.sliderTwistObject(friction_twist_path,
                                    (WIDTH//2,70),(10,27),
                                    0,0.99,default_friction,friction_rail)
friction_font=pygame.font.SysFont("times new roman",20)
friction_text=friction_font.render(f"friction: {friction_twist.current_val:.2f}",True,BLACK)

# 反彈 + 追蹤
x2, y2 = 600, 300
size2 = 20
follow_accel = 0.005  # 追蹤a
max_speed = 10    # MAX V
vx2, vy2 = max_speed, max_speed

font = pygame.font.Font(None, 30)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT :
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                if event.key not in pressed_keys:
                    pressed_keys.append(event.key)
            if event.key==pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        elif event.type == pygame.KEYUP:
            if event.key in pressed_keys:
                pressed_keys.remove(event.key)


    
    # WASD
    friction_twist.update()
    friction_rail.update()

    if pressed_keys:
        key = pressed_keys[-1]
        if key == pygame.K_w:
            vx1, vy1 = 0, -speed1
        elif key == pygame.K_s:
            vx1, vy1 = 0, speed1
        elif key == pygame.K_a:
            vx1, vy1 = -speed1, 0
        elif key == pygame.K_d:
            vx1, vy1 = speed1, 0
    else:
        vx1 *= friction_twist.current_val
        vy1 *= friction_twist.current_val

    x1 += vx1
    y1 += vy1

    if x1 - size1 < 0:
        x1 = size1
        vx1 = 0
    if x1 + size1 > WIDTH:
        x1 = WIDTH - size1
        vx1 = 0
    if y1 - size1 < 0:
        y1 = size1
        vy1 = 0
    if y1 + size1 > HEIGHT:
        y1 = HEIGHT - size1
        vy1 = 0

    # 向量
    dx = x1 - x2
    dy = y1 - y2

    vx2 += dx * follow_accel
    vy2 += dy * follow_accel

    # limit V
    speed = (vx2**2 + vy2**2)**0.5
    if speed > max_speed:
        factor = max_speed / speed
        vx2 *= factor
        vy2 *= factor

    x2 += vx2
    y2 += vy2

    if x2 - size2 < 0 or x2 + size2 > WIDTH:
        vx2 = -vx2
    if y2 - size2 < 0 or y2 + size2 > HEIGHT:
        vy2 = -vy2

    # 畫面更新
    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (int(x1), int(y1)), size1)
    pygame.draw.circle(screen, RED, (int(x2), int(y2)), size2)

    display_keys = [pygame.key.name(k) for k in pressed_keys]
    keys_text = font.render(f"Pressed keys: {display_keys}", True, BLACK)
    screen.blit(keys_text, (10, 10))
    screen.blit(friction_rail.image,friction_rail.rect)
    screen.blit(friction_twist.image,friction_twist.rect)
    friction_text=friction_font.render(f"friction: {friction_twist.current_val:.2f}",True,BLACK)
    screen.blit(friction_text,(WIDTH//2-50,90))
    
    pygame.display.flip()
    clock.tick(60)

#test
