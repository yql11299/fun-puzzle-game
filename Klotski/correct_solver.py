# 在文件开头导入必要的库
import time
import heapq
from collections import deque, defaultdict
import cProfile
import pstats
from io import StringIO

# ================= 工具函数 =================
def serialize_board(board):
    return tuple(tuple(row) for row in board)

def deserialize_board(state):
    return [list(row) for row in state]

def find_blocks(board):
    """找到所有方块：block_id -> [(x,y),...]"""
    m, n = len(board), len(board[0])
    blocks = defaultdict(list)
    for i in range(m):
        for j in range(n):
            if board[i][j] > 0:
                blocks[board[i][j]].append((i, j))
    return blocks

def find_all_paths(board, start, goal):
    """找到所有可能的路径"""
    m, n = len(board), len(board[0])
    paths = []
    def dfs(x, y, path):
        if (x, y) == goal:
            paths.append(path)
            return
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and board[nx][ny] == 0:
                dfs(nx, ny, path + [(nx, ny)])
    dfs(start[0], start[1], [start])
    return paths

def remove_suboptimal_paths(paths):
    """
    删除次优路径
    
    如果一条路径A的所有点都包含在另一条路径B中，则B是次优路径，将被删除
    （注意：路径的起点和终点必须相同）
    
    参数:
    paths (list): 路径列表，每个路径是坐标点的列表
    
    返回:
    list: 过滤后的路径列表，只包含最优路径
    """
    if not paths:
        return []
    
    # 存储要保留的最优路径索引
    optimal_indices = list(range(len(paths)))
    
    # 为每条路径创建点集合，用于快速检查包含关系
    path_sets = [set(path) for path in paths]
    
    # 检查每对路径之间的包含关系
    for i in range(len(paths)):
        if i not in optimal_indices:  # 如果已经标记为次优，跳过
            continue
            
        for j in range(len(paths)):
            if i == j or j not in optimal_indices:  # 跳过自己和已标记为次优的路径
                continue
                
            # 检查路径i是否被路径j完全包含
            if path_sets[i].issubset(path_sets[j]):
                # 路径j是次优的，标记为要删除
                if j in optimal_indices:
                    optimal_indices.remove(j)
            # 检查路径j是否被路径i完全包含
            elif path_sets[j].issubset(path_sets[i]):
                # 路径i是次优的，标记为要删除
                if i in optimal_indices:
                    optimal_indices.remove(i)
                    break  # 一旦当前路径被标记为次优，就不需要再检查其他路径
    
    # 根据保留的索引提取最优路径
    optimal_paths = [paths[i] for i in sorted(optimal_indices)]
    
    return optimal_paths

def can_move(block_cells, dx, dy, board):
    """检查方块是否能整体移动"""
    m, n = len(board), len(board[0])
    for x, y in block_cells:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < m and 0 <= ny < n):
            return False
        if board[nx][ny] not in (0, board[x][y]):
            return False
    return True

def move_block(block_id, dx, dy, board):
    """执行移动，返回新棋盘"""
    new_board = [row[:] for row in board]
    cells = [(i, j) for i in range(len(board)) for j in range(len(board[0])) if board[i][j] == block_id]
    for x, y in cells:
        new_board[x][y] = 0
    for x, y in cells:
        new_board[x + dx][y + dy] = block_id
    return new_board

# def empty_path_exists(board, start, goal,paths):
#     return heuristic(board, start, goal, paths) == 0

def empty_path_exists(board, start, goal):
    """
    判断：是否存在一条仅由 0 组成的 4-连通路径（包括起点和终点）。
    board: m x n 列表（含 -1 墙，0 空，>0 方块）
    start, goal: (r, c) 0-based 坐标
    返回: True / False
    """
    m = len(board)
    if m == 0:
        return False
    n = len(board[0])

    sr, sc = start
    gr, gc = goal

    # 1) 边界检查：坐标必须在棋盘内
    if not (0 <= sr < m and 0 <= sc < n and 0 <= gr < m and 0 <= gc < n):
        return False

    # 2) 起点、终点必须都是 0（严格按照你定义，包括起点/终点）
    if board[sr][sc] != 0 or board[gr][gc] != 0:
        return False

    # 3) 快速处理：起点等于终点且其为 0，则存在（长度为0 的路径）
    if (sr, sc) == (gr, gc):
        return True

    # 4) 常规 BFS（4方向），仅在遇到值为 0 的邻居时扩展
    visited = [[False] * n for _ in range(m)]
    dq = deque()
    dq.append((sr, sc))
    visited[sr][sc] = True

    while dq:
        r, c = dq.popleft()
        # 遍历四个方向
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and not visited[nr][nc]:
                # 只能进入值为 0 的格子（严格）
                if board[nr][nc] == 0:
                    if (nr, nc) == (gr, gc):
                        return True
                    visited[nr][nc] = True
                    dq.append((nr, nc))
    return False

