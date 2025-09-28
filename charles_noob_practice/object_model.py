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
bg.fill((0,0,0)) # black
pressKeyQueue=[]

# --- 為了跨平台相容性而進行的路徑設定 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)

# --- Sprite Groups ---
main_menu_sprites = pg.sprite.Group()
#in_game_sprites = pg.sprite.Group()
empty_array=[]#佔位用
empty_sprite_group=pg.sprite.Group()
in_game_npc=[]
in_game_wall=[]
in_game_door=[]
in_ac_wall=[]
in_ac_door=[]
pause_sprites = pg.sprite.Group()
#map_sprites = pg.sprite.Group()
state_pos={}
state_pos["in_game"]=(w/2,h/2)
state_pos["in_ac"]=(2048/2,1160-100)

def collision_by_mask_with_mouse(rect,mask):
    mouse_pos = pg.mouse.get_pos()
    # 計算滑鼠相對於圖片的偏移量
    offset_x = mouse_pos[0] - rect.x
    offset_y = mouse_pos[1] - rect.y
    if rect.collidepoint(mouse_pos):# 如果滑鼠在矩形內，檢查遮罩
        # 這裡使用 try-except 是為了避免滑鼠座標超出遮罩範圍時的索引錯誤
        try:
            if mask.get_at((offset_x, offset_y)):
                return True
            else:
                return False
        except IndexError:
            # 座標超出遮罩範圍，通常表示滑鼠在矩形邊緣
            return False
    return False

class moveObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size,v,israndom):
        super().__init__()
        self.image=pg.transform.scale(
            pg.image.load(
                os.path.join(
                    picture_paths)).convert_alpha(),
            size)
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
        self._is_held=False# 內部狀態：追蹤滑鼠是否正按在按鈕上
        self.ispress=False
        self.images = [
            pg.transform.scale(pg.image.load(os.path.join(picture_paths[0])).convert_alpha(), size),
            pg.transform.scale(pg.image.load(os.path.join(picture_paths[1])).convert_alpha(), size),
            pg.transform.scale(pg.image.load(os.path.join(picture_paths[2])).convert_alpha(), size)
        ]
        self.image=self.images[0]
        self.rect=self.image.get_rect(center=center)
        self.mask=pg.mask.from_surface(self.image)
    def update(self):
        self.ispress = False
        #mouse_pos = pg.mouse.get_pos()
        mouse_down = pg.mouse.get_pressed()[0]
        #is_mouse_over = self.rect.collidepoint(mouse_pos)
        is_mouse_over=collision_by_mask_with_mouse(self.rect,self.mask)

        if is_mouse_over:
            if mouse_down:
                # 情況1: 滑鼠在按鈕上，且正被按住
                self.image = self.images[2] 
                self._is_held = True
            else:
                # 情況2: 滑鼠在按鈕上，但沒有被按住
                self.image = self.images[1] 
                # 如果上一幀是按住的狀態，代表滑鼠剛被釋放，這就是一次 "點擊"
                if self._is_held:
                    self.ispress = True
                self._is_held = False
        else:
            # 情況3: 滑鼠不在按鈕上
            self.image = self.images[0]
            self._is_held = False

class sliderRailObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size):
        super().__init__()
        self.image=pg.transform.scale(
            pg.image.load(
                os.path.join(
                    picture_paths)).convert_alpha(),
            size)
        self.rect=self.image.get_rect(center=center)
        self.minx=self.rect.left
        self.maxx=self.rect.right

class sliderTwistObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size,min_val,max_val,default_val,rail):
        super().__init__()
        self.rail=rail
        self.min_val=min_val
        self.max_val=max_val
        self.current_val=default_val
        #self.isdrag=False
        self.last_press=False
        self.image=pg.transform.scale(
            pg.image.load(
                os.path.join(
                    base_dir, picture_paths)).convert_alpha(),
            size)
        self.rect=self.image.get_rect(center=center)
        self.rect.centerx=self.rail.minx+\
                            (self.rail.maxx-self.rail.minx)*\
                            (self.current_val-self.min_val)/(self.max_val-self.min_val)
    def update(self):
        minx=self.rail.minx
        maxx=self.rail.maxx
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]

        if mouse_pressed:
            if self.rect.collidepoint(mouse_pos):
                self.isdrag=True
        else:
            self.isdrag=False
        #move logic
        if self.isdrag:
            self.rect.centerx = mouse_pos[0]
            # Clamp the position to the rail's boundaries
            minx = self.rail.minx
            maxx = self.rail.maxx
            if self.rect.centerx < minx:
                self.rect.centerx = minx
            if self.rect.centerx > maxx:
                self.rect.centerx = maxx
            self.current_val=self.min_val+\
                            (self.max_val-self.min_val)*\
                            (self.rect.centerx-minx)/(maxx-minx)

class characterObject(pg.sprite.Sprite):
    def __init__(self,picture_paths_stand,picture_paths_move,default_center,size):
        super().__init__()
        self.map_x=0
        self.map_y=0
        self.images = [] 
        self.moves=[]
        self.move_index=0
        self.flipx=0
        self.flipy=0
        try:
            for path in picture_paths_stand:
                self.images.append(pg.transform.scale(
                    pg.image.load(
                        os.path.join(path)
                        ).convert_alpha(),size))
            self.image = self.images[0]
        except pg.error:
            self.image = pg.Surface(size)
            self.image.fill((0, 255, 0)) # Green placeholder
        try:
            for path in picture_paths_move:
                self.moves.append(pg.transform.scale(
                    pg.image.load(
                        os.path.join(path)).convert_alpha(),size))
        except pg.error:
            self.image = pg.Surface(size)
            self.image.fill((0, 255, 0)) # Green placeholder
        self.v=10
        self.rect=self.image.get_rect(center=default_center)
        self.is_move=False
        self.move_state="left"
        self.mask=pg.mask.from_surface(self.image)
        self.mask_rect=self.mask.get_rect(center=default_center)
        self.half_w=self.mask_rect.width/2
        self.half_h=self.mask_rect.height/2
    def update(self,pressKeyQueue):
        self.move_character = False
        self.is_move = False
        self.last_move_state = self.move_state
        self.dx, self.dy = 0, 0

        # 處理按鍵輸入
        if pressKeyQueue:
            latest_key = pressKeyQueue[-1]
            
            if latest_key == pg.K_w:
                self.map_y-=self.v
                self.dy = -self.v
                self.move_state = "up"
                self.is_move = True
                self.flipy = 1
            elif latest_key == pg.K_s:
                self.map_y+=self.v
                self.dy = self.v
                self.move_state = "down"
                self.is_move = True
                self.flipy = 0
            elif latest_key == pg.K_a:
                self.map_x-=self.v
                self.dx = -self.v
                self.move_state = "left"
                self.is_move = True
                self.flipx = 0
            elif latest_key == pg.K_d:
                self.map_x+=self.v
                self.dx = self.v
                self.move_state = "right"
                self.is_move = True
                self.flipx = 1
        
        # 更新動畫
        if self.move_index >= len(self.moves) * 7:
            self.move_index = 0
            
        if not self.is_move:
            self.image = pg.transform.flip(self.images[0], self.flipx, self.flipy)
            self.move_index = 0
        else:
            if self.move_index // 4 == 0 or self.move_index // 4 == 1:
                real_index = 0
            elif self.move_index // 4 == 2 or self.move_index // 4 == 3:
                real_index = 1
            self.image = pg.transform.flip(self.moves[real_index], self.flipx, self.flipy)
            self.move_index += 1

        # 更新遮罩
        if self.last_move_state != self.move_state:
            self.mask = pg.mask.from_surface(self.image)
            self.rect=self.image.get_rect(center=(self.map_x,self.map_y))
            self.last_move_state=self.move_state
            self.half_w=self.mask_rect.width/2
            self.half_h=self.mask_rect.height/2

class npcObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size):
        super().__init__()
        self.images = []
        for path in picture_paths:
            self.images.append(pg.transform.scale(
                pg.image.load(
                    os.path.join(path)).convert_alpha(),size))
        self.image=self.images[0]
        #self.rect=self.image.get_rect(center=center)
        self.map_x,self.map_y=center
        self.image_w=self.image.get_width()
        self.image_h=self.image.get_height()
    def update(self,camera_x,camera_y):
        self.need_draw=False
        if self.map_x-camera_x<=w+self.image_w/2 and self.map_y-camera_y<=h+self.image_h/2\
            and self.map_x-camera_x>=0-self.image_w/2 and self.map_y-camera_y>=0-self.image_h/2:
            self.need_draw=True
            self.rect=self.image.get_rect(center=(self.map_x-camera_x,self.map_y-camera_y))

class mapObject(pg.sprite.Sprite):
    def __init__(self,picture_path,center,size):
        super().__init__()   
        self.image=pg.transform.scale(
            pg.image.load(
                os.path.join(
                    picture_path)).convert_alpha(),
            size)
        self.rect=self.image.get_rect(center=center)
        self.map_w=self.rect.width
        self.map_h=self.rect.height
    def update(self):
        pass# deal in in_game()
        '''self.rect.x-=dx
        self.rect.y-=dy
        if self.rect.top>0:
            self.rect.top=0
        elif self.rect.bottom<h:
            self.rect.bottom=h
        if self.rect.left>0:
            self.rect.left=0
        elif self.rect.right<w:
            self.rect.right=w'''

class wallObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,picture_index,center,size,visible):
        super().__init__()
        self.images = []
        for path in picture_paths:
            self.images.append(pg.transform.scale(
                pg.image.load(
                    os.path.join(path)
                    ).convert_alpha(),size))
        self.image=self.images[picture_index]
        self.rect=self.image.get_rect(center=(10000,10000))#初始位置放在看不到的地方
        self.map_x,self.map_y=center
        self.mask=pg.mask.from_surface(self.image)
        self.mask_rect=self.mask.get_rect(center=center)
        self.half_w=self.mask_rect.width/2
        self.half_h=self.mask_rect.height/2
        self.need_deter=False
        self.visible=visible
    def update(self,camera_x,camera_y):
        self.need_deter=False#需要判定=false
        #和npc一樣的判斷邏輯
        if self.map_x-camera_x<=w+self.half_w and self.map_y-camera_y<=h+self.half_h\
            and self.map_x-camera_x>=0-self.half_w and self.map_y-camera_y>=0-self.half_h:
            self.need_deter=True
            self.rect=self.image.get_rect(center=(self.map_x-camera_x,self.map_y-camera_y))

class doorObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size,target_state,visible):
        super().__init__()
        self.images=[]
        for path in picture_paths:
            self.images.append(pg.transform.scale(
                pg.image.load(
                    os.path.join(path)).convert_alpha(),size))
        self.image=self.images[0]
        self.rect=self.image.get_rect(center=(10000,10000))
        self.target=target_state
        self.visible=visible
        self.need_deter=False
        self.map_x,self.map_y=center
        self.mask=pg.mask.from_surface(self.image)
        self.mask_rect=self.mask.get_rect(center=center)
        self.half_w=self.mask_rect.width/2
        self.half_h=self.mask_rect.height/2
    def update(self,camera_x,camera_y):
        self.need_deter=False#需要判定=false
        #和npc一樣的判斷邏輯
        if self.map_x-camera_x<=w+self.half_w and self.map_y-camera_y<=h+self.half_h\
            and self.map_x-camera_x>=0-self.half_w and self.map_y-camera_y>=0-self.half_h:
            self.need_deter=True
            self.rect=self.image.get_rect(center=(self.map_x-camera_x,self.map_y-camera_y))
