import pygame
import sys
from game import Game
from solver import Solver
from levels import LevelManager
from constants import *

class KlotskiApp:
    def __init__(self):
        pygame.init()
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        # 字体设置
        self.font = get_font()
        self.level_manager = LevelManager()
        self.game = None
        self.solver = None
        self.game_mode = None
        self.state = "menu"
        self.menu_options = MENU_OPTIONS
        self.selected_option = 0
        self.board_size = DEFAULT_BOARD_SIZE  # 默认棋盘大小
        self.selected_number = 1  # 默认选中的数字
        self.selected_level = 0  # 默认选中的关卡
        self.margin = MARGIN  # 棋盘边距
        # 棋盘大小输入状态
        self.input_rows = ""
        self.input_cols = ""
        self.input_state = "rows"
        self.solution = None
        # 初始化默认的Game对象，避免None值引用问题
        self.game = Game(self.board_size, mode="create")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:
                            self.state = "input_board_size"
                        elif self.selected_option == 1:
                            if self.level_manager.has_levels():
                                self.state = "select_level"
                            else:
                                # 显示提示：题库为空
                                pass
                        elif self.selected_option == 2:
                            pygame.quit()
                            sys.exit()
                elif self.state == "input_board_size":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                    elif event.key == pygame.K_RETURN:
                        try:
                            if self.input_rows and self.input_cols:
                                rows = int(self.input_rows)
                                cols = int(self.input_cols)
                                if 2 <= rows < 10 and 2 <= cols < 10:
                                    self.board_size = (rows, cols)
                                else:
                                    # 显示错误：数字必须在2-9之间
                                    error_text = self.font.render(TEXT_MESSAGES["INVALID_NUMBER"], True, RED)
                                    self.screen.blit(error_text, (self.width//2 - error_text.get_width()//2, 300))
                                    pygame.display.flip()
                                    pygame.time.delay(1000)
                                    return
                            # 直接按回车，使用默认的5x5棋盘
                            self.game = Game(self.board_size, mode="create")
                            self.state = "create_level"
                        except ValueError:
                            # 显示错误：请输入有效数字
                            error_text = self.font.render(TEXT_MESSAGES["INPUT_NUMBER"], True, RED)
                            self.screen.blit(error_text, (self.width//2 - error_text.get_width()//2, 300))
                            pygame.display.flip()
                            pygame.time.delay(1000)
                    elif event.key == pygame.K_TAB:
                        self.input_state = "cols" if self.input_state == "rows" else "rows"
                    elif event.key == pygame.K_BACKSPACE:
                        if self.input_state == "rows":
                            self.input_rows = self.input_rows[:-1] if self.input_rows else ""
                        else:
                            self.input_cols = self.input_cols[:-1] if self.input_cols else ""
                    elif pygame.K_0 <= event.key <= pygame.K_9:
                        digit = chr(event.key)
                        if self.input_state == "rows":
                            self.input_rows += digit
                        else:
                            self.input_cols += digit
                elif self.state == "create_level":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                    elif event.key == pygame.K_s and self.game and self.game.mode == "create":
                        # 保存关卡
                        level_name = f"custom_level_{len(self.level_manager.levels) + 1}"
                        success = self.level_manager.save_level(
                            (self.game.rows, self.game.cols),
                            self.game.board,
                            self.game.targets,
                            level_name
                        )
                        if success:
                            print(f"关卡已保存: {level_name}")
                            # 锁定棋盘，切换到解题模式
                            self.game.board_locked = True
                            self.game.mode = "solve"
                            # 启动用户求解计时器
                            self.game.start_user_solve_timer()
                    elif event.key == pygame.K_SPACE and self.game and (self.game.mode == "solve" or (self.game.mode == "create" and self.game.level_complete)):
                        # 自动求解
                        solver = Solver(self.game)
                        solution = solver.solve()
                        if solution is not None:
                            if len(solution) == 0:
                                self.solution = "初始状态已经是目标状态，无需移动"
                                print("初始状态已经是目标状态，无需移动")
                            else:
                                formatted_solution = solver.format_solution(solution)
                                self.solution = formatted_solution
                                print(f"求解结果: {formatted_solution}")
                        else:
                            self.solution = "无解"
                            print("无解")
                    else:
                        # 传递键盘事件给游戏处理
                        self.game.handle_keyboard(event)
                elif self.state == "select_level":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                    elif event.key == pygame.K_UP:
                        self.selected_level = (self.selected_level - 1) % len(self.level_manager.levels)
                    elif event.key == pygame.K_DOWN:
                        self.selected_level = (self.selected_level + 1) % len(self.level_manager.levels)
                    elif event.key == pygame.K_RETURN:
                        # 选择关卡并进入解题模式
                        if self.level_manager.levels:
                            level_data = self.level_manager.levels[self.selected_level]
                            board_size = level_data["board_size"]
                            board = level_data["board"]
                            targets = level_data["targets"]
                            # 创建新的游戏实例并设置为解题模式
                            self.game = Game(board_size, mode="solve", board=board, targets=targets)
                            self.game.board_locked = True
                            # 启动用户求解计时器
                            self.game.start_user_solve_timer()
                            self.state = "create_level"  # 复用create_level状态进行显示
                # 其他状态的事件处理...

    def draw(self):
        self.screen.fill((240, 240, 240))
        if self.state == "menu":
            # 绘制菜单
            title = self.font.render("华容道游戏", True, (0, 0, 0))
            self.screen.blit(title, (self.width//2 - title.get_width()//2, 100))
            for i, option in enumerate(self.menu_options):
                color = (255, 0, 0) if i == self.selected_option else (0, 0, 0)
                text = self.font.render(option, True, color)
                self.screen.blit(text, (self.width//2 - text.get_width()//2, 200 + i * 50))
        elif self.state == "input_board_size":
            # 绘制棋盘大小输入界面
            title = self.font.render("请输入棋盘大小", True, (0, 0, 0))
            self.screen.blit(title, (self.width//2 - title.get_width()//2, 100))

            row_text = self.font.render("行数: ", True, (0, 0, 0))
            self.screen.blit(row_text, (self.width//2 - 150, 200))
            row_input = self.font.render(self.input_rows, True, (0, 0, 0))
            self.screen.blit(row_input, (self.width//2 - 50, 200))
            if self.input_state == "rows":
                pygame.draw.rect(self.screen, (255, 0, 0), 
                                (self.width//2 - 50, 200, row_input.get_width() + 10, 30), 2)

            col_text = self.font.render("列数: ", True, (0, 0, 0))
            self.screen.blit(col_text, (self.width//2 - 150, 250))
            col_input = self.font.render(self.input_cols, True, (0, 0, 0))
            self.screen.blit(col_input, (self.width//2 - 50, 250))
            if self.input_state == "cols":
                pygame.draw.rect(self.screen, (255, 0, 0), 
                                (self.width//2 - 50, 250, col_input.get_width() + 10, 30), 2)

            hint = self.font.render("按Tab切换输入，Enter确认", True, (100, 100, 100))
            self.screen.blit(hint, (self.width//2 - hint.get_width()//2, 350))
        elif self.state == "create_level":
            # 绘制游戏界面
            if self.game:
                self.game.draw(self.screen)
                
                # 绘制右侧快捷键帮助侧边栏
                sidebar_x = self.margin + self.game.cols * self.game.cell_size + 20
                sidebar_y = self.margin
                sidebar_width = self.width - sidebar_x - self.margin
                sidebar_height = self.height - 2 * self.margin
                
                # 绘制侧边栏背景
                pygame.draw.rect(self.screen, (220, 220, 220), 
                                (sidebar_x, sidebar_y, sidebar_width, sidebar_height), border_radius=4)
                pygame.draw.rect(self.screen, (0, 0, 0), 
                                (sidebar_x, sidebar_y, sidebar_width, sidebar_height), 2, border_radius=4)
                
                # 绘制侧边栏标题
                # 创建一个较小的字体用于侧边栏
                sidebar_font = pygame.font.SysFont(["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"], 24)
                title = sidebar_font.render("快捷键帮助", True, (0, 0, 0))
                self.screen.blit(title, (sidebar_x + sidebar_width//2 - title.get_width()//2, sidebar_y + 10))
                
                # 绘制快捷键说明
                if self.game and self.game.mode == "create":
                    help_texts = HELP_TEXTS["create"]
                else:
                    help_texts = HELP_TEXTS["solve"]
                
                for i, text in enumerate(help_texts):
                    help_text = sidebar_font.render(text, True, (0, 0, 0))
                    self.screen.blit(help_text, (sidebar_x + 10, sidebar_y + 50 + i * 25))
                
                # 显示求解结果
                if hasattr(self, 'solution') and self.solution:
                    solution_title = sidebar_font.render("求解结果:", True, (0, 0, 0))
                    self.screen.blit(solution_title, (sidebar_x + 10, sidebar_y + 50 + len(help_texts) * 25 + 10))
                    
                    # 显示解决方案的步骤（支持多行）
                    solution_lines = self.solution.split('\n')
                    for i, line in enumerate(solution_lines):
                        solution_text = sidebar_font.render(line, True, (0, 0, 0))
                        self.screen.blit(solution_text, (sidebar_x + 10, sidebar_y + 50 + len(help_texts) * 25 + 40 + i * 25))
        elif self.state == "select_level":
            # 绘制关卡选择界面
            title = self.font.render("选择关卡", True, (0, 0, 0))
            self.screen.blit(title, (self.width//2 - title.get_width()//2, 100))
            
            # 绘制关卡列表
            if self.level_manager.levels:
                for i, level in enumerate(self.level_manager.levels):
                    color = (255, 0, 0) if i == self.selected_level else (0, 0, 0)
                    level_name = level["name"]
                    level_size = level["board_size"]
                    level_text = self.font.render(f"{level_name} ({level_size[0]}x{level_size[1]})", True, color)
                    self.screen.blit(level_text, (self.width//2 - level_text.get_width()//2, 200 + i * 50))
                    
                hint = self.font.render("上下方向键选择，Enter确认，Esc返回", True, (100, 100, 100))
                self.screen.blit(hint, (self.width//2 - hint.get_width()//2, self.height - 100))
            else:
                empty_text = self.font.render("题库为空，请先创建关卡", True, (100, 100, 100))
                self.screen.blit(empty_text, (self.width//2 - empty_text.get_width()//2, 300))
                back_hint = self.font.render("按Esc返回菜单", True, (100, 100, 100))
                self.screen.blit(back_hint, (self.width//2 - back_hint.get_width()//2, self.height - 100))
        # 其他状态的绘制...

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    app = KlotskiApp()
    app.run()