import json
import os
from typing import List, Dict, Tuple

class LevelManager:
    def __init__(self):
        self.levels_dir = "levels"
        self.levels = []
        # 确保levels目录存在
        if not os.path.exists(self.levels_dir):
            os.makedirs(self.levels_dir)
        self.load_levels()

    def load_levels(self):
        # 加载所有关卡
        self.levels = []
        if not os.path.exists(self.levels_dir):
            return
        for filename in os.listdir(self.levels_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.levels_dir, filename), "r") as f:
                        level = json.load(f)
                        self.levels.append(level)
                except Exception as e:
                    print(f"加载关卡 {filename} 失败: {e}")

    def save_level(self, board_size: Tuple[int, int], board: List[List[int]], targets: Tuple[Tuple[int, int]], name: str = None):
        # 保存关卡
        if name is None:
            name = f"level_{len(self.levels) + 1}"
        else:
            # 确保名称不重复
            original_name = name
            count = 1
            while any(level['name'] == name for level in self.levels):
                name = f"{original_name}_{count}"
                count += 1
        level = {
            "name": name,
            "board_size": board_size,
            "board": board,
            "targets": targets
        }
        filename = os.path.join(self.levels_dir, f"{name}.json")
        with open(filename, "w") as f:
            json.dump(level, f, indent=4)
        self.levels.append(level)
        return True

    def get_level(self, index: int) -> Dict:
        # 获取指定关卡
        if 0 <= index < len(self.levels):
            return self.levels[index]
        return None

    def has_levels(self) -> bool:
        # 检查是否有关卡
        return len(self.levels) > 0

    def get_level_count(self) -> int:
        # 获取关卡数量
        return len(self.levels)