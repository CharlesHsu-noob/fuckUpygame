import pygame as pg
import math,random
import os
import picture_dictionary as pd
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
if __name__ == '__main__':
    w=1200
    h=700
    pg.init()
    screen = pg.display.set_mode((w,h))
    pg.display.set_caption('Undyne Fight')
    clock = pg.time.Clock()
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill((0,0,0))
        pg.display.flip()
        clock.tick(60)
    pg.quit()

class oiiai(pg.sprite.Sprite):
    def __init__(self,game) -> None:
        super().__init__()
        size=(100,100)
        self.image=pg.transform.scale(pg.image.load(os.path.join(base_dir,"picture","undyne","oiiai_stand.png")),size)
        self.rect=self.image.get_rect(center=(game.w/2,game.h/2))
        self.can_interact=False
    def update(self,game):
        self.can_interact=False
        if pg.sprite.collide_rect(game.kingnom,self):
            self.can_interact=True
        if self.can_interact and game.InteractKeyQueue:
            key=game.InteractKeyQueue[-1]
            if key==pg.K_f:
                game.game_state="undyne_transition"
    def draw(self,game):
        game.screen.blit(self.image,self.rect)

class heart(pg.sprite.Sprite):
    def __init__(self,picture_paths,game) -> None:
        super().__init__()
        size=(25,25)
        self.images=[]
        for path in picture_paths:
            self.images.append(pg.transform.scale(pg.image.load(path).convert_alpha(),size))
        self.image=self.images[0]
        self.rect=self.image.get_rect(center=(game.w/2,game.h/2))

         # --- 閃爍控制 ---
        self.is_flashing = False   # 是否正在閃爍
        self.flash_timer = 0       # 閃爍計時器 (總共要閃爍多少幀)
        self.flash_interval = 3    # 閃爍間隔 (每 x 幀切換一次顯示/隱藏)
        self.invincible = False    # 是否處於無敵狀態
    def update(self):
        # --- 處理閃爍計時器 ---
        if self.is_flashing:
            self.flash_timer -= 1
            
            if self.flash_timer <= 0:
                self.is_flashing = False # 閃爍結束
                self.invincible = False  # 關閉無敵
    def take_damage(self,game,damage):
        if not self.invincible:
            #self.health -= damage
            # 啟動閃爍 
            self.flash_timer = game.fps*0.5
            self.is_flashing = True
            self.invincible = True # 開啟無敵，直到閃爍結束
    
    def draw(self, game):
        # 1. 計算是否應該繪製
        should_draw = True
        
        if self.is_flashing:
            # 當前計時器的值對 (flash_interval * 2) 取餘數
            # 如果餘數小於 flash_interval，則隱藏 (不繪製)
            # 例如： flash_interval=5，總週期是 10 幀。0-4 幀繪製，5-9 幀隱藏。
            if (self.flash_timer % (self.flash_interval * 2)) < self.flash_interval:
                should_draw = False

        # 2. 執行繪製
        if should_draw:   
            game.screen.blit(self.image,self.rect)
    '''def draw(self, game):
        if self.is_flashing:
            # 檢查是否應該跳過繪製
            if (self.flash_timer % (self.flash_interval * 2)) < self.flash_interval:
                return # <--- 如果正在閃爍且處於隱藏幀，直接退出 draw 函式
                
        # 如果沒有閃爍，或閃爍中處於顯示幀，則執行正常的繪製
        game.screen.blit(self.image, self.rect)'''

