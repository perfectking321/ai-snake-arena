import heapq

def get_action_from_move(curr_dx, curr_dy, move_dx, move_dy):
    cwd = [(1,0), (0,1), (-1,0), (0,-1)]
    try: idx = cwd.index((curr_dx, curr_dy))
    except: idx = 0
    try: move_idx = cwd.index((move_dx, move_dy))
    except: move_idx = 0
    if move_idx == idx: return [1,0,0]
    elif move_idx == (idx + 1) % 4: return [0,1,0]
    elif move_idx == (idx - 1) % 4: return [0,0,1]
    return [1,0,0] 

def h(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def solve(snake, food, grid_size):
    start = tuple(snake[0])
    goal = tuple(food)
    obstacles = set(tuple(p) for p in snake[:-1])
    
    # f, g, curr, path
    pq = [(h(start, goal), 0, start, [])] 
    visited = {} # nodes and their strictly lowest g
    explored_nodes = []
    
    found_path = None
    
    if len(snake) > 1:
        dx = snake[0][0] - snake[1][0]
        dy = snake[0][1] - snake[1][1]
    else: dx, dy = 1, 0
        
    while pq:
        f_val, g_val, curr, path = heapq.heappop(pq)
        
        if curr in visited and visited[curr] <= g_val:
            continue
            
        visited[curr] = g_val
        if curr != start:
            explored_nodes.append(list(curr))
            
        if curr == goal:
            found_path = path
            break
            
        for dx_step, dy_step in [(0,-1), (0,1), (-1,0), (1,0)]:
            nxt = (curr[0] + dx_step, curr[1] + dy_step)
            if 0 <= nxt[0] < grid_size and 0 <= nxt[1] < grid_size:
                if nxt not in obstacles:
                    nxt_g = g_val + 1
                    nxt_f = nxt_g + h(nxt, goal)
                    heapq.heappush(pq, (nxt_f, nxt_g, nxt, path + [nxt]))
                    
    action = [1,0,0] 
    path_coords = []
    path_len = 0
    if found_path and len(found_path) > 0:
        first_step = found_path[0]
        move_dx = first_step[0] - start[0]
        move_dy = first_step[1] - start[1]
        action = get_action_from_move(dx, dy, move_dx, move_dy)
        path_coords = [list(p) for p in found_path]
        path_len = len(path_coords)
        
    return {
        "action": action,
        "explored": explored_nodes,
        "path": path_coords,
        "algo_stat": {"label": "path", "value": path_len}
    }