def heuristic(board, start, goal, paths):
    """
    新的启发式函数：计算从起点到终点路径上最少需要清理的方块总代价（考虑墙壁、终点状态和方块大小）
    """
    cost = float('inf')
    for path in paths:
        cost = min(cost, calculate_cost(path, board))
    return cost

def calculate_cost(path, board):
    """
    计算路径上需要清理的方块总代价
    """
    cost = 0
    blocks = []
    for x, y in path:
        if board[x][y] > 0 and board[x][y] not in blocks:
            blocks.append(board[x][y])
            cost += 1
    return cost

# ... 其他工具函数保持不变 ...
# ================= 启发式函数 =================
# def heuristic(board, start, goal):
#     """启发式函数：计算从起点到终点路径上最少需要清理的方块总代价（考虑墙壁、终点状态和方块大小）"""
#     m, n = len(board), len(board[0])
#     gr, gc = goal
    
#     # 检查终点是否为墙壁，如果是则直接返回无穷大
#     if board[gr][gc] == -1:
#         return float('inf')
    
#     # 使用 (x, y, visited_blocks) 作为状态，其中 visited_blocks 是路径上遇到的不同方块ID集合
#     q = deque([(start[0], start[1], frozenset(), 0)])  # (x, y, visited_blocks, total_cost)
#     # 状态访问记录，使用坐标和解过的方块集合作为键
#     visited = set()
#     visited.add(((start[0], start[1]), frozenset()))
    
#     while q:
#         x, y, blocks, total_cost = q.popleft()
        
#         # 到达终点时，根据终点的不同状态返回不同的值
#         if (x, y) == goal:
#             # 如果终点是方块，需要额外清理
#             if board[x][y] > 0:
#                 # 检查终点方块是否已经在清理列表中
#                 if board[x][y] not in blocks:
#                     return total_cost + 1
#             # 如果终点是空位，直接返回总代价
#             return total_cost
            
#         # 遍历四个方向
#         for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
#             nx, ny = x+dx, y+dy
#             # 检查边界
#             if 0 <= nx < m and 0 <= ny < n:
#                 # 跳过墙壁
#                 if board[nx][ny] == -1:
#                     continue
                    
#                 # 计算新的方块集合和总代价
#                 new_blocks = blocks
#                 new_total_cost = total_cost
#                 # 如果是方块（值>0），将其添加到集合中，并加上其代价
#                 if board[nx][ny] > 0:
#                     if board[nx][ny] not in blocks:
#                         new_blocks = blocks | {board[nx][ny]}
#                         new_total_cost = total_cost + 1
#                     else:
#                         new_blocks = blocks
#                         new_total_cost = total_cost
                
#                 # 构建新状态
#                 new_state = ((nx, ny), new_blocks)
#                 # 如果新状态未访问过，加入队列
#                 if new_state not in visited:
#                     visited.add(new_state)
#                     q.append((nx, ny, new_blocks, new_total_cost))
    
#     # 如果无法到达终点，返回一个很大的值表示不可达
#     return float('inf')