#path setup,excluding map and background
#one path for one object
volume_rail_path=os.path.join(base_dir,"picture","sound_slider","slider_rail.png")
volume_twist_path=os.path.join(base_dir,"picture","sound_slider","slider_twist.png")
mrbeast_path=os.path.join(base_dir,"picture","MrBeast.png")
milk_path=os.path.join(base_dir,"picture","milkdragon.png")
#multiple path for one object
sybau_paths=[os.path.join(base_dir, "picture", "sybau", "sybau1.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau2.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau3.png")]

exit_paths=[os.path.join(base_dir, "picture", "exit", "exit1.png"),
            os.path.join(base_dir, "picture", "exit", "exit2.png"),
            os.path.join(base_dir, "picture", "exit", "exit3.png")]

back_paths=[os.path.join(base_dir, "picture", "return", "return1.png"),
            os.path.join(base_dir, "picture", "return", "return2.png"),
            os.path.join(base_dir, "picture", "return", "return3.png")]

kingnom_stand_paths=[os.path.join(base_dir, "picture", "kingnom", "kingnom_stand1.png"),
             os.path.join(base_dir, "picture", "kingnom", "kingnom_stand2.png")]

kingnom_move_paths=[os.path.join(base_dir, "picture", "kingnom", "kingnom_move1.png"),
    os.path.join(base_dir, "picture", "kingnom", "kingnom_move2.png")]

hitler_paths=[os.path.join(base_dir,"picture","hitler","hitler1.png")]

barrier_paths=[os.path.join(base_dir,"picture","barrier","barrier_wall_vert.png"),
    os.path.join(base_dir,"picture","barrier","barrier_wall_hori.png")]

door_paths=[os.path.join(base_dir,"picture","door","door1.png")]
#----------------------------------------------------------------------------------------------
#object setup
#pause
defaultvol=0.0
volume_rail=sliderRailObject(volume_rail_path,(w/2,h/2),(300,10))
volume_twist=sliderTwistObject(volume_twist_path,(w/2,h/2),(10,27),0,0.3,defaultvol,volume_rail)
pause_sprites.add(volume_rail)
pause_sprites.add(volume_twist)
pause_exit=buttonObject(exit_paths,(w/2,h-200),(105,45))
pause_sprites.add(pause_exit)
pause_back=buttonObject(back_paths,center=(w/2-100,h-200),size=(150,150))
pause_sprites.add(pause_back)

#main menu
mrbeast=moveObject(mrbeast_path,(300,550),(200,130),7,False)
main_menu_sprites.add(mrbeast)
milk=moveObject(milk_path,(random.randint(100,250),random.randint(150,250)),(130,170),8,True)
main_menu_sprites.add(milk)
sybau=buttonObject(sybau_paths,(200,325),(200,200))
main_menu_sprites.add(sybau)

#transition
transition_omega=2
transition_d_scale=0.1
sybau_transition=pg.transform.scale(pg.image.load(sybau_paths[2]),(200,200))

#in game
kingnom=characterObject(kingnom_stand_paths,kingnom_move_paths,state_pos["in_game"],(88,100))
kingnom.map_x=1040#4160/2#2080
kingnom.map_y=1880#3760/2#1880
char_half=[kingnom.rect.width / 2,kingnom.rect.height / 2]
    #in game npc
hitler=npcObject(hitler_paths,(300,1880),(200,145))
in_game_npc.append(hitler)
    #in game wall
barrier1=wallObject(barrier_paths,0,(200,1780),(40,480),True)
in_game_wall.append(barrier1)
barrier2=wallObject(barrier_paths,1,(500,1500),(700,40),True)
in_game_wall.append(barrier2)
barrier3=wallObject(barrier_paths,1,(500,2050),(700,40),True)
in_game_wall.append(barrier3)