class shield(pg.sprite.Sprite):
    def __init__(self,picture_paths,game) -> None:
        super().__init__()
        size=(80,12)
        self.images=[]
        for path in picture_paths:
            self.images.append(
                pg.transform.scale(
                    pg.image.load(path).convert_alpha(),size))
        self.image=self.images[0]
        self.rect=self.image.get_rect(center=(game.w/2,game.h/2))
        self.target_deg=270
        self.current_deg=270
        self.counter=0
        self.r=30
        self.rotation_speed=40
    def update(self,game):
        self.last_deg=self.target_deg
        if not game.MoveKeyQueue:
            return
        if game.MoveKeyQueue[-1]==pg.K_w:
            self.target_deg=270
        elif game.MoveKeyQueue[-1]==pg.K_s:
            self.target_deg=90
        elif game.MoveKeyQueue[-1]==pg.K_d:
            self.target_deg=0
        elif game.MoveKeyQueue[-1]==pg.K_a:
            self.target_deg=180
        else:
            return

    def _smooth_rotate(self):
        # 計算當前角度和目標角度之間最短的路徑差值
        delta_deg = self.target_deg - self.current_deg
        
        # 處理循環：確保旋轉不會繞遠路 (例如從 10度到 350度，應該逆時針轉 20度，而不是順時針轉 340度)
        if delta_deg > 180:
            delta_deg -= 360
        elif delta_deg < -180:
            delta_deg += 360

        if abs(delta_deg) < self.rotation_speed:
            self.current_deg = self.target_deg# 角度差小於速度，直接到達目標
        elif delta_deg > 0:
            self.current_deg += self.rotation_speed# 順時針(Pygame正)
        else:
            self.current_deg -=self.rotation_speed# 逆時針(Pygame負)
        # 5. 校正 current_deg，確保它維持在 0 到 360 之間
        self.current_deg %= 360

    def draw(self,game):
        self._smooth_rotate()
        out_image = pg.transform.rotate(self.image,-self.current_deg+90)
        rad = math.radians(self.current_deg)
        self.x = game.w / 2 + math.cos(rad) * self.r
        self.y = game.h / 2 + math.sin(rad) * self.r
        #self.mask = pg.mask.from_surface(out_image)
        rect = out_image.get_rect(center=(self.x, self.y))
        self.rect=rect
        game.screen.blit(out_image, rect)

    def flash(self,game,flash):
        if flash:
            self.image=self.images[1]
        if game.shield_tick%12==0:
            self.image=self.images[0]
            game.shield_tick=0
        
class arrow(pg.sprite.Sprite):
    def __init__(self,picture_paths,game) -> None:
        super().__init__()
        size=(30,20)
        self.images=[]
        for path in picture_paths:
            self.images.append(
                pg.transform.scale(
                    pg.image.load(os.path.join(path)).convert_alpha(),size))
        type=["normal","special"]
        angle=[0,90,180,270]#箭頭方向  0:向右  90:向上  180:向左  270:向下
        #where_apper=["left","bottom","right","top"]#從哪裡出現
        where_apper_pos=[(0,game.h/2),
                         (game.w/2,game.h),
                         (game.w,game.h/2),
                         (game.w/2,0)]
        #下面的變數每個物件都不一樣
        self.angle=angle[random.randint(0,3)]
        self.type_index=int(self.angle/90)
        #self.where_apper=where_apper[self.type_index]

        for i in range(0,3):
            self.images[i]=pg.transform.rotate(self.images[i],self.angle)
        self.image=self.images[0]#預設向右(從左邊出現)
        self.type=type[0]
        if self.type==type[1]:
            self.image=self.images[2]
        self.mask = pg.mask.from_surface(self.image)
        self.rect=self.image.get_rect(center=where_apper_pos[self.type_index])

        self.v=random.randint(2,7)
        if self.type_index==0 or self.type_index==2:
            self.arrive_tick=(game.w/2)/self.v
        else:
            self.arrive_tick=(game.h/2)/self.v
        game.bullet_counter+=1
    def update(self,game) -> tuple[int,int,bool,bool]:#damage,arrive_tick,shield_flash,heart_flash
        dx=[self.v,0,-self.v,0]
        dy=[0,-self.v,0,self.v]

        self.rect.centerx+=dx[self.type_index]
        self.rect.centery+=dy[self.type_index]
        self.arrive_tick-=1
        if pg.sprite.collide_rect(game.shield,self):
            game.arrow_hit_shield.play()
            game.bullet_counter-=1
            self.kill()
            return 0,self.arrive_tick,True,False 
        elif pg.sprite.collide_mask(game.heart,self):
            #放音效
            game.bullet_counter-=1
            self.kill()
            return 1,self.arrive_tick,False,True
        else:return 0,self.arrive_tick,False,False

