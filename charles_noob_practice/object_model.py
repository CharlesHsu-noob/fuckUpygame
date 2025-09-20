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
in_game_sprites = pg.sprite.Group()
in_game_special=[]
pause_sprites = pg.sprite.Group()
#map_sprites = pg.sprite.Group()

def collision_by_mask_with_mouse(image,rect):
    mouse_pos = pg.mouse.get_pos()
    mask=pg.mask.from_surface(image)
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
            pass

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
        self._is_held=False# 內部狀態：追蹤滑鼠是否正按在按鈕上
        self.ispress=False
        self.images = [
            pg.transform.scale(pg.image.load(picture_paths[0]).convert_alpha(), size),
            pg.transform.scale(pg.image.load(picture_paths[1]).convert_alpha(), size),
            pg.transform.scale(pg.image.load(picture_paths[2]).convert_alpha(), size)
        ]
        self.image=self.images[0]
        self.rect=self.image.get_rect(center=center)
    def update(self):
        self.ispress = False
        mouse_pos = pg.mouse.get_pos()
        mouse_down = pg.mouse.get_pressed()[0]
        #is_mouse_over = self.rect.collidepoint(mouse_pos)
        is_mouse_over=collision_by_mask_with_mouse(self.image,self.rect)

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
    def __init__(self,picture_path,center,size):
        super().__init__()
        load_image=pg.image.load(picture_path).convert_alpha()
        self.image=pg.transform.scale(load_image,size)
        self.rect=self.image.get_rect(center=center)
        self.minx=self.rect.left
        self.maxx=self.rect.right

class sliderTwistObject(pg.sprite.Sprite):
    def __init__(self,picture_path,center,size,min_val,max_val,default_val,rail):
        super().__init__()
        self.rail=rail
        self.min_val=min_val
        self.max_val=max_val
        self.current_val=default_val
        #self.isdrag=False
        self.last_press=False
        self.image=pg.transform.scale(pg.image.load(picture_path).convert_alpha(), size)
        self.rect=self.image.get_rect(center=center)
    def update(self):
        minx=self.rail.minx
        maxx=self.rail.maxx
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        '''if mouse_pressed:
            self.last_press=True
        else:
            self.last_press=False
        #isdrag logic:True
        if self.rect.collidepoint(mouse_pos) and mouse_pressed:
            self.isdrag=True
            self.last_press=True
        elif not self.rect.collidepoint(mouse_pos) and self.last_press and mouse_pressed:
            self.isdrag=True
        #isdrag logic:False
        if self.rect.collidepoint(mouse_pos) and not self.last_press and not mouse_pressed:
            self.isdrag=False
        elif not self.rect.collidepoint(mouse_pos) and not self.last_press:
            self.isdrag=False
            if mouse_pressed:
                self.last_press=True'''
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
            self.current_val=self.min_val+(self.max_val-self.min_val)*(self.rect.centerx-minx)/(maxx-minx)

class characterObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,move_paths,default_center,size):
        super().__init__()
        self.map_x=0
        self.map_y=0
        self.screen_x=w/2
        self.screen_y=h/2
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
        self.v=10
        self.rect=self.image.get_rect(center=default_center)
        self.is_move=False
    def update(self,pressKeyQueue):
        self.move_character=False
        #akey_ispress=False
        self.is_move=False
        dx=0
        dy=0
        # 如果列表中有按鍵，就處理最新按下的那個
        if pressKeyQueue:
            latest_key = pressKeyQueue[-1] # 獲取列表最後一個元素
            
            if latest_key == pg.K_w:
                self.map_y-=self.v
                dy = -self.v
                self.is_move = True
                self.flipy = 1
            elif latest_key == pg.K_s:
                self.map_y+=self.v
                dy = self.v
                self.is_move = True
                self.flipy = 0
            elif latest_key == pg.K_a:
                self.map_x-=self.v
                dx = -self.v
                self.is_move = True
                self.flipx = 0
            elif latest_key == pg.K_d:
                self.map_x+=self.v
                dx = self.v
                self.is_move = True
                self.flipx = 1
        if self.move_index >= len(self.moves) * 7:
            self.move_index=0
        
        if not self.is_move:
            self.image=pg.transform.flip(self.images[0],self.flipx,self.flipy)
            self.move_index = 0
        else:
            if self.move_index //4==0 or self.move_index//4==1:
                real_index=0
            elif self.move_index //4==2 or self.move_index//4==3:
                real_index=1
            self.image=pg.transform.flip(self.moves[real_index],self.flipx,self.flipy)
            self.move_index+=1
        self.distant=[dx,dy]