#door
in_game_to_ac=doorObject(door_paths,(900,1640),(75,75),"in_ac",True)#ac=activity center
in_game_door.append(in_game_to_ac)
ac_to_in_game=doorObject(door_paths,(2048/2,1160-20),(75,75),"in_game",True)
in_ac_door.append(ac_to_in_game)
#----------------------------------------------------------------------------------------------
#music init
pg.mixer.music.load(os.path.join(base_dir, "voice", "soundtrack", "red_sun_in_the_sky.wav"))#mainMenuBgm
#defaultvol=0.2  #在object裡面已經定義過
pg.mixer.music.set_volume(defaultvol)
pg.mixer.music.play(loops=-1, fade_ms=1500)
#----------------------------------------------------------------------------------------------
#map and background setup
#pause
pause_bg_or=pg.image.load(os.path.join(base_dir,"picture","back_ground","president_mao.png")).convert_alpha()
pause_bg=pg.transform.scale(pause_bg_or,(w,h))
pause_bg_alpha=100
pause_bg.set_alpha(pause_bg_alpha)
#main menu
main_menu_bg_or=pg.image.load(os.path.join(base_dir, "picture", "back_ground", "main_menu_bg.png"))
main_menu_bg_or.convert()
mainMenuBg=pg.transform.scale(main_menu_bg_or.convert_alpha(),(w,h))

#in game
#inGameBg=mapObject(os.path.join(base_dir, "picture", "back_ground", "in_game_map2.png"),(w/2,h/2),(4160,3760))
in_game_bg=mapObject(os.path.join(base_dir, "picture", "back_ground", "in_game_map2_debug.png"),(w/2,h/2),(4160,3760))

#in ac
ac_bg=mapObject(os.path.join(base_dir,"picture","back_ground","ac_bg.png"),(w/2,h/2),(2048,1160))
#----------------------------------------------------------------------------------------------
#text setup
#volume
vol_percent=0
vol_font=pg.font.SysFont("times new roman",20)
vol_text=vol_font.render(str(vol_percent),True,(255,255,255))

#main menu
title=pg.font.Font(os.path.join(base_dir, "font", "LavishlyYours-Regular.ttf"), 65)
titletext=title.render("KINGNOM's big adventure",True,(0,200,200))
titleZH=pg.font.Font(os.path.join(base_dir, "font", "bpm", "BpmfZihiSerif-Regular.ttf"),40)
titleZHtext=titleZH.render("金農的大冒險",True,(255,200,200))
hint=pg.font.Font(os.path.join(base_dir,"font","bpm","BpmfZihiSerif-Light.ttf"),20)
hint_text=hint.render("點擊ESC鍵以暫停遊戲",True,(255,220,100))
#----------------------------------------------------------------------------------------------
#universal function
def draw_sence(bg,npc_list,door_list,char,wall_list,sprites):#依照圖層序排列
    screen.blit(bg.image,bg.rect)
    for npc in npc_list:
        if npc.need_draw:
            screen.blit(npc.image,npc.rect)
    for door in door_list:
        if door.need_deter and door.visible:
            screen.blit(door.image,door.rect)
    screen.blit(char.image,char.rect)
    for wall in wall_list:
        if wall.need_deter and wall.visible:
            screen.blit(wall.image,wall.rect)
    sprites.draw(screen)

def wall_collision(char,wall_list,last_map_x,last_map_y):
    wall_rect_corretion_x=20#校正空氣牆
    wall_rect_corretion_y=3
    #global last_map_x,last_map_y
    return_x=char.map_x
    return_y=char.map_y
    for wall in wall_list:
        if wall.need_deter:
            if char.map_x+char.half_w>wall.map_x-wall.half_w +wall_rect_corretion_x and\
                char.map_x-kingnom.half_w<wall.map_x+wall.half_w -wall_rect_corretion_x and\
                abs(char.map_y-wall.map_y)<char.half_h+wall.half_h -wall_rect_corretion_y:
                return_x=last_map_x
            if char.map_y+char.half_h>wall.map_y-wall.half_h +wall_rect_corretion_y and\
                char.map_y-char.half_h<wall.map_y+wall.half_h -wall_rect_corretion_y and\
                abs(char.map_x-wall.map_x)<char.half_w+wall.half_w -wall_rect_corretion_x:
                return_y=last_map_y
    return return_x,return_y

