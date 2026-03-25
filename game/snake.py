"""
Core Python logic for the AI Snake game on a 16x16 grid.
"""

import enum
import random
from collections import namedtuple
import numpy as np

class Direction(enum.Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

GRID_SIZE = 16
BLOCK_SIZE = 1

class SnakeGame:
    def __init__(self):
        self.GRID_SIZE = GRID_SIZE
        self.w = GRID_SIZE   # used by state.py for grid_size calculation
        self.reset()
        
    def reset(self):
        """Reset the game state to start a new game."""
        self.direction = Direction.RIGHT
        
        # Start in the middle
        self.head = Point(GRID_SIZE // 2, GRID_SIZE // 2)
        self.snake = [
            self.head,
            Point(self.head.x - BLOCK_SIZE, self.head.y),
            Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        ]
        
        self.score = 0
        self.food = None
        self.place_food()
        self.frame_iteration = 0
        
    def place_food(self):
        """Places food in a random unoccupied cell."""
        empty_spots = []
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                pt = Point(x, y)
                if pt not in self.snake:
                    empty_spots.append(pt)
        
        if empty_spots:
            self.food = random.choice(empty_spots)
        else:
            self.food = self.head  # Grid full
            
    def play_step(self, action):
        """
        Takes an action and plays one game step.
        action: list or array of 3 ints [straight, right, left]
        Returns: (reward, game_over, score)
        Rewards: +10 eat, -10 die, +1 closer to food, -1 farther
        """
        self.frame_iteration += 1

        # Calculate distance to food BEFORE move
        old_head = self.head
        distance_before = abs(old_head.x - self.food.x) + abs(old_head.y - self.food.y)

        # 1. move -> update head
        self._move(action)
        self.snake.insert(0, self.head)

        # 2. check game over
        reward = 0
        game_over = False

        # Timeout if we loop too long without eating
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 3. eat food or remove tail
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.place_food()
        else:
            self.snake.pop()
            # Distance-based reward - encourage moving towards food
            distance_after = abs(self.head.x - self.food.x) + abs(self.head.y - self.food.y)
            if distance_after < distance_before:
                reward = 1  # Moved closer to food
            else:
                reward = -1  # Moved away from food

        return reward, game_over, self.score
        
    def is_collision(self, pt=None):
        """Checks if pt hits boundary or snake body. Defaults to head."""
        if pt is None:
            pt = self.head
            
        # boundary collision
        if pt.x < 0 or pt.x >= GRID_SIZE or pt.y < 0 or pt.y >= GRID_SIZE:
            return True
            
        # self collision
        if pt in self.snake[1:]:
            return True
            
        return False
        
    def _move(self, action):
        """Moves head based on [straight, right_turn, left_turn] array."""
        # [straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
        
        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            new_idx = (idx + 1) % 4
            new_dir = clock_wise[new_idx] # right turn
        else: # [0, 0, 1]
            new_idx = (idx - 1) % 4
            new_dir = clock_wise[new_idx] # left turn
            
        self.direction = new_dir
        
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)


