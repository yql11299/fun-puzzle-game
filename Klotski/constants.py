# 常量定义文件
import pygame

# 窗口尺寸
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# 游戏标题
GAME_TITLE = "华容道游戏"

# 菜单选项
MENU_OPTIONS = ["出题模式", "解题模式", "退出游戏"]

# 棋盘默认设置
DEFAULT_BOARD_SIZE = (5, 5)
CELL_SIZE = 80
MARGIN = 50

# 颜色定义
# 基本颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (160, 160, 160)
DARK_GRAY = (60, 60, 60)

# 棋盘颜色方案
COLORS = {
    0: (238, 228, 218),  # 空白格子
    99: DARK_GRAY        # 墙体
}

# 形状颜色列表
SHAPE_COLORS = [
    (255, 87, 34),  # 橙色
    (63, 81, 181),  # 深蓝色
    (76, 175, 80),  # 绿色
    (255, 235, 59), # 黄色
    (255, 152, 0),  # 橙色
    (156, 39, 176), # 紫色
    (0, 188, 212),  # 青色
    (233, 30, 99),  # 粉红色
    (121, 85, 72),  # 棕色
    WHITE           # 白色（备用）
]

# 默认颜色
DEFAULT_COLOR = LIGHT_GRAY

# 游戏文本信息
TEXT_MESSAGES = {
    "WIN": "游戏胜利！",
    "BOARD_LOCKED": "棋盘已锁定，按S键自动求解",
    "INVALID_NUMBER": "数字必须在2-9之间",
    "INPUT_NUMBER": "请输入有效数字",
    "NO_LEVELS": "题库为空"
}

# 方向映射
DIRECTION_MAP = {
    "up": "上",
    "down": "下",
    "left": "左",
    "right": "右"
}

# 字体设置
def get_font(size=36):
    """获取支持中文的字体"""
    try:
        return pygame.font.SysFont(["SimHei", "Microsoft YaHei", "WenQuanYi Micro Hei"], size)
    except:
        return pygame.font.Font(None, size)

# 快捷键说明
HELP_TEXTS = {
    "create": [
        "方向键: 移动选中的格子",
        "数字键1-9: 输入多位数",
        "小键盘0-9: 输入多位数",
        "退格键: 删除输入的最后一个数字",
        "Enter键: 确认输入(1-81)",
        "0键: 清除方块值",
        "B键: 设置墙体",
        "Q键: 设置起点",
        "E键: 设置终点",
        "ESC: 返回菜单",
        "S键: 保存关卡"
    ],
    "solve": [
        "方向键: 移动选中的格子",
        "WASD: 移动选中的方块",
        "数字键1-9: 选择方块",
        "0键: 取消选择",
        "Q键: 设置起点",
        "E键: 设置终点",
        "ESC: 返回菜单",
        "S键: 自动求解"
    ]
}