def boundary_deter(char,bg,char_half):
    return_x=char.map_x
    return_y=char.map_y
    if char.map_x < char_half[0]:
        return_x = char_half[0]
    elif char.map_x > bg.map_w - char_half[0]:
        return_x = bg.map_w - char_half[0]
    if char.map_y < char_half[1]:
        return_y = char_half[1]
    elif char.map_y > bg.map_h - char_half[1]:
        return_y = bg.map_h - char_half[1]
    return return_x,return_y

def door_update(char,door_list,camera_x,camera_y):
    global game_state
    break_function=False
    for door in door_list:
        door.update(camera_x,camera_y)
        if abs(door.rect.centerx-char.rect.centerx)<char.half_w and\
            abs(door.rect.centery-char.rect.centery)<char.half_h:
            frozen=screen.copy()
            if char.move_state=="up":
                char.map_y+=30
            elif char.move_state=="down":
                char.map_y-=30
            if char.move_state=="left":
                char.map_x+=30
            elif char.move_state=="right":
                char.map_x-=30
            state_pos[game_state]=char.map_x,char.map_y
            char.map_x,char.map_y=state_pos[door.target]
            sence_fade_out(frozen)
            game_state=door.target
            break_function=True
            return break_function

def sence_fade_out(frozen):
    fade_surface = pg.Surface(screen.get_size())
    fade_surface = fade_surface.convert() # 為了更快的 blit 速度
    fade_surface.fill((0, 0, 0)) # 填滿黑色
    for alpha in range(0,86):
        screen.blit(frozen, (0, 0))
        fade_surface.set_alpha(alpha*3)
        screen.blit(fade_surface, (0, 0))
        pg.display.update()

def sence_fade_in(frozen):
    fade_surface = pg.Surface(screen.get_size())
    fade_surface = fade_surface.convert() # 為了更快的 blit 速度
    fade_surface.fill((0, 0, 0)) # 填滿黑色
    for alpha in range(85,-1,-1):
        screen.blit(frozen, (0, 0))
        fade_surface.set_alpha(alpha*3)
        screen.blit(fade_surface, (0, 0))
        pg.display.update()
#----------------------------------------------------------------------------------------------
def vol_update():
    global vol_percent,vol_text,vol_font
    vol_font = pg.font.Font(None, 30)
    vol_percent=float(volume_twist.current_val*100)/0.4
    display_text=f"Volume: {int(vol_percent)}"
    display_surface=vol_font.render(display_text, True, (0, 255, 255))
    screen.blit(display_surface,(w/2-270,h/2-8))
    pg.mixer.music.set_volume(volume_twist.current_val)

#pause init
is_pause=False
def pause_menu(global_bg):
    screen.blit(global_bg,(0,0))
    screen.blit(pause_bg,(0,0))
    pause_sprites.update()
    pause_sprites.draw(screen)
    vol_update()

#main menu init
def main_menu():
    screen.blit(mainMenuBg,(0,0))
    screen.blit(titletext,(100,80))
    screen.blit(titleZHtext,(100,170))
    screen.blit(hint_text,(w-280,h-30))
    main_menu_sprites.update()
    main_menu_sprites.draw(screen)
    #vol_update()

#transition init
transition_counter = 0 # <--轉場計數器
def in_game_transition():
    global transition_counter, game_state
    # 在 transition 狀態下，每一幀執行一次動畫
    if transition_counter < 50: 
        current_scale = 1 + (transition_counter / 30) * 7
        current_angle = transition_counter * 8
        trans_image = pg.transform.rotozoom(sybau_transition, current_angle, current_scale)
        trans_rect = trans_image.get_rect(center=(sybau.rect.centerx, sybau.rect.centery))
        alpha=255-(transition_counter*5)
        trans_image.set_alpha(alpha)
        mainMenuBg.set_alpha(alpha)
        kingnom.image.set_alpha(transition_counter*5)
        screen.blit(inGameBg.image,inGameBg.rect)
        screen.blit(kingnom.image,kingnom.rect)
        screen.blit(mainMenuBg,(0,0))
        screen.blit(trans_image, trans_rect)
        transition_counter += 1
    else:
        game_state = "in_game"
        transition_counter = 0

