from game import Game
from typing import List, Tuple, Dict, Set
from collections import deque
from game import Game
from constants import DIRECTION_MAP
from utils import get_block_positions

class Solver:
    def __init__(self, game: Game):
        self.game = game
        self.rows = game.rows
        self.cols = game.cols
        self.targets = game.targets

    def solve(self):
        # 使用BFS求解华容道
        start_state = self.get_state()
        if self.is_goal_state(start_state):
            return []

        visited = set()
        visited.add(start_state)
        queue = deque([(start_state, [])])

        while queue:
            state, path = queue.popleft()
            # 尝试所有可能的移动
            blocks = self.get_blocks(state)
            for block in blocks:
                for direction in ["up", "down", "left", "right"]:
                    new_state = self.move_block(state, block, direction)
                    if new_state and new_state not in visited:
                        if self.is_goal_state(new_state):
                            return path + [(block, direction)]
                        visited.add(new_state)
                        queue.append((new_state, path + [(block, direction)]))
        return None  # 无解

    def get_state(self):
        # 获取当前游戏状态
        return tuple(tuple(row) for row in self.game.board)

    def is_goal_state(self, state):
        # 检查是否为目标状态
        # 复制状态到临时游戏对象
        temp_game = Game((self.rows, self.cols), board=[list(row) for row in state], targets=self.targets)
        temp_game.check_win()  # 调用check_win方法更新win属性
        return temp_game.win  # 返回win属性的值

    def get_blocks(self, state):
        # 获取所有非零且非墙体方块
        blocks = set()
        for row in state:
            blocks.update(row)
        blocks.discard(0)
        blocks.discard(99)  # 排除墙体
        return blocks

    def move_block(self, state, block, direction):
        # 尝试移动方块，返回新状态
        # 复制状态
        new_state = [list(row) for row in state]
        # 找到方块的所有位置
        block_positions = []
        for i in range(self.rows):
            for j in range(self.cols):
                if new_state[i][j] == block:
                    block_positions.append((i, j))
        # 计算新位置
        new_positions = []
        if direction == "up":
            new_positions = [(i-1, j) for (i, j) in block_positions]
        elif direction == "down":
            new_positions = [(i+1, j) for (i, j) in block_positions]
        elif direction == "left":
            new_positions = [(i, j-1) for (i, j) in block_positions]
        elif direction == "right":
            new_positions = [(i, j+1) for (i, j) in block_positions]
        # 检查移动是否合法
        for (i, j) in new_positions:
            if i < 0 or i >= self.rows or j < 0 or j >= self.cols:
                return None
            if new_state[i][j] != 0 and new_state[i][j] != block:
                return None
        # 执行移动
        for (i, j) in block_positions:
            new_state[i][j] = 0
        for (i, j) in new_positions:
            new_state[i][j] = block
        return tuple(tuple(row) for row in new_state)

    def format_solution(self, solution):
        # 格式化解决方案为易读的步骤
        if not solution:
            return "无解"
        steps = []
        direction_map = {
            "up": "上",
            "down": "下",
            "left": "左",
            "right": "右"
        }
        for block, direction in solution:
            steps.append(f"{block}{direction_map[direction]}")
        # 使用换行符分隔步骤，以便在侧边栏中正确显示
        return "\n".join(steps)