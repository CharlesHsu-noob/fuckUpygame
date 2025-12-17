import pygame, math, random, time

class DBDQTE:
    def __init__(self, screen, WIDTH, HEIGHT):
        self.screen = screen
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.C = (WIDTH // 2, HEIGHT // 2 + 50)
        self.R = 100

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)

        # 指針設定
        self.pointer_angle = 0.0  # 初始 0 度
        self.pointer_speed = math.radians(150)  # 每秒旋轉角度
        self.direction = -1  # 初始逆時針

        # perfect 區域
        self.perfect_range = math.radians(5)
        self.center_angle = random.uniform(math.radians(20), math.radians(160))

        self.current_keys = set()
        self.running = True
        self.waiting = False
        self.results = []

        # 判定次數
        self.steps = 4

        # 時間控制
        self.dt = 0
        self.last_time = time.time()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key).upper()
                self.current_keys.add(key_name)

                if event.key == pygame.K_SPACE and not self.waiting:
                    # 判定
                    gap = (self.pointer_angle - self.center_angle + math.pi) % (2*math.pi) - math.pi
                    if abs(gap) <= self.perfect_range:
                        self.results.append("PERFECT")
                    else:
                        self.results.append("MISS")
                    self.waiting = True

            elif event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key).upper()
                if key_name in self.current_keys:
                    self.current_keys.remove(key_name)

    def update(self):
        # 計算 dt
        now = time.time()
        self.dt = now - self.last_time
        self.last_time = now

        if self.waiting:
            # 判定後等待短暫時間，準備下一回合
            time.sleep(0.2)
            self.waiting = False
            if len(self.results) < self.steps:
                # 反轉方向
                self.direction *= -1
                # 新 perfect 區域
                self.center_angle = random.uniform(math.radians(20), math.radians(160))
                # 從當前角度開始旋轉
                # self.pointer_angle 保持不變
            return

        # 指針旋轉
        self.pointer_angle += self.pointer_speed * self.dt * self.direction

        # 判定旋轉 360 度
        if self.pointer_angle >= 2*math.pi:
            self.pointer_angle -= 2*math.pi
            if len(self.results) < self.steps:
                self.results.append("MISS")
                self.waiting = True
        elif self.pointer_angle < 0:
            self.pointer_angle += 2*math.pi
            if len(self.results) < self.steps:
                self.results.append("MISS")
                self.waiting = True

    def draw(self):
        self.screen.fill((30, 30, 30))

        # 畫底圈
        pygame.draw.arc(self.screen, (200,200,200),
                        (self.C[0]-self.R, self.C[1]-self.R, 2*self.R, 2*self.R),
                        0, 2*math.pi, 5)

        # 畫 perfect 區域
        pygame.draw.arc(self.screen, (0,255,0),
                        (self.C[0]-self.R, self.C[1]-self.R, 2*self.R, 2*self.R),
                        self.center_angle - self.perfect_range,
                        self.center_angle + self.perfect_range,
                        10)

        # 畫指針
        pointer_x = self.C[0] + self.R * math.cos(self.pointer_angle)
        pointer_y = self.C[1] - self.R * math.sin(self.pointer_angle)
        pygame.draw.line(self.screen, (255,0,0), self.C, (pointer_x, pointer_y), 5)

        # 顯示結果
        if self.waiting and self.results:
            text_surf = self.font.render(self.results[-1], True, (255,255,255))
            self.screen.blit(text_surf, (self.C[0]-text_surf.get_width()/2, self.C[1]-self.R-60))

        pygame.display.flip()

    def run_four_steps(self):
        self.running = True
        self.last_time = time.time()
        while self.running and len(self.results) < self.steps:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        return self.results


# 對外呼叫
def play_qte_dbd(screen, WIDTH, HEIGHT):
    qte = DBDQTE(screen, WIDTH, HEIGHT)
    return qte.run_four_steps()


# 測試
if __name__ == "__main__":
    pygame.init()
    WIDTH, HEIGHT = 500, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    results = play_qte_dbd(screen, WIDTH, HEIGHT)
    print("QTE Results:", results)
    pygame.quit()