#in game init
last_map_x=kingnom.map_x
last_map_y=kingnom.map_y
def in_game(pressKeyQueue):
    global kingnom
    global w,h,game_state,play_animation
    global last_map_x,last_map_y
    #in_game_sprites.update()
    last_map_x=kingnom.map_x
    last_map_y=kingnom.map_y
    kingnom.update(pressKeyQueue)
    #2. 邊界判定
    kingnom.map_x,kingnom.map_y=boundary_deter(kingnom,in_game_bg,char_half)

    #2.1 牆壁碰撞
    kingnom.map_x,kingnom.map_y=wall_collision(kingnom,in_game_wall,last_map_x,last_map_y)
            
    # 3. 根據角色的世界座標計算攝影機的理想位置 (目標是讓角色保持在螢幕中央)
    camera_x = kingnom.map_x - w / 2#由 camera_x+w/2=map_x 推導而來
    camera_y = kingnom.map_y - h / 2#由 camera_y+h/2=map_y 推導而來

    #4.1 將攝影機限制在地圖邊界內，避免顯示地圖外的黑色區域
    if camera_x < 0:
        camera_x = 0
    if camera_x > in_game_bg.map_w - w:
        camera_x = in_game_bg.map_w - w
    if camera_y < 0:
        camera_y = 0
    if camera_y > in_game_bg.map_h - h:
        camera_y = in_game_bg.map_h - h
    
    #4.2 需要camera 的物件更新
    for npc in in_game_npc:
        npc.update(camera_x,camera_y)
    for wall in in_game_wall:
        wall.update(camera_x,camera_y) 
    if door_update(kingnom,in_game_door,camera_x,camera_y):return
    '''for door in in_game_door:
        door.update(camera_x,camera_y)
        if abs(door.rect.centerx-kingnom.rect.centerx)<kingnom.half_w and\
            abs(door.rect.centery-kingnom.rect.centery)<kingnom.half_h:
            frozen=screen.copy()
            if kingnom.move_state=="up":
                kingnom.map_y+=30
            elif kingnom.move_state=="down":
                kingnom.map_y-=30
            if kingnom.move_state=="left":
                kingnom.map_x+=30
            elif kingnom.move_state=="right":
                kingnom.map_x-=30
            state_pos[game_state]=kingnom.map_x,kingnom.map_y
            kingnom.map_x,kingnom.map_y=state_pos[door.target]
            sence_fade_out(frozen)
            game_state=door.target
            return'''

    # 5. 根據攝影機的位置，更新地圖的螢幕位置 (地圖的移動方向與攝影機相反)
    in_game_bg.rect.x = -camera_x
    in_game_bg.rect.y = -camera_y
    
    # 6. 根據攝影機位置和角色的世界座標，計算角色在螢幕上的最終位置
    kingnom.rect.centerx = kingnom.map_x - camera_x
    kingnom.rect.centery = kingnom.map_y - camera_y

    #7. draw
    screen.blit(in_game_bg.image,in_game_bg.rect)
    #in_game_sprites.draw(screen)
    if hitler.need_draw:
        screen.blit(hitler.image,hitler.rect)
    for door in in_game_door:
        if door.need_deter and door.visible:
            screen.blit(door.image,door.rect)
    screen.blit(kingnom.image,kingnom.rect)
    for wall in in_game_wall:
        if wall.need_deter and wall.visible:
            screen.blit(wall.image,wall.rect)

    if play_animation:
        draw_sence(in_game_bg,in_game_npc,in_game_door,kingnom,in_game_wall,empty_sprite_group)
        frozen=screen.copy()
        sence_fade_in(frozen)
        play_animation=False

