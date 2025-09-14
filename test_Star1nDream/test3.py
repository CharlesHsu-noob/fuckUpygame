import  pygame as pg
pg.init()

width,height= pg.display.Info().current_w, pg.display.Info().current_h
screen=pg.display.set_mode((width,height))
pg.display.set_caption("test3")

bg=pg.Surface(screen.get_size())
bg=bg.convert()
bg.fill((93, 129, 199))
screen.blit(bg,(0,0))
pg.display.update()

bgi=pg.image.load("C:\Users\yazhu\OneDrive\Desktop\Untitled_Project\test_image\test3-1.png").convert()

running= True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False

pg.quit()