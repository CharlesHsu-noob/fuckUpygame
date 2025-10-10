import picture_dictionary as pd
import pygame as pg
import os,sys,random
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
#將父目錄路徑添加到 Python 的搜尋路徑中
#sys.path.insert(0, ...) 將路徑添加到清單的最前面
sys.path.insert(0, base_dir)
import XddObjects as xo
#sys.path.remove(base_dir)
if __name__=="__main__":
    pg.init()
    screeninfo=pg.display.Info()
    w,h=screeninfo.current_w,screeninfo.current_h-80
    screen = pg.display.set_mode((w,h))
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
    in_ma_u_door=[]
    pause_sprites = pg.sprite.Group()


def object_setup(state_pos,w,h,game):
    #pause
    game.defaultvol=0.0
    game.volume_rail=xo.sliderRailObject(pd.volume_rail_path,(w/2,h/2),(300,10))
    game.volume_twist=xo.sliderTwistObject(pd.volume_twist_path,(w/2,h/2),(10,27),0.0,0.4,game.defaultvol,game.volume_rail)
    game.pause_sprites.add(game.volume_rail)
    game.pause_sprites.add(game.volume_twist)
    game.pause_exit=xo.buttonObject(pd.exit_paths,(w/2,h-200),(105,45))
    game.pause_sprites.add(game.pause_exit)
    game.pause_back=xo.buttonObject(pd.back_paths,center=(w/2-100,h-200),size=(150,150))
    game.pause_sprites.add(game.pause_back)

    #main menu
    game.mrbeast=xo.moveObject(pd.mrbeast_path,(300,550),(200,130),7,False)
    game.main_menu_sprites.append(game.mrbeast)
    game.milk=xo.moveObject(pd.milk_path,(random.randint(100,250),random.randint(150,250)),(130,170),8,True)
    game.main_menu_sprites.append(game.milk)
    game.sybau=xo.buttonObject(pd.sybau_paths,(200,325),(200,200))
    #game.main_menu_sprites.append(game.sybau)

    #transition
    game.transition_omega=2
    game.transition_d_scale=0.1
    game.sybau_transition=pg.transform.scale(pg.image.load(pd.sybau_paths[2]),(200,200))

    #in game
    game.kingnom=xo.characterObject(pd.kingnom_stand_paths,pd.kingnom_move_paths,state_pos["in_game"],(88,100))
    game.kingnom.map_x=4160/2#2080
    game.kingnom.map_y=3760/2#1880
    game.char_half=[game.kingnom.rect.width / 2,game.kingnom.rect.height / 2]
        #in game npc
    game.hitler=xo.npcObject(pd.hitler_paths,(300,1880),(200,145))
    game.in_game_npc.append(game.hitler)
        #in game wall
    game.barrier1=xo.wallObject(pd.barrier_paths,0,(200,1780),(40,480),True)
    game.in_game_wall.append(game.barrier1)
    game.barrier2=xo.wallObject(pd.barrier_paths,1,(500,1500),(700,40),True)
    game.in_game_wall.append(game.barrier2)
    game.barrier3=xo.wallObject(pd.barrier_paths,1,(500,2050),(700,40),True)
    game.in_game_wall.append(game.barrier3)
    game.ma_u_guan_barrier=xo.wallObject(pd.barrier_paths,2,(3700,1600),(400,600),False)
    game.in_game_wall.append(game.ma_u_guan_barrier)
        #in game door
    game.in_game_to_ac=xo.doorObject(pd.door_paths,(900,1640),(75,75),"in_ac",True)#ac=activity center
    game.in_game_door.append(game.in_game_to_ac)
    game.ac_to_in_game=xo.doorObject(pd.door_paths,(2048/2,1160-20),(75,75),"in_game",True)
    game.in_ac_door.append(game.ac_to_in_game)
        #in game ma_u_guan door
    game.in_game_to_ma_u=xo.doorObject(pd.door_paths,(3470,1610),(75,75),"in_ma_u",True)#美玉管
    game.in_game_door.append(game.in_game_to_ma_u)
    game.ma_u_to_in_game=xo.doorObject(pd.door_paths,(2048/2,h-20),(75,75),"in_game",True)
    game.in_ma_u_door.append(game.ma_u_to_in_game)

def music_setup(self):
    #music init
    # --- Music Playlist ---
    self.music_playlist = {
        "main_menu": os.path.join(base_dir, "voice", "soundtrack", "red_sun_in_the_sky.wav"),
        "in_game": os.path.join(base_dir, "voice", "soundtrack", "german_erika.wav"),
        "in_ma_u":os.path.join(base_dir,"voice","soundtrack","bonetrousle.wav"),
        "undyne_fight":os.path.join(base_dir,"voice","soundtrack","a_true_hero.wav")
    }
    self.current_music = None # 用於追蹤目前播放的音樂

def effect_sound_setup(self):
    self.arrow_hit_shield=pg.mixer.Sound(os.path.join(base_dir,"voice","effect","undyne","undertale_ding.wav"))
    self.effect_sound.append(self.arrow_hit_shield)

def map_and_bg_setup(self):
    #map and background setup
    #pause
    self.pause_bg_or=pg.image.load(os.path.join(base_dir,"picture","back_ground","president_mao.png")).convert_alpha()
    self.pause_bg=pg.transform.scale(self.pause_bg_or,(self.w,self.h))
    self.pause_bg_alpha=100
    self.pause_bg.set_alpha(self.pause_bg_alpha)
    #main menu
    self.main_menu_bg_or=pg.image.load(os.path.join(base_dir, "picture", "back_ground", "main_menu_bg.png"))
    self.main_menu_bg_or.convert()
    self.mainMenuBg=pg.transform.scale(self.main_menu_bg_or.convert_alpha(),(self.w,self.h))

    #in game
    #inGameBg=mapObject(os.path.join(base_dir, "picture", "back_ground", "in_game_map2.png"),(w/2,h/2),(4160,3760))
    self.in_game_bg=xo.mapObject(os.path.join(base_dir, "picture", "back_ground", "in_game_map2_debug.png"),(self.w/2,self.h/2),(4160,3760))

    #in ac
    self.ac_bg=xo.mapObject(os.path.join(base_dir,"picture","back_ground","ac_bg.png"),(self.w/2,self.h/2),(2048,1160))

    #in ma u
    self.ma_u_bg=xo.mapObject(os.path.join(base_dir,"picture","back_ground","ma_u_bg.png"),(self.w/2,self.h/2),(self.w,self.h))

def text_setup(self):
    #text setup
    #volume
    self.vol_percent=0
    self.vol_font=pg.font.SysFont("times new roman",20)
    self.vol_text=self.vol_font.render(str(self.vol_percent),True,(255,255,255))

    #main menu
    self.title=pg.font.Font(os.path.join(base_dir, "font", "LavishlyYours-Regular.ttf"), 65)
    self.titletext=self.title.render("KINGNOM's big adventure",True,(0,200,200))
    self.titleZH=pg.font.Font(os.path.join(base_dir, "font", "bpm", "BpmfZihiSerif-Regular.ttf"),40)
    self.titleZHtext=self.titleZH.render("金農的大冒險",True,(255,200,200))
    self.hint=pg.font.Font(os.path.join(base_dir,"font","bpm","BpmfZihiSerif-Light.ttf"),20)
    self.hint_text=self.hint.render("點擊ESC鍵以暫停遊戲",True,(255,220,100))

    #in game
    self.pos_font=pg.font.SysFont("times new roman",20)