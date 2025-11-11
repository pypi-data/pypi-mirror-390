import os
from tkinter import PhotoImage

ASSETS = {}

def load_image(path, size=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    img = PhotoImage(file=path)
    ASSETS[path] = img
    return img

def load_folder_images(folder, nested=True):
    result = {}
    for item in os.listdir(folder):
        full_path = os.path.join(folder, item)
        if os.path.isdir(full_path) and nested:
            result[item] = load_folder_images(full_path, nested=True)
        elif item.lower().endswith((".png", ".gif")):  # Tk supports PNG/GIF
            result[item] = load_image(full_path)
    return result

def load_music(path):
    """No-op: Tkinter does not handle music. Placeholder for compatibility."""
    print(f"[assets] Music loading not supported in this current crystalwindow ver sorry! ~Crystal: {path}")
    return None

def play_music(loop=-1):
    """No-op: placeholder."""
    print("[assets] Music playback not supported in this current crystalwindow ver sorry! ~Crystal")
