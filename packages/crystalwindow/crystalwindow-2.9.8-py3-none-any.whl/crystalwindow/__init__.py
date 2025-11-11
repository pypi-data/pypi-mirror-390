# crystalwindow/__init__.py
# 💎 CrystalWindow - Master Import Hub
from .ver_warner import check_for_update
check_for_update("crystalwindow")

# === Core Systems ===
from .window import Window
from .sprites import Sprite
from .tilemap import TileMap
from .player import Player
from .gravity import Gravity
from .FileHelper import FileHelper
from .math import Mathematics

# === Assets & Animation ===
from .assets import load_image, load_folder_images, load_music, play_music
from .animation import Animation

# === Collision ===
from .collision import check_collision, resolve_collision

# === GUI & Extensions ===
from .gui import Button, Label, GUIManager, random_color, hex_to_rgb
from .gui_ext import Toggle, Slider

# === Drawing Helpers ===
from .draw_helpers import gradient_rect, CameraShake
from .draw_rects import DrawHelper
from .draw_text_helper import DrawTextManager
from .draw_tool import CrystalDraw

# === Misc Helpers ===
from .fun_helpers import random_name, DebugOverlay


__all__ = [
    # --- Core ---
    "Window", "Sprite", "TileMap", "Player", "Gravity", "FileHelper", "Mathematics",
    
    # --- Assets & Animation ---
    "load_image", "load_folder_images", "load_music", "play_music", "Animation",
    
    # --- Collision ---
    "check_collision", "resolve_collision",
    
    # --- GUI ---
    "Button", "Label", "GUIManager", "random_color", "hex_to_rgb",
    
    # --- GUI Extensions ---
    "Toggle", "Slider",
    
    # --- Drawing ---
    "gradient_rect", "CameraShake", "DrawHelper", "DrawTextManager", "CrystalDraw",
    
    # --- Misc ---
    "random_name", "DebugOverlay",
]
