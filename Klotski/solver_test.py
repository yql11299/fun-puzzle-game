import time
import sys
import os
import pygame

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Klotski.game import Game
from Klotski.solver import Solver

class SolverTester:
    def __init__(self):
        # 初始化测试器
        pass
    
    def convert_input_board(self, input_board):
        """将用户输入的棋盘格式转换为Game类需要的格式
        
        用户输入格式：
        - 1~81: 代表所属方块
        - 0: 空位
        - -1: 墙体
        
        转换为Game类格式：
        - 1~81: 保持不变
        - 0: 保持不变
        - -1: 转换为99（游戏中墙体的表示）
        """
        rows = len(input_board)
        cols = len(input_board[0]) if rows > 0 else 0
        
        # 初始化转换后的棋盘
        converted_board = []
        
        # 遍历用户输入的棋盘
        for i in range(rows):
            new_row = []
            for j in range(cols):
                cell = input_board[i][j]
                
                if cell == -1:
                    # 墙体转换为99
                    new_row.append(99)
                else:
                    # 其他值保持不变
                    new_row.append(cell)
            converted_board.append(new_row)
        
        return converted_board
    
    def test_solver(self, input_board, start_point=None, end_point=None, enable_graphics=False, time_limit=30):
        """测试求解器并输出结果和时间
        
        参数:
        input_board: 用户提供的二维数组，表示初始棋盘状态
        start_point: 起点坐标，格式为(i, j)，默认为(0, 0)
        end_point: 终点坐标，格式为(i, j)，默认为(rows-1, cols-1)
        enable_graphics: 是否启用图形界面（默认为False，仅用于测试）
        time_limit: 求解时间限制（秒），默认为30秒
        
        返回:
        tuple: (是否有解, 解步骤列表, 求解时间(秒))
        """
        # 确保pygame已初始化
        if not pygame.get_init():
            pygame.init()
            
            # 如果不需要图形界面，可以设置为无头模式
            if not enable_graphics:
                os.environ['SDL_VIDEODRIVER'] = 'dummy'
                pygame.display.set_mode((1, 1))
        
        # 转换用户输入的棋盘格式
        converted_board = self.convert_input_board(input_board)
        
        # 获取棋盘大小
        rows = len(converted_board)
        cols = len(converted_board[0]) if rows > 0 else 0
        
        # 设置默认起点和终点
        if start_point is None:
            start_point = (0, 0)
        if end_point is None:
            end_point = (rows-1, cols-1)
        
        # 设置targets
        targets = [start_point, end_point]
        
        # 创建Game实例
        game = Game((rows, cols), board=converted_board, targets=targets, mode="solve")
        
        # 创建Solver实例
        solver = Solver(game)
        
        # 记录开始时间
        start_time = time.time()
        
        # 使用BFS暴力搜索算法求解
        solution = None
        try:
            solution = solver.solve()
        except KeyboardInterrupt:
            print("求解被用户中断")
            return False, "求解被用户中断", time.time() - start_time
        
        # 记录结束时间
        end_time = time.time()
        solve_time = end_time - start_time
        
        # 检查是否超时
        if solve_time > time_limit:
            return False, f"求解超时（超过{time_limit}秒）", solve_time
        
        # 检查是否有解
        # 修改检查逻辑：空列表表示初始状态已经是目标状态，也是有解的
        has_solution = solution is not None
        
        # 格式化解决方案
        formatted_solution = None
        if has_solution:
            if solution == []:
                formatted_solution = "初始状态已经是目标状态，无需移动"
            else:
                formatted_solution = solver.format_solution(solution)
        
        return has_solution, formatted_solution, solve_time
        
    # 移除了test_solver_connectivity方法，因为我们只保留BFS算法

# 示例用法
if __name__ == "__main__":
    tester = SolverTester()
    
    # 示例1: 简单的3x3棋盘，有解
    print("===== 示例1: 简单的3x3棋盘，有解 =====")
    sample_board1 = [
        [1, 1, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    start_point1 = (0, 2)  # 起点坐标
    end_point1 = (2, 2)    # 终点坐标
    has_solution1, solution1, time1 = tester.test_solver(sample_board1, start_point1, end_point1)
    print(f"有解: {has_solution1}")
    print(f"求解时间: {time1:.4f}秒")
    if has_solution1:
        print(f"解决方案:\n{solution1}")
    print()
    
    # 示例2: 4x4棋盘，有墙体
    print("===== 示例2: 4x4棋盘，有墙体 =====")
    sample_board2 = [
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [-1, -1, -1, 2],
        [0, 0, 0, 0]
    ]
    start_point2 = (0, 0)  # 起点坐标
    end_point2 = (3, 3)    # 终点坐标
    has_solution2, solution2, time2 = tester.test_solver(sample_board2, start_point2, end_point2)
    print(f"有解: {has_solution2}")
    print(f"求解时间: {time2:.4f}秒")
    if has_solution2:
        print(f"解决方案:\n{solution2}")
    print()
    
    # 示例3: 起点和终点被方块占据的情况
    print("===== 示例3: 起点和终点被方块占据的情况 =====")
    sample_board3 = [
        [3, 0, 0],
        [3, 1, 0],
        [0, 0, 2]
    ]
    start_point3 = (0, 0)  # 起点坐标（被方块3占据）
    end_point3 = (2, 2)    # 终点坐标（被方块2占据）
    has_solution3, solution3, time3 = tester.test_solver(sample_board3, start_point3, end_point3)
    print(f"有解: {has_solution3}")
    print(f"求解时间: {time3:.4f}秒")
    if has_solution3:
        print(f"解决方案:\n{solution3}")
    
    # 测试复杂案例（使用BFS算法）
    print("\n\n========== 测试复杂案例 ==========")
    
    # 复杂的棋盘
    print("\n===== 复杂棋盘1，有解 =====")
    sample_board_complex = [
        [1, 1, 1, 1, 2, 3],
        [1, 4, 0, 1, 5, 0],
        [1, 1, 0, 1, 5, 0],
        [6, 7, 0, 6, 0, 0],
        [6, 6, 6, 6, 0, 0]
    ]
    start_point_complex = (4, 0)  # 起点坐标
    end_point_complex = (2, 5)    # 终点坐标
    
    # 测试复杂棋盘
    sample_board_complex = [
        [-1, -1, 1, 2, -1, -1],
        [3, 1, 1, 2, 2, 5],
        [3, 4, 4, 0, 6, 6],
        [0, 4, 0, 0, 0, 0],
        [7, 8, 9, 9, 10, 11],
        [7, 9, 9, 10, 10, 11]
    ]
    start_point_complex = (3, 0)  # 起点坐标
    end_point_complex = (3, 5)    # 终点坐标

    print("\n使用BFS暴力搜索算法求解（时间限制30秒）...")
    has_solution_bfs, solution_bfs, time_bfs = tester.test_solver(
        sample_board_complex, start_point_complex, end_point_complex, time_limit=100)
    print(f"有解: {has_solution_bfs}")
    print(f"求解时间: {time_bfs:.4f}秒")
    if has_solution_bfs:
        print(f"解决方案:\n{solution_bfs}")