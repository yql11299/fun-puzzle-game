import pygame
from typing import List, Tuple, Dict, Set

class Game:
    def __init__(self, board_size: Tuple[int, int], board=None, targets=None, mode="solve"):
        self.board_size = board_size
        self.rows, self.cols = board_size
        if board is None:
            self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        else:
            self.board = board
        # 初始默认左上角为起点，右下角为终点
        self.targets = targets or [(0, 0), (self.rows-1, self.cols-1)]
        # 明确区分起点和终点
        self.start_point = self.targets[0]
        self.end_point = self.targets[1]
        self.cell_size = 80
        self.margin = 50
        # 参考game2048设计的颜色方案
        self.colors = {
            0: (238, 228, 218),  # 空白格子
            1: (255, 87, 34),    # 目标1 (鲜艳的橙色)
            2: (63, 81, 181),    # 目标2 (深蓝色)
            3: (76, 175, 80),    # 方块3 (绿色)
            4: (255, 235, 59),   # 方块4 (黄色)
            5: (255, 152, 0),    # 方块5 (橙色)
            6: (156, 39, 176),   # 方块6 (紫色)
            7: (0, 188, 212),    # 方块7 (青色)
            8: (233, 30, 99),    # 方块8 (粉红色)
            9: (121, 85, 72),    # 方块9 (棕色)
        }
        # 使用支持中文的字体
        try:
            # 尝试加载系统中文字体
            self.font = pygame.font.SysFont(["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"], 36)
        except:
            # 如果加载失败，使用默认字体
            self.font = pygame.font.Font(None, 36)
        self.selected_block = None
        self.win = False
        self.mode = mode  # 'create' for level creation, 'solve' for solving
        # 当前选中的格子位置
        self.selected_cell = (0, 0) if self.rows > 0 and self.cols > 0 else None
        # 当前选中的方块
        self.selected_block = None
        # 棋盘锁定状态
        self.board_locked = False

    def draw(self, screen):
        # 绘制棋盘
        for i in range(self.rows):
            for j in range(self.cols):
                x = self.margin + j * self.cell_size
                y = self.margin + i * self.cell_size
                color = self.colors.get(self.board[i][j], (128, 128, 128))
                # 绘制带圆角的方块
                pygame.draw.rect(screen, color, (x, y, self.cell_size, self.cell_size), border_radius=4)
                pygame.draw.rect(screen, (0, 0, 0), (x, y, self.cell_size, self.cell_size), 2, border_radius=4)
                # 绘制数字
                if self.board[i][j] != 0:
                    text = self.font.render(str(self.board[i][j]), True, (0, 0, 0))
                    screen.blit(text, (x + self.cell_size//2 - text.get_width()//2, 
                                      y + self.cell_size//2 - text.get_height()//2))
                # 绘制起点和终点标记
                if (i, j) == self.start_point:
                    # 绘制起点标记 (绿色)
                    pygame.draw.circle(screen, (0, 255, 0), (x + self.cell_size//2, y + self.cell_size//2), 10)
                    text = self.font.render("S", True, (0, 0, 0))
                    screen.blit(text, (x + self.cell_size//2 - text.get_width()//2, 
                                      y + self.cell_size//2 - text.get_height()//2))
                elif (i, j) == self.end_point:
                    # 绘制终点标记 (红色)
                    pygame.draw.circle(screen, (255, 0, 0), (x + self.cell_size//2, y + self.cell_size//2), 10)
                    text = self.font.render("E", True, (0, 0, 0))
                    screen.blit(text, (x + self.cell_size//2 - text.get_width()//2, 
                                      y + self.cell_size//2 - text.get_height()//2))
        
        # 框选相同数字的格子
        if self.mode != "create":  # 只在解题模式下显示
            # 找出所有非零数字及其位置
            block_positions = {}
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.board[i][j] != 0:
                        num = self.board[i][j]
                        if num not in block_positions:
                            block_positions[num] = []
                        block_positions[num].append((i, j))
            
            # 为每个数字绘制边框
            for num, positions in block_positions.items():
                if len(positions) > 1:  # 只框选包含多个格子的方块
                    # 计算边框的边界
                    min_i = min(pos[0] for pos in positions)
                    max_i = max(pos[0] for pos in positions)
                    min_j = min(pos[1] for pos in positions)
                    max_j = max(pos[1] for pos in positions)
                    
                    # 计算边框的位置和大小
                    x = self.margin + min_j * self.cell_size
                    y = self.margin + min_i * self.cell_size
                    width = (max_j - min_j + 1) * self.cell_size
                    height = (max_i - min_i + 1) * self.cell_size
                    
                    # 绘制边框
                    pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height), 3, border_radius=6)
        # 绘制目标点
        for (i, j) in self.targets:
            x = self.margin + j * self.cell_size
            y = self.margin + i * self.cell_size
            pygame.draw.circle(screen, (255, 255, 0), (x + self.cell_size//2, y + self.cell_size//2), 10)
        # 绘制选中的格子
        if self.selected_cell:
            i, j = self.selected_cell
            x = self.margin + j * self.cell_size
            y = self.margin + i * self.cell_size
            pygame.draw.rect(screen, (255, 255, 0), (x, y, self.cell_size, self.cell_size), 4)
        # 显示胜利信息
        if self.win:
            text = self.font.render("游戏胜利！", True, (255, 0, 0))
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, self.margin//2))
        # 显示棋盘锁定状态
        if self.board_locked and self.mode == "solve":
            text = self.font.render("棋盘已锁定，按S键自动求解", True, (255, 0, 0))
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, self.margin//2 + 40))

    def handle_click(self, pos):
        # 处理鼠标点击
        x, y = pos
        if (x < self.margin or x > self.margin + self.cols * self.cell_size or 
           y < self.margin or y > self.margin + self.rows * self.cell_size):
            return False
        j = (x - self.margin) // self.cell_size
        i = (y - self.margin) // self.cell_size
        if 0 <= i < self.rows and 0 <= j < self.cols:
            self.selected_cell = (i, j)
            if self.board[i][j] != 0:
                self.selected_block = self.board[i][j]
            else:
                self.selected_block = None
            return True
        return False

    def handle_keyboard(self, event):
        # 无论哪种模式，Q和E键都可以设置起点和终点
        if event.key == pygame.K_q:
            # Q键设置起点
            if self.selected_cell:
                self.set_start_point(self.selected_cell)
                print(f"已设置起点: {self.selected_cell}")
        elif event.key == pygame.K_e:
            # E键设置终点
            if self.selected_cell:
                self.set_end_point(self.selected_cell)
                print(f"已设置终点: {self.selected_cell}")

        if self.mode == "create":
            # 出题模式下的键盘处理
            if self.board_locked:
                # 棋盘已锁定，不允许编辑
                return
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                          pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                # 数字键设置方块值
                if self.selected_cell:
                    i, j = self.selected_cell
                    self.board[i][j] = event.key - pygame.K_0
            elif event.key == pygame.K_0:
                # 0键清除方块值
                if self.selected_cell:
                    i, j = self.selected_cell
                    self.board[i][j] = 0
            # 方向键仍然可以移动选中的格子
            elif event.key == pygame.K_UP:
                if self.selected_cell:
                    i, j = self.selected_cell
                    if i > 0:
                        self.selected_cell = (i-1, j)
            elif event.key == pygame.K_DOWN:
                if self.selected_cell:
                    i, j = self.selected_cell
                    if i < self.rows - 1:
                        self.selected_cell = (i+1, j)
            elif event.key == pygame.K_LEFT:
                if self.selected_cell:
                    i, j = self.selected_cell
                    if j > 0:
                        self.selected_cell = (i, j-1)
            elif event.key == pygame.K_RIGHT:
                if self.selected_cell:
                    i, j = self.selected_cell
                    if j < self.cols - 1:
                        self.selected_cell = (i, j+1)
            return

        # 解题模式下的键盘处理
        # 处理键盘事件
        if event.key == pygame.K_UP:
            # 上移选中的格子
            if self.selected_cell:
                i, j = self.selected_cell
                if i > 0:
                    self.selected_cell = (i-1, j)
                    self.selected_block = self.board[i-1][j] if self.board[i-1][j] != 0 else None
        elif event.key == pygame.K_DOWN:
            # 下移选中的格子
            if self.selected_cell:
                i, j = self.selected_cell
                if i < self.rows - 1:
                    self.selected_cell = (i+1, j)
                    self.selected_block = self.board[i+1][j] if self.board[i+1][j] != 0 else None
        elif event.key == pygame.K_LEFT:
            # 左移选中的格子
            if self.selected_cell:
                i, j = self.selected_cell
                if j > 0:
                    self.selected_cell = (i, j-1)
                    self.selected_block = self.board[i][j-1] if self.board[i][j-1] != 0 else None
        elif event.key == pygame.K_RIGHT:
            # 右移选中的格子
            if self.selected_cell:
                i, j = self.selected_cell
                if j < self.cols - 1:
                    self.selected_cell = (i, j+1)
                    self.selected_block = self.board[i][j+1] if self.board[i][j+1] != 0 else None
        elif event.key == pygame.K_w:
            # 上移选中的方块
            self.move_block("up")
        elif event.key == pygame.K_s:
            # 下移选中的方块
            self.move_block("down")
        elif event.key == pygame.K_a:
            # 左移选中的方块
            self.move_block("left")
        elif event.key == pygame.K_d:
            # 右移选中的方块
            self.move_block("right")
        elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                          pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
            # 数字键选择方块
            self.selected_block = event.key - pygame.K_0
            # 查找并选中该数字的第一个出现位置
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.board[i][j] == self.selected_block:
                        self.selected_cell = (i, j)
                        return
        elif event.key == pygame.K_0:
            # 0键取消选择
            self.selected_block = None

    def move_block(self, direction):
        # 移动选中的方块
        if self.selected_block is None or self.selected_block == 0:
            return False

        # 找到方块的所有位置
        block_positions = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == self.selected_block:
                    block_positions.append((i, j))

        # 计算移动后的新位置
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
        if not self.is_move_valid(block_positions, new_positions):
            return False

        # 执行移动
        for (i, j) in block_positions:
            self.board[i][j] = 0
        for (i, j) in new_positions:
            self.board[i][j] = self.selected_block
            # 更新选中的位置
            if self.selected_cell in block_positions:
                idx = block_positions.index(self.selected_cell)
                self.selected_cell = new_positions[idx]

        # 检查胜利条件
        self.check_win()
        return True        

    def is_move_valid(self, old_positions, new_positions):
        # 检查移动是否合法
        # 1. 所有新位置必须在棋盘内
        for (i, j) in new_positions:
            if i < 0 or i >= self.rows or j < 0 or j >= self.cols:
                return False
        # 2. 所有新位置必须是空的或属于同一个方块
        for (i, j) in new_positions:
            if self.board[i][j] != 0 and self.board[i][j] != self.selected_block:
                return False
        return True

    def is_board_valid(self):
        # 检查棋盘是否有效（方块连通性等）
        # 获取所有非零方块
        blocks = set()
        for row in self.board:
            blocks.update(row)
        blocks.discard(0)

        # 检查每个方块是否连通
        for block in blocks:
            positions = []
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.board[i][j] == block:
                        positions.append((i, j))
            if not self.is_block_connected(positions):
                return False
        return True

    def is_block_connected(self, positions):
        # 检查方块是否连通
        if not positions:
            return True
        visited = set()
        queue = [positions[0]]
        visited.add(positions[0])
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        while queue:
            i, j = queue.pop(0)
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if (ni, nj) in positions and (ni, nj) not in visited:
                    visited.add((ni, nj))
                    queue.append((ni, nj))
        return len(visited) == len(positions)

    def check_win(self):
        # 检查是否胜利：两个目标点之间有一条连通的路径
        start, end = self.targets
        visited = set()
        if self.bfs(start, end, visited):
            self.win = True
        else:
            self.win = False

    def get_targets(self):
        # 获取目标点
        return self.targets

    def set_start_point(self, point):
        # 设置起点
        self.start_point = point
        self.targets = [self.start_point, self.end_point]

    def set_end_point(self, point):
        # 设置终点
        self.end_point = point
        self.targets = [self.start_point, self.end_point]

    def bfs(self, start, end, visited):
        # BFS算法检查两个点是否连通
        # 通路上所有格子（包括起点和终点）必须是空位
        if start == end:
            # 起点和终点相同，检查是否为空位
            return self.board[start[0]][start[1]] == 0
        
        # 检查起点和终点是否为空位
        if self.board[start[0]][start[1]] != 0 or self.board[end[0]][end[1]] != 0:
            return False
        
        queue = [start]
        visited.add(start)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        while queue:
            i, j = queue.pop(0)
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                    if (ni, nj) == end:
                        return True
                    # 只允许空位作为通路的一部分
                    if self.board[ni][nj] == 0 and (ni, nj) not in visited:
                        visited.add((ni, nj))
                        queue.append((ni, nj))
        return False

    def get_state(self):
        # 获取当前游戏状态（用于求解器）
        return tuple(tuple(row) for row in self.board)