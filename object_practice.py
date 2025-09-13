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
mainMenuBg=pg.transform.scale(pg.image.load("picture/main_menu_bg.png").convert_alpha(),(w,h))
objectlist=pg.sprite.Group()

class moveObject(pg.sprite.Sprite):
    def __init__(self,picture_path,center,size,v,israndom):
        super().__init__()
        load_image=pg.image.load(picture_path).convert_alpha()
        self.image=pg.transform.scale(load_image,size)
        self.rect=self.image.get_rect(center=center)
        if israndom:
            self.pos=(random.randint(20,70))
        else:
            self.pos=0
        self.dx=v*math.cos(self.pos)
        self.dy=v*math.sin(self.pos)
        
    def update(self):
        self.rect.x+=self.dx
        self.rect.y+=self.dy
        if(self.rect.left<=0 or self.rect.right>=screen.get_width()):
            self.dx*=-1
        if(self.rect.top<=0 or self.rect.bottom>=screen.get_height()):
            self.dy*=-1


mrbeast=moveObject("picture/MrBeast.png",(300,550),(200,130),7,False)
objectlist.add(mrbeast)
milk=moveObject("picture/milkdragon.png",(random.randint(100,250),random.randint(150,250)),(130,170),8,True)
objectlist.add(milk)

title=pg.font.SysFont("arial",72)
titletext=title.render("TEST MENU",True,(0,0,255))
#main loop
running=True
while running:
    clock.tick(30)
    screen.blit(bg,(0,0))
    screen.blit(mainMenuBg,(0,0))
    screen.blit(titletext,(100,100))
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
    objectlist.update()
    objectlist.draw(screen)
    pg.display.update()
pg.quit()


