import  pygame as pg
pg.init()

width,height= pg.display.Info().current_w, pg.display.Info().current_h
screen=pg.display.set_mode((width,height))
#set icon and caption
icon=pg.image.load(r"test_Star1nDream/image/logo.png")
pg.display.set_caption("test3")
pg.display.set_icon(icon)

#bg=pg.Surface(screen.get_size())
#bg=bg.convert()
#bg.fill((93, 129, 199))
bgi=pg.image.load(r"test_Star1nDream/image/test3-1.png").convert()
screen.blit(bgi,(0,0))  
pg.display.update()

class player():
    def __init__(self):
        super().__init__()
        self.image=[pg.image.load(r"test_Star1nDream/image/test3-2.png").convert_alpha(),
                    pg.image.load(r"test_Star1nDream/image/test3-3.png").convert_alpha()]
        self.rect=self.image.get_rect(center=(width//2,height//2))
    def update(self):
        screen.blit(self.image[0],self.rect)
        


#Main
running= True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
    

pg.quit()