import pygame as pg

pg.init()
WIDTH, HEIGHT = 800, 600
screen = pg.display.set_mode((WIDTH, HEIGHT))

font_path = "C:\\Windows\\Fonts\\msjh.ttc"
font = pg.font.Font(font_path, 28)
small_font = pg.font.Font(font_path, 22)

clock = pg.time.Clock()


# ==========================================================
#               Dialogue Manager（通用型）
# ==========================================================
class DialogueManager:
    def __init__(self):
        self.active = False
        self.pages = []
        self.index = 0
        self.option_index = 0

    def start(self, pages):
        """pages = [ {text:..} , {options:[..]} , {text:..} ]"""
        self.active = True
        self.pages = pages
        self.index = 0
        self.option_index = 0

    def close(self):
        self.active = False

    def current(self):
        return self.pages[self.index]

    def next_page(self):
        if self.index < len(self.pages) - 1:
            self.index += 1
            self.option_index = 0
        else:
            self.close()


dialogue = DialogueManager()


# ==========================================================
#                     介面繪製
# ==========================================================
def draw_dialog_box():
    box = pg.Rect(50, HEIGHT - 180, WIDTH - 100, 130)
    pg.draw.rect(screen, (20, 20, 20), box)
    pg.draw.rect(screen, (255, 255, 255), box, 3)
    return box


def draw_text_page(text):
    box = draw_dialog_box()
    t = font.render(text, True, (255, 255, 255))
    screen.blit(t, (box.x + 20, box.y + 20))

    # 右下角提示
    prompt = small_font.render("按 Enter 繼續", True, (200, 200, 200))
    screen.blit(prompt, (box.right - 160, box.bottom - 30))


def draw_option_page(options):
    box = draw_dialog_box()

    title = font.render("請選擇：", True, (255, 255, 255))
    screen.blit(title, (box.x + 20, box.y + 20))

    for i, opt in enumerate(options):
        color = (255, 230, 80) if i == dialogue.option_index else (255, 255, 255)
        line = font.render(opt, True, color)
        screen.blit(line, (box.x + 50, box.y + 60 + i * 35))


# ==========================================================
#                  主遊戲迴圈
# ==========================================================
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        # --- 啟動對話（示範用：按E觸發） ---
        if event.type == pg.KEYDOWN and not dialogue.active:
            if event.key == pg.K_e:
                # ⭐ 這裡換成任何對話都可以！！
                dialogue.start([
                    {"text": "一個生機蓬勃的湖泊。"},
                    {"options": ["釣魚", "離開"]},
                    {"text": "你發現你沒有釣竿。"}
                ])

        # --- 對話中控制 ---
        if event.type == pg.KEYDOWN and dialogue.active:
            cur = dialogue.current()

            # (1) 文字頁面 → Enter 下一頁
            if "text" in cur:
                if event.key == pg.K_RETURN:
                    dialogue.next_page()

            # (2) 選項頁面
            elif "options" in cur:
                if event.key == pg.K_w:
                    dialogue.option_index = (dialogue.option_index - 1) % len(cur["options"])
                if event.key == pg.K_s:
                    dialogue.option_index = (dialogue.option_index + 1) % len(cur["options"])

                if event.key == pg.K_RETURN:
                    choice = dialogue.option_index

                    # ⭐ 這裡可以做不同行為
                    if choice == 0:  # 是
                        dialogue.next_page()  # 進入「你沒有釣竿」
                    else:  # 否
                        dialogue.close()  # 直接離開


    # ------------------ 畫面 ------------------
    screen.fill((50, 90, 160))

    if dialogue.active:
        cur = dialogue.current()

        if "text" in cur:
            draw_text_page(cur["text"])

        elif "options" in cur:
            draw_option_page(cur["options"])

    pg.display.flip()
    clock.tick(60)

pg.quit()
