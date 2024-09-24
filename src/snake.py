import enum
import logging
import random
from collections import deque

import pygame

from libs.grid import BaseGridGame

logger = logging.getLogger(__name__)


class Direction(enum.Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


DirectionMapping = {
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT
}
Level = {
    0: 10,
    1: 6,
    2: 4,
    3: 3,
    4: 2,
    5: 1,
}


class SnakeGame(BaseGridGame):
    def __init__(self, width: int, height: int, barriers: int):
        self.width = width
        self.height = height
        self.barrier_size = barriers
        self.is_failed = False
        self.snake = None
        self.direction = None
        self.food = None
        self.barriers = None
        self.level = 0
        self.tick = Level[self.level]
        super().__init__(self.width, self.height, 10, 1, color_mode=2)
        self.register_key_callback(pygame.K_UP, self.direction_key_handler)
        self.register_key_callback(pygame.K_DOWN, self.direction_key_handler)
        self.register_key_callback(pygame.K_LEFT, self.direction_key_handler)
        self.register_key_callback(pygame.K_RIGHT, self.direction_key_handler)
        self.register_key_callback(pygame.K_SPACE, self.space_key_handler)
        self.register_key_callback(pygame.K_ESCAPE, self.quit_handler)
        self.init_map()

    def init_map(self):
        self.screen.fill(self.bg_color)
        self.level = 0
        self.tick = Level[self.level]
        center = (self.width // 2, self.height // 2)
        self.snake = deque([(center[0] + 1, center[1]), center, ])
        self.direction = Direction.RIGHT
        self.barriers = []
        for i in range(self.barrier_size):
            while True:
                p = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
                d = random.randint(0, 1)
                if d == 0:
                    barrier = [(p[0], p[1] + j) for j in range(5) if p[1] + j < self.height]
                else:
                    barrier = [(p[0] + j, p[1]) for j in range(5) if p[0] + j < self.width]
                if self.snake[0] in barrier or self.snake[1] in barrier or self.food in barrier:
                    continue
                self.barriers.append(barrier)
                break
        self.food = self.new_food()
        for grid in self.snake:
            self.fill_grid(*grid)
        self.fill_cycle(*self.food)

        for barrier in self.barriers:
            for grid in barrier:
                self.fill_checkmark(*grid, with_bg=False)

    def direction_key_handler(self, event: pygame.event.EventType):
        key = event.key
        logger.info('F={}, K={}', self.current_frame_no, event)
        if key in (pygame.K_UP, pygame.K_DOWN) and self.direction in (Direction.UP, Direction.DOWN):
            return
        if key in (pygame.K_LEFT, pygame.K_RIGHT) and self.direction in (Direction.LEFT, Direction.RIGHT):
            return
        self.direction = DirectionMapping[key]

    def space_key_handler(self, _):
        if self.is_failed:
            self.restart()
        else:
            pass

    def new_food(self):
        while True:
            food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            for barrier in self.barriers:
                if food in barrier:
                    continue
            if food not in self.snake:
                return food

    def move(self):
        head = self.snake[0]
        match self.direction:
            case Direction.UP:
                new_head = (head[0], head[1] - 1)
            case Direction.DOWN:
                new_head = (head[0], head[1] + 1)
            case Direction.LEFT:
                new_head = (head[0] - 1, head[1])
            case Direction.RIGHT:
                new_head = (head[0] + 1, head[1])
            case _:
                new_head = (-1, -1)
        if new_head[0] < 0 or new_head[0] >= self.width or new_head[1] < 0 or new_head[1] >= self.height:
            return False
        for barrier in self.barriers:
            if new_head in barrier:
                return False
        if new_head in self.snake:
            return False
        if new_head == self.food:
            self.fill_grid(*new_head)
            self.food = self.new_food()
            self.fill_cycle(*self.food)
            self.snake.appendleft(new_head)
            self.level = min((len(self.snake) - 2) // 10, 5)
            self.tick = Level[self.level]
            return True
        self.snake.appendleft(new_head)
        tail = self.snake.pop()
        self.free_grid(*tail)
        self.fill_grid(*new_head)
        return True

    def restart(self):
        for grid in self.snake:
            self.free_grid(*grid)
        self.free_grid(*self.food)
        self.init_map()
        self.is_failed = False

    def fail(self):
        self.is_failed = True
        for grid in self.snake:
            self.fill_checkmark(*grid)

    def do_every_frame(self, current_frame: int):
        if self.is_failed:
            return
        if current_frame % self.tick == 0:
            status = self.move()
            if status:
                pass
            else:
                self.fail()
        else:
            pass


if __name__ == '__main__':
    game = SnakeGame(30, 20, 2)
    game.run()