# ================= A* 主体 =================
def solve_puzzle(initial_board, start, goal):
    """
    A*算法求解推箱子谜题，包含性能分析
    """
    # 记录开始时间
    start_time = time.time()
    
    # 性能统计变量
    perf_stats = {
        'heuristic_time': 0,        # 启发函数计算时间
        'serialize_time': 0,        # 序列化时间
        'deserialize_time': 0,      # 反序列化时间
        'empty_path_time': 0,       # empty_path_exists函数计算时间
        'hash_operations': 0,       # 哈希操作计数
        'heuristic_calls': 0,       # 启发函数调用次数
        'serialize_calls': 0,       # 序列化调用次数
        'deserialize_calls': 0,     # 反序列化调用次数
        'empty_path_calls': 0       # empty_path_exists调用次数
    }

    all_paths = find_all_paths(initial_board, start, goal)
    valid_paths = remove_suboptimal_paths(all_paths)
    
    # 初始化优先队列（Open表），用于存储待访问的状态
    open_heap = []
    
    # 序列化初始状态并计时
    serialize_start = time.time()
    initial_state = serialize_board(initial_board)
    perf_stats['serialize_time'] += time.time() - serialize_start
    perf_stats['serialize_calls'] += 1
    
    # g_scores字典：记录从初始状态到每个状态的实际代价
    g_scores = {initial_state: 0}
    
    # 计算初始状态的启发值并计时
    heuristic_start = time.time()
    h = heuristic(initial_board, start, goal, valid_paths)
    perf_stats['heuristic_time'] += time.time() - heuristic_start
    perf_stats['heuristic_calls'] += 1
    
    # 计算初始状态的f值（f = g + h）
    f = 0 + h
    
    # 将初始状态加入优先队列
    heapq.heappush(open_heap, (f, 0, initial_state, []))

    # 统计变量：expanded为已扩展的节点数，opened为已打开的状态数
    expanded, opened = 0, 1
    
    # visited集合：记录已经访问过的状态，避免重复访问
    visited = set()

    # 主循环：处理优先队列中的状态
    while open_heap:
        # 从优先队列中取出f值最小的状态
        f, g, state, path = heapq.heappop(open_heap)
        
        # 哈希操作计数
        perf_stats['hash_operations'] += 1
        if state in visited:
            continue
        
        # 将状态标记为已访问
        visited.add(state)
        
        # 反序列化状态并计时
        deserialize_start = time.time()
        board = deserialize_board(state)
        perf_stats['deserialize_time'] += time.time() - deserialize_start
        perf_stats['deserialize_calls'] += 1
        
        # 增加已扩展节点计数
        expanded += 1

        # 检查当前状态是否为目标状态：起点到终点是否存在空路径
        # 计时empty_path_exists函数调用
        empty_path_start = time.time()
        is_goal = empty_path_exists(board, start, goal)
        perf_stats['empty_path_time'] += time.time() - empty_path_start
        perf_stats['empty_path_calls'] += 1
        
        if is_goal:
            duration = time.time() - start_time
            # 打印性能统计信息
            print_performance_stats(perf_stats, duration)
            return path, board, duration, expanded, opened

        # 找到当前棋盘上的所有方块
        blocks = find_blocks(board)
        
        # 尝试移动每个方块的四个方向
        for block_id, cells in blocks.items():
            for dx, dy, move_label in [(1,0,"D"),(-1,0,"U"),(0,1,"R"),(0,-1,"L")]:
                if can_move(cells, dx, dy, board):
                    # 执行移动，生成新的棋盘状态
                    new_board = move_block(block_id, dx, dy, board)
                    
                    # 序列化新状态并计时
                    serialize_start = time.time()
                    new_state = serialize_board(new_board)
                    perf_stats['serialize_time'] += time.time() - serialize_start
                    perf_stats['serialize_calls'] += 1
                    
                    # 哈希操作计数
                    perf_stats['hash_operations'] += 1
                    new_g = g + 1
                    if new_state not in g_scores or new_g < g_scores[new_state]:
                        g_scores[new_state] = new_g
                        
                        # 计算新状态的启发值并计时
                        heuristic_start = time.time()
                        new_h = heuristic(new_board, start, goal, valid_paths)
                        perf_stats['heuristic_time'] += time.time() - heuristic_start
                        perf_stats['heuristic_calls'] += 1
                        
                        new_f = new_g + new_h
                        new_path = path + [(block_id, move_label)]
                        heapq.heappush(open_heap, (new_f, new_g, new_state, new_path))
                        opened += 1

    # 如果无法找到解，返回None和统计信息
    duration = time.time() - start_time
    print_performance_stats(perf_stats, duration)
    return None, None, duration, expanded, opened

