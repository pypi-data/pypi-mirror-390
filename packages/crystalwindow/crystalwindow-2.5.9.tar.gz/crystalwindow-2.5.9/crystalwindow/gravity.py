class Gravity:
    def __init__(self, obj, force=1, terminal_velocity=15, bouncy=False, bounce_strength=0.7):
        self.obj = obj
        if not hasattr(self.obj, "vel_y"):
            self.obj.vel_y = 0
        self.force = force
        self.terminal_velocity = terminal_velocity
        self.bouncy = bouncy
        self.bounce_strength = bounce_strength
        self.on_ground = False
        self.stretch_factor = 0  # for squishy effect

        # --- NEW: choose mode ---
        # If object has .sprite use that, else fallback to rect mode
        if hasattr(obj, "sprite"):
            self.mode = "sprite"
        else:
            self.mode = "rect"

    def get_obj_rect(self):
        # helper to get x,y,w,h depending on mode
        if self.mode == "sprite":
            s = self.obj.sprite
            x = getattr(s, "x", 0)
            y = getattr(s, "y", 0)
            w = getattr(s, "width", getattr(s, "w", 32))
            h = getattr(s, "height", getattr(s, "h", 32))
        else:
            x = getattr(self.obj, "x", 0)
            y = getattr(self.obj, "y", 0)
            w = getattr(self.obj, "width", getattr(self.obj, "w", 32))
            h = getattr(self.obj, "height", getattr(self.obj, "h", 32))
        return x, y, w, h

    def update(self, dt, platforms=[]):
        # apply gravity
        self.obj.vel_y += self.force * dt * 60
        if self.obj.vel_y > self.terminal_velocity:
            self.obj.vel_y = self.terminal_velocity

        # move object
        x, y, w, h = self.get_obj_rect()
        y += self.obj.vel_y
        self.on_ground = False

        # check collisions
        for plat in platforms:
            plat_w = getattr(plat, "width", getattr(plat, "w", 0))
            plat_h = getattr(plat, "height", getattr(plat, "h", 0))
            if (x + w > plat.x and x < plat.x + plat_w and
                y + h > plat.y and y < plat.y + plat_h):
                
                y = plat.y - h
                self.on_ground = True

                if self.bouncy:
                    self.obj.vel_y = -self.obj.vel_y * self.bounce_strength
                    self.stretch_factor = min(0.5, self.stretch_factor + 0.2)
                else:
                    self.obj.vel_y = 0
                    self.stretch_factor = 0

        # slowly reset stretch
        if self.stretch_factor > 0:
            self.stretch_factor -= 0.05
            if self.stretch_factor < 0:
                self.stretch_factor = 0

        # write back position
        if self.mode == "sprite":
            self.obj.sprite.x = x
            self.obj.sprite.y = y
        else:
            self.obj.x = x
            self.obj.y = y
