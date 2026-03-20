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

def heuristic(snake, food, grid_size):
    head = snake[0]
    dist_food = abs(head[0] - food[0]) + abs(head[1] - food[1])
    return -dist_food

def get_neighbors(head, grid_size):
    return [(head[0] + dx, head[1] + dy) 
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)] 
            if 0 <= head[0] + dx < grid_size and 0 <= head[1] + dy < grid_size]

def minimax(snake, food, grid_size, depth, alpha, beta, maximising):
    if depth == 0:
        return heuristic(snake, food, grid_size), None
        
    head = snake[0]
    obstacles = set(tuple(p) for p in snake[:-1])
    
    if tuple(head) in obstacles:
        return -99999 - depth, None
        
    neighbors = get_neighbors(head, grid_size)
    valid_moves = [n for n in neighbors if n not in obstacles]
    
    if not valid_moves and maximising:
        return -99999 - depth, None
        
    best_move = None
    
    if maximising:
        max_eval = float('-inf')
        for move in neighbors:
            if move in obstacles:
                eval_val = -99999 - depth
            else:
                new_snake = [move] + snake[:-1]
                eval_val, _ = minimax(new_snake, food, grid_size, depth - 1, alpha, beta, False)
            
            if eval_val > max_eval:
                max_eval = eval_val
                best_move = move
                
            alpha = max(alpha, eval_val)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        block_candidates = [n for n in get_neighbors(head, grid_size) if n not in obstacles]
        
        if not block_candidates:
            eval_val, _ = minimax(snake, food, grid_size, depth-1, alpha, beta, True)
            return eval_val, None
            
        for block in block_candidates:
            new_snake = list(snake)
            new_snake.append(block) # Phantom block acts as tail extension
            
            eval_val, _ = minimax(new_snake, food, grid_size, depth - 1, alpha, beta, True)
            
            if eval_val < min_eval:
                min_eval = eval_val
                best_move = block
                
            beta = min(beta, eval_val)
            if beta <= alpha:
                break
        return min_eval, best_move

def solve(snake, food, grid_size):
    start = tuple(snake[0])
    
    if len(snake) > 1:
        dx = snake[0][0] - snake[1][0]
        dy = snake[0][1] - snake[1][1]
    else:
        dx, dy = 1, 0
        
    val, best_move = minimax(snake, food, grid_size, 4, float('-inf'), float('inf'), True)
    
    action = [1,0,0]
    if best_move is not None:
        move_dx = best_move[0] - start[0]
        move_dy = best_move[1] - start[1]
        action = get_action_from_move(dx, dy, move_dx, move_dy)

    return {
        "action": action,
        "explored": [], # Minimax search tree is large, returning explored nodes lags canvas.
        "path": [], # Minimax doesn't yield a continuous path in the same way 
        "algo_stat": {"label": "depth", "value": 4}
    }
