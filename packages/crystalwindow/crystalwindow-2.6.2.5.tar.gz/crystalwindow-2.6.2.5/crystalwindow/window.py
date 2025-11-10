#Window Management.
import pygame
from pygame import image
import os
import sys
import contextlib
import base64, io

# === Console Boot Message ===
main_file = os.path.basename(sys.argv[0])
print(f"Welcome Future Dev!, running.. '{main_file}'")
# Remove the default pygame welcome message
with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
    pygame.init()

DEFAULT_LOGO_BASE64 = "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"

def decode_logo():
    """Decode the base64 logo and return a pygame surface."""
    logo_data = base64.b64decode(DEFAULT_LOGO_BASE64)
    with io.BytesIO(logo_data) as logo_bytes:
        return image.load(logo_bytes)
class Window:
    # friendly string -> pygame constant mapping
    KEY_MAP = {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "space": pygame.K_SPACE,
        "enter": pygame.K_RETURN,
        "backspace": pygame.K_BACKSPACE,
        "tab": pygame.K_TAB,
        "escape": pygame.K_ESCAPE,
        "Rshift": pygame.K_LSHIFT,
        "Lctrl": pygame.K_LCTRL,
        "Rshift": pygame.K_RSHIFT,
        "Rctrl": pygame.K_RCTRL,
        "alt": pygame.K_LALT,
        "keya": pygame.K_a,
        "keyb": pygame.K_b,
        "keyc": pygame.K_c,
        "keyd": pygame.K_d,
        "keye": pygame.K_e,
        "keyf": pygame.K_f,
        "keyg": pygame.K_g,
        "keyh": pygame.K_h,
        "keyi": pygame.K_i,
        "keyj": pygame.K_j,
        "keyk": pygame.K_k,
        "keyl": pygame.K_l,
        "keym": pygame.K_m,
        "keyn": pygame.K_n,
        "keyo": pygame.K_o,
        "keyp": pygame.K_p,
        "keyq": pygame.K_q,
        "keyr": pygame.K_r,
        "keys": pygame.K_s,
        "keyt": pygame.K_t,
        "keyu": pygame.K_u,
        "keyv": pygame.K_v,
        "keyw": pygame.K_w,
        "keyx": pygame.K_x,
        "keyy": pygame.K_y,
        "keyz": pygame.K_z,
        "0": pygame.K_0,
        "1": pygame.K_1,
        "2": pygame.K_2,
        "3": pygame.K_3,
        "4": pygame.K_4,
        "5": pygame.K_5,
        "6": pygame.K_6,
        "7": pygame.K_7,
        "8": pygame.K_8,
        "9": pygame.K_9,
        "f1": pygame.K_F1,
        "f2": pygame.K_F2,
        "f3": pygame.K_F3,
        "f4": pygame.K_F4,
        "f5": pygame.K_F5,
        "f6": pygame.K_F6,
        "f7": pygame.K_F7,
        "f8": pygame.K_F8,
        "f9": pygame.K_F9,
        "f10": pygame.K_F10,
        "f11": pygame.K_F11,
        "f12": pygame.K_F12,
        "insert": pygame.K_INSERT,
        "delete": pygame.K_DELETE,
        "home": pygame.K_HOME,
        "end": pygame.K_END,
        "pageup": pygame.K_PAGEUP,
        "pagedown": pygame.K_PAGEDOWN,
        "capslock": pygame.K_CAPSLOCK,
        "numlock": pygame.K_NUMLOCK,
        "scrolllock": pygame.K_SCROLLLOCK,
        "+": pygame.K_PLUS,
        "-": pygame.K_MINUS,
        "/": pygame.K_SLASH,
        "backslash": pygame.K_BACKSLASH,
        "*": pygame.K_ASTERISK,
        "=": pygame.K_EQUALS
    }


    def __init__(self, width=640, height=480, title="Game Window", icon=None):
        # temporarily silence pygame print
        with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
            pygame.init()  # <- no more hello message

        self.width = width
        self.height = height
        self.title = title
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        # --- ICON HANDLING ---
        if icon:
            # User provided icon logic
            if isinstance(icon, str):  # Path provided as string
                icon_path = icon
                if not os.path.isabs(icon_path):
                    icon_path = os.path.join(os.getcwd(), icon)  # Relative path, make it absolute
                
                if os.path.exists(icon_path):  # Valid path
                    img = pygame.image.load(icon_path).convert_alpha()
                    pygame.display.set_icon(img)
                else:  # File not found
                    print(f"⚠️ Icon file not found: {icon_path}")
                    img = decode_logo()  # Use default base64 logo
                    pygame.display.set_icon(img)
            else:
                pygame.display.set_icon(icon)  # Use the provided icon directly
        else:
            # No icon provided, check for default in the local directory
            default_icon_path = os.path.join(os.path.dirname(__file__), "icons", "default_icon.png")
            if os.path.exists(default_icon_path):
                img = pygame.image.load(default_icon_path).convert_alpha()
                pygame.display.set_icon(img)
            else:
                # Use base64 fallback
                img = decode_logo()
                pygame.display.set_icon(img)

        self.clock = pygame.time.Clock()
        self.running = True
        self.keys = {}
        self.mouse_pos = (0, 0)
        self._mouse_pressed = (False, False, False)  # <-- renamed w/ underscore
        self.draw_calls = []

    # === input helpers ===
    def key_pressed(self, key):
        # key can be pygame constant OR string from KEY_MAP
        if isinstance(key, str):
            key = self.KEY_MAP.get(key, None)
            if key is None:
                return False
        return self.keys.get(key, False)

    def mouse_pressed(self, button=1):
        return self._mouse_pressed[button - 1]

    # === font system ===
    def get_font(self, name="Arial", size=16, bold=False, italic=False):
        if not hasattr(self, "font_cache"):
            self.font_cache = {}
        key = (name, size, bold, italic)
        if key not in self.font_cache:
            try:
                font = pygame.font.SysFont(name, size, bold, italic)
            except:
                font = pygame.font.Font(None, size)
            self.font_cache[key] = font
        return self.font_cache[key]

    def draw_text(self, text, font="Arial", size=16, color=(255,255,255), pos=(0,0), bold=False, italic=False):
        f = self.get_font(font, size, bold, italic)
        surf = f.render(text, True, color)
        self.screen.blit(surf, pos)

    # === drawing helpers ===
    def draw_rect(self, color, rect):
        self.draw_calls.append(("rect", color, rect))

    def draw_circle(self, color, pos, radius):
        self.draw_calls.append(("circle", color, pos, radius))

    def draw_sprite(self, sprite):
        self.draw_calls.append(("sprite", sprite))

    def draw_text_later(self, *args, **kwargs):
        self.draw_calls.append(("text", args, kwargs))

    # === main loop ===
    def run(self, update_func=None, bg=(20,20,50)):
        if bg is not None:
            self._bg_color = bg
        if not hasattr(self, "_bg_color"):
            self._bg_color = (20, 20, 50)

        self.running = True        
        while self.running:
            self._filled_this_frame = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    print("Bye Bye!, Future Dev!. quitting '{main_file}'......")
                elif event.type == pygame.KEYDOWN:
                    self.keys[event.key] = True
                elif event.type == pygame.KEYUP:
                    self.keys[event.key] = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._mouse_pressed = pygame.mouse.get_pressed()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self._mouse_pressed = pygame.mouse.get_pressed()
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos

            if update_func:
                update_func(self)
    
            # only auto-fill if user didnt fill manually this frame
            if not getattr(self, "_filled_this_frame", False):
                self.screen.fill(self._bg_color)                   

            for call in self.draw_calls:
                if call[0] == "rect":
                    pygame.draw.rect(self.screen, call[1], call[2])
                elif call[0] == "circle":
                    pygame.draw.circle(self.screen, call[1], call[2], call[3])
                elif call[0] == "sprite":
                    call[1].draw(self.screen)
                elif call[0] == "text":
                    self.draw_text(*call[1], **call[2])

            self.draw_calls.clear()


            pygame.display.flip()
            self.clock.tick(60)

    def fill(self, color):
        """Change the window's background color immediately.
        Supports:
            - RGB tuple: (255, 0, 0)
            - Hex string: "#FF00FF" or "FF00FF"
            - Predefined color variable (tuple)
        """
        # if its a string (hex)
        if isinstance(color, str):
            hex_str = color.lstrip("#")  # remove # if present
            if len(hex_str) == 6:  # standard RGB
                try:
                    color = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
                except ValueError:
                    print(f"[fill warning] invalid hex color: {color}")
                    color = (0, 0, 0)  # fallback
            else:
                print(f"[fill warning] hex must be 6 digits: {color}")
                color = (0, 0, 0)
        # if its not a tuple now, try to use it directly (like a predefined tuple)
        elif not isinstance(color, tuple):
            try:
                color = tuple(color)
            except Exception:
                print(f"[fill warning] invalid color: {color}")
                color = (0, 0, 0)

        self._bg_color = color
        self.screen.fill(color)
        self._filled_this_frame = True

    def check_events(self):
        """Handle quit, keyboard, and mouse events (like pygame.event.get())."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.keys[event.key] = True
            elif event.type == pygame.KEYUP:
                self.keys[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_pressed = pygame.mouse.get_pressed()
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_pressed = pygame.mouse.get_pressed()
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

    def quit(self):
        pygame.quit()
        sys.exit()
