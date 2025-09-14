import pygame as pg
import random,math,os
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

# --- Sprite Groups ---
main_menu_sprites = pg.sprite.Group()
in_game_sprites = pg.sprite.Group()
all_sprites = pg.sprite.Group() # Group for sprites that appear in all states, like exit button

class moveObject(pg.sprite.Sprite):
    def __init__(self,picture_path,center,size,v,israndom):
        super().__init__()
        load_image=pg.image.load(picture_path).convert_alpha()
        self.image=pg.transform.scale(load_image,size)
        self.rect=self.image.get_rect(center=center)
        if israndom:
            self.pos=(random.randint(20,70))
            self.pos=math.radians(self.pos)
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

class buttonObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size):
        super().__init__()
        self.istouch=False
        self.ispress=False
        self.images = [
            pg.transform.scale(pg.image.load(picture_paths[0]).convert_alpha(), size),
            pg.transform.scale(pg.image.load(picture_paths[1]).convert_alpha(), size),
            pg.transform.scale(pg.image.load(picture_paths[2]).convert_alpha(), size)
        ]
        self.image=self.images[0]
        self.rect=self.image.get_rect(center=center)
    def update(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        # 使用 collidepoint 進行更簡單的碰撞偵測
        if self.rect.collidepoint(mouse_pos):
            self.image = self.images[1]
            self.istouch=True
        else:
            self.image = self.images[0]
            self.istouch=False
        if self.istouch and mouse_pressed:
            self.image=self.images[2]
            self.ispress=True
        elif self.istouch:
            self.image=self.images[1]
            self.ispress=False
        else:
            self.image=self.images[0]
            self.ispress=False

class sliderRailObject(pg.sprite.Sprite):
    def __init__(self,picture_path,center,size):
        super().__init__()
        load_image=pg.image.load(picture_path).convert_alpha()
        self.image=pg.transform.scale(load_image,size)
        self.rect=self.image.get_rect(center=center)
        self.minx=self.rect.left,self.maxx=self.rect.right

class sliderTwistObject(pg.sprite.Sprite):
    def __init__(self,picture_path,center,size,min_val,max_val,default_val):
        super().__init__()
        self.min_val=min_val
        self.max_val=max_val
        self.current_val=default_val
        self.isdrag=False
        self.image=pg.transform.scale(pg.image.load(picture_path).convert_alpha(), size)
        self.rect=self.image.get_rect(center=center)
    def update(self,minx,maxx):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        if self.rect.collidepoint(mouse_pos) and mouse_pressed:
            self.isdrag=True
        else:
            self.isdrag=False
        if self.isdrag and self.rect.left<=maxx and self.rect.right>=minx:
            self.rect.x=mouse_pos[0]
            self.current_val=self.min_val+((self.rect.centerx-minx)/(maxx-minx))*(self.max_val-self.min_val)



class characterObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,move_paths,default_center,size):
        super().__init__()
        self.images = [] 
        self.moves=[]
        self.move_index=0
        self.flipx=0
        self.flipy=0
        try:
            for path in picture_paths:
                self.images.append(pg.transform.scale(pg.image.load(path).convert_alpha(), size))
            self.image = self.images[0]
        except pg.error:
            self.image = pg.Surface(size)
            self.image.fill((0, 255, 0)) # Green placeholder
        try:
            for path in move_paths:
                self.moves.append(pg.transform.scale(pg.image.load(path).convert_alpha(),size))
        except pg.error:
            self.image = pg.Surface(size)
            self.image.fill((0, 255, 0)) # Green placeholder
        self.v=5
        self.rect=self.image.get_rect(center=default_center)
        self.is_move=False
    def update(self):
        self.is_move=False
        keys=pg.key.get_pressed()
        if keys[pg.K_w] and self.rect.top>0:
            self.rect.y-=self.v
            self.is_move=True
            self.flipy=1
        if keys[pg.K_s] and self.rect.bottom<h:
            self.rect.y+=self.v
            self.is_move=True
            self.flipy=0
        if keys[pg.K_a] and self.rect.left>0:
            self.rect.x-=self.v
            self.is_move=True
            self.flipx=0
        if keys[pg.K_d] and self.rect.right<w:
            self.rect.x+=self.v
            self.is_move=True
            self.flipx=1
        if self.move_index>=3:
            self.move_index=0
        
        if not self.is_move:
            self.image=pg.transform.flip(self.images[0],self.flipx,self.flipy)
        else:
            self.image=pg.transform.flip(self.moves[self.move_index // 2],self.flipx,self.flipy)
            self.move_index+=1
        


mrbeast=moveObject("picture/MrBeast.png",(300,550),(200,130),7,False)
main_menu_sprites.add(mrbeast)
milk=moveObject("picture/milkdragon.png",(random.randint(100,250),random.randint(150,250)),(130,170),8,True)
main_menu_sprites.add(milk)

sybau_paths=["picture/sybau/sybau1.png",
             "picture/sybau/sybau2.png",
             "picture/sybau/sybau3.png"]
sybau=buttonObject(sybau_paths,(200,300),(200,200))
main_menu_sprites.add(sybau)
exit_paths=["picture/exit/exit1.png",
            "picture/exit/exit2.png",
            "picture/exit/exit3.png"]
exit=buttonObject(exit_paths,(w-60,h-30),(105,45))
all_sprites.add(exit)

kingnom_paths=["picture/kingnom/kingnom_stand1.png",
             "picture/kingnom/kingnom_stand2.png"]
kingnom_move_paths=[
    "picture/kingnom/kingnom_move1.png",
    "picture/kingnom/kingnom_move2.png"
]
kingnom=characterObject(kingnom_paths,kingnom_move_paths,(w/2,h/2),(110,125))
in_game_sprites.add(kingnom)

title=pg.font.SysFont("arial",72)
titletext=title.render("TEST MENU",True,(0,0,255))

main_menu_bg_or=pg.image.load("picture/back_ground/main_menu_bg.png")
main_menu_bg_or.convert()
mainMenuBg=pg.transform.scale(main_menu_bg_or.convert_alpha(),(w,h))
def main_menu():
    screen.blit(mainMenuBg,(0,0))
    screen.blit(titletext,(100,100))
    main_menu_sprites.update()
    main_menu_sprites.draw(screen)

in_game_bg_or=pg.image.load("picture/back_ground/in_game_bg.png")
in_game_bg_or.convert()
inGameBg=pg.transform.scale(in_game_bg_or.convert_alpha(),(w,h))
def in_game():
    screen.blit(inGameBg,(0,0))
    in_game_sprites.update()
    in_game_sprites.draw(screen)
    


#main loop
running=True
game_state="main_menu"
while running:
    clock.tick(30)
    #screen.blit(bg,(0,0))
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
    all_sprites.update()
    if game_state == "main_menu":
        main_menu()
        if sybau.ispress:
            game_state = "in_game"
    elif game_state == "in_game":
        in_game()
    all_sprites.draw(screen)
    if exit.ispress:
        running = False 
    pg.display.update()
pg.quit()


