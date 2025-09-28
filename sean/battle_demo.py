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
pygame.display.set_caption("球")
pressed_keys = []

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

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

vx, vy = 0, 0

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

    friction_twist.update()
    friction_rail.update()

    if pressed_keys:
        key = pressed_keys[-1] 
        if key == pygame.K_w:
            vx, vy = 0, -speed
        elif key == pygame.K_s:
            vx, vy = 0, speed
        elif key == pygame.K_a:
            vx, vy = -speed, 0
        elif key == pygame.K_d:
            vx, vy = speed, 0
    else:
        vx *= friction_twist.current_val
        vy *= friction_twist.current_val

    x += vx
    y += vy

    # 邊界檢查
    if x - size < 0:
        x = size
        vx = 0
    if x + size > WIDTH:
        x = WIDTH - size
        vx = 0
    if y - size < 0:
        y = size
        vy = 0
    if y + size > HEIGHT:
        y = HEIGHT - size
        vy = 0

    screen.fill(WHITE)
    pygame.draw.circle(screen, BLUE, (int(x), int(y)), size)

    display_keys = [pygame.key.name(k) for k in pressed_keys]  
    keys_text = font.render(f"Pressed keys: {display_keys}", True, BLACK)
    screen.blit(keys_text, (10, 10))
    screen.blit(friction_rail.image,friction_rail.rect)
    screen.blit(friction_twist.image,friction_twist.rect)
    friction_text=friction_font.render(f"friction: {friction_twist.current_val:.2f}",True,BLACK)
    screen.blit(friction_text,(WIDTH//2-50,90))
    
    pygame.display.flip()
    clock.tick(60)
