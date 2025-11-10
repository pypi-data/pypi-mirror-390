#Sprites.py
import pygame

class Sprite:
    def __init__(self, pos, size=None, image=None, color=(255, 0, 0)):
        """
        pos: (x, y) topleft
        size: (w, h) if you want a plain rect
        image: pygame.Surface if u have an image
        color: fill color if size is used
        """
        # position setup
        self.pos = pos
        self.x, self.y = pos  

        # choose between image or color surface
        if image is not None:
            self.image = image
        elif size is not None:
            self.image = pygame.Surface(size)
            self.image.fill(color)
        else:
            raise ValueError("Sprite needs either size or image")

        # rect + size setup
        self.rect = self.image.get_rect(topleft=pos)
        self.width, self.height = self.image.get_size()  # <-- added!

    def draw(self, win):
        """Draw sprite on given surface"""
        win.blit(self.image, self.rect)

    def move(self, dx, dy):
        """Move sprite by dx/dy"""
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)
        self.pos = (self.x, self.y)  # <-- keeps pos synced too!
