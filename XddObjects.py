import pygame as pg
import random,math,os
# --- 為了跨平台相容性而進行的路徑設定 ---
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)

#init
#screeninfo=pg.display.Info()
#w,h=screeninfo.current_w,screeninfo.current_h-80
#screen = pg.display.set_mode((w,h))

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
        mouse_pos = pg.mouse.get_pos()
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
        self.screen_x=w/2
        self.screen_y=h/2
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
    def update(self,pressKeyQueue):
        self.move_character=False
        #akey_ispress=False
        self.is_move=False
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
    def __init__(self,picture_paths,center,size):
        super().__init__()
        self.images = []
        for path in picture_paths:
            self.images.append(pg.transform.scale(
                pg.image.load(
                    os.path.join(path)
                    ).convert_alpha(),size))
        self.image=self.images[0]
        #self.rect=self.image.get_rect(center=center)
        self.map_x,self.map_y=center
        self.image_w=self.image.get_width()
        self.image_h=self.image.get_height()
        self.mask=pg.mask.from_surface(self.image)
        self.need_deter=False
    def update(self,camera_x,camera_y):
        self.need_deter=False#需要判定=false
        #和npc一樣的判斷邏輯
        if self.map_x-camera_x<=w+self.image_w/2 and self.map_y-camera_y<=h+self.image_h/2\
            and self.map_x-camera_x>=0-self.image_w/2 and self.map_y-camera_y>=0-self.image_h/2:
            self.need_deter=True
            self.rect=self.image.get_rect(center=(self.map_x-camera_x,self.map_y-camera_y))