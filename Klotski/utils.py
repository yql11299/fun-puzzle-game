# 工具函数文件
from typing import List, Tuple, Set, FrozenSet, Optional


def get_block_positions(board: List[List[int]], block_number: int, rows: int, cols: int) -> List[Tuple[int, int]]:
    """
    获取指定方块的所有位置
    :param board: 游戏棋盘
    :param block_number: 方块编号
    :param rows: 棋盘行数
    :param cols: 棋盘列数
    :return: 方块的位置列表
    """
    positions = []
    for i in range(rows):
        for j in range(cols):
            if board[i][j] == block_number:
                positions.append((i, j))
    return positions


def get_block_shape(board: List[List[int]], block_number: int, rows: int, cols: int) -> Optional[FrozenSet[Tuple[int, int]]]:
    """
    获取方块的形状特征（考虑旋转等价性）
    :param board: 游戏棋盘
    :param block_number: 方块编号
    :param rows: 棋盘行数
    :param cols: 棋盘列数
    :return: 规范化的形状表示
    """
    positions = get_block_positions(board, block_number, rows, cols)
    
    if not positions:
        return None
        
    # 将形状标准化为相对坐标
    min_i = min(pos[0] for pos in positions)
    min_j = min(pos[1] for pos in positions)
    normalized_shape = frozenset((pos[0] - min_i, pos[1] - min_j) for pos in positions)
    
    # 生成所有可能的旋转形状并取最小的作为规范化表示
    normalized_rotations = _get_rotated_shapes(normalized_shape)
    # 使用frozenset的哈希值作为字典键
    return min(normalized_rotations)


def _get_rotated_shapes(shape: FrozenSet[Tuple[int, int]]) -> List[FrozenSet[Tuple[int, int]]]:
    """
    生成一个形状的所有可能旋转变体
    :param shape: 一个frozenset of (i,j)坐标
    :return: 所有唯一旋转变体的列表
    """
    if not shape:
        return [shape]
        
    # 获取形状的边界
    min_i = min(pos[0] for pos in shape)
    max_i = max(pos[0] for pos in shape)
    min_j = min(pos[1] for pos in shape)
    max_j = max(pos[1] for pos in shape)
    
    height = max_i - min_i + 1
    width = max_j - min_j + 1
    
    rotations = []
    
    # 生成4种可能的旋转（0°, 90°, 180°, 270°）
    for rotation in range(4):
        if rotation == 0:
            # 原始方向
            rotated = shape
        elif rotation == 1:
            # 顺时针旋转90度
            rotated = frozenset((pos[1], height - 1 - pos[0]) for pos in shape)
        elif rotation == 2:
            # 旋转180度
            rotated = frozenset((height - 1 - pos[0], width - 1 - pos[1]) for pos in shape)
        elif rotation == 3:
            # 顺时针旋转270度（逆时针旋转90度）
            rotated = frozenset((width - 1 - pos[1], pos[0]) for pos in shape)
        
        # 对旋转后的形状进行再规范化
        min_ri = min(pos[0] for pos in rotated)
        min_rj = min(pos[1] for pos in rotated)
        normalized_rotated = frozenset((pos[0] - min_ri, pos[1] - min_rj) for pos in rotated)
        rotations.append(normalized_rotated)
    
    # 去重并返回所有唯一的旋转变体
    return list(set(rotations))


def are_shapes_equal(shape1: Optional[FrozenSet[Tuple[int, int]]], shape2: Optional[FrozenSet[Tuple[int, int]]]) -> bool:
    """
    判断两个形状是否相同（考虑旋转等价性）
    :param shape1: 第一个形状
    :param shape2: 第二个形状
    :return: 形状是否相同
    """
    if shape1 is None or shape2 is None:
        return shape1 == shape2
        
    # 由于形状已经被规范化，只需要直接比较
    return shape1 == shape2


def is_position_in_board(pos: Tuple[int, int], rows: int, cols: int) -> bool:
    """
    检查位置是否在棋盘内
    :param pos: 位置坐标 (i, j)
    :param rows: 棋盘行数
    :param cols: 棋盘列数
    :return: 是否在棋盘内
    """
    i, j = pos
    return 0 <= i < rows and 0 <= j < cols


def calculate_block_bounds(positions: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    """
    计算方块的边界
    :param positions: 方块的位置列表
    :return: (min_i, max_i, min_j, max_j)
    """
    if not positions:
        return 0, 0, 0, 0
    
    min_i = min(pos[0] for pos in positions)
    max_i = max(pos[0] for pos in positions)
    min_j = min(pos[1] for pos in positions)
    max_j = max(pos[1] for pos in positions)
    
    return min_i, max_i, min_j, max_j