import pygame as pg
import sys

pg.init()

WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()

# 遊戲狀態
paused = False

# 字型
font_big = pg.font.Font(None, 80)
font_small = pg.font.Font(None, 50)

# 左上角「暫停按鈕」
pause_button_rect = pg.Rect(10, 10, 100, 40)

# 建立選單按鈕（文字本身當按鈕）
def make_button(text, y):
    label = font_small.render(text, True, (255, 255, 255))
    rect = label.get_rect(center=(WIDTH//2, y))
    return {"text": text, "surface": label, "rect": rect}

menu_buttons = [
    make_button("Resume", HEIGHT//2 - 40),
    make_button("Main Menu", HEIGHT//2 + 20),
    make_button("Quit", HEIGHT//2 + 80)
]

def draw_game():
    """繪製遊戲畫面"""
    screen.fill((30, 120, 200))
    pg.draw.circle(screen, (255, 255, 255), (WIDTH//2, HEIGHT//2), 50)

    # 左上角暫停按鈕
    pg.draw.rect(screen, (200, 200, 200), pause_button_rect, border_radius=8)
    text = font_small.render("Pause", True, (0, 0, 0))
    screen.blit(text, (pause_button_rect.centerx - text.get_width()//2,
                       pause_button_rect.centery - text.get_height()//2))

def draw_pause_menu(mouse_pos):
    """繪製暫停選單"""
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # 標題
    title = font_big.render("PAUSED", True, (255, 255, 255))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 150))

    # 繪製選單按鈕（文字）
    for btn in menu_buttons:
        if btn["rect"].collidepoint(mouse_pos):  # 滑鼠移上去 → 變色
            label = font_small.render(btn["text"], True, (255, 200, 100))
        else:
            label = btn["surface"]

        screen.blit(label, btn["rect"].topleft)
        btn["current"] = label

def handle_click(mouse_pos):
    """處理選單點擊"""
    global paused
    for btn in menu_buttons:
        if btn["rect"].collidepoint(mouse_pos):
            if btn["text"] == "Resume":
                paused = False
            elif btn["text"] == "Main Menu":
                print("回主選單（可切換場景）")
                paused = False
            elif btn["text"] == "Quit":
                pg.quit(); sys.exit()

while True:
    mouse_pos = pg.mouse.get_pos()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit(); sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            if not paused:
                # 點擊左上角按鈕 → 暫停
                if pause_button_rect.collidepoint(mouse_pos):
                    paused = True
            else:
                # 點擊選單 → 執行功能
                handle_click(mouse_pos)

    draw_game()
    if paused:
        draw_pause_menu(mouse_pos)

    pg.display.flip()
    clock.tick(60)
