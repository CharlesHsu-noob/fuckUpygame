import pygame, math, time, random

class QTE_DBDmode:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 500, 400
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()

        self.C = (250, 200)
        self.R = 100

        self.pointer_angle = 0.0
        self.pointer_speed = math.radians(400)
        self.direction = random.choice([1, -1])  # 隨機方向

        self.num = random.randint(165, 330)
        self.center_angle = math.radians(self.num)
        self.perfect_range = math.radians(10)

        self.font = pygame.font.SysFont(None, 48)
        self.result = ""
        self.waiting = False

        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if not self.waiting and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                gap = (self.pointer_angle - self.center_angle + math.pi) % (2 * math.pi) - math.pi
                if abs(gap) <= self.perfect_range:
                    self.result = "PERFECT"
                else:
                    self.result = "MISS"
                self.waiting = True
                self.wait_time = time.time()

            elif self.waiting and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # 重置新一輪
                self.pointer_angle = 0.0
                self.direction = random.choice([1, -1])
                self.result = ""
                self.num = random.randint(165, 330)
                self.center_angle = math.radians(self.num)
                self.waiting = False

    def update(self, dt):
        if not self.waiting:
            self.pointer_angle += self.pointer_speed * dt * self.direction
            if self.pointer_angle > math.radians(360) or self.pointer_angle < math.radians(0):
                self.result = "MISS"
                self.waiting = True

    def draw(self):
        self.screen.fill((30, 30, 30))

        # 底圓
        pygame.draw.arc(self.screen, (200, 200, 200),
                        (self.C[0]-self.R, self.C[1]-self.R, 2*self.R, 2*self.R), 0, 2*math.pi, 5)

        # 只有 PERFECT 區域
        pygame.draw.arc(self.screen, (0, 255, 0),
                        (self.C[0]-self.R, self.C[1]-self.R, 2*self.R, 2*self.R),
                        self.center_angle - self.perfect_range, self.center_angle + self.perfect_range, 10)

        # 指針
        pointer_x = self.C[0] + self.R * math.cos(self.pointer_angle)
        pointer_y = self.C[1] - self.R * math.sin(self.pointer_angle)
        pygame.draw.line(self.screen, (255, 0, 0), self.C, (pointer_x, pointer_y), 5)

        # 結果顯示
        if self.result:
            text_surf = self.font.render(self.result, True, (255, 255, 255))
            self.screen.blit(text_surf, (self.C[0]-text_surf.get_width()/2, self.C[1]-self.R-60))

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()

            if self.result:
                pygame.time.delay(300)
                self.running = False

        return self.result

def play_qte_dbd():
    game = QTE_DBDmode()
    return game.run()


# ---------- Defend技能呼叫範例 ----------
def defend_qte(enemy_damage):
    """
    shield_turns >0 時，每次敵方攻擊觸發此函式
    會連續出現4次QTE，每次PERFECT減少20%敵方傷害
    """
    perfect_count = 0
    for _ in range(4):
        result = play_qte_dbd()
        if result == "PERFECT":
            perfect_count += 1

    damage_multiplier = 1 - 0.2 * perfect_count
    final_damage = int(enemy_damage * damage_multiplier)
    return final_damage
