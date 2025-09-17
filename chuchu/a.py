import pygame as pg
import os

import sys
import os

# 1. 取得當前腳本的目錄
#    os.path.abspath(__file__) 獲取當前腳本的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 獲取父目錄路徑
#    os.path.dirname() 獲取父目錄
parent_dir = os.path.dirname(current_dir)

# 3. 將父目錄路徑添加到 Python 的搜尋路徑中
#    sys.path.insert(0, ...) 將路徑添加到清單的最前面
sys.path.insert(0, parent_dir)

# 執行這段程式碼後，Python 就能找到上一層資料夾的模組了
# 你的程式碼現在可以正常運作
from charles_noob_practice.object_model import buttonObject

# ... 你的程式碼 ...
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
sybau_paths=[os.path.join(base_dir, "picture", "sybau", "sybau1.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau2.png"),
             os.path.join(base_dir, "picture", "sybau", "sybau3.png")]
sybau=buttonObject(sybau_paths,(200,325),(200,200))

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

running=True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running=False
            pg.quit()
    screen.fill((255,255,255))
    screen.blit(sybau.image,sybau.rect)
    pg.display.update()