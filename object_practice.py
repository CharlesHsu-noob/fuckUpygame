import pygame as pg
import random,math
pg.init()
pg.mixer.init()
clock=pg.time.Clock()
screeninfo=pg.display.Info()
w,h=screeninfo.current_w,screeninfo.current_h-80
screen = pg.display.set_mode((w,h))
pg.display.set_caption("object_practice")
bg=pg.Surface(screen.get_size())
bg=bg.convert()
bg.fill((255,255,255)) # white

mrbeast=pg.image.load("picture/mrbeast.png")
class mrbeast:
    def __init()__:
        self.image=pg.transform.scale(mrbeast,(200,130))
        self.rect=self.image.get_rect()
        self.rect.center=(300,550)
        self.v=7
    def move()
objectlist=pg.sprite.Group()

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


