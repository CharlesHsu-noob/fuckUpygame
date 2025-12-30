import pygame as pg
import sys
import pause_menu # 引用我們拆分出來的檔案

# ==========================================
# === 主程式初始化 ===
# ==========================================
pg.init()
pg.key.set_repeat(300, 30)

info = pg.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.FULLSCREEN | pg.HWSURFACE | pg.DOUBLEBUF)
pg.display.set_caption("Milk Tea Save System - Main Loop")
clock = pg.time.Clock()

# === 重要：初始化暫停系統，傳入視窗大小 ===
pause_menu.init_pause_system(WIDTH, HEIGHT)

# 字體 (僅供主畫面顯示除錯訊息用，與 pause_menu 無關)
font_debug = pg.font.SysFont("arial", 24)

# ==========================================
# === 遊戲迴圈 ===
# ==========================================
while True:
    clock.tick(30)
    events = pg.event.get()
    
    # 1. 全域輸入處理 (包含 ESC 切換暫停狀態)
    pause_menu.handle_global_input(events)

    # 2. 根據狀態繪圖
    if pause_menu.paused:
        # 如果暫停中，交給 pause_menu 繪製與處理
        pause_menu.run_pause_menu(screen, events)
    else:
        # === 這裡是你的遊戲主畫面 ===
        screen.fill((216, 226, 233)) 
        
        # 顯示提示
        msg = font_debug.render("GAME RUNNING - Press ESC for Menu", True, (100, 100, 100))
        screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
        
        hint = font_debug.render("[B] Add Nut Bar | [N] Add Drink (Test Inventory)", True, (100, 100, 100))
        screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))

        # === 測試區：在主遊戲中按鍵加物品 ===
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_b:
                    print("Added Nut Bar")
                    pause_menu.add_item_to_bag("堅果棒", 1)
                elif event.key == pg.K_n:
                    print("Added Drink")
                    pause_menu.add_item_to_bag("能量飲料", 1)
    
    pg.display.flip()