import pygame, sys
pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("反彈")
clock = pygame.time.Clock()

x, y = WIDTH // 2, HEIGHT // 2 
vx, vy = 4, 3 
size = 20

WHITE = (255, 255, 255)
RED = (255, 0, 0)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    x += vx
    y += vy

    if x - size < 0 or x + size > WIDTH:
        vx = -vx
    if y - size < 0 or y + size > HEIGHT:
        vy = -vy

    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (x, y), size)
    pygame.display.flip()
    clock.tick(60) 
