from game import Game
from typing import List, Tuple, Dict, Set, Optional
from collections import deque
import heapq
from constants import DIRECTION_MAP

class Solver:
    def __init__(self, game: Game):
        self.game = game
        self.rows = game.rows
        self.cols = game.cols
        self.targets = game.targets
        # 初始化时不预计算目标位置
        # 删除了所有与A*算法和连通性启发式算法相关的实现

    def get_state(self):
        # 获取当前游戏状态
        return tuple(tuple(row) for row in self.game.board)

    def is_goal_state(self, state):
        # 检查是否为目标状态
        # 直接实现BFS逻辑，避免创建Game对象和额外的函数调用开销
        start_point = self.game.start_point
        end_point = self.game.end_point
        
        if not start_point or not end_point:
            return False
            
        # BFS算法检查两个点是否连通
        # 通路上所有格子（包括起点和终点）必须是空位
        # 检查起点和终点是否为空位
        # 注意：起点和终点必须是空位才能形成有效的路径
        start_valid = state[start_point[0]][start_point[1]] == 0
        end_valid = state[end_point[0]][end_point[1]] == 0
        
        if not start_valid or not end_valid:
            return False
            
        if start_point == end_point:
            # 起点和终点相同，且都为空位
            return True
        
        # 使用更高效的deque作为队列
        from collections import deque
        visited = set()
        queue = deque([start_point])
        visited.add(start_point)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        rows = len(state)
        cols = len(state[0]) if rows > 0 else 0
        
        while queue:
            i, j = queue.popleft()  # 使用popleft提高效率
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < rows and 0 <= nj < cols:
                    if (ni, nj) == end_point:
                        return True
                    # 只允许空位作为通路的一部分，不允许墙体或方块
                    if state[ni][nj] == 0 and (ni, nj) not in visited:
                        visited.add((ni, nj))
                        queue.append((ni, nj))
        return False
        
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
        # 添加自动求解时间到结果中
        solve_time = self.game.get_auto_solve_time_formatted()
        steps.append(f"\n求解时间: {solve_time}")
        # 使用换行符分隔步骤，以便在侧边栏中正确显示
        return "\n".join(steps)
        
    def solve(self):
        """使用BFS暴力搜索算法求解华容道，保证找到最短路径解
        
        返回值:
        - 如果有解，返回方块移动的序列
        - 如果无解，返回None
        """
        # 调用BFS求解方法
        return self.solve_with_bfs()
    def solve_with_bfs(self):
        """使用BFS暴力搜索算法求解华容道，保证找到最短路径解
        
        返回值:
        - 如果有解，返回方块移动的序列
        - 如果无解，返回None
        """
        # 开始自动求解计时器
        self.game.start_auto_solve_timer()
        
        start_state = self.get_state()
        if self.is_goal_state(start_state):
            # 停止自动求解计时器
            self.game.stop_auto_solve_timer()
            return []
            
        # 初始化队列，用于BFS搜索
        # 队列元素格式：(状态, 到达该状态的路径)
        queue = deque()
        queue.append((start_state, []))
        
        # 使用更高效的visited实现，将状态转换为字符串以提高哈希效率
        visited = set()
        start_state_str = str(start_state)
        visited.add(start_state_str)
        
        while queue:
            # 取出队列中的第一个元素
            current_state, current_path = queue.popleft()
            
            # 尝试所有可能的移动
            blocks = self.get_blocks(current_state)
            for block in blocks:
                for direction in ["up", "down", "left", "right"]:
                    # 尝试移动方块
                    new_state = self.move_block(current_state, block, direction)
                    if new_state:
                        new_state_str = str(new_state)
                        if new_state_str not in visited:
                            # 生成新的路径
                            new_path = current_path + [(block, direction)]
                            
                            # 检查是否达到目标状态
                            if self.is_goal_state(new_state):
                                # 停止自动求解计时器
                                self.game.stop_auto_solve_timer()
                                return new_path
                            
                            # 将新状态加入队列和已访问集合
                            queue.append((new_state, new_path))
                            visited.add(new_state_str)
                        
        # 停止自动求解计时器（无解的情况）
        self.game.stop_auto_solve_timer()
        return None  # 无解