from .window import Window
from .assets import load_image
from .sprites import Sprite
from .gui import Button

class Toggle:
    def __init__(self, rect, value=False, color=(200,200,200), hover_color=(255,255,255)):
        # rect = (x, y, w, h)
        self.rect = rect
        self.value = value
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def update(self, win: Window):
        mx, my = win.mouse_pos
        x, y, w, h = self.rect
        self.hovered = x <= mx <= x+w and y <= my <= y+h
        if self.hovered and win.mouse_pressed(1):
            self.value = not self.value

    def draw(self, win: Window):
        draw_color = self.hover_color if self.hovered else self.color
        win.draw_rect(draw_color, self.rect)
        # optional: small “on” indicator
        if self.value:
            inner = (self.rect[0]+4, self.rect[1]+4, self.rect[2]-8, self.rect[3]-8)
            win.draw_rect((0,255,0), inner)


class Slider:
    def __init__(self, rect, min_val=0, max_val=100, value=50, color=(150,150,150), handle_radius=10):
        # rect = (x, y, w, h)
        self.rect = rect
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.color = color
        self.handle_radius = handle_radius
        self.dragging = False

    def update(self, win: Window):
        mx, my = win.mouse_pos
        x, y, w, h = self.rect

        handle_x = x + ((self.value - self.min_val) / (self.max_val - self.min_val)) * w
        handle_y = y + h // 2

        # start drag if mouse clicks inside slider bar area
        if win.mouse_pressed(1):
            if not self.dragging and (x <= mx <= x+w and y <= my <= y+h):
                self.dragging = True
        else:
            self.dragging = False  # stop drag when released

        # update value while dragging
        if self.dragging:
            rel_x = max(0, min(mx - x, w))  # clamp
            self.value = self.min_val + (rel_x / w) * (self.max_val - self.min_val)

    def draw(self, win: Window):
        x, y, w, h = self.rect
        win.draw_rect(self.color, (x, y + h//2 - 2, w, 4))
        handle_x = x + ((self.value - self.min_val) / (self.max_val - self.min_val)) * w
        handle_y = y + h // 2
        win.draw_circle((255, 0, 0), (int(handle_x), int(handle_y)), self.handle_radius)
