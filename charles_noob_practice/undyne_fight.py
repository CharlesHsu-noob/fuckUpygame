import pygame as pg
import math,random
import os
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
        size=(100,100)
        self.image=pg.transform.scale(pg.image.load(os.path.join(base_dir,"picture","undyne","oiiai_stand.png")),size)
        self.rect=self.image.get_rect(center=(game.w/2,game.h/2))
        self.can_interact=False
    def update(self,game):
        self.can_interact=False
        if pg.sprite.collide_rect(game.kingnom,self):
            self.can_interact=True
        if self.can_interact and game.pressKeyQueue:
            key=game.pressKeyQueue[-1]
            if key==pg.K_f:
                game.game_state="undyne_transition"
    def draw(self,game):
        game.screen.blit(self.image,self.rect)

class heart(pg.sprite.Sprite):
    def __init__(self,game) -> None:
        self.image=pg.image.load(os.path.join(base_dir,"picture","undyne","heart.png"))
        self.image=pg.transform.scale(self.image,(25,25))
        self.rect=self.image.get_rect(center=(game.w/2,game.h/2))
    def update(self,game):
        pass

class shield(pg.sprite.Sprite):
    def __init__(self,game) -> None:
        size=(80,12)
        self.image=pg.transform.scale(pg.image.load(os.path.join(base_dir,"picture","undyne","shield.png")).convert_alpha(),size)
        self.rect=self.image.get_rect(center=(game.w/2,game.h/2))
        self.target_deg=270
        self.current_deg=270
        self.counter=0
        self.r=30
        self.rotation_speed=40
    def update(self,game):
        self.last_deg=self.target_deg
        if not game.pressKeyQueue:
            return
        if game.pressKeyQueue[-1]==pg.K_w:
            self.target_deg=270
        elif game.pressKeyQueue[-1]==pg.K_s:
            self.target_deg=90
        elif game.pressKeyQueue[-1]==pg.K_d:
            self.target_deg=0
        elif game.pressKeyQueue[-1]==pg.K_a:
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
        rect = out_image.get_rect(center=(self.x, self.y))
        game.screen.blit(out_image, rect)

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
    game.shield=shield(game)
    game.oiiai=oiiai(game)
    game.in_ma_u_npc.append(game.oiiai)
    game.heart=heart(game)
    game.undyne_bg=pg.Surface(game.screen.get_size())
    game.undyne_bg=game.undyne_bg.convert()
    game.undyne_bg.fill((0,0,0)) # black
    game.line_lenth=3

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

def fight(game):
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
    game.screen.blit(game.heart.image,game.heart.rect)
    game.shield.draw(game)