import pygame as pg
import random,math,os
import setup
class Global_var():
    def __init__(self) -> None:
        pg.init()
        pg.mixer.init()
        self.clock=pg.time.Clock()
        screeninfo=pg.display.Info()
        self.w,self.h=screeninfo.current_w,screeninfo.current_h-80
        self.screen = pg.display.set_mode((self.w,self.h))
        pg.display.set_caption("object_practice")
        self.bg=pg.Surface(self.screen.get_size())
        self.bg=self.bg.convert()
        self.bg.fill((0,0,0)) # black
        self.pressKeyQueue=[]

        self.running=True
        self.game_state = "main_menu" # "main_menu", "transition", "in_game", "pause_menu"
        self.last_game_state=""
        self.fps=45
        #pause init
        self.is_pause=False
        
        # --- 為了跨平台相容性而進行的路徑設定 ---
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.dirname(self.script_dir)

        # --- Sprite Groups & Object Lists ---
        self.main_menu_sprites =[]
        self.empty_sprite_group = pg.sprite.Group()
        self.empty_array=[]
        self.in_game_npc = []
        self.in_game_wall = []
        self.in_game_door = []
        self.in_ac_wall = []
        self.in_ac_door = []
        self.in_ma_u_door = []
        self.pause_sprites = pg.sprite.Group()

        self.state_pos={}
        self.state_pos["in_game"]=(self.w/2,self.h/2)
        self.state_pos["in_ac"]=(2048/2,1160-100)
        self.state_pos["in_ma_u"]=(1023,588)

        setup.object_setup(self.state_pos,self.w,self.h,self)

        setup.music_setup(self.defaultvol)

        setup.map_and_bg_setup(self)

        setup.text_setup(self)

        #in game init
        self.last_map_x=self.kingnom.map_x
        self.last_map_y=self.kingnom.map_y

global_var=Global_var()
#----------------------------------------------------------------------------------------------
#universal function
def draw_sence(bg,npc_list,door_list,char,wall_list,sprites):#依照圖層序排列
    global_var.screen.blit(bg.image,bg.rect)
    for npc in npc_list:
        if npc.need_draw:
                global_var.screen.blit(npc.image,npc.rect)
    for door in door_list:
        if door.need_deter and door.visible:
            global_var.screen.blit(door.image,door.rect)
    global_var.screen.blit(char.image,char.rect)
    for wall in wall_list:
        if wall.need_deter and wall.visible:
                global_var.screen.blit(wall.image,wall.rect)
    sprites.draw(global_var.screen)

def wall_collision(char,wall_list,last_map_x,last_map_y):
    wall_rect_corretion_x=20#校正空氣牆
    wall_rect_corretion_y=3
    #global last_map_x,last_map_y
    return_x=char.map_x
    return_y=char.map_y
    for wall in wall_list:
        if wall.need_deter:
            if char.map_x+char.half_w>wall.map_x-wall.half_w +wall_rect_corretion_x and\
                char.map_x-char.half_w<wall.map_x+wall.half_w -wall_rect_corretion_x and\
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
    break_function=False
    for door in door_list:
        door.update(camera_x,camera_y,global_var.w,global_var.h)
        if abs(door.rect.centerx-char.rect.centerx)<char.half_w and\
            abs(door.rect.centery-char.rect.centery)<char.half_h:
            frozen=global_var.screen.copy()
            if char.move_state=="up":
                char.map_y+=30
            elif char.move_state=="down":
                char.map_y-=30
            if char.move_state=="left":
                char.map_x+=30
            elif char.move_state=="right":
                char.map_x-=30
            global_var.state_pos[global_var.game_state]=char.map_x,char.map_y
            char.map_x,char.map_y=global_var.state_pos[door.target]
            sence_fade_out(frozen)
            global_var.game_state=door.target
            break_function=True
            return break_function

def sence_fade_out(frozen):
    fade_surface = pg.Surface(global_var.screen.get_size())
    fade_surface = fade_surface.convert() # 為了更快的 blit 速度
    fade_surface.fill((0, 0, 0)) # 填滿黑色
    for alpha in range(0,86):
        global_var.screen.blit(frozen, (0, 0))
        fade_surface.set_alpha(alpha*3)
        global_var.screen.blit(fade_surface, (0, 0))
        pg.display.update()

def sence_fade_in(frozen):
    fade_surface = pg.Surface(global_var.screen.get_size())
    fade_surface = fade_surface.convert() # 為了更快的 blit 速度
    fade_surface.fill((0, 0, 0)) # 填滿黑色
    for alpha in range(85,-1,-1):
        global_var.screen.blit(frozen, (0, 0))
        fade_surface.set_alpha(alpha*3)
        global_var.screen.blit(fade_surface, (0, 0))
        pg.display.update()

