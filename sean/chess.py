import pygame
import random

pygame.init()

# --- 可調整參數 ---
GRID = 7
WIDTH, HEIGHT = 500, 500
LINE_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)
BALL_COLOR = (255, 0, 0)          # 紅色球
PREVIEW_COLOR = (0, 0, 255, 100)  # 半透明藍色
NUM_WALLS = 2

# --- 初始化 ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

CELL_SIZE = WIDTH // GRID

# 球位置
ball_row = GRID // 2
ball_col = GRID // 2

# 隨機生成障礙，避開球
walls = set()
while len(walls) < NUM_WALLS:
    r = random.randint(0, GRID - 1)
    c = random.randint(0, GRID - 1)
    if (r, c) != (ball_row, ball_col):
        walls.add((r, c))

# 預定軌跡（初始沒有藍色）
preview_cells = []
current_direction = (0, 0)  # dr, dc


def draw_grid():
    for row in range(GRID):
        for col in range(GRID):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)
            if (row, col) in walls:
                pygame.draw.rect(screen, (100, 100, 100), rect)  # 灰色牆


def draw_preview():
    for r, c in preview_cells:
        if (r, c) != (ball_row, ball_col):  # 紅球在最上層
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            s.fill(PREVIEW_COLOR)
            screen.blit(s, rect.topleft)
    # 角色格也要顯示藍色
    if preview_cells:
        r, c = preview_cells[0]
        rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        s.fill(PREVIEW_COLOR)
        screen.blit(s, rect.topleft)


def draw_center_ball():
    center_x = ball_col * CELL_SIZE + CELL_SIZE // 2
    center_y = ball_row * CELL_SIZE + CELL_SIZE // 2
    radius = CELL_SIZE // 3
    pygame.draw.circle(screen, BALL_COLOR, (center_x, center_y), radius)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            dr, dc = 0, 0
            if event.key == pygame.K_UP:
                dr = -1
            elif event.key == pygame.K_DOWN:
                dr = 1
            elif event.key == pygame.K_LEFT:
                dc = -1
            elif event.key == pygame.K_RIGHT:
                dc = 1

            if dr != 0 or dc != 0:
                # 按方向鍵時刷新預覽
                preview_cells = [(ball_row, ball_col)]  # 角色格也加入
                current_direction = (dr, dc)
                for step in range(1, 3):
                    nr = ball_row + dr * step
                    nc = ball_col + dc * step
                    if 0 <= nr < GRID and 0 <= nc < GRID:
                        if (nr, nc) in walls:
                            break
                        preview_cells.append((nr, nc))

            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # Enter → 移動紅球
                if len(preview_cells) > 1:  # 超過角色格才移動
                    ball_row, ball_col = preview_cells[-1]
                preview_cells = []  # 移動後清掉藍色

    screen.fill(BG_COLOR)
    draw_grid()
    draw_preview()      # 藍色格
    draw_center_ball()  # 紅球最上層

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
