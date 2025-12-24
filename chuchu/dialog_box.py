import pygame as pg
import sys

# ==========================
# 1. 介面與參數設定
# ==========================
WIDTH, HEIGHT = 800, 600

UI_SETTINGS = {
    "BOX_COLOR": (20, 20, 20),
    "BORDER_COLOR": (255, 255, 255),
    "BOX_X": 50,
    "BOX_Y": HEIGHT - 170,          
    "BOX_W": WIDTH - 100,
    "BOX_H": 150,
    "TEXT_X": 30,
    "TEXT_Y": 30,
    "OPTION_X": 50,
    "OPTION_START_Y": 60,
    "OPTION_SPACING": 35,
    "PROMPT_RIGHT_MARGIN": 160,
    "PROMPT_BOTTOM_MARGIN": 30,
    "TYPING_SPEED": 50, 
}

# ==========================
# 2. 初始化
# ==========================
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("RPG 對話系統 (完美循環版)")

try:
    font_path = "C:\\Windows\\Fonts\\msjh.ttc"
    font = pg.font.Font(font_path, 28)
    small_font = pg.font.Font(font_path, 22)
except FileNotFoundError:
    font = pg.font.Font(None, 32)
    small_font = pg.font.Font(None, 24)

clock = pg.time.Clock()

# ==========================
# 3. 對話資料 (拆分 Intro 與 Menu)
# ==========================
DIALOGUES = {
    # --- 1. 湖泊的開場白 (只講一次) ---
    "lake_intro": [
        {"type": "text", "content": "一個生機蓬勃的湖泊。"},
        # 講完這句，立刻自動跳進選單
        {"type": "jump", "next": "lake_menu"}
    ],

    # --- 2. 湖泊的選單 (循環中心) ---
    "lake_menu": [
        {
            "type": "choice",
            "options": [
                {"text": "釣魚", "next": "no_rod"},
                {"text": "離開", "next": "exit_prompt"}
            ]
        }
    ],

    # --- 3. 沒釣竿 (講完跳回選單，不跳回開場白) ---
    "no_rod": [
        {"type": "text", "content": "你發現你沒有釣竿。"},
        # ★ 關鍵：這裡指回 lake_menu (直接進選項)，而不是 intro
        {"type": "jump", "next": "lake_menu"} 
    ],

    "signpost": [
        {"type": "text", "content": "   <-森林 小鎮->   "},
        {"type": "text", "content": "墨星怕人 絕對不可能往鎮上走 我應該去森林裡找牠"},
        {"type": "end"}
    ],
    "exit_prompt": [
        {"type": "text", "content": "於是你轉身向山裡走去。"},
        {"type": "end"}
    ]
}