class npcObject(pg.sprite.Sprite):
    def __init__(self,picture_paths,center,size):
        super().__init__()
        self.images = []
        for i in picture_paths:
            self.images.append(pg.transform.scale(pg.image.load(i).convert_alpha(),size))
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
        self.image=pg.transform.scale(pg.image.load(picture_path).convert_alpha(),size)
        self.rect=self.image.get_rect(center=center)
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
    def __init__(self,picture_path,center,size):
        super().__init__()
        self.image=pg.transform.scale(pg.image.load(picture_path[0]).convert_alpha(),size)
        #self.rect=self.image.get_rect(center=center)
        self.map_x,self.map_y=center
        self.image_w=self.image.get_width()
        self.image_h=self.image.get_height()
    def update(self,camera_x,camera_y):
        self.need_deter=False#需要判定=false
        #和npc一樣的判斷邏輯
        if self.map_x-camera_x<=w+self.image_w/2 and self.map_y-camera_y<=h+self.image_h/2\
            and self.map_x-camera_x>=0-self.image_w/2 and self.map_y-camera_y>=0-self.image_h/2:
            self.need_deter=True
            self.rect=self.image.get_rect(center=(self.map_x-camera_x,self.map_y-camera_y))

mrbeast=moveObject(os.path.join(base_dir, "picture", "MrBeast.png"),(300,550),(200,130),7,False)
main_menu_sprites.add(mrbeast)
milk=moveObject(os.path.join(base_dir, "picture", "milkdragon.png"),(random.randint(100,250),random.randint(150,250)),(130,170),8,True)
main_menu_sprites.add(milk)

sybau_paths=[os.path.join(base_dir, "picture", "sybau", "sybau1.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau2.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau3.png")]

exit_paths=[os.path.join(base_dir, "picture", "exit", "exit1.png"),
            os.path.join(base_dir, "picture", "exit", "exit2.png"),
            os.path.join(base_dir, "picture", "exit", "exit3.png")]

back_paths=[os.path.join(base_dir, "picture", "return", "return1.png"),
            os.path.join(base_dir, "picture", "return", "return2.png"),
            os.path.join(base_dir, "picture", "return", "return3.png")]

transition_omega=2
transition_d_scale=0.1
sybau_transition=pg.image.load(os.path.join(base_dir, "picture", "sybau", "sybau3.png")).convert_alpha()
sybau_transition=pg.transform.scale(sybau_transition,(200,200))

kingnom_paths=[os.path.join(base_dir, "picture", "kingnom", "kingnom_stand1.png"),
             os.path.join(base_dir, "picture", "kingnom", "kingnom_stand2.png")]
kingnom_move_paths=[
    os.path.join(base_dir, "picture", "kingnom", "kingnom_move1.png"),
    os.path.join(base_dir, "picture", "kingnom", "kingnom_move2.png")
]
kingnom=characterObject(kingnom_paths,kingnom_move_paths,(w/2,h/2),(110,125))
#in_game_sprites.add(kingnom)
kingnom.map_x=4160/2#2080
kingnom.map_y=3760/2#1880

hitler_paths=[os.path.join(base_dir,"picture","hitler","hitler1.png")]
hitler=npcObject(hitler_paths,(300,1880),(200,145))
in_game_special.append(hitler)

barrier1_path=[os.path.join(base_dir,"picture","barrier","barrier_wall.png")]
barrier1=wallObject(barrier1_path,(250,1880),(40,220))
in_game_special.append(barrier1)

defaultvol=0.2
volume_rail=sliderRailObject(os.path.join(base_dir, "picture", "sound_slider", "slider_rail.png"),(w/2,h/2),(300,10))
volume_twist=sliderTwistObject(os.path.join(base_dir, "picture", "sound_slider", "slider_twist.png"),(w/2,h/2),(10,27),0,0.4,defaultvol,volume_rail)
pause_sprites.add(volume_rail)
pause_sprites.add(volume_twist)

#music init
main_menu_bg_or=pg.image.load(os.path.join(base_dir, "picture", "back_ground", "main_menu_bg.png"))
main_menu_bg_or.convert()
mainMenuBg=pg.transform.scale(main_menu_bg_or.convert_alpha(),(w,h))
pg.mixer.music.load(os.path.join(base_dir, "voice", "soundtrack", "red_sun_in_the_sky.wav"))#mainMenuBgm
defaultvol=0.2
pg.mixer.music.set_volume(defaultvol)
pg.mixer.music.play(loops=-1, fade_ms=1500)

#sound value text init
vol_percent=0
vol_font=pg.font.SysFont("times new roman",20)
vol_text=vol_font.render(str(vol_percent),True,(255,255,255))
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
pause_bg_or=pg.image.load(os.path.join(base_dir,"picture","back_ground","president_mao.png")).convert_alpha()
pause_bg=pg.transform.scale(pause_bg_or,(w,h))
pause_bg_alpha=100
pause_bg.set_alpha(pause_bg_alpha)
pause_exit=buttonObject(exit_paths,(w/2,h-200),(105,45))
pause_sprites.add(pause_exit)
pause_back=buttonObject(back_paths,center=(w/2-100,h-200),size=(150,150))
pause_sprites.add(pause_back)
def pause_menu(global_bg):
    screen.blit(global_bg,(0,0))
    screen.blit(pause_bg,(0,0))
    pause_sprites.update()
    pause_sprites.draw(screen)
    vol_update()

