# STATE VECTOR UPDATE — Paste this into your Backend Agent

STOP. Before doing anything, read this fully.

Do NOT touch any file you have already completed.
Only create/modify these 2 files:
1. game/snake_sensors.py  (CREATE — new file)
2. game/state.py          (MODIFY — replace build_state only)
3. agents/rl_agent.py     (MODIFY — change INPUT_SIZE from 27 to 28 only)

---

## STEP 1 — Create game/snake_sensors.py

Create this file EXACTLY as written below. Do not change a single line:

```python
"""
SnakeSensors — adapted from SnakeQ by ludius0 (MIT License)
Provides 8-direction vision rays for wall distance, food detection, body distance.
"""
import numpy as np


class SnakeSensors:
    def __init__(self, row, moves):
        self.row = row
        self.dis = self.row - 1
        self.moves = moves
        self.next_to_head_dir = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def update_sensor_board(self, board, snake_head):
        self.board = board
        self.head_y, self.head_x = snake_head
        self.dis_y_down = self.dis - self.head_y
        self.dis_y_up = self.dis - self.dis_y_down
        self.dis_x_right = self.dis - self.head_x
        self.dis_x_left = self.dis - self.dis_x_right

    def check_up(self, target):
        if self.head_y == 0: return 0
        for i in range(self.head_y - 1, -1, -1):
            if self.board[i, self.head_x] == target:
                return i
        return 0

    def check_down(self, target):
        if self.head_y == self.dis: return 0
        for i in range(self.head_y + 1, self.row):
            if self.board[i, self.head_x] == target:
                return i
        return 0

    def check_right(self, target):
        if self.head_x == self.dis: return 0
        for i in range(self.head_x + 1, self.row):
            if self.board[self.head_y, i] == target:
                return i
        return 0

    def check_left(self, target):
        if self.head_x == 0: return 0
        for i in range(self.head_x - 1, -1, -1):
            if self.board[self.head_y, i] == target:
                return i
        return 0

    def check_right_up(self, target):
        distance = self.dis_y_up if self.dis_y_up < self.dis_x_right else self.dis_x_right
        if distance == 0: return 0
        for n in range(1, distance + 1):
            if self.board[self.head_y - n, self.head_x + n] == target:
                return n
        return 0

    def check_right_down(self, target):
        distance = self.dis_y_down if self.dis_y_down < self.dis_x_right else self.dis_x_right
        if distance == self.row: return 0
        for n in range(1, distance + 1):
            if self.board[self.head_y + n, self.head_x + n] == target:
                return n
        return 0

    def check_left_up(self, target):
        distance = self.dis_y_up if self.dis_y_up < self.dis_x_left else self.dis_x_left
        if distance == 0: return 0
        for n in range(1, distance + 1):
            if self.board[self.head_y - n, self.head_x - n] == target:
                return n
        return 0

    def check_left_down(self, target):
        distance = self.dis_y_down if self.dis_y_down < self.dis_x_left else self.dis_x_left
        if distance == self.row: return 0
        for n in range(1, distance + 1):
            if self.board[self.head_y + n, self.head_x - n] == target:
                return n
        return 0

    def all_eight_directions(self, target):
        return np.array([
            self.check_up(target),
            self.check_right_up(target),
            self.check_right(target),
            self.check_right_down(target),
            self.check_down(target),
            self.check_left_down(target),
            self.check_left(target),
            self.check_left_up(target),
        ])

    def distance_to_walls(self):
        return np.round(
            np.array([self.dis_y_up, self.dis_x_right, self.dis_y_down, self.dis_x_left]) / self.dis, 1
        )

    def get_head_direction(self, head_dir):
        if head_dir is None:
            return np.array([0, 0, 0, 0])
        if np.array_equal(head_dir, self.moves["up"]):    return np.array([1, 0, 0, 0])
        if np.array_equal(head_dir, self.moves["right"]): return np.array([0, 1, 0, 0])
        if np.array_equal(head_dir, self.moves["down"]):  return np.array([0, 0, 1, 0])
        if np.array_equal(head_dir, self.moves["left"]):  return np.array([0, 0, 0, 1])
        return np.array([0, 0, 0, 0])

    def get_tail_direction(self, snake_body):
        """snake_body: numpy array of shape (N, 2) in (y, x) order"""
        if len(snake_body) > 1:
            tail_dir = tuple(
                (np.array(snake_body[1]) - np.array(snake_body[0])).tolist()
            )
            moves = self.moves
            if np.array_equal(tail_dir, moves["up"]):    return np.array([1, 0, 0, 0])
            if np.array_equal(tail_dir, moves["right"]): return np.array([0, 1, 0, 0])
            if np.array_equal(tail_dir, moves["down"]):  return np.array([0, 0, 1, 0])
            if np.array_equal(tail_dir, moves["left"]):  return np.array([0, 0, 0, 1])
        return np.array([0, 0, 0, 0])
```

---