# ================= 性能统计函数 =================
def print_performance_stats(perf_stats, total_time):
    """\打印性能统计信息"""
    print("\n=== 性能分析结果 ===")
    print(f"总耗时: {total_time:.4f} 秒")
    print(f"启发函数计算: {perf_stats['heuristic_time']:.4f} 秒 ({perf_stats['heuristic_time']/total_time*100:.2f}%), 调用次数: {perf_stats['heuristic_calls']}")
    print(f"棋盘序列化: {perf_stats['serialize_time']:.4f} 秒 ({perf_stats['serialize_time']/total_time*100:.2f}%), 调用次数: {perf_stats['serialize_calls']}")
    print(f"棋盘反序列化: {perf_stats['deserialize_time']:.4f} 秒 ({perf_stats['deserialize_time']/total_time*100:.2f}%), 调用次数: {perf_stats['deserialize_calls']}")
    print(f"路径存在检查(empty_path_exists): {perf_stats['empty_path_time']:.4f} 秒 ({perf_stats['empty_path_time']/total_time*100:.2f}%), 调用次数: {perf_stats['empty_path_calls']}")
    print(f"哈希操作次数: {perf_stats['hash_operations']}")
    
    # 计算各部分时间占比并找出主要瓶颈
    bottlenecks = []
    if perf_stats['heuristic_time'] > 0.5 * total_time:
        bottlenecks.append("启发函数计算")
    if perf_stats['serialize_time'] > 0.3 * total_time:
        bottlenecks.append("棋盘序列化")
    if perf_stats['deserialize_time'] > 0.2 * total_time:
        bottlenecks.append("棋盘反序列化")
    if perf_stats['empty_path_time'] > 0.2 * total_time:
        bottlenecks.append("路径存在检查")
    
    if bottlenecks:
        print(f"\n主要性能瓶颈: {', '.join(bottlenecks)}")
    else:
        print("\n各部分耗时分布较为均衡，没有明显的性能瓶颈")


# ================= 更详细的性能分析（使用cProfile） =================
def profile_solver(board, start, goal):
    """使用cProfile进行更详细的性能分析"""
    pr = cProfile.Profile()
    pr.enable()
    
    # 运行求解器
    path, final_board, duration, expanded, opened = solve_puzzle(board, start, goal)
    
    pr.disable()
    
    # 输出分析结果
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    # 只显示前20个耗时最多的函数
    print("\n=== 详细性能分析（前20个最耗时函数）===")
    print(s.getvalue().split('\n')[0:25])
    
    return path, final_board, duration, expanded, opened

# ================= 示例运行 =================
if __name__ == "__main__":
    # board = [
    #     [0,0,-1,-1,0,0],
    #     [0,0,8,0,0,0],
    #     [1,0,8,9,9,9],
    #     [1,-1,3,4,-1,9],
    #     [2,-1,5,7,-1,10],
    #     [2,-1,6,7,-1,10],
    # ]
    # start = (1,0)
    # goal = (4,5)
    board = [
        [1, 1, 1, 1, 3, 4],
        [1, 2, 0, 1, 5, 0],
        [1, 1, 0, 1, 5, 0],
        [6, 7, 0, 6, 0, 0],
        [6, 6, 6, 6, 0, 0],
    ]
    start = (4,0)
    goal = (2,5)
    
    # 使用基本性能分析
    print("运行基本性能分析...")
    path, final_board, duration, expanded, opened = solve_puzzle(board, start, goal)
    
    # 可选：使用详细性能分析（使用cProfile）
    # print("\n\n运行详细性能分析...")
    # path, final_board, duration, expanded, opened = profile_solver(board, start, goal)
    
    # 原有输出代码保持不变
    # print("\n初始棋盘：")
    # for row in board:
    #     print(" ".join(f"{x:2d}" for x in row))
    # print(f"\n起点: {start}, 终点: {goal}\n")
    
    if path is None:
        print("未找到解。")
    else:
        print(f"找到解！共 {len(path)} 步。")
        # 输出移动步骤...
        
    print(f"\n用时: {duration:.4f} 秒，展开(expanded)节点数: {expanded}, 打开(opened)状态数: {opened}")