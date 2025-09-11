import pygame as pg

pg.init()
w,h=400,400
screen=pg.display.set_mode((w,h))
pg.display.set_caption("practice")

bg=pg.Surface(screen.get_size())
bg=bg.convert()
bg.fill((255,255,255)) # white
screen.blit(bg,(0,0))#display the background
pg.display.update()

# main loop
running=True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
pg.quit()
