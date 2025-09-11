import pygame as pg
import random,math
pg.init()
pg.mixer.init()
clock=pg.time.Clock()
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
mrbeast_or=pg.image.load("picture/MrBeast.png")
mrbeast_or.convert()
mrbeast=pg.transform.scale(mrbeast_or,(200,130))
beastRect=mrbeast.get_rect()
beastRect.center=(300,550)
beastV=7

milkgragon_or=pg.image.load("picture/milkdragon.png")
milkgragon_or.convert()
milkgragon=pg.transform.scale(milkgragon_or,(130,170))
milkRect=milkgragon.get_rect()
milkRect.center=(random.randint(100,250),random.randint(150,250))
milkdir=random.randint(20,70)
milkdX=5*math.cos(milkdir)
milkdY=5*math.sin(milkdir)

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
    clock.tick(30)
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False

    beastRect.x+=beastV
    if(beastRect.left<=0 or beastRect.right>=screen.get_width()):
        beastV*=-1
    milkRect.x+=milkdX
    milkRect.y+=milkdY
    if(milkRect.left<=0 or milkRect.right>=screen.get_width()):
        milkdX*=-1
    if(milkRect.top<=0 or milkRect.bottom>=screen.get_height()):
        milkdY*=-1
    
    screen.blit(bg,(0,0))
    screen.blit(titletext,(100,100))
    screen.blit(sybau,(100,200))
    screen.blit(mrbeast,beastRect)
    screen.blit(milkgragon,milkRect)

    pg.display.update()
pg.quit()
