import pygame
import time
from typing import List, Tuple, Dict, Set
from constants import *
from utils import get_block_shape, are_shapes_equal, get_block_positions, calculate_block_bounds, is_position_in_board

class Game:
    def __init__(self, board_size: Tuple[int, int], board=None, targets=None, mode="solve"):
        self.board_size = board_size
        self.rows, self.cols = board_size
        self.board = self._initialize_board(board)
        # 初始化目标点
        self._initialize_targets(targets)
        # 形状到颜色的映射字典，根据形状特征生成颜色
        self.shape_color_map = {}
        self.cell_size = CELL_SIZE
        self.margin = MARGIN
        # 颜色方案
        self.colors = COLORS
        # 字体设置
        self.font = get_font()
        self.selected_block = None
        self.win = False
        self.mode = mode  # 'create' for level creation, 'solve' for solving
        # 当前选中的格子位置
        self.selected_cell = (0, 0) if self.rows > 0 and self.cols > 0 else None
        # 当前选中的方块
        self.selected_block = None
        # 棋盘锁定状态
        self.board_locked = False
        # 出题完成标记
        self.level_complete = False
        # 用于输入多位数的缓冲区
        self.number_input_buffer = ""
        # 用于存储每个格子的颜色
        self.cell_colors = {}
        # 计时器相关属性
        self._initialize_timers()
        
    def _initialize_board(self, board):
        # 初始化棋盘
        if board is None:
            return [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        else:
            return board
            
    def _initialize_targets(self, targets):
        # 初始化目标点
        # 初始默认左上角为起点，右下角为终点
        self.targets = targets or [(0, 0), (self.rows-1, self.cols-1)]
        # 明确区分起点和终点
        self.start_point = self.targets[0]
        self.end_point = self.targets[1] if len(self.targets) > 1 else None
        
    def _initialize_timers(self):
        # 初始化计时器相关属性
        self.user_solve_start_time = None  # 用户求解开始时间
        self.user_solve_end_time = None    # 用户求解结束时间
        self.auto_solve_start_time = None  # 自动求解开始时间
        self.auto_solve_end_time = None    # 自动求解结束时间

    def draw(self, screen):
        # 显示用户求解计时器（仅在解题模式下显示）
        if self.mode == "solve" and self.user_solve_start_time:
            time_text = self.font.render(f"用时: {self.get_user_solve_time_formatted()}", True, (0, 0, 0))
            screen.blit(time_text, (self.margin, 10))
        
        # 绘制棋盘
        self._draw_board(screen)
        
        # 绘制选中的格子
        if self.selected_cell:
            self._draw_selected_cell(screen)
            
        # 显示胜利信息
        if self.win:
            text = self.font.render(TEXT_MESSAGES["WIN"], True, RED)
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, self.margin//2))
        # 显示棋盘锁定状态
        if self.board_locked and self.mode == "solve":
            text = self.font.render(TEXT_MESSAGES["BOARD_LOCKED"], True, RED)
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, self.margin//2 + 40))

    def _draw_board(self, screen):
        # 绘制棋盘格子
        self._draw_board_cells(screen)
        
        # 绘制起点和终点标记
        self._draw_start_end_markers(screen)
        
        # 绘制数字
        self._draw_numbers(screen)
        
        # 绘制起点和终点的字母标记
        self._draw_start_end_labels(screen)
        
        # 框选相同数字的格子
        if self.mode != "create":  # 只在解题模式下显示
            self._draw_block_borders(screen)
        # 绘制目标点
        self._draw_targets(screen)
        
    def _draw_board_cells(self, screen):
        # 绘制棋盘格子
        for i in range(self.rows):
            for j in range(self.cols):
                x = self.margin + j * self.cell_size
                y = self.margin + i * self.cell_size
                # 检查是否有自定义颜色
                if (i, j) in self.cell_colors:
                    color = self.cell_colors[(i, j)]
                elif self.board[i][j] == 0:
                    # 空白格子使用预定义颜色
                    color = self.colors.get(self.board[i][j], GRAY)
                elif self.board[i][j] == 99:
                    # 墙体方块涂黑
                    color = (0, 0, 0)
                elif self.mode == "create" and not self.level_complete:
                    # 出题模式下且未完成时，使用默认颜色
                    color = DEFAULT_COLOR
                else:
                    # 解题模式或出题完成后，根据形状获取颜色
                    color = self.get_block_color(self.board[i][j])
                # 绘制带圆角的方块
                pygame.draw.rect(screen, color, (x, y, self.cell_size, self.cell_size), border_radius=4)
                pygame.draw.rect(screen, (0, 0, 0), (x, y, self.cell_size, self.cell_size), 2, border_radius=4)
                
    def _draw_start_end_markers(self, screen):
        # 绘制起点和终点标记 (在方块之上，数字之下)
        for i in range(self.rows):
            for j in range(self.cols):
                x = self.margin + j * self.cell_size
                y = self.margin + i * self.cell_size
                if (i, j) == self.start_point:
                    # 绘制起点标记 (绿色) 在左上角
                    pygame.draw.circle(screen, (0, 255, 0), (x + 5, y + 5), 5)
                elif (i, j) == self.end_point:
                    # 绘制终点标记 (红色) 在左上角
                    pygame.draw.circle(screen, (255, 0, 0), (x + 5, y + 5), 5)
                    
    def _draw_numbers(self, screen):
        # 绘制数字，但不在墙体上显示 (在最上层)
        for i in range(self.rows):
            for j in range(self.cols):
                x = self.margin + j * self.cell_size
                y = self.margin + i * self.cell_size
                if self.board[i][j] != 0 and self.board[i][j] != 99:
                    text = self.font.render(str(self.board[i][j]), True, (0, 0, 0))
                    screen.blit(text, (x + self.cell_size//2 - text.get_width()//2, 
                                      y + self.cell_size//2 - text.get_height()//2))
                    
    def _draw_start_end_labels(self, screen):
        # 绘制起点和终点的字母标记 (在数字旁边)
        for i in range(self.rows):
            for j in range(self.cols):
                x = self.margin + j * self.cell_size
                y = self.margin + i * self.cell_size
                if (i, j) == self.start_point:
                    text = self.font.render("S", True, (0, 0, 0))
                    screen.blit(text, (x + self.cell_size - text.get_width() - 5, 5))
                elif (i, j) == self.end_point:
                    text = self.font.render("E", True, (0, 0, 0))
                    screen.blit(text, (x + self.cell_size - text.get_width() - 5, 5))
                    
    def _draw_targets(self, screen):
        # 绘制目标点
        for (i, j) in self.targets:
            x = self.margin + j * self.cell_size
            y = self.margin + i * self.cell_size
            pygame.draw.circle(screen, (255, 255, 0), (x + self.cell_size//2, y + self.cell_size//2), 10)
            
    def _draw_block_borders(self, screen):
        # 出题模式下且未完成时，不绘制边框
        if self.mode == "create" and not self.level_complete:
            return
        # 找出所有非零且非墙体数字及其位置
        block_positions = {}
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != 0 and self.board[i][j] != 99:
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
                
    def _draw_selected_cell(self, screen):
        # 绘制选中的格子
        i, j = self.selected_cell
        x = self.margin + j * self.cell_size
        y = self.margin + i * self.cell_size
        pygame.draw.rect(screen, (255, 255, 0), (x, y, self.cell_size, self.cell_size), 4)

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

    # 方块形状和颜色相关方法
    def get_block_shape(self, block_number):
        # 获取方块的形状特征（考虑旋转等价性）
        return get_block_shape(self.board, block_number, self.rows, self.cols)
        
    def are_shapes_equal(self, shape1, shape2):
        # 判断两个形状是否相同（考虑旋转等价性）
        return are_shapes_equal(shape1, shape2)
        
    def get_block_color(self, block_number):
        # 出题模式下且未完成时，返回默认颜色
        if self.mode == "create" and not self.level_complete:
            return DEFAULT_COLOR
        # 根据形状获取方块颜色
        shape = self.get_block_shape(block_number)
        
        # 如果形状为None，返回默认颜色
        if shape is None:
            return GRAY
            
        # 如果这个形状还没有颜色映射，为其分配一个颜色
        if shape not in self.shape_color_map:
            # 检查是否已经有相同形状的方块，如果有则使用相同颜色
            # 遍历所有已分配的形状颜色对
            for existing_shape, color in self.shape_color_map.items():
                if self.are_shapes_equal(shape, existing_shape):
                    # 找到了相同形状，使用相同颜色
                    self.shape_color_map[shape] = color
                    return color
            
            # 如果没有找到相同形状，分配新颜色
            color_index = len(self.shape_color_map) % len(SHAPE_COLORS)
            self.shape_color_map[shape] = SHAPE_COLORS[color_index]
        
        return self.shape_color_map[shape]
        
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
            self._handle_create_mode_keyboard(event)
        else:
            self._handle_solve_mode_keyboard(event)
            
    def _handle_create_mode_keyboard(self, event):
        # 出题模式下的键盘处理
        if self.board_locked:
            # 检查棋盘是否已锁定，不允许编辑
            return
        # 处理数字键输入
        if self._handle_digit_input(event):
            return
        # 非数字键按下时确认当前输入
        self._confirm_number_input()
        
        if event.key == pygame.K_BACKSPACE:
            # 退格键删除最后一个数字
            if self.number_input_buffer:
                self.number_input_buffer = self.number_input_buffer[:-1]
        elif event.key == pygame.K_0:
            # 0键清除方块值
            if self.selected_cell:
                i, j = self.selected_cell
                self.board[i][j] = 0
                # 清除对应的cell_colors
                if (i, j) in self.cell_colors:
                    del self.cell_colors[(i, j)]
            # 0键也触发数字输入确认
            self._confirm_number_input()
        elif event.key == pygame.K_b:
            # B键设置墙体
            if self.selected_cell:
                i, j = self.selected_cell
                # 确保墙体不会设置在起点或终点上
                if (i, j) != self.start_point and (i, j) != self.end_point:
                    self.board[i][j] = 99
                    # 立即更新墙体颜色
                    self.cell_colors[i][j] = (0, 0, 0)
            # B键也触发数字输入确认
            self._confirm_number_input()
        elif event.key == pygame.K_RETURN:
            # Enter键完成出题
            if not self.number_input_buffer:
                self.level_complete = True
        # 方向键仍然可以移动选中的格子
        elif event.key == pygame.K_UP:
            if self.selected_cell:
                i, j = self.selected_cell
                if i > 0:
                    self.selected_cell = (i-1, j)
                    self.selected_block = self.board[i-1][j] if self.board[i-1][j] != 0 else None
            # 方向键也触发数字输入确认
            self._confirm_number_input()
        elif event.key == pygame.K_DOWN:
            if self.selected_cell:
                i, j = self.selected_cell
                if i < self.rows - 1:
                    self.selected_cell = (i+1, j)
                    self.selected_block = self.board[i+1][j] if self.board[i+1][j] != 0 else None
            # 方向键也触发数字输入确认
            self._confirm_number_input()
        elif event.key == pygame.K_LEFT:
            if self.selected_cell:
                i, j = self.selected_cell
                if j > 0:
                    self.selected_cell = (i, j-1)
                    self.selected_block = self.board[i][j-1] if self.board[i][j-1] != 0 else None
            # 方向键也触发数字输入确认
            self._confirm_number_input()
        elif event.key == pygame.K_RIGHT:
            if self.selected_cell:
                i, j = self.selected_cell
                if j < self.cols - 1:
                    self.selected_cell = (i, j+1)
                    self.selected_block = self.board[i][j+1] if self.board[i][j+1] != 0 else None
            # 方向键也触发数字输入确认
            self._confirm_number_input()
                    
    def _confirm_number_input(self):
        # 确认当前输入的数字
        if self.number_input_buffer and self.selected_cell:
            # 确认多位数输入，添加错误处理
            try:
                num = int(self.number_input_buffer)
                # 限制数字范围在1-81之间
                if 1 <= num <= 81:
                    i, j = self.selected_cell
                    # 允许在起点和终点位置设置方块值
                    self.board[i][j] = num
                    # 清除对应的cell_colors
                    if (i, j) in self.cell_colors:
                        del self.cell_colors[(i, j)]
            except ValueError:
                # 如果转换失败，清空缓冲区
                print("无效的数字输入")
            # 清空输入缓冲区
            self.number_input_buffer = ""
                    
    def _handle_digit_input(self, event):
        # 处理数字键输入
        if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                      pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
            # 开始或继续输入多位数
            if self.selected_cell:
                # 获取按下的数字，并确保只提取数字部分
                key_name = pygame.key.name(event.key)
                # 过滤出数字字符
                digit = ''.join(filter(str.isdigit, key_name))
                if digit:  # 确保确实找到了数字
                    self.number_input_buffer += digit
                    # 如果是单个数字，立即显示到棋盘上
                    if len(self.number_input_buffer) == 1:
                        i, j = self.selected_cell
                        self.board[i][j] = int(self.number_input_buffer)
                        # 清除对应的cell_colors
                        if (i, j) in self.cell_colors:
                            del self.cell_colors[(i, j)]
            return True
        elif pygame.K_KP1 <= event.key <= pygame.K_KP9:
            # 小键盘数字输入
            if self.selected_cell:
                # 获取按下的数字
                key_name = pygame.key.name(event.key)
                # 过滤出数字字符
                digit = ''.join(filter(str.isdigit, key_name))
                if digit:  # 确保确实找到了数字
                    self.number_input_buffer += digit
                    # 如果是单个数字，立即显示到棋盘上
                    if len(self.number_input_buffer) == 1:
                        i, j = self.selected_cell
                        self.board[i][j] = int(self.number_input_buffer)
                        # 清除对应的cell_colors
                        if (i, j) in self.cell_colors:
                            del self.cell_colors[(i, j)]
            return True
        elif event.key == pygame.K_KP0:
            # 小键盘0输入
            if self.selected_cell:
                key_name = pygame.key.name(event.key)
                # 过滤出数字字符
                digit = ''.join(filter(str.isdigit, key_name))
                if digit:  # 确保确实找到了数字
                    self.number_input_buffer += digit
                    # 如果是单个数字，立即显示到棋盘上
                    if len(self.number_input_buffer) == 1:
                        i, j = self.selected_cell
                        self.board[i][j] = int(self.number_input_buffer)
                        # 清除对应的cell_colors
                        if (i, j) in self.cell_colors:
                            del self.cell_colors[(i, j)]
            return True
        return False
                    
    def _handle_solve_mode_keyboard(self, event):
        # 解题模式下的键盘处理
        # 处理键盘事件
        if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
            # 处理方向键移动选中的格子
            self._handle_direction_keys(event.key)
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
        elif pygame.K_KP1 <= event.key <= pygame.K_KP9:
            # 小键盘数字键选择方块
            self.selected_block = (event.key - pygame.K_KP0) + 9
            # 查找并选中该数字的第一个出现位置
            for i in range(self.rows):
                for j in range(self.cols):
                    if self.board[i][j] == self.selected_block:
                        self.selected_cell = (i, j)
                        return
        elif event.key == pygame.K_0:
            # 0键取消选择
            self.selected_block = None
            
    def _handle_direction_keys(self, key):
        # 处理方向键移动选中的格子
        if key == pygame.K_UP:
            # 上移选中的格子
            if self.selected_cell:
                i, j = self.selected_cell
                if i > 0:
                    self.selected_cell = (i-1, j)
                    self.selected_block = self.board[i-1][j] if self.board[i-1][j] != 0 else None
        elif key == pygame.K_DOWN:
            # 下移选中的格子
            if self.selected_cell:
                i, j = self.selected_cell
                if i < self.rows - 1:
                    self.selected_cell = (i+1, j)
                    self.selected_block = self.board[i+1][j] if self.board[i+1][j] != 0 else None
        elif key == pygame.K_LEFT:
            # 左移选中的格子
            if self.selected_cell:
                i, j = self.selected_cell
                if j > 0:
                    self.selected_cell = (i, j-1)
                    self.selected_block = self.board[i][j-1] if self.board[i][j-1] != 0 else None
        elif key == pygame.K_RIGHT:
            # 右移选中的格子
            if self.selected_cell:
                i, j = self.selected_cell
                if j < self.cols - 1:
                    self.selected_cell = (i, j+1)
                    self.selected_block = self.board[i][j+1] if self.board[i][j+1] != 0 else None

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
        # 2. 所有新位置必须是空的或属于同一个方块，不能是墙体
        for (i, j) in new_positions:
            # 新位置不能是墙体
            if self.board[i][j] == 99:
                return False
            # 新位置必须是空的或属于同一个方块
            if self.board[i][j] != 0 and self.board[i][j] != self.selected_block:
                return False
        # 3. 墙体不可移动
        if self.selected_block == 99:
            return False
        return True

    def is_board_valid(self):
        # 检查棋盘是否有效（方块连通性等）
        # 获取所有非零方块
        blocks = set()
        for row in self.board:
            blocks.update(row)
        blocks.discard(0)
        blocks.discard(99)  # 不检查墙体的连通性

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
        # 检查是否胜利：起点和终点之间有一条连通的路径
        if not self.start_point or not self.end_point:
            self.win = False
            return
            
        visited = set()
        if self._is_path_connected(self.start_point, self.end_point, visited):
            self.win = True
            # 如果游戏胜利且计时器正在运行，记录结束时间
            if self.user_solve_start_time and not self.user_solve_end_time:
                self.user_solve_end_time = time.time()
        else:
            self.win = False

    def get_targets(self):
        # 获取目标点
        return self.targets

    def set_start_point(self, point):
        # 设置起点
        self.start_point = point
        # 确保targets列表中包含所有目标点
        if not self.targets:
            self.targets = [self.start_point]
        elif self.start_point not in self.targets:
            self.targets[0] = self.start_point

    def set_end_point(self, point):
        # 设置终点
        self.end_point = point
        # 确保targets列表中包含所有目标点
        if not self.targets:
            self.targets = [self.start_point, self.end_point]
        elif len(self.targets) < 2:
            self.targets.append(self.end_point)
        elif self.end_point not in self.targets:
            self.targets[1] = self.end_point

    def _is_path_connected(self, start, end, visited):
        # BFS算法检查两个点是否连通
        # 通路上所有格子（包括起点和终点）必须是空位
        # 检查起点和终点是否为空位
        # 注意：起点和终点必须是空位才能形成有效的路径
        start_valid = self.board[start[0]][start[1]] == 0
        end_valid = self.board[end[0]][end[1]] == 0
        
        if not start_valid or not end_valid:
            return False
            
        if start == end:
            # 起点和终点相同，且都为空位
            return True
        
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
                    # 只允许空位作为通路的一部分，不允许墙体或方块
                    if self.board[ni][nj] == 0 and (ni, nj) not in visited:
                        visited.add((ni, nj))
                        queue.append((ni, nj))
        return False

    def get_state(self):
        # 获取当前游戏状态（用于求解器）
        return tuple(tuple(row) for row in self.board)
    
    # 计时器管理
    def start_user_solve_timer(self):
        # 开始用户求解计时器
        self.user_solve_start_time = time.time()
        self.user_solve_end_time = None
        self.win = False
        
    def stop_user_solve_timer(self):
        # 停止用户求解计时器
        if self.user_solve_start_time and not self.user_solve_end_time:
            self.user_solve_end_time = time.time()
            
    def start_auto_solve_timer(self):
        # 开始自动求解计时器
        self.auto_solve_start_time = time.time()
        self.auto_solve_end_time = None
        
    def stop_auto_solve_timer(self):
        # 停止自动求解计时器
        if self.auto_solve_start_time and not self.auto_solve_end_time:
            self.auto_solve_end_time = time.time()
            
    def get_user_solve_time(self):
        # 获取用户求解时间（秒）
        if not self.user_solve_start_time:
            return 0
        if self.user_solve_end_time:
            return self.user_solve_end_time - self.user_solve_start_time
        return time.time() - self.user_solve_start_time
        
    def get_auto_solve_time(self):
        # 获取自动求解时间（秒）
        if not self.auto_solve_start_time or not self.auto_solve_end_time:
            return 0
        return self.auto_solve_end_time - self.auto_solve_start_time
        
    def get_formatted_time(self, seconds):
        # 格式化时间为 分:秒.毫秒
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        seconds_int = int(remaining_seconds)
        milliseconds = int((remaining_seconds - seconds_int) * 1000)
        return f"{minutes:02d}:{seconds_int:02d}.{milliseconds:03d}"
        
    def get_user_solve_time_formatted(self):
        # 获取格式化的用户求解时间
        return self.get_formatted_time(self.get_user_solve_time())
        
    def get_auto_solve_time_formatted(self):
        # 获取格式化的自动求解时间
        return self.get_formatted_time(self.get_auto_solve_time())