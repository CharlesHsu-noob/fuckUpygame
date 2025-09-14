import  pygame as pg
pg.init()

width,height= pg.display.Info().current_w, pg.display.Info().current_h
screen=pg.display.set_mode((width,height))
pg.display.set_caption("test3")

#bg=pg.Surface(screen.get_size())
#bg=bg.convert()
#bg.fill((93, 129, 199))
bgi=pg.image.load(r"C:\Users\yazhu\OneDrive\Desktop\Untitled_Project\fuckUpygame-1\test_Star1nDream\image\test3-1.png").convert()
screen.blit(bgi,(0,0))  
pg.display.update()



running= True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False

pg.quit()