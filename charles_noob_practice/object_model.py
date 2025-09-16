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
#map_sprites = pg.sprite.Group()

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
        is_mouse_over = self.rect.collidepoint(mouse_pos)

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
        if self.move_index >= len(self.moves) * 2:
            self.move_index=0
        
        if not self.is_move:
            self.image=pg.transform.flip(self.images[0],self.flipx,self.flipy)
            self.move_index = 0
        else:
            self.image=pg.transform.flip(self.moves[self.move_index // 2],self.flipx,self.flipy)
            self.move_index+=1
        self.distant=[dx,dy]

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

mrbeast=moveObject(os.path.join(base_dir, "picture", "MrBeast.png"),(300,550),(200,130),7,False)
main_menu_sprites.add(mrbeast)
milk=moveObject(os.path.join(base_dir, "picture", "milkdragon.png"),(random.randint(100,250),random.randint(150,250)),(130,170),8,True)
main_menu_sprites.add(milk)

sybau_paths=[os.path.join(base_dir, "picture", "sybau", "sybau1.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau2.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau3.png")]
sybau=buttonObject(sybau_paths,(200,325),(200,200))
main_menu_sprites.add(sybau)
exit_paths=[os.path.join(base_dir, "picture", "exit", "exit1.png"),
            os.path.join(base_dir, "picture", "exit", "exit2.png"),
            os.path.join(base_dir, "picture", "exit", "exit3.png")]
exit=buttonObject(exit_paths,(w-60,h-30),(105,45))
main_menu_sprites.add(exit)
in_game_sprites.add(exit)
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
kingnom.map_x=4160/2
kingnom.map_y=3760/2

defaultvol=0.2
volume_rail=sliderRailObject(os.path.join(base_dir, "picture", "sound_slider", "slider_rail.png"),(w-300,h-30),(300,10))
volume_twist=sliderTwistObject(os.path.join(base_dir, "picture", "sound_slider", "slider_twist.png"),(w-300,h-30),(10,27),0,0.4,defaultvol,volume_rail)
main_menu_sprites.add(volume_rail)
main_menu_sprites.add(volume_twist)
in_game_sprites.add(volume_rail)
in_game_sprites.add(volume_twist)

title=pg.font.Font(os.path.join(base_dir, "font", "Sacramento-Regular.ttf"), 65)
titletext=title.render("KINGNOM's big adventure",True,(0,200,200))
titleZH=pg.font.Font(os.path.join(base_dir, "font", "bpm", "BpmfZihiSerif-Regular.ttf"),40)
titleZHtext=titleZH.render("金農的大冒險",True,(255,200,200))
volvalue=0
vol_value=pg.font.SysFont("times new roman",20)
vol_valuetext=vol_value.render(str(volvalue),True,(255,255,255))

main_menu_bg_or=pg.image.load(os.path.join(base_dir, "picture", "back_ground", "main_menu_bg.png"))
main_menu_bg_or.convert()
mainMenuBg=pg.transform.scale(main_menu_bg_or.convert_alpha(),(w,h))
pg.mixer.music.load(os.path.join(base_dir, "voice", "soundtrack", "red_sun_in_the_sky.wav"))#mainMenuBgm
defaultvol=0.2
pg.mixer.music.set_volume(defaultvol)
pg.mixer.music.play(loops=-1, fade_ms=1500)
def main_menu():
    screen.blit(mainMenuBg,(0,0))
    screen.blit(titletext,(100,100))
    screen.blit(titleZHtext,(100,170))
    main_menu_sprites.update()
    main_menu_sprites.draw(screen)
    volvalue=float(volume_twist.current_val*100)/0.4
    vol_valuetext=vol_value.render(str(int(volvalue)),True,(255,255,255))
    screen.blit(vol_valuetext,(w-490,h-40))
    pg.mixer.music.set_volume(volume_twist.current_val)


inGameBg=mapObject(os.path.join(base_dir, "picture", "back_ground", "map2.png"),(w/2,h/2),(4160,3760))
def in_game(pressKeyQueue):
    #screen.blit(inGameBg.image,inGameBg.rect)
    in_game_sprites.update()
    kingnom.update(pressKeyQueue)
    #AI
    #2. 將角色的世界座標限制在地圖範圍內
    map_width, map_height = inGameBg.rect.width, inGameBg.rect.height
    char_half_w = kingnom.rect.width / 2
    char_half_h = kingnom.rect.height / 2
    
    if kingnom.map_x < char_half_w:
        kingnom.map_x = char_half_w
    if kingnom.map_x > map_width - char_half_w:
        kingnom.map_x = map_width - char_half_w
    if kingnom.map_y < char_half_h:
        kingnom.map_y = char_half_h
    if kingnom.map_y > map_height - char_half_h:
        kingnom.map_y = map_height - char_half_h

    # 3. 根據角色的世界座標計算攝影機的理想位置 (目標是讓角色保持在螢幕中央)
    camera_x = kingnom.map_x - w / 2
    camera_y = kingnom.map_y - h / 2

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
    screen.blit(inGameBg.image,inGameBg.rect)
    in_game_sprites.draw(screen)
    screen.blit(kingnom.image,kingnom.rect)
    pg.mixer.music.set_volume(volume_twist.current_val)

#main loop
running=True
game_state = "main_menu"
transition_counter = 0 # <--- 新增轉場計數器

# game loop
running=True
while running:
    clock.tick(30)
    #screen.blit(bg,(0,0))
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
         # 偵測按鍵事件，並更新按鍵列表
        if event.type == pg.KEYDOWN:
            # 確保同一個鍵不會被重複加入
            if event.key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
                if event.key not in pressKeyQueue:
                    pressKeyQueue.append(event.key)

        if event.type == pg.KEYUP:
            if event.key in pressKeyQueue:
                pressKeyQueue.remove(event.key)
    
    if game_state == "main_menu":
        main_menu()
        if sybau.ispress:
            game_state = "transition" 
            sybau.ispress = False 

    elif game_state == "transition":
        # 在 transition 狀態下，每一幀執行一次動畫
        if transition_counter < 50: 
            current_scale = 1 + (transition_counter / 30) * 7
            current_angle = transition_counter * 8
            new_image = pg.transform.rotozoom(sybau_transition, current_angle, current_scale)
            new_rect = new_image.get_rect(center=(sybau.rect.centerx, sybau.rect.centery))
            alpha=255-(transition_counter*5)
            new_image.set_alpha(alpha)
            mainMenuBg.set_alpha(alpha)
            kingnom.image.set_alpha(transition_counter*5)
            screen.blit(inGameBg.image,inGameBg.rect)
            screen.blit(kingnom.image,kingnom.rect)
            screen.blit(mainMenuBg,(0,0))
            screen.blit(new_image, new_rect)
            transition_counter += 1
        else:
            game_state = "in_game"
            transition_counter = 0

    elif game_state == "in_game":
        in_game(pressKeyQueue)
    
    if exit.ispress:
        running = False 
    pg.display.update()
pg.quit()