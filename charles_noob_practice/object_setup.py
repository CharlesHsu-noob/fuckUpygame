import picture_dictionary as pd
import pygame as pg
import os,sys,random
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
#將父目錄路徑添加到 Python 的搜尋路徑中
#sys.path.insert(0, ...) 將路徑添加到清單的最前面
sys.path.insert(0, base_dir)
import XddObjects as xo
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
    state_pos={}
    state_pos["in_game"]=(w/2,h/2)
    state_pos["in_ac"]=(2048/2,1160-100)
    state_pos["in_ma_u"]=(1023,588)
    #pause
    defaultvol=0.0
    game.volume_rail=xo.sliderRailObject(pd.volume_rail_path,(w/2,h/2),(300,10))
    game.volume_twist=xo.sliderTwistObject(pd.volume_twist_path,(w/2,h/2),(10,27),0,0.3,defaultvol,game.volume_rail)
    game.pause_sprites.add(game.volume_rail)
    game.pause_sprites.add(game.volume_twist)
    game.pause_exit=xo.buttonObject(pd.exit_paths,(w/2,h-200),(105,45))
    game.pause_sprites.add(game.pause_exit)
    game.pause_back=xo.buttonObject(pd.back_paths,center=(w/2-100,h-200),size=(150,150))
    game.pause_sprites.add(game.pause_back)

    #main menu
    game.mrbeast=xo.moveObject(pd.mrbeast_path,(300,550),(200,130),7,False)
    game.main_menu_sprites.add(game.mrbeast)
    game.milk=xo.moveObject(pd.milk_path,(random.randint(100,250),random.randint(150,250)),(130,170),8,True)
    game.main_menu_sprites.add(game.milk)
    game.sybau=xo.buttonObject(pd.sybau_paths,(200,325),(200,200))
    game.main_menu_sprites.add(game.sybau)

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
    in_game_npc.append(game.hitler)
        #in game wall
    game.barrier1=xo.wallObject(pd.barrier_paths,0,(200,1780),(40,480),True)
    in_game_wall.append(game.barrier1)
    game.barrier2=xo.wallObject(pd.barrier_paths,1,(500,1500),(700,40),True)
    in_game_wall.append(game.barrier2)
    game.barrier3=xo.wallObject(pd.barrier_paths,1,(500,2050),(700,40),True)
    in_game_wall.append(game.barrier3)
    game.ma_u_guan_barrier=xo.wallObject(pd.barrier_paths,2,(3700,1600),(400,600),False)
    in_game_wall.append(game.ma_u_guan_barrier)
        #in game door
    game.in_game_to_ac=xo.doorObject(pd.door_paths,(900,1640),(75,75),"in_ac",True)#ac=activity center
    in_game_door.append(game.in_game_to_ac)
    game.ac_to_in_game=xo.doorObject(pd.door_paths,(2048/2,1160-20),(75,75),"in_game",True)
    in_ac_door.append(game.ac_to_in_game)
        #in game ma_u_guan door
    game.in_game_to_ma_u=xo.doorObject(pd.door_paths,(3470,1610),(75,75),"in_ma_u",True)#美玉管
    in_game_door.append(game.in_game_to_ma_u)
    game.ma_u_to_in_game=xo.doorObject(pd.door_paths,(2048/2,h-20),(75,75),"in_game",True)
    in_ma_u_door.append(game.ma_u_to_in_game)
