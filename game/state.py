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


def build_state_simple(game) -> np.ndarray:
    """
    EXACT patrickloeber/snake-ai-pytorch get_state.
    11 binary inputs. Proven to score 10-15 in 50 games.
    Uses game.is_collision() exactly as original.
    """
    from game.snake import Point, Direction
    head = game.snake[0]

    point_l = Point(head.x - 1, head.y)
    point_r = Point(head.x + 1, head.y)
    point_u = Point(head.x, head.y - 1)
    point_d = Point(head.x, head.y + 1)

    dir_l = game.direction == Direction.LEFT
    dir_r = game.direction == Direction.RIGHT
    dir_u = game.direction == Direction.UP
    dir_d = game.direction == Direction.DOWN

    state = [
        # Danger straight
        (dir_r and game.is_collision(point_r)) or
        (dir_l and game.is_collision(point_l)) or
        (dir_u and game.is_collision(point_u)) or
        (dir_d and game.is_collision(point_d)),

        # Danger right
        (dir_u and game.is_collision(point_r)) or
        (dir_d and game.is_collision(point_l)) or
        (dir_l and game.is_collision(point_u)) or
        (dir_r and game.is_collision(point_d)),

        # Danger left
        (dir_d and game.is_collision(point_r)) or
        (dir_u and game.is_collision(point_l)) or
        (dir_r and game.is_collision(point_u)) or
        (dir_l and game.is_collision(point_d)),

        dir_l, dir_r, dir_u, dir_d,

        game.food.x < head.x,
        game.food.x > head.x,
        game.food.y < head.y,
        game.food.y > head.y,
    ]
    return np.array(state, dtype=int).astype(np.float32)

def build_state(game, extended=False) -> np.ndarray:
    if not extended:
        return build_state_simple(game)

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

    # Safe assumption for 16x16 grid
    if hasattr(game, 'w'):
        grid_size = game.w // BLOCK_SIZE
    else:
        grid_size = 16

    sensors = _get_sensors(grid_size)

    board = np.zeros((grid_size, grid_size), dtype=np.float32)

    for pt in game.snake:
        col = int(pt.x) % grid_size
        row = int(pt.y) % grid_size
        col = max(0, min(grid_size - 1, col))
        row = max(0, min(grid_size - 1, row))
        board[row, col] = 1.0

    food_col = max(0, min(grid_size - 1, int(game.food.x)))
    food_row = max(0, min(grid_size - 1, int(game.food.y)))
    board[food_row, food_col] = 2.0

    head_col = max(0, min(grid_size - 1, int(game.snake[0].x)))
    head_row = max(0, min(grid_size - 1, int(game.snake[0].y)))

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
    snake_yx = np.array([
        [int(pt.y // BLOCK_SIZE), int(pt.x // BLOCK_SIZE)]
        for pt in reversed(game.snake)
    ])
    tail_dir = sensors.get_tail_direction(snake_yx)

    state = np.concatenate([wall_dist, see_food, see_body, head_dir, tail_dir])
    return state.astype(np.float32)