def move_update(char,pressKeyQueue,bg,npc_list,wall_list,door_list):
    global last_map_x,last_map_y
    last_map_x=char.map_x
    last_map_y=char.map_y
    
    char.update(pressKeyQueue)
    #2. 邊界判定
    char.map_x,char.map_y=boundary_deter(char,bg,global_var.char_half)

    #2.1 牆壁碰撞
    char.map_x,char.map_y=wall_collision(char, wall_list,last_map_x,last_map_y)

     # 3. 根據角色的世界座標計算攝影機的理想位置 (目標是讓角色保持在螢幕中央)
    camera_x = char.map_x - global_var.w / 2#由 camera_x+w/2=map_x 推導而來
    camera_y = char.map_y - global_var.h / 2#由 camera_y+h/2=map_y 推導而來

    #4.1 將攝影機限制在地圖邊界內，避免顯示地圖外的黑色區域
    if camera_x < 0:
        camera_x = 0
    if camera_x > bg.map_w - global_var.w:
        camera_x = bg.map_w - global_var.w
    if camera_y < 0:
        camera_y = 0
    if camera_y > bg.map_h - global_var.h:
        camera_y = bg.map_h - global_var.h

    #4.2
    for npc in npc_list:
        npc.update(camera_x,camera_y,global_var.w,global_var.h)
    for wall in wall_list:
        wall.update(camera_x,camera_y,global_var.w,global_var.h) 
    if door_update(char,door_list,camera_x,camera_y):return   

    # 5. 根據攝影機的位置，更新地圖的螢幕位置 (地圖的移動方向與攝影機相反)
    bg.rect.x = -camera_x
    bg.rect.y = -camera_y
    
    # 6. 根據攝影機位置和角色的世界座標，計算角色在螢幕上的最終位置
    char.rect.centerx = char.map_x - camera_x
    char.rect.centery = char.map_y - camera_y

    #draw
    global_var.screen.blit(bg.image,bg.rect)
    for npc in npc_list:
        if npc.need_draw:
             global_var.screen.blit(npc.image,npc.rect)
    for door in door_list:
        if door.need_deter and door.visible:
            global_var.screen.blit(door.image,door.rect)
    global_var.screen.blit(char.image,char.rect)
    for wall in wall_list:
        if wall.need_deter and wall.visible:
             global_var.screen.blit(wall.image,wall.rect)
    pos_text=f"pos:({str(global_var.kingnom.map_x)},{str(global_var.kingnom.map_y)})"
    pos_surface=global_var.pos_font.render(pos_text,True,rainbow_text_color.get_color())
    global_var.screen.blit(pos_surface,(10,10))

class ColorCycler:
    """
    自動管理計數器，用正弦波實現平滑的 RGB 循環顏色變換。
    """
    def __init__(self, speed: float = 0.02):
        self.counter = 0.0
        self.speed = speed

    def get_color(self) -> tuple[int, int, int]:
        """
        更新計數器並回傳當前的彩虹循環顏色。
        """
        # 1. 更新計數器
        self.counter += self.speed
        if self.counter>=10000:
            self.counter=0
        time = self.counter

        # 2. 計算 R, G, B 分量 (使用不同的相位差)
        R = math.sin(time) * 127.5 + 127.5
        G = math.sin(time + 2 * math.pi / 3) * 127.5 + 127.5
        B = math.sin(time + 4 * math.pi / 3) * 127.5 + 127.5

        # 3. 確保 R, G, B 值在 0-255 的整數範圍內
        return (int(R), int(G), int(B))
rainbow_text_color = ColorCycler(speed=0.08)
#----------------------------------------------------------------------------------------------
def vol_update():
    global vol_percent,vol_text,vol_font
    vol_font = pg.font.Font(None, 30)
    vol_percent=float(global_var.volume_twist.current_val*100)/0.4
    display_text=f"Volume: {int(vol_percent)}"
    display_surface=vol_font.render(display_text, True, (0, 255, 255))
    global_var.screen.blit(display_surface,(global_var.w/2-270,global_var.h/2-8))
    pg.mixer.music.set_volume(global_var.volume_twist.current_val)


def pause_menu(global_bg):
    global_var.screen.blit(global_bg,(0,0))
    global_var.screen.blit(global_var.pause_bg,(0,0))
    global_var.pause_sprites.update()
    global_var.pause_sprites.draw(global_var.screen)
    vol_update()

#main menu init
def main_menu(main_menu_sprite):
    global_var.screen.blit(global_var.mainMenuBg,(0,0))
    global_var.screen.blit(global_var.titletext,(100,80))
    global_var.screen.blit(global_var.titleZHtext,(100,170))
    global_var.screen.blit(global_var.hint_text,(global_var.w-280,global_var.h-30))
    for i in main_menu_sprite:
        i.update(global_var.screen)
        global_var.screen.blit(i.image,i.rect)
    global_var.sybau.update()
    global_var.screen.blit(global_var.sybau.image,global_var.sybau.rect)
    #vol_update()