## STEP 2 — Replace build_state() in game/state.py

Find the existing build_state() function and replace it with this.
Keep everything else in state.py unchanged.

```python
"""
State vector builder — 28 inputs (SnakeQ architecture, MIT License)
[0-3]   wall distances 4 directions      (float 0-1)
[4-11]  food visible in 8 directions     (bool 0/1)
[12-19] body distance in 8 directions    (float, normalised)
[20-23] head direction                   (one-hot 4)
[24-27] tail direction                   (one-hot 4)
"""
import numpy as np
from game.snake_sensors import SnakeSensors

INPUT_SIZE = 28

MOVES_DIR = {
    "up":    np.array([-1,  0]),
    "right": np.array([ 0,  1]),
    "down":  np.array([ 1,  0]),
    "left":  np.array([ 0, -1]),
}

_sensors = None

def _get_sensors(grid_size):
    global _sensors
    if _sensors is None:
        _sensors = SnakeSensors(grid_size, MOVES_DIR)
    return _sensors


def build_state(game) -> np.ndarray:
    """
    Convert game object into a 28-element float32 numpy array.

    Expects game to have:
      game.snake   : list of Point(x, y) namedtuples, index 0 = head
      game.food    : Point(x, y)
      game.direction: Direction enum (Direction.UP/DOWN/LEFT/RIGHT)
      game.w, game.h: grid width/height in pixels
      BLOCK_SIZE   : imported from game.snake
    """
    from game.snake import BLOCK_SIZE, Direction

    grid_size = game.w // BLOCK_SIZE   # e.g. 640 // 40 = 16

    sensors = _get_sensors(grid_size)

    # Build numpy board (grid_size x grid_size)
    # 0 = empty, 1 = snake body, 2 = food
    board = np.zeros((grid_size, grid_size), dtype=np.float32)

    # Place snake body (convert Point(x,y) → board[row, col] i.e. board[y, x])
    for pt in game.snake:
        col = int(pt.x // BLOCK_SIZE)
        row = int(pt.y // BLOCK_SIZE)
        if 0 <= row < grid_size and 0 <= col < grid_size:
            board[row, col] = 1.0

    # Place food
    food_col = int(game.food.x // BLOCK_SIZE)
    food_row = int(game.food.y // BLOCK_SIZE)
    board[food_row, food_col] = 2.0

    # Head position in (y, x) / (row, col) order for sensors
    head_col = int(game.snake[0].x // BLOCK_SIZE)
    head_row = int(game.snake[0].y // BLOCK_SIZE)

    sensors.update_sensor_board(board, (head_row, head_col))

    # --- Wall distances (4) ---
    wall_dist = sensors.distance_to_walls()

    # --- Food in 8 directions (8) ---
    see_food = sensors.all_eight_directions(2.0)
    see_food = np.where(see_food > 0, 1.0, 0.0)   # convert to bool

    # --- Body distance in 8 directions (8) ---
    see_body = sensors.all_eight_directions(1.0)
    see_body = (see_body / (grid_size - 1)) * -1   # normalise + negate like SnakeQ

    # --- Head direction (4) ---
    dir_map = {
        Direction.UP:    MOVES_DIR["up"],
        Direction.DOWN:  MOVES_DIR["down"],
        Direction.LEFT:  MOVES_DIR["left"],
        Direction.RIGHT: MOVES_DIR["right"],
    }
    head_dir_vec = dir_map.get(game.direction, None)
    head_dir = sensors.get_head_direction(head_dir_vec)

    # --- Tail direction (4) ---
    # Convert snake Points to (y, x) numpy rows for get_tail_direction
    snake_yx = np.array([
        [int(pt.y // BLOCK_SIZE), int(pt.x // BLOCK_SIZE)]
        for pt in reversed(game.snake)   # SnakeQ: index 0 = tail, last = head
    ])
    tail_dir = sensors.get_tail_direction(snake_yx)

    state = np.concatenate([wall_dist, see_food, see_body, head_dir, tail_dir])
    return state.astype(np.float32)
```

---

## STEP 3 — Update INPUT_SIZE in agents/rl_agent.py

Find this line:
```python
self.model = Linear_QNet(11, 256, 3)
```
or wherever INPUT_SIZE or the first Linear layer input is defined.

Change the input size from whatever it currently is to 28:
```python
self.model = Linear_QNet(28, 256, 3)
```

If there is a constant INPUT_SIZE = 27 (or 11), change it to INPUT_SIZE = 28.

---

## STEP 4 — Update task.md

Mark M1-03 as:
✅ | "Updated to 28-input SnakeQ state vector (wall×4, food×8, body×8, head×4, tail×4)"

---

## WHAT NOT TO TOUCH

- Do NOT modify game/snake.py
- Do NOT modify any file in agents/ except changing the one number in rl_agent.py
- Do NOT modify main.py
- Do NOT modify frontend/index.html
- Do NOT delete or rename any existing file
