import enum
import sys
from typing import Callable, Optional, Tuple

import pygame


class GridColor(enum.Enum):
    DARK = pygame.Color(0, 0, 0)
    LIGHT = pygame.Color(255, 255, 255)


class BaseGridGame:
    def __init__(self,
                 width: int,
                 height: int,
                 grid_size: int = 10,
                 grid_border: int = 1,
                 margin: Optional[Tuple[int, int, int, int]] = None,
                 scale_factor: int = 1,
                 color_mode: int = 1,
                 fps: int = 60,
                 ):
        if margin is None:
            margin = (0, 0, 0, 0)
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.grid_border = grid_border
        self.margin_top = margin[0]
        self.margin_right = margin[1]
        self.margin_bottom = margin[2]
        self.margin_left = margin[3]
        self.scale_factor = scale_factor
        self.color_mode = color_mode
        self.fps = fps

        self.screen_width = (width * grid_size + (width - 1) * grid_border + self.margin_left + self.margin_right) * scale_factor
        self.screen_height = (height * grid_size + (height - 1) * grid_border + self.margin_top + self.margin_bottom) * scale_factor
        self.grid_pixel_size = grid_size * scale_factor

        self.events_registry = {}
        self.key_registry = {}
        self.register_event_callback(pygame.KEYDOWN, self.keydown_handler)
        self.register_event_callback(pygame.QUIT, self.quit_handler)

        pygame.init()
        self.fps_control = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        match self.color_mode:
            case 1:
                self.bg_color = GridColor.LIGHT.value
                self.fg_color = GridColor.DARK.value
            case 2:
                self.bg_color = GridColor.DARK.value
                self.fg_color = GridColor.LIGHT.value
            case _:
                self.bg_color = GridColor.LIGHT.value
                self.fg_color = GridColor.DARK.value
        self.screen.fill(self.bg_color)
        self.current_frame_no = 0

    def quit(self):
        pygame.quit()
        sys.exit()

    def draw_grid(self, x: int, y: int, color: pygame.Color):
        pixel_x = (self.grid_size * x + self.margin_left + self.grid_border * x) * self.scale_factor
        pixel_y = (self.grid_size * y + self.margin_top + self.grid_border * y) * self.scale_factor
        area = (pixel_x, pixel_y, self.grid_pixel_size, self.grid_pixel_size)
        pygame.draw.rect(self.screen, color, area)

    def fill_grid(self, x: int, y: int):
        self.draw_grid(x, y, self.fg_color)

    def free_grid(self, x: int, y: int):
        self.draw_grid(x, y, self.bg_color)

    def fill_checkmark(self, x: int, y: int, with_bg: bool = True):
        pixel_x = (self.grid_size * x + self.margin_left + self.grid_border * x) * self.scale_factor
        pixel_y = (self.grid_size * y + self.margin_top + self.grid_border * y) * self.scale_factor
        p0 = (pixel_x, pixel_y)
        p1 = (pixel_x + self.grid_size * self.scale_factor, pixel_y)
        p2 = (pixel_x, pixel_y + self.grid_size * self.scale_factor)
        p3 = (p1[0], p2[1])
        if with_bg:
            self.fill_grid(x, y)
            pygame.draw.line(self.screen, self.bg_color, p0, p3, 2 * self.scale_factor)
            pygame.draw.line(self.screen, self.bg_color, p1, p2, 2 * self.scale_factor)
        else:
            self.free_grid(x, y)
            pygame.draw.line(self.screen, self.fg_color, p0, p3, 2 * self.scale_factor)
            pygame.draw.line(self.screen, self.fg_color, p1, p2, 2 * self.scale_factor)

    def fill_cycle(self, x: int, y: int):
        pixel_x = (self.grid_size * x + self.margin_left + self.grid_border * x) * self.scale_factor
        pixel_y = (self.grid_size * y + self.margin_top + self.grid_border * y) * self.scale_factor
        radius = self.grid_size * self.scale_factor // 2
        center = (pixel_x + radius, pixel_y + radius)
        self.free_grid(x, y)
        pygame.draw.circle(self.screen, self.fg_color, center, radius)

    def register_event_callback(self, event_type: int, callback: Callable):
        self.events_registry[event_type] = callback

    def register_key_callback(self, event_key: int, callback: Callable):
        self.key_registry[event_key] = callback

    def quit_handler(self, _):
        self.quit()

    def keydown_handler(self, event: pygame.event.EventType):
        if event.key in self.key_registry:
            self.key_registry[event.key](event)

    def do_every_frame(self, current_frame: int):
        pass

    def run(self, reset_frame: bool = True):
        while True:
            for event in pygame.event.get():
                if event.type in self.events_registry:
                    self.events_registry[event.type](event)
            self.do_every_frame(self.current_frame_no)
            pygame.display.update()
            self.fps_control.tick(self.fps)
            if reset_frame and self.current_frame_no % self.fps == 0:
                self.current_frame_no = 0
            self.current_frame_no += 1
