import pygame as pg
import sys
pg.init()


width,height= pg.display.Info().current_w/2, pg.display.Info().current_h/2
screen=pg.display.set_mode((width,height))
pg.display.set_caption("test1")

bg=pg.Surface(screen.get_size())
bg=bg.convert()
bg.fill((93, 129, 199))
screen.blit(bg,(0,0))
pg.display.update()



running = True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
        if event.type==pg.KEYDOWN:
            if event.key==pg.K_F11: #toggle fullscreen
                pg.display.toggle_fullscreen()
                screen=pg.display.get_surface()
                bg=pg.transform.scale(bg,screen.get_size())
                screen.blit(bg,(0,0))
                pg.display.update()
                
pg.quit()
sys.exit()