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

objectlist=pg.sprite.Group()

class moveObject(pg.sprite.Sprite):
    def __init__(self,picture_path,center,size,v):
        super().__init__()
        load_image=pg.image.load(picture_path).convert_alpha()
        self.image=pg.transform.scale(load_image,size)
        self.rect=self.image.get_rect(center=center)
        self.v=v
    def update(self):
        self.rect.x+=self.v
        if(self.rect.left<=0 or self.rect.right>=screen.get_width()):
            self.v*=-1

mrbeast=moveObject("picture/MrBeast.png",(300,550),(200,130),7)
objectlist.add(mrbeast)

#main loop
running=True
while running:
    clock.tick(30)
    screen.blit(bg,(0,20))
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
    objectlist.update()
    objectlist.draw(screen)
    pg.display.update()
pg.quit()


