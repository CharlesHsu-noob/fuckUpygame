import pygame, math, time, random, sys

class RhythmGame:
    # ★ 修改 1: 增加 draw_bg_func 參數
    def __init__(self, screen=None, width=None, height=None, draw_bg_func=None):
        # --- 視窗與縮放初始化 ---
        if screen is None:
            pygame.init()
            self.WIDTH, self.HEIGHT = 500, 400
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        else:
            self.screen = screen
            self.WIDTH, self.HEIGHT = width, height

        self.clock = pygame.time.Clock()
        self.draw_bg_func = draw_bg_func  # ★ 保存繪圖函式

        # --- 計算縮放比例 ---
        ORIG_W, ORIG_H = 500, 400
        self.sx = self.WIDTH / ORIG_W
        self.sy = self.HEIGHT / ORIG_H
        self.sr = min(self.sx, self.sy)

        # --- 應用縮放參數 ---
        self.C = (int(250 * self.sx), int(350 * self.sy))
        self.R = int(100 * self.sr)
        self.line_w_base = max(1, int(5 * self.sr))
        self.line_w_arc = max(1, int(10 * self.sr))

        # --- 遊戲邏輯參數 ---
        self.num = random.randint(165, 330)
        self.pointer_angle = math.radians(180)
        self.pointer_speed = math.radians(150)
        self.direction = -1

        self.center_angle = math.radians(135)
        self.perfect_range = math.radians(5)
        self.great_range = math.radians(15)

        self.start_time = time.time()
        self.a = math.radians(70)

        self.font = pygame.font.SysFont(None, int(48 * self.sr))
        self.small_font = pygame.font.SysFont(None, int(24 * self.sr))
        
        self.result = ""
        self.puss_time = 0
        self.waiting = False
        self.animation = True
        self.pre_start = time.time()

        self.current_keys = set()
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.result = "MISS"
                self.running = False

            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key).upper()
                self.current_keys.add(key_name)

            if event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key).upper()
                if key_name in self.current_keys:
                    self.current_keys.remove(key_name)

            if not self.animation:
                if not self.waiting and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    gap = (self.pointer_angle - self.center_angle + math.pi) % (2 * math.pi) - math.pi
                    if abs(gap) <= self.perfect_range:
                        self.result = "PERFECT"
                    elif abs(gap) <= self.great_range:
                        self.result = "GREAT"
                    else:
                        self.result = "MISS"

                    self.waiting = True
                    self.puss_time = time.time()

                elif self.waiting and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.waiting = False
                    self.pointer_angle = 0.0
                    self.direction = 1
                    self.result = ""
                    self.num = random.randint(165, 330)
                    self.center_angle = math.radians(135)
                    self.start_time = time.time()
                    self.pointer_speed = math.radians(100)
                    self.animation = True
                    self.direction = -1
                    self.pre_start = time.time()
                    self.pointer_angle = math.radians(180)
                    self.pointer_speed = math.radians(150)

    def update(self, dt):
        if self.animation:
            self.pointer_angle += self.pointer_speed * dt * self.direction
            if self.pointer_angle < math.radians(1):
                self.animation = False
                self.start_time = time.time()
                self.pointer_angle = 0.0
                self.pointer_speed = math.radians(50)
                self.direction = 1

        elif not self.waiting:
            self.pointer_speed = self.pointer_speed + self.a * (time.time() - self.start_time)
            self.pointer_angle += self.pointer_speed * dt * self.direction
            if self.pointer_angle > math.radians(179):
                self.pointer_angle = math.radians(180)
                self.result = "MISS"
                self.waiting = True

    # ★ 修改 2: draw 接收 dt 參數
    def draw(self, dt):
        # --- 繪製背景 ---
        if self.draw_bg_func:
            # 如果有背景函式，呼叫它畫出戰鬥場景
            self.draw_bg_func(dt)
        else:
            # 沒有的話就用純色
            self.screen.fill((30, 30, 30))

        # --- 繪製半透明遮罩 ---
        # 建立一個與螢幕一樣大的表面，支援透明度 (SRCALPHA)
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        # 填滿黑色，透明度 200 (0全透 ~ 255不透)
        overlay.fill((0, 0, 0, 200)) 
        self.screen.blit(overlay, (0, 0))
        
        # --- 正常繪製遊戲元件 (在遮罩之上) ---
        pygame.draw.arc(self.screen, (200, 200, 200),
                        (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                        0, math.pi, self.line_w_base)

        if not self.animation:
            pygame.draw.arc(self.screen, (0, 0, 255),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.center_angle - self.great_range, self.center_angle + self.great_range, self.line_w_arc)
            pygame.draw.arc(self.screen, (0, 255, 0),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.center_angle - self.perfect_range, self.center_angle + self.perfect_range, self.line_w_arc)

        if self.animation and self.center_angle - self.great_range < self.pointer_angle < self.center_angle + self.great_range:
            pygame.draw.arc(self.screen, (0, 0, 255),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.pointer_angle, self.center_angle + self.great_range, self.line_w_arc)
        elif self.animation and self.pointer_angle < self.center_angle + self.great_range:
            pygame.draw.arc(self.screen, (0, 0, 255),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.center_angle - self.great_range, self.center_angle + self.great_range, self.line_w_arc)

        if self.animation and self.center_angle - self.perfect_range < self.pointer_angle < self.center_angle + self.perfect_range:
            pygame.draw.arc(self.screen, (0, 255, 0),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.pointer_angle, self.center_angle + self.perfect_range, self.line_w_arc)
        elif self.animation and self.pointer_angle < self.center_angle + self.perfect_range:
            pygame.draw.arc(self.screen, (0, 255, 0),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.center_angle - self.perfect_range, self.center_angle + self.perfect_range, self.line_w_arc)

        pointer_x = self.C[0] + self.R * math.cos(self.pointer_angle)
        pointer_y = self.C[1] - self.R * math.sin(self.pointer_angle)
        pygame.draw.line(self.screen, (255, 0, 0), self.C, (pointer_x, pointer_y), self.line_w_base)

        if self.result:
            text_surf = self.font.render(self.result, True, (255, 255, 255))
            text_offset_y = int(60 * self.sy)
            self.screen.blit(text_surf, (self.C[0] - text_surf.get_width() / 2, self.C[1] - self.R - text_offset_y))

        key_text = " ".join(sorted(self.current_keys))
        key_surf = self.small_font.render(f"Keys: {key_text}", True, (200, 200, 200))
        self.screen.blit(key_surf, (int(10 * self.sx), int(10 * self.sy)))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            # ★ 修改 3: 傳遞 dt 給 draw
            self.draw(dt)

            if self.result:
                pygame.time.delay(300)
                self.running = False

        return self.result

# ★ 修改 4: 對外接口增加 draw_bg_func
def play_qte(screen=None, WIDTH=None, HEIGHT=None, draw_bg_func=None):
    game = RhythmGame(screen, WIDTH, HEIGHT, draw_bg_func)
    return game.run()

if __name__ == "__main__":
    result = play_qte()
    print("QTE Result:", result)