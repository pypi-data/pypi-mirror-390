#assets.py
import pygame
import os

ASSETS = {}

def load_image(path, size=None):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    ASSETS[path] = img
    return img

def load_folder_images(folder, size=None, nested=True):
    result = {}
    for item in os.listdir(folder):
        full_path = os.path.join(folder, item)
        if os.path.isdir(full_path) and nested:
            result[item] = load_folder_images(full_path, size=size, nested=True)
        elif item.lower().endswith((".png", ".jpg", ".jpeg")):
            result[item] = load_image(full_path, size=size)
    return result

def load_music(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Music not found: {path}")
    pygame.mixer.music.load(path)
    ASSETS[path] = path
    return path

def play_music(loop=-1):
    pygame.mixer.music.play(loop)