#main menu text init
title=pg.font.Font(os.path.join(base_dir, "font", "LavishlyYours-Regular.ttf"), 65)
titletext=title.render("KINGNOM's big adventure",True,(0,200,200))
titleZH=pg.font.Font(os.path.join(base_dir, "font", "bpm", "BpmfZihiSerif-Regular.ttf"),40)
titleZHtext=titleZH.render("金農的大冒險",True,(255,200,200))
hint=pg.font.Font(os.path.join(base_dir,"font","bpm","BpmfZihiSerif-Light.ttf"),20)
hint_text=hint.render("點擊ESC鍵以暫停遊戲",True,(255,220,100))

sybau=buttonObject(sybau_paths,(200,325),(200,200))
main_menu_sprites.add(sybau)
def main_menu():
    screen.blit(mainMenuBg,(0,0))
    screen.blit(titletext,(100,80))
    screen.blit(titleZHtext,(100,170))
    screen.blit(hint_text,(w-280,h-30))
    main_menu_sprites.update()
    main_menu_sprites.draw(screen)
    #vol_update()

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

inGameBg=mapObject(os.path.join(base_dir, "picture", "back_ground", "map2.png"),(w/2,h/2),(4160,3760))
map_width, map_height = inGameBg.rect.width, inGameBg.rect.height
char_half_w = kingnom.rect.width / 2
char_half_h = kingnom.rect.height / 2
def in_game(pressKeyQueue):
    global w,h
    global map_width, map_height, char_half_w, char_half_h
    #screen.blit(inGameBg.image,inGameBg.rect)
    in_game_sprites.update()
    kingnom.update(pressKeyQueue)
    #AI
    #2. 將角色的世界座標限制在地圖範圍內
    if kingnom.map_x < char_half_w:
        kingnom.map_x = char_half_w
    if kingnom.map_x > map_width - char_half_w:
        kingnom.map_x = map_width - char_half_w
    if kingnom.map_y < char_half_h:
        kingnom.map_y = char_half_h
    if kingnom.map_y > map_height - char_half_h:
        kingnom.map_y = map_height - char_half_h

    # 3. 根據角色的世界座標計算攝影機的理想位置 (目標是讓角色保持在螢幕中央)
    camera_x = kingnom.map_x - w / 2#由 camera_x+w/2=map_x 推導而來
    camera_y = kingnom.map_y - h / 2#由 camera_y+h/2=map_y 推導而來

    # 4. 將攝影機限制在地圖邊界內，避免顯示地圖外的黑色區域
    if camera_x < 0:
        camera_x = 0
    if camera_x > map_width - w:
        camera_x = map_width - w
    if camera_y < 0:
        camera_y = 0
    if camera_y > map_height - h:
        camera_y = map_height - h

    # 5. 根據攝影機的位置，更新地圖的螢幕位置 (地圖的移動方向與攝影機相反)
    inGameBg.rect.x = -camera_x
    inGameBg.rect.y = -camera_y
    
    # 6. 根據攝影機位置和角色的世界座標，計算角色在螢幕上的最終位置
    kingnom.rect.centerx = kingnom.map_x - camera_x
    kingnom.rect.centery = kingnom.map_y - camera_y
    #AI
    for k in in_game_special:
        k.update(camera_x,camera_y)
    #hitler.update(camera_x,camera_y)
    #barrier1.update(camera_x,camera_y)

    screen.blit(inGameBg.image,inGameBg.rect)
    in_game_sprites.draw(screen)
    if hitler.need_draw:
        screen.blit(hitler.image,hitler.rect)
    screen.blit(kingnom.image,kingnom.rect)
    if barrier1.need_deter:
        screen.blit(barrier1.image,barrier1.rect)
    #vol_update()

#main loop
running=True
game_state = "main_menu"
last_state=""

# game loop
running=True
while running:
    clock.tick(30)
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
                    last_state=game_state
                if is_pause:  
                    game_state="pause_menu"
                elif not is_pause:
                    game_state=last_state
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
        game_state=last_state
        pause_back.ispress=False

    if game_state=="pause_menu":
        pause_menu(frozen)
    elif game_state == "main_menu":
        main_menu()
        if sybau.ispress:
            game_state = "transition" 
            sybau.ispress = False 
    elif game_state == "transition":
        in_game_transition()
    elif game_state == "in_game":
        in_game(pressKeyQueue)
    if pause_exit.ispress:
        running = False 
    pg.display.update()
pg.quit()