#AI
def draw_pixel_circle(screen, color, center, radius, line_lenth,scale_factor=5):
    """
    在主螢幕上繪製一個空心、像素化的圓形框框。

    參數:
    screen: 主 Surface
    color: 圓形的顏色 (R, G, B)
    center: 圓形框框的中心座標 (x, y)
    radius: 低解析度 Surface 上的圓形半徑 (決定圓形的基本大小)
    border_width: 低解析度 Surface 上的邊框像素寬度 (決定線條粗細)
    scale_factor: 放大倍數 (決定顆粒感的大小)
    """
    
    # 1. 計算低解析度 Surface 的尺寸
    # 尺寸需要比半徑大一點，以避免邊框被截斷
    low_res_size = (radius * 2 + line_lenth * 2, radius * 2 + line_lenth * 2)
    
    # 2. 創建一個小的 Surface
    low_res_surf = pg.Surface(low_res_size, pg.SRCALPHA)
    low_res_center = (low_res_size[0] // 2, low_res_size[1] // 2)

    # 3. 在低解析度 Surface 上繪製空心圓
    # 參數：(Surface, Color, Center, Radius, Width)
    pg.draw.circle(
        low_res_surf, 
        color, 
        low_res_center, 
        radius, 
        line_lenth
    )
    
    # 4. 放大 Surface (使用 Nearest Neighbor 實現顆粒感)
    target_size = (low_res_size[0] * scale_factor, low_res_size[1] * scale_factor)
    pixel_image = pg.transform.scale(low_res_surf, target_size)
    
    # 5. 繪製到主螢幕
    rect = pixel_image.get_rect(center=center)
    screen.blit(pixel_image, rect)

def setup(game):
    game.shield=shield(pd.shield_paths,game)
    game.oiiai=oiiai(game)
    game.in_ma_u_npc.append(game.oiiai)
    game.heart=heart(pd.heart_paths,game)
    game.undyne_bg=pg.Surface(game.screen.get_size())
    game.undyne_bg=game.undyne_bg.convert()
    game.undyne_bg.fill((0,0,0)) # black
    game.line_lenth=3
    game.bullet=pg.sprite.Group()

def transition(game):
    fade_surface=pg.Surface(game.screen.get_size())
    fade_surface=fade_surface.convert()
    fade_surface.fill((0,0,0))
    game.heart.rect=game.kingnom.rect
    for i in range(0,86):
        t = i / 85
        x = game.heart.rect.centerx*(1-t) + (game.w/2)*t
        y = game.heart.rect.centery*(1-t) + (game.h/2)*t

        fade_surface.set_alpha(i*3)
        game.heart.image.set_alpha(i*3)
        game.screen.blit(fade_surface,(0,0))

        heart_blit_rect = game.heart.image.get_rect(center=(x, y))
        game.screen.blit(game.heart.image, heart_blit_rect)
        
        pg.display.update()
        pg.time.delay(10)
    game.heart.rect=heart_blit_rect
    game.game_state="undyne_fight"

def fight_shield_update(game):
    game.screen.fill((0,0,0))
    pg.draw.rect(
        game.screen,
        (150,150,150),
        (game.w/2-50,game.h/2-50,100,100),
        game.line_lenth+2
    )
    draw_pixel_circle(
        game.screen,
        (11,160,16),
        (game.w/2,game.h/2),
        18.5,
        1,
        2
    )
    game.shield.update(game)

def fight_bullet_update(game):
    if game.buttle_tick>=game.create_bullet_tick:
        game.buttle_tick=0
        game.create_bullet_tick=random.randint(30,90)
        if game.bullet_counter<=8:
            game.bullet.add(arrow(pd.arrow_paths,game))

    bullet_color=[]
    shield_flash=False
    heart_flash=False
    for bullet in game.bullet.sprites():
        damage,temp,shield_flash,heart_flash=bullet.update(game)
        bullet_color.append(temp)
        game.shield.flash(game,shield_flash)
        if heart_flash:
            game.heart.take_damage(game,damage)

    if bullet_color: 
        min_bullet = min(bullet_color)
    
    for bullet in game.bullet.sprites():
        bullet.image=bullet.images[0]
        if bullet.arrive_tick==min_bullet:
            bullet.image=bullet.images[1]
    
    game.heart.update()

    game.heart.draw(game)
    game.shield.draw(game)
    game.bullet.draw(game.screen)
    game.buttle_tick+=1
    if game.shield_tick>=12:
        game.shield_tick=0
    game.shield_tick+=1