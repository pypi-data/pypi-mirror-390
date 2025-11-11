#Sprites.py
from tkinter import PhotoImage

class Sprite:
    def __init__(self, pos, size=None, image=None, color=(255, 0, 0)):
        """
        pos: (x, y) top-left
        size: (w, h) if you want a plain colored rect
        image: PhotoImage (Tkinter)
        color: fill color if size is used
        """
        self.pos = pos
        self.x, self.y = pos

        if image is not None:
            self.image = image
            self.width = image.width()
            self.height = image.height()
        elif size is not None:
            self.width, self.height = size
            self.image = None
            self.color = color
        else:
            raise ValueError("Sprite needs either size or image")

    def draw(self, win):
        """Draw sprite on given Window"""
        if self.image:
            win.canvas.create_image(self.x, self.y, anchor="nw", image=self.image)
        else:
            win.draw_rect(self.color, (self.x, self.y, self.width, self.height))

    def move(self, dx, dy):
        """Move sprite by dx/dy"""
        self.x += dx
        self.y += dy
        self.pos = (self.x, self.y)
