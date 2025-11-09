#draw_tool.py

import pygame
from .gui import hex_to_rgb

class CrystalDraw:
    def __init__(self, surface, brush_color="#00aaff", brush_size=8, canvas_rect=None):
        """
        surface: pygame.Surface to draw on
        brush_color: str or tuple, brush color
        brush_size: int, size of the brush
        canvas_rect: pygame.Rect or tuple (x, y, w, h) defining canvas area (optional)
        """
        self.surface = surface
        self.brush_color = hex_to_rgb(brush_color)
        self.brush_size = brush_size
        self.drawing = False
        self.last_pos = None

        # define drawing area (whole screen if None)
        if canvas_rect:
            self.canvas_rect = pygame.Rect(canvas_rect)
        else:
            self.canvas_rect = surface.get_rect()

        # transparent canvas layer
        self.canvas = pygame.Surface(self.canvas_rect.size, pygame.SRCALPHA)
        self.canvas.fill((0, 0, 0, 0))

    def set_color(self, color):
        if isinstance(color, str):
            self.brush_color = hex_to_rgb(color)
        else:
            self.brush_color = color

    def set_brush_size(self, size):
        self.brush_size = max(1, int(size))

    def clear(self):
        self.canvas.fill((0, 0, 0, 0))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.canvas_rect.collidepoint(event.pos):
                self.drawing = True
                self.last_pos = (event.pos[0] - self.canvas_rect.x, event.pos[1] - self.canvas_rect.y)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drawing = False
            self.last_pos = None
        elif event.type == pygame.MOUSEMOTION and self.drawing:
            rel_pos = (event.pos[0] - self.canvas_rect.x, event.pos[1] - self.canvas_rect.y)
            if 0 <= rel_pos[0] < self.canvas_rect.w and 0 <= rel_pos[1] < self.canvas_rect.h:
                if self.last_pos:
                    pygame.draw.line(self.canvas, self.brush_color, self.last_pos, rel_pos, self.brush_size)
                self.last_pos = rel_pos

    def draw(self):
        self.surface.blit(self.canvas, self.canvas_rect.topleft)