#transition init
transition_counter = 0
def in_game_transition():
    global transition_counter
    # 在 transition 狀態下，每一幀執行一次動畫
    if transition_counter < 50: 
        current_scale = 1 + (transition_counter / 30) * 7
        current_angle = transition_counter * 8
        trans_image = pg.transform.rotozoom(global_var.sybau_transition, current_angle, current_scale)
        trans_rect = trans_image.get_rect(center=(global_var.kingnom.rect.centerx, global_var.kingnom.rect.centery))
        alpha=255-(transition_counter*5)
        trans_image.set_alpha(alpha)
        global_var.mainMenuBg.set_alpha(alpha)
        global_var.kingnom.image.set_alpha(transition_counter*5)
        global_var.screen.blit(global_var.in_game_bg.image,global_var.in_game_bg.rect)
        global_var.screen.blit(global_var.kingnom.image,global_var.kingnom.rect)
        global_var.screen.blit(global_var.mainMenuBg,(0,0))
        global_var.screen.blit(trans_image, trans_rect)
        transition_counter += 1
    else:
        global_var.game_state = "in_game"
        transition_counter = 0


def in_game(pressKeyQueue):
    global play_animation
    
    move_update(global_var.kingnom,
                pressKeyQueue,
                global_var.in_game_bg,
                global_var.in_game_npc,
                global_var.in_game_wall,
                global_var.in_game_door)

    if play_animation:
        draw_sence(global_var.in_game_bg,global_var.in_game_npc,global_var.in_game_door,global_var.kingnom,global_var.in_game_wall,global_var.empty_sprite_group)
        frozen=global_var.screen.copy()
        sence_fade_in(frozen)
        play_animation=False

#in ac init
def in_ac(pressKeyQueue):
    global play_animation
    
    move_update(global_var.kingnom,
                pressKeyQueue,
                global_var.ac_bg,
                global_var.empty_array,#npc_list
                global_var.in_ac_wall,
                global_var.in_ac_door)

    if play_animation:
        draw_sence(global_var.ac_bg,
                   global_var.empty_array,
                   global_var.in_ac_door,
                   global_var.kingnom,
                   global_var.in_ac_wall,
                   global_var.empty_sprite_group)
        frozen=global_var.screen.copy()
        sence_fade_in(frozen)
        play_animation=False

#in ma u init
def in_ma_u(pressKeyQueue):
    global play_animation
    
    move_update(global_var.kingnom,
                pressKeyQueue,
                global_var.ma_u_bg,
                global_var.in_game_npc,
                global_var.empty_array,
                global_var.in_ma_u_door)

    if play_animation:
        draw_sence(global_var.ma_u_bg,
                   global_var.empty_array,
                   global_var.in_ma_u_door,
                   global_var.kingnom,
                   global_var.empty_array,
                   global_var.empty_sprite_group)
        frozen=global_var.screen.copy()
        sence_fade_in(frozen)
        play_animation=False

# game loop
while global_var.running:
    global_var.clock.tick(global_var.fps)
    #screen.blit(bg,(0,0))
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
        #偵測暫停
        if event.type==pg.KEYDOWN:
            if event.key==pg.K_ESCAPE:
                if not global_var.is_pause:
                    frozen=global_var.screen.copy()
                
                global_var.is_pause = not global_var.is_pause

                if not global_var.game_state=="pause_menu":
                    global_var.last_pause_state=global_var.game_state
                if global_var.is_pause:  
                    global_var.game_state="pause_menu"
                elif not global_var.is_pause:
                    global_var.game_state=global_var.last_pause_state
        # 偵測按鍵事件，並更新按鍵列表
        if event.type == pg.KEYDOWN:
            # 確保同一個鍵不會被重複加入
            if event.key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
                if event.key not in global_var.pressKeyQueue:
                    global_var.pressKeyQueue.append(event.key)

        if event.type == pg.KEYUP:
            if event.key in global_var.pressKeyQueue:
                global_var.pressKeyQueue.remove(event.key)
    
    if global_var.pause_back.ispress:
        is_pause=False
        global_var.game_state=global_var.last_pause_state
        global_var.pause_back.ispress=False

    play_animation=False
    if global_var.last_game_state!=global_var.game_state and\
        global_var.last_game_state!="pause_menu":
        play_animation=True
    global_var.last_game_state=global_var.game_state
    match global_var.game_state:
        case "pause_menu":
            pause_menu(frozen)
        case "main_menu":
            main_menu(global_var.main_menu_sprites)
            if global_var.sybau.ispress:
                global_var.game_state = "transition" 
                global_var.sybau.ispress = False
        case "transition":
            in_game_transition()
        case "in_game":
            in_game(global_var.pressKeyQueue)
        case "in_ac":
            in_ac(global_var.pressKeyQueue)
        case "in_ma_u":
            in_ma_u(global_var.pressKeyQueue)
        case _:
            pass

    if global_var.pause_exit.ispress:
        global_var.running = False 
    pg.display.update()
pg.quit()