import pygame as pg
import os

base_dir=os.path.dirname(__file__)

#path setup
sybau_paths=[os.path.join(base_dir, "picture", "sybau", "sybau1.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau2.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau3.png")]

exit_paths=[os.path.join(base_dir, "picture", "exit", "exit1.png"),
            os.path.join(base_dir, "picture", "exit", "exit2.png"),
            os.path.join(base_dir, "picture", "exit", "exit3.png")]

back_paths=[os.path.join(base_dir, "picture", "return", "return1.png"),
            os.path.join(base_dir, "picture", "return", "return2.png"),
            os.path.join(base_dir, "picture", "return", "return3.png")]

kingnom_paths=[os.path.join(base_dir, "picture", "kingnom", "kingnom_stand1.png"),
             os.path.join(base_dir, "picture", "kingnom", "kingnom_stand2.png")]

kingnom_move_paths=[
    os.path.join(base_dir, "picture", "kingnom", "kingnom_move1.png"),
    os.path.join(base_dir, "picture", "kingnom", "kingnom_move2.png")
]

hitler_paths=[os.path.join(base_dir,"picture","hitler","hitler1.png")]

barrier1_path=[os.path.join(base_dir,"picture","barrier","barrier_wall.png")]


#pre load images as a dictionary
#map and background is not included
PICTURES={}
#only one picture
PICTURES["mrbeast"]=pg.image.load(os.path.join(base_dir, "picture", "MrBeast.png")).convert_alpha()
PICTURES["milk"]=pg.image.load(os.path.join(base_dir, "picture", "milkdragon.png")).convert_alpha()
PICTURES["slider_rail"]=pg.image.load(os.path.join(base_dir, "picture", "sound_slider", "slider_rail.png")).convert_alpha()
PICTURES["slider_twist"]=pg.image.load(os.path.join(base_dir, "picture", "sound_slider", "slider_twist.png")).convert_alpha()
#multiple pictures
PICTURES["sybau1"]=pg.image.load(sybau_paths[0]).convert_alpha()
PICTURES["sybau2"]=pg.image.load(sybau_paths[1]).convert_alpha()
PICTURES["sybau3"]=pg.image.load(sybau_paths[2]).convert_alpha()
PICTURES["exit1"]=pg.image.load(exit_paths[0]).convert_alpha()
PICTURES["exit2"]=pg.image.load(exit_paths[1]).convert_alpha()
PICTURES["exit3"]=pg.image.load(exit_paths[2]).convert_alpha()
PICTURES["back1"]=pg.image.load(back_paths[0]).convert_alpha()
PICTURES["back2"]=pg.image.load(back_paths[1]).convert_alpha()
PICTURES["back3"]=pg.image.load(back_paths[2]).convert_alpha()
PICTURES["kingnom_stand1"]=pg.image.load(kingnom_paths[0]).convert_alpha()
PICTURES["kingnom_stand2"]=pg.image.load(kingnom_paths[1]).convert_alpha()
PICTURES["kingnom_move1"]=pg.image.load(kingnom_move_paths[0]).convert_alpha()
PICTURES["kingnom_move2"]=pg.image.load(kingnom_move_paths[1]).convert_alpha()
PICTURES["hitler1"]=pg.image.load(hitler_paths[0]).convert_alpha()
PICTURES["barrier_wall"]=pg.image.load(barrier1_path[0]).convert_alpha()

#add object surface to *_pre_load arrays 
exit_pre_load=[PICTURES["exit1"],PICTURES["exit2"],PICTURES["exit3"]]
back_pre_load=[PICTURES["back1"],PICTURES["back2"],PICTURES["back3"]]
sybau_pre_load=[PICTURES["sybau1"],PICTURES["sybau2"],PICTURES["sybau3"]]
kingnom_stand_pre_load=[PICTURES["kingnom_stand1"],PICTURES["kingnom_stand2"]]
kingnom_move_pre_load=[PICTURES["kingnom_move1"],PICTURES["kingnom_move2"]]
hitler_pre_load=[PICTURES["hitler1"]]
barrier1_pre_load=[PICTURES["barrier_wall"]]