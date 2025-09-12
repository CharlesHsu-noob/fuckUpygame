import pygame as pg
import random,math
pg.init()
pg.mixer.init()
clock=pg.time.Clock()

objectlist=pg.sprite.Group()
screeninfo=pg.display.Info()
w,h=screeninfo.current_w,screeninfo.current_h-80
screen = pg.display.set_mode((w,h))
pg.display.set_caption("object_practice")

bg=pg.Surface(screen.get_size())
bg=bg.convert()
bg.fill((255,255,255)) # white

#main loop
running=True
while running:
    clock.tick(30)
    screen.blit(bg,(0,20))
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
    pg.display.update()
pg.quit()


