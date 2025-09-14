import  pygame as pg
import math
pg.init()

width,height= pg.display.Info().current_w, pg.display.Info().current_h
screen=pg.display.set_mode((width,height))
#set icon and caption
icon=pg.image.load(r"test_Star1nDream/image/logo.png")
pg.display.set_caption("test3")
pg.display.set_icon(icon)

bg=pg.Surface(screen.get_size())
bg=bg.convert()
bg.fill((93, 129, 199))
bgi=pg.image.load(r"test_Star1nDream/image/test3-1.png").convert()
screen.blit(bg,(0,0))  
screen.blit(bgi,(0,0))  
pg.display.update()

class player():
    
    def __init__(self,picpath):
        super().__init__()
        self.image=pg.image.load(picpath).convert_alpha()
        self.rect=self.image.get_rect(center=(width/2, height/2))
    def face(self):
        event = pg.event.poll()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d:
                return 0
            elif event.key == pg.K_w:
                return 1
            elif event.key == pg.K_a:
                return 2
            elif event.key == pg.K_s:
                return 3
        else:
            return 0
    def move(self,face):
        
        #event = pg.event.poll()
       
        keys=pg.key.get_pressed()
        if keys[pg.K_w] or keys[pg.K_a] or keys[pg.K_s] or keys[pg.K_d]:
            r=face/2
            nx=self.rect.x+math.cos(r*math.pi)*5
            ny=self.rect.y-math.sin(r*math.pi)*5
            if nx>=0 and nx<=width and ny>=0 and ny<=height:
                self.rect.x=nx
                self.rect.y=ny
    def draw(self):
        screen.blit(self.image,self.rect)


        
        
        


#Main
#rock_path=[pg.image.load(r"test_Star1nDream/image/test3-2.png").convert_alpha(),
               #pg.image.load(r"test_Star1nDream/image/test3-3.png").convert_alpha()]
rock=player("test_Star1nDream/image/test3-2.png")

running=True

while running:
    screen.blit(bg,(0,0))  
    screen.blit(bgi,(0,0))
    #face=rock.face() 
    
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_d:
                face= 0
            elif event.key == pg.K_w:
                face= 1
            elif event.key == pg.K_a:
                face= 2
            elif event.key == pg.K_s:
                face= 3
        if event.type==pg.QUIT:
            running=False
    rock.move(face)
    rock.draw()
    pg.display.update()
    

pg.quit()