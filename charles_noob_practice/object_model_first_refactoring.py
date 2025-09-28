# game_core.py - 遊戲主核心邏輯
import pygame as pg
import random, math, os
from typing import Dict, Any, List, Optional, Tuple
import sys
# ----------------------------------------------------------------------
# 匯入外部模組：物件類別 (xo) 和 數據設定 (gd)
# ----------------------------------------------------------------------
# 假設這兩個檔案已存在於你的專案結構中
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
#將父目錄路徑添加到 Python 的搜尋路徑中
#sys.path.insert(0, ...) 將路徑添加到清單的最前面
sys.path.insert(0, base_dir)
import XddObjects as xo 
import object_setup
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
# --- 輔助函式與工具 ---
# 這裡應該只包含與狀態機或遊戲流程相關的工具
# 碰撞、邊界判定等邏輯建議移至 game_objects.py 或 BaseMapScene 內部
# ----------------------------------------------------------------------
# I. 狀態模式架構 (STATE PATTERN)
# ----------------------------------------------------------------------

class BaseState:
    """所有遊戲狀態 (場景) 的基底類別。"""
    def __init__(self, game: 'Game'):
        self.game = game  # 取得中央 Game 實例
        
    def update(self):
        pass
        
    def draw(self):
        pass

class BaseMapScene(BaseState):
    """處理 InGame, InAc 等地圖場景的共享邏輯。"""
    def __init__(self, game: 'Game', bg: xo.moveObject, walls: List[xo.wallObject], doors: List[xo.doorObject], npcs: List[xo.npcObject]):
        super().__init__(game)
        self.bg = bg
        self.wall_list = walls
        self.door_list = doors
        self.npc_list = npcs
        # 將所有需要繪製的物件加入 Group
        self.all_scene_sprites = pg.sprite.Group(*walls, *doors, *npcs)

    def update(self):
        selfself = self.game
        
        # 1. 角色移動 (假設 xo.characterObject.update 處理了移動)
        selfself.kingnom.update(selfself.pressKeyQueue, self.wall_list, selfself.camera_x, selfself.camera_y)
        
        # 2. 攝影機計算 (這裡的邏輯需要你的 BaseMapScene 來實現)
        map_w, map_h = self.bg.rect.width, self.bg.rect.height
        selfself.camera_x = max(0, min(selfself.kingnom.map_x - selfself.w // 2, map_w - selfself.w))
        selfself.camera_y = max(0, min(selfself.kingnom.map_y - selfself.h // 2, map_h - selfself.h))
        
        # 3. 門的互動與狀態切換
        next_state = xo.door_update(selfself.kingnom, self.door_list, selfself.camera_x, selfself.camera_y)
        if next_state:
            selfself.set_state("transition", next_state) 

        # 4. 更新物件的螢幕 rect (基於攝影機)
        self.bg.rect.x = -selfself.camera_x
        self.bg.rect.y = -selfself.camera_y
        selfself.kingnom.rect.centerx = selfself.kingnom.map_x - selfself.camera_x
        selfself.kingnom.rect.centery = selfself.kingnom.map_y - selfself.camera_y
        
        # 5. 更新所有精靈
        self.all_scene_sprites.update() 
        
    def draw(self):
        selfself = self.game
        selfself.screen.blit(self.bg.image, self.bg.rect)
        self.all_scene_sprites.draw(selfself.screen) 
        selfself.screen.blit(selfself.kingnom.image, selfself.kingnom.rect) 

# --- 具體場景類別 (繼承 BaseState 或 BaseMapScene) ---

class MainMenu(BaseState):
    def update(self):
        self.game.main_menu_sprites.update()
        if self.game.sybau.ispress:
            self.game.set_state("transition", "in_game")
            self.game.sybau.ispress = False

    def draw(self):
        self.game.screen.fill((0, 0, 0))
        self.game.main_menu_sprites.draw(self.game.screen)

class InGame(BaseMapScene):
    def __init__(self, game):
        # 從 game_data 模組中，透過 Game 實例獲取數據
        super().__init__(game, game.in_game_bg, game.in_game_wall, game.in_game_door, game.in_game_npc)

class InAc(BaseMapScene):
    def __init__(self, game):
        super().__init__(game, game.ac_bg, game.in_ac_wall, game.in_ac_door, game.empty_array)

class PauseMenu(BaseState):
    def update(self):
        self.game.pause_sprites.update()
        if self.game.pause_back.ispress:
            self.game.set_state(self.game.last_pause_state) 
            self.game.pause_back.ispress = False

    def draw(self):
        self.game.screen.blit(self.game.frozen, (0, 0)) 
        # 假設你的半透明繪圖邏輯
        s = pg.Surface(self.game.screen.get_size(), pg.SRCALPHA); s.fill((0,0,0,150)); self.game.screen.blit(s, (0,0))
        self.game.pause_sprites.draw(self.game.screen)

class Transition(BaseState):
    def update(self):
        if self.transition_counter < 50:
            self.transition_counter += 1
        else:
            self.game.set_state(self.target_state)
            self.transition_counter = 0
            
    def draw(self):
        # 繪製你的過渡動畫
        pass

# ----------------------------------------------------------------------
# II. 主遊戲類別 (GAME)
# ----------------------------------------------------------------------

class Game:
    def __init__(self):
        # 1. 初始化 Pygame 環境 (解決初始化錯誤的關鍵步驟)
        pg.init()
        pg.mixer.init()
        self.clock = pg.time.Clock()
        
        # 2. 設置螢幕 (必須在所有圖片載入前完成)
        screeninfo = pg.display.Info()
        self.w, self.h = screeninfo.current_w, screeninfo.current_h - 80
        self.screen = pg.display.set_mode((self.w, self.h)) 
        pg.display.set_caption("Object Practice - Refactored")
        
        # 3. 遊戲物件和數據初始化 (安全地載入圖片和建立物件)
        self.init_game_data(self)

        # 4. 狀態和輸入管理
        self.pressKeyQueue = []
        self.running = True
        self.fps = 45
        self.frozen = None 
        self.camera_x, self.camera_y = 0, 0 
        
        # 5. 場景管理
        self.scenes = self.init_scenes()
        self.game_state = "main_menu"
        self.last_pause_state = "main_menu"
        self.current_scene = self.scenes[self.game_state]
        '''self.state_pos={}
        self.state_pos["in_game"]=(self.w/2,self.h/2)
        self.state_pos["in_ac"]=(2048/2,1160-100)
        self.state_pos["in_ma_u"]=(1023,588)'''

    def init_game_data(self,game):
        """從 game_data 模組載入所有數據和物件，並將它們附加到 Game 實例上。"""
        # 這裡執行 game_data 模組中的初始化函式
        object_setup.object_setup(self,self.w,self.h,game)
        
        # 假設 gd.initialize_data(self) 會將以下屬性附加到 self 上：
        # self.kingnom, self.sybau, self.pause_back, self.in_game_wall, ...

    def init_scenes(self):
        """實例化所有狀態物件。"""
        return {
            "main_menu": MainMenu(self),
            "transition": Transition(self),
            "in_game": InGame(self),
            "in_ac": InAc(self),
            "pause_menu": PauseMenu(self),
            # 請加入你的 "in_ma_u" 狀態
        }

    def set_state(self, new_state: str, target_state: Optional[str] = None):
        """統一的狀態切換方法。"""
        if new_state == "pause_menu":
            self.frozen = self.screen.copy() 
            self.last_pause_state = self.game_state
        
        self.game_state = new_state
        self.current_scene = self.scenes[new_state]
        
        if target_state and isinstance(self.current_scene, Transition):
            self.current_scene.target_state = target_state

    def handle_events(self):
        """統一處理所有事件。"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if self.game_state == "pause_menu":
                    self.set_state(self.last_pause_state)
                else:
                    self.set_state("pause_menu")

            # 按鍵佇列更新 (保持你原本的邏輯)
            if event.type == pg.KEYDOWN and event.key in [pg.K_w, pg.K_a, pg.K_s, pg.K_d]:
                if event.key not in self.pressKeyQueue:
                    self.pressKeyQueue.append(event.key)
            if event.type == pg.KEYUP and event.key in self.pressKeyQueue:
                self.pressKeyQueue.remove(event.key)

    def run(self):
        """主遊戲迴圈。"""
        while self.running:
            self.clock.tick(self.fps)
            self.handle_events() 
            
            self.current_scene.update()
            self.current_scene.draw()
            
            pg.display.update()
        pg.quit()

# ----------------------------------------------------------------------
# III. 程式進入點
# ----------------------------------------------------------------------

if __name__ == "__main__":
    game_instance = Game() 
    game_instance.run()