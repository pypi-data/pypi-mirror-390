import math, os, re
from .assets import load_folder_images
from .animation import Animation

class Player:
    def __init__(self, pos=(0, 0), speed=5, size=(32, 32)):
        self.x, self.y = pos
        self.speed = speed
        self.width, self.height = size
        self.animations = {}
        self.current_anim = None
        self.image = None
        self.rect = self._make_rect()
    
    # make a lil rect obj for collisions
    def _make_rect(self):
        return type("Rect", (), {"x": self.x, "y": self.y, "w": self.width, "h": self.height,
                                 "topleft": (self.x, self.y)})()

    # === animation setup ===
    def idle(self, folder):
        imgs = self._load_sorted(folder)
        anim = Animation(imgs)
        self.animations["idle"] = anim
        self.current_anim = anim
        return anim

    class walk:
        @staticmethod
        def cycle(folder):
            imgs = Player._load_sorted_static(folder)
            anim = Animation(imgs)
            anim.loop = True
            return anim
        
        @staticmethod
        def once(folder):
            imgs = Player._load_sorted_static(folder)
            anim = Animation(imgs)
            anim.loop = False
            return anim

    class jump:
        @staticmethod
        def cycle(folder):
            imgs = Player._load_sorted_static(folder)
            anim = Animation(imgs)
            anim.loop = True
            return anim

        @staticmethod
        def once(folder):
            imgs = Player._load_sorted_static(folder)
            anim = Animation(imgs)
            anim.loop = False
            return anim

    # === main update ===
    def update(self, dt, win):
        moving = False
        if win.is_key_pressed("left"):
            self.x -= self.speed * dt * 60
            moving = True
        if win.is_key_pressed("right"):
            self.x += self.speed * dt * 60
            moving = True
        if win.is_key_pressed("up"):
            self.y -= self.speed * dt * 60
            moving = True
        if win.is_key_pressed("down"):
            self.y += self.speed * dt * 60
            moving = True

        # update animation
        if moving and "run" in self.animations:
            self.current_anim = self.animations["run"]
        elif not moving and "idle" in self.animations:
            self.current_anim = self.animations["idle"]

        if self.current_anim:
            self.current_anim.update(dt)
            self.image = self.current_anim.get_frame()

        self.rect.x, self.rect.y = self.x, self.y
        self.rect.topleft = (self.x, self.y)

    def draw(self, win):
        if self.image:
            win.screen.blit(self.image, (self.x, self.y))

    # ---------- helpers ----------
    def _load_sorted(self, folder):
        imgs_dict = load_folder_images(folder)
        return self._sort_images(imgs_dict)

    @staticmethod
    def _load_sorted_static(folder):
        imgs_dict = load_folder_images(folder)
        return Player._sort_images(imgs_dict)

    @staticmethod
    def _sort_images(imgs_dict):
        def extract_num(filename):
            match = re.search(r'(\d+)', filename)
            return int(match.group(1)) if match else 0
        return [img for name, img in sorted(imgs_dict.items(), key=lambda x: extract_num(x[0]))]
