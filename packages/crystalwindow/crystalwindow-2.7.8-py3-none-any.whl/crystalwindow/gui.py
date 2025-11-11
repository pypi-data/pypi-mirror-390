#gui.py
import random

# ----------------- Color Helpers -----------------
def hex_to_rgb(hex_str):
    """Convert hex color string to RGB tuple"""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def random_color():
    """Return a random RGB color"""
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

def lerp_color(c1, c2, t):
    """Linearly interpolate between two colors"""
    return tuple(int(a + (b-a)*t) for a,b in zip(c1,c2))

# ----------------- GUI Elements -----------------
class Button:
    def __init__(self, rect, text, color=(200,200,200), hover_color=(255,255,255), callback=None):
        self.rect = rect  # (x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.callback = callback
        self.hovered = False

    def draw(self, win):
        x, y, w, h = self.rect
        mx, my = win.mouse_pos
        self.hovered = x <= mx <= x+w and y <= my <= y+h
        cur_color = self.hover_color if self.hovered else self.color
        win.draw_rect(cur_color, self.rect)
        win.draw_text(self.text, pos=(x+5, y+5))

    def check_click(self, win):
        mx, my = win.mouse_pos
        x, y, w, h = self.rect
        if x <= mx <= x+w and y <= my <= y+h and win.mouse_pressed(1):
            if self.callback:
                self.callback()

class Label:
    def __init__(self, pos, text, color=(255,255,255), font="Arial", size=16):
        self.pos = pos
        self.text = text
        self.color = color
        self.font = font
        self.size = size

    def draw(self, win):
        win.draw_text(self.text, font=self.font, size=self.size, color=self.color, pos=self.pos)

# ----------------- Optional GUI Manager -----------------
class GUIManager:
    def __init__(self):
        self.elements = []

    def add(self, element):
        self.elements.append(element)

    def draw(self, win):
        for e in self.elements:
            e.draw(win)

    def update(self, win):
        for e in self.elements:
            if isinstance(e, Button):
                e.check_click(win)
