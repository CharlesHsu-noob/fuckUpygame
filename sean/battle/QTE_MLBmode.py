import pygame, math, time, random

class RhythmGame:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 500, 400
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()

        self.C = (250, 350)
        self.R = 100

        self.num = random.randint(165, 330)
        self.pointer_angle = math.radians(180)
        self.pointer_speed = math.radians(150)
        self.direction = -1

        self.center_angle = math.radians(135)
        self.perfect_range = math.radians(5)
        self.great_range = math.radians(15)

        self.start_time = time.time()
        self.a = math.radians(70)

        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)
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

    def draw(self):
        self.screen.fill((30, 30, 30))
        pygame.draw.arc(self.screen, (200, 200, 200),
                        (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                        0, math.pi, 5)

        if not self.animation:
            pygame.draw.arc(self.screen, (0, 0, 255),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.center_angle - self.great_range, self.center_angle + self.great_range, 10)
            pygame.draw.arc(self.screen, (0, 255, 0),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.center_angle - self.perfect_range, self.center_angle + self.perfect_range, 10)

        if self.animation and self.center_angle - self.great_range < self.pointer_angle < self.center_angle + self.great_range:
            pygame.draw.arc(self.screen, (0, 0, 255),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.pointer_angle, self.center_angle + self.great_range, 10)
        elif self.animation and self.pointer_angle < self.center_angle + self.great_range:
            pygame.draw.arc(self.screen, (0, 0, 255),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.center_angle - self.great_range, self.center_angle + self.great_range, 10)

        if self.animation and self.center_angle - self.perfect_range < self.pointer_angle < self.center_angle + self.perfect_range:
            pygame.draw.arc(self.screen, (0, 255, 0),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.pointer_angle, self.center_angle + self.perfect_range, 10)
        elif self.animation and self.pointer_angle < self.center_angle + self.perfect_range:
            pygame.draw.arc(self.screen, (0, 255, 0),
                            (self.C[0] - self.R, self.C[1] - self.R, 2 * self.R, 2 * self.R),
                            self.center_angle - self.perfect_range, self.center_angle + self.perfect_range, 10)

        pointer_x = self.C[0] + self.R * math.cos(self.pointer_angle)
        pointer_y = self.C[1] - self.R * math.sin(self.pointer_angle)
        pygame.draw.line(self.screen, (255, 0, 0), self.C, (pointer_x, pointer_y), 5)

        if self.result:
            text_surf = self.font.render(self.result, True, (255, 255, 255))
            self.screen.blit(text_surf, (self.C[0] - text_surf.get_width() / 2, self.C[1] - self.R - 60))

        key_text = " ".join(sorted(self.current_keys))
        key_surf = self.small_font.render(f"Keys: {key_text}", True, (200, 200, 200))
        self.screen.blit(key_surf, (10, 10))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

            # ★ 一旦有結果就結束並回傳，不退出 Pygame
            if self.result:
                pygame.time.delay(300)
                self.running = False

        return self.result  # 回傳結果，但不關閉外部視窗

# 對外呼叫用函式
def play_qte():
    game = RhythmGame()
    return game.run()

if __name__ == "__main__":
    result = play_qte()
    print("QTE Result:", result)
