import os,sys
import pygame as pg
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
# 將父目錄路徑添加到 Python 的搜尋路徑中
#    sys.path.insert(0, ...) 將路徑添加到清單的最前面
sys.path.insert(0, base_dir)

#from XddObjects import buttonObject
import XddObjects as xo
#----------^--important--^------------

pg.init()
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

# 建立「暫停」按鈕
pause_btn = xo.buttonObject(#<-------look this
    [os.path.join(base_dir,"picture","NoWrongWay","NoWrongWay1.png"),
     os.path.join(base_dir,"picture","NoWrongWay","NoWrongWay2.png"),
     os.path.join(base_dir,"picture","NoWrongWay","NoWrongWay3.png")], 
    center=(60, 60), size=(75, 75)
)
buttons = pg.sprite.Group(pause_btn)
paused = False
font = pg.font.Font(None, 80)
while True:
    clock.tick(30)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit(); sys.exit()
    buttons.update()
    buttons.draw(screen)
    if pause_btn.ispress:
        paused = not paused

    if paused:
        # 半透明黑幕
        overlay = pg.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 暫停文字
        text = font.render("PAUSED", True, (255, 255, 255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))
    else:
        # 遊戲正常時顯示按鈕
        buttons.draw(screen)

    pg.display.flip()
    
