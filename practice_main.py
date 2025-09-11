import pygame as pg

pg.init()
pg.mixer.init()
menuvol=0.5#volume of menu bgm 0~1
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

sybau=pg.image.load("picture/sybau.png")
sybau.convert()

menubgm=pg.mixer.Sound("voice/soundtrack/000 Edit 1 Export 1.wav")
menubgm.set_volume(menuvol)
menubgm.play()

screen.blit(bg,(0,0))#display the background
screen.blit(titletext,(100,100))
screen.blit(sybau,(100,200))
pg.display.update()
# main loop
running=True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
pg.quit()