#in ac init
def in_ac(pressKeyQueue):
    global game_state,last_game_state,w,h
    global kingnom
    global play_animation
    
    kingnom.update(pressKeyQueue)
    #2. 邊界判定
    kingnom.map_x,kingnom.map_y=boundary_deter(kingnom,ac_bg,char_half)

    #2.1 牆壁碰撞
    kingnom.map_x,kingnom.map_y=wall_collision(kingnom,in_ac_wall,last_map_x,last_map_y)

     # 3. 根據角色的世界座標計算攝影機的理想位置 (目標是讓角色保持在螢幕中央)
    camera_x = kingnom.map_x - w / 2#由 camera_x+w/2=map_x 推導而來
    camera_y = kingnom.map_y - h / 2#由 camera_y+h/2=map_y 推導而來

    #4.1 將攝影機限制在地圖邊界內，避免顯示地圖外的黑色區域
    if camera_x < 0:
        camera_x = 0
    if camera_x > ac_bg.map_w - w:
        camera_x = ac_bg.map_w - w
    if camera_y < 0:
        camera_y = 0
    if camera_y > ac_bg.map_h - h:
        camera_y = ac_bg.map_h - h

    #4.2
    for wall in in_ac_wall:
        wall.update(camera_x,camera_y) 
    if door_update(kingnom,in_ac_door,camera_x,camera_y):return   

    # 5. 根據攝影機的位置，更新地圖的螢幕位置 (地圖的移動方向與攝影機相反)
    ac_bg.rect.x = -camera_x
    ac_bg.rect.y = -camera_y
    
    # 6. 根據攝影機位置和角色的世界座標，計算角色在螢幕上的最終位置
    kingnom.rect.centerx = kingnom.map_x - camera_x
    kingnom.rect.centery = kingnom.map_y - camera_y

    #draw
    screen.blit(ac_bg.image,ac_bg.rect)
    for door in in_ac_door:
        if door.need_deter and door.visible:
            screen.blit(door.image,door.rect)
    screen.blit(kingnom.image,kingnom.rect)
    for wall in in_ac_wall:
        if wall.need_deter and wall.visible:
            screen.blit(wall.image,wall.rect)

    if play_animation:
        draw_sence(ac_bg,empty_array,in_ac_door,kingnom,in_ac_wall,empty_sprite_group)
        frozen=screen.copy()
        sence_fade_in(frozen)
        play_animation=False

#main loop
running=True
game_state = "in_game" # "main_menu", "transition", "in_game", "pause_menu"
last_game_state=""
fps=45

# game loop
running=True
while running:
    clock.tick(fps)
    #screen.blit(bg,(0,0))
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
        #偵測暫停
        if event.type==pg.KEYDOWN:
            if event.key==pg.K_ESCAPE:
                if not is_pause:
                    frozen=screen.copy()
                
                is_pause = not is_pause

                if not game_state=="pause_menu":
                    last_pause_state=game_state
                if is_pause:  
                    game_state="pause_menu"
                elif not is_pause:
                    game_state=last_pause_state
        # 偵測按鍵事件，並更新按鍵列表
        if event.type == pg.KEYDOWN:
            # 確保同一個鍵不會被重複加入
            if event.key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
                if event.key not in pressKeyQueue:
                    pressKeyQueue.append(event.key)

        if event.type == pg.KEYUP:
            if event.key in pressKeyQueue:
                pressKeyQueue.remove(event.key)
    
    if pause_back.ispress:
        is_pause=False
        game_state=last_pause_state
        pause_back.ispress=False

    play_animation=False
    if last_game_state!=game_state and\
        last_game_state!="pause_menu":
        play_animation=True
    last_game_state=game_state
    match game_state:
        case "pause_menu":
            pause_menu(frozen)
        case "main_menu":
            main_menu()
            if sybau.ispress:
                game_state = "transition" 
                sybau.ispress = False
        case "transition":
            in_game_transition()
        case "in_game":
            in_game(pressKeyQueue)
        case "in_ac":
            in_ac(pressKeyQueue)
        case _:
            pass

    if pause_exit.ispress:
        running = False 
    pg.display.update()
pg.quit()