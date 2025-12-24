import json
import os
import time

SAVE_FILE = "save_full.json"

class GameData:
    def __init__(self):
        # --- 1. 系統設定 ---
        self.volume = 0.5  # 音量 (0.0 ~ 1.0)
        
        # --- 2. 遊戲進度與時間 ---
        self.chapter = 1   # 當前章節
        self.total_playtime = 0.0  # 總遊玩秒數 (從存檔讀取)
        self._session_start = time.time()  # 這次開啟遊戲的時間點 (不存檔)

        # --- 3. 玩家位置與資源 ---
        self.x = 0
        self.y = 0
        self.money = 0
        
        # --- 4. 符文升級 (Dictionary) ---
        self.runes = {
            "fire_rune": 0,
            "ice_rune": 0
        }

        # --- 5. 物品欄 (List of Dictionaries) ---
        self.inventory = [] 

        # --- 6. 隊伍狀態 (List of Dictionaries) ---
        # 預設有一位勇者
        self.party = [
            {"name": "勇者", "hp": 100, "max_hp": 100, "status": "normal"}
        ]

    # === 計算當前總遊玩時間 ===
    def get_current_playtime(self):
        # 總時間 = 舊存檔時間 + (現在時間 - 剛開遊戲的時間)
        current_session_time = time.time() - self._session_start
        return self.total_playtime + current_session_time

    # === 序列化：轉成 Dictionary 以便存檔 ===
    def to_dict(self):
        return {
            "system": {
                "volume": self.volume
            },
            "progress": {
                "chapter": self.chapter,
                "playtime_seconds": self.get_current_playtime() # 存檔時更新總時間
            },
            "player": {
                "x": self.x,
                "y": self.y,
                "money": self.money,
                "runes": self.runes
            },
            "inventory": self.inventory,
            "party": self.party
        }

    # === 反序列化：讀檔還原資料 ===
    def load_from_dict(self, data):
        # 使用 .get() 給予預設值，防止存檔格式版本不同導致崩潰
        
        # 1. 讀取系統
        sys_data = data.get("system", {})
        self.volume = sys_data.get("volume", 0.5)

        # 2. 讀取進度
        prog_data = data.get("progress", {})
        self.chapter = prog_data.get("chapter", 1)
        self.total_playtime = prog_data.get("playtime_seconds", 0.0)
        self._session_start = time.time() # 讀檔後，重新開始計算「本次」時長

        # 3. 讀取玩家
        p_data = data.get("player", {})
        self.x = p_data.get("x", 0)
        self.y = p_data.get("y", 0)
        self.money = p_data.get("money", 0)
        self.runes = p_data.get("runes", {"fire_rune": 0, "ice_rune": 0})

        # 4. 讀取背包與隊伍 (直接覆蓋 list)
        self.inventory = data.get("inventory", [])
        self.party = data.get("party", [])


# ===== 存檔與讀檔功能 =====
def save_game(game_data):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(game_data.to_dict(), f, indent=4, ensure_ascii=False)
        print(">>> 存檔成功！")
    except Exception as e:
        print(f">>> 存檔失敗: {e}")

def load_game(game_data):
    if not os.path.exists(SAVE_FILE):
        print(">>> 找不到存檔！")
        return
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        game_data.load_from_dict(data)
        print(">>> 讀檔成功！")
    except Exception as e:
        print(f">>> 讀檔失敗: {e}")

# ===== 格式化時間顯示 (秒 -> 時:分:秒) =====
def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ===== 主程式測試 =====
def main():
    game = GameData()

    while True:
        # 顯示當前狀態
        print("\n" + "="*30)
        print(f"【遊玩時間】: {format_time(game.get_current_playtime())}")
        print(f"【座標】: ({game.x}, {game.y}) | 【金錢】: ${game.money}")
        print(f"【符文】: 火({game.runes.get('fire_rune',0)}) 冰({game.runes.get('ice_rune',0)})")
        print(f"【音量】: {game.volume}")
        
        print("【隊伍】:")
        for member in game.party:
            print(f"  - {member['name']}: HP {member['hp']}/{member['max_hp']} [{member['status']}]")
        
        print(f"【背包】: {game.inventory}")
        print("="*30)

        print("1. 移動 (X+1)")
        print("2. 賺錢 (+$100)")
        print("3. 升級符文 (火符文+1)")
        print("4. 受傷測試 (勇者扣血)")
        print("5. 獲得道具 (撿到藥水)")
        print("6. 調整音量")
        print("7. 存檔")
        print("8. 讀檔")
        print("9. 離開")

        cmd = input("請選擇: ")

        if cmd == "1":
            game.x += 1
        elif cmd == "2":
            game.money += 100
        elif cmd == "3":
            game.runes["fire_rune"] += 1
        elif cmd == "4":
            # 扣第一位角色的血9
            9
            9
            9
            if len(game.party) > 0:
                game.party[0]["hp"] = max(0, game.party[0]["hp"] - 10)
                if game.party[0]["hp"] == 0:
                    game.party[0]["status"] = "dead"
        elif cmd == "5":
            # 簡單的背包邏輯：直接加入 list
            game.inventory.append({"id": "potion", "count": 1})
        elif cmd == "6":
            game.volume = round((game.volume + 0.1) % 1.1, 1) # 循環調整
        elif cmd == "7":
            save_game(game)
        elif cmd == "8":
            load_game(game)
        elif cmd == "9":
            break

if __name__ == "__main__":
    main()