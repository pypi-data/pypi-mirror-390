from .sprites import Sprite

class TileMap:
    def __init__(self, tile_size):
        self.tile_size = tile_size
        self.tiles = []

    def add_tile(self, image, x, y):
        self.tiles.append(Sprite(image, x, y))

    def draw(self, win):
        for t in self.tiles:
            win.draw_sprite(t)