# ==========================
# 4. 對話系統
# ==========================
class DialogueSystem:
    def __init__(self, screen, font, small_font, dialogue_data):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.dialogue_data = dialogue_data
        self.clock = pg.time.Clock()

    def _draw_box(self):
        box = pg.Rect(UI_SETTINGS["BOX_X"], UI_SETTINGS["BOX_Y"], UI_SETTINGS["BOX_W"], UI_SETTINGS["BOX_H"])
        pg.draw.rect(self.screen, UI_SETTINGS["BOX_COLOR"], box)
        pg.draw.rect(self.screen, UI_SETTINGS["BORDER_COLOR"], box, 3)
        return box

    def _draw_text_page(self, text, is_finished):
        box = self._draw_box()
        t = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(t, (box.x + UI_SETTINGS["TEXT_X"], box.y + UI_SETTINGS["TEXT_Y"]))
        if is_finished:
            prompt = self.small_font.render("▼", True, (200, 200, 200))
            self.screen.blit(prompt, (box.right - 50, box.bottom - 40))

    def _draw_option_page(self, options, selected_index):
        box = self._draw_box()
        title = self.font.render("請選擇：", True, (255, 255, 255))
        self.screen.blit(title, (box.x + UI_SETTINGS["TEXT_X"], box.y + UI_SETTINGS["TEXT_Y"]))
        for i, opt in enumerate(options):
            color = (255, 230, 80) if i == selected_index else (255, 255, 255)
            line = self.font.render(opt, True, color)
            opt_y = box.y + UI_SETTINGS["OPTION_START_Y"] + (i * UI_SETTINGS["OPTION_SPACING"])
            self.screen.blit(line, (box.x + UI_SETTINGS["OPTION_X"], opt_y))

    def show(self, key):
        if key not in self.dialogue_data: return

        background_snapshot = self.screen.copy()
        current_pages = self.dialogue_data[key]
        
        index = 0
        option_index = 0
        
        displayed_text = ""
        target_text = ""
        char_index = 0
        last_typing_time = 0
        page_init = True

        running_dialogue = True

        while running_dialogue:
            current_time = pg.time.get_ticks()
            self.clock.tick(60)

            if index >= len(current_pages): break
            cur = current_pages[index]

            if cur["type"] == "jump":
                if cur["next"] in self.dialogue_data:
                    current_pages = self.dialogue_data[cur["next"]]
                    index = 0; option_index = 0; page_init = True; continue
                else: break

            if cur["type"] == "end": break

            if page_init:
                if cur["type"] == "text":
                    target_text = cur["content"]
                    displayed_text = ""
                    char_index = 0
                    last_typing_time = current_time
                page_init = False

            if cur["type"] == "text":
                if char_index < len(target_text):
                    if current_time - last_typing_time > UI_SETTINGS["TYPING_SPEED"]:
                        char_index += 1
                        displayed_text = target_text[:char_index]
                        last_typing_time = current_time
                else:
                    displayed_text = target_text

            self.screen.blit(background_snapshot, (0, 0))
            
            if cur["type"] == "text":
                self._draw_text_page(displayed_text, char_index >= len(target_text))
            elif cur["type"] == "choice":
                opts = [o["text"] for o in cur["options"]]
                self._draw_option_page(opts, option_index)

            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()

                if event.type == pg.KEYDOWN:
                    if cur["type"] == "text":
                        if event.key == pg.K_RETURN:
                            if char_index < len(target_text):
                                char_index = len(target_text)
                                displayed_text = target_text
                            else:
                                index += 1
                                page_init = True

                    elif cur["type"] == "choice":
                        if event.key == pg.K_UP:
                            option_index = (option_index - 1) % len(cur["options"])
                        if event.key == pg.K_DOWN:
                            option_index = (option_index + 1) % len(cur["options"])
                        if event.key == pg.K_RETURN:
                            selected = cur["options"][option_index]
                            if "next" in selected:
                                current_pages = self.dialogue_data[selected["next"]]
                                index = 0; option_index = 0; page_init = True
                            else:
                                running_dialogue = False

# ==========================
# 5. 主程式
# ==========================
class Player(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((32, 32))
        self.image.fill((220, 50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 4
    def move(self, keys):
        if keys[pg.K_LEFT]:  self.rect.x -= self.speed
        if keys[pg.K_RIGHT]: self.rect.x += self.speed
        if keys[pg.K_UP]:    self.rect.y -= self.speed
        if keys[pg.K_DOWN]:  self.rect.y += self.speed

def main():
    player = Player(400, 300)
    dialogue_sys = DialogueSystem(screen, font, small_font, DIALOGUES)

    triggers = {
        "lake_intro": pg.Rect(450, 300, 150, 100), # 這裡改成呼叫 lake_intro
        "signpost": pg.Rect(200, 100, 40, 60)
    }

    running = True
    while running:
        clock.tick(60)
        player.move(pg.key.get_pressed())
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_e:
                for key, rect in triggers.items():
                    if player.rect.colliderect(rect):
                        dialogue_sys.show(key)

        screen.fill((60, 140, 80)) 
        pg.draw.ellipse(screen, (50, 120, 200), triggers["lake_intro"])
        pg.draw.rect(screen, (139, 69, 19), triggers["signpost"])
        screen.blit(player.image, player.rect)

        for rect in triggers.values():
            if player.rect.colliderect(rect):
                hint = small_font.render("E", True, (255, 255, 255))
                screen.blit(hint, (player.rect.centerx, player.rect.top - 20))

        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    main()