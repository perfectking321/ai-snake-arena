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
        if distance == 0: return 0
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
        if distance == 0: return 0
        for n in range(1, distance + 1):
            if self.board[self.head_y + n, self.head_x - n] == target:
                return n
        return 0

    def all_eight_directions(self, target):
        results = []
        for val in [
            self.check_up(target),
            self.check_right_up(target),
            self.check_right(target),
            self.check_right_down(target),
            self.check_down(target),
            self.check_left_down(target),
            self.check_left(target),
            self.check_left_up(target),
        ]:
            results.append(max(0, min(self.row - 1, val)))
        return np.array(results)

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
