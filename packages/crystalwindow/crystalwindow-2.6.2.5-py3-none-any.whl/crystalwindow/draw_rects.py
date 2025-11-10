#draw_rects.py
import pygame as py
from crystalwindow import *

class DrawHelper:
    def __init__(self):
        pass

    def rect(self, win, x, y, w, h, color):
        py.draw.rect(win.screen, color, (x, y, w, h))
        return self

    def square(self, win, x, y, size, color):
        py.draw.rect(win.screen, color, (x, y, size, size))
        return self

    def circle(self, win, x, y, radius, color):
        py.draw.circle(win.screen, color, (x, y), radius)
        return self

    def triangle(self, win, points, color):
        py.draw.polygon(win.screen, color, points)
        return self

    def texture(self, win, x, y, w, h, image):
        if image:
            img = py.transform.scale(image, (w, h))
            win.screen.blit(img, (x, y))
        return self

    def text(self, win, text, font="Arial", size=16, x=0, y=0, color=(255,255,255), bold=False, cursive=False):
        fnt = py.font.SysFont(font, size, bold=bold, italic=cursive)
        surf = fnt.render(text, True, color)
        win.screen.blit(surf, (x, y))
        return self

    def gradient_rect(self, win, x, y, w, h, start_color, end_color, vertical=True):
        if vertical:
            for i in range(h):
                ratio = i / h
                r = int(start_color[0]*(1-ratio) + end_color[0]*ratio)
                g = int(start_color[1]*(1-ratio) + end_color[1]*ratio)
                b = int(start_color[2]*(1-ratio) + end_color[2]*ratio)
                py.draw.line(win.screen, (r, g, b), (x, y+i), (x+w, y+i))
        else:
            for i in range(w):
                ratio = i / w
                r = int(start_color[0]*(1-ratio) + end_color[0]*ratio)
                g = int(start_color[1]*(1-ratio) + end_color[1]*ratio)
                b = int(start_color[2]*(1-ratio) + end_color[2]*ratio)
                py.draw.line(win.screen, (r, g, b), (x+i, y), (x+i, y+h))
        return self
