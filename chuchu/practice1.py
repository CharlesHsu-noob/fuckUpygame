import pygame as pg
import sys
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

pg.init()
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

# 建立「暫停」按鈕
pause_btn = buttonObject(
    ["pause_normal.png", "pause_hover.png", "pause_pressed.png"], 
    center=(60, 30), size=(100, 50)
)
buttons = pg.sprite.Group(pause_btn)

paused = False
font = pg.font.Font(None, 80)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit(); sys.exit()

    # 更新按鈕
    buttons.update()

    # 檢查是否點擊
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
    clock.tick(60)
