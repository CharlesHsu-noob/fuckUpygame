import pygame as pg

pg.init()
w,h=1300,700
screen=pg.display.set_mode((w,h))
pg.display.set_caption("practice")

bg=pg.Surface(screen.get_size())
bg=bg.convert()
bg.fill((255,255,255)) # white

#pg.draw.rect(bg,(0,0,255),(50,50,100,100),2) #blue rectangle
#pg.draw.circle(bg,(255,0,0),(200,200),50) #red circle
#pg.draw.line(bg,(0,255,0),(300,300),(400,400),5) #green line
title=pg.font.SysFont("arial",72)
titletext=title.render("FUCK U PYTHON",True,(0,0,0)) #black text
screen.blit(bg,(0,0))#display the background
screen.blit(titletext,(100,100))
pg.display.update()
# main loop
running=True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
pg.quit()
