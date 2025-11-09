from crystalwindow import *

# --- custom player/ball class ---
class PlayerRect:
    def __init__(self, x, y, w=32, h=32, color=(255,0,0)):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.color = color
        self.vel_y = 0

    # draw either sprite or rect
    def draw(self, win):
        win.draw_rect(self.color, (self.x, self.y, self.width, self.height))

# --- setup window ---
win = Window(800, 600, "Gravity Sprite/Rect Test")

# --- player as colored rect ---
player = PlayerRect(100, 100, 50, 50, color=(0,255,0))

# --- platform as rect ---
class Platform:
    def __init__(self, x, y, w, h, color=(100,200,100)):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.color = color
    def draw(self, win):
        win.draw_rect(self.color, (self.x, self.y, self.width, self.height))

platform = Platform(0, 500, 800, 50)

# --- attach gravity ---
player.gravity = Gravity(player, force=1, bouncy=True, bounce_strength=0.7)

# --- main loop ---
def update(win):
    player.gravity.update(1/60, [platform])
    win.screen.fill((20,20,50))
    player.draw(win)
    platform.draw(win)

win.run(update)
win.quit()
