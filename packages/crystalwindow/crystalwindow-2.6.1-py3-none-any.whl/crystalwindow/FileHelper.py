"""
CrystalWindow FileHelper
------------------------
A utility class that handles saving/loading text, JSON, and pickle files,
with optional Tk file dialogs and a default 'saves' directory.
"""

import os
import json
import pickle
import tkinter as tk
from tkinter import filedialog


class FileHelper:
    """CrystalWindow integrated file helper with default folders & Tk dialogs."""

    def __init__(self, default_save_folder="saves"):
        """
        Initialize the FileHelper.

        Args:
            default_save_folder (str): Folder to save files in by default.
                                       Created automatically if missing.
        """
        self.default_save_folder = default_save_folder
        os.makedirs(self.default_save_folder, exist_ok=True)

    # -------------------------------------------------------------------------
    # TK FILE DIALOGS
    # -------------------------------------------------------------------------
    def ask_save_file(self, default_name="save.json",
                      filetypes=[("JSON files", "*.json"), ("All files", "*.*")]):
        """Open a Tkinter Save dialog starting in the default folder."""
        root = tk.Tk()
        root.withdraw()
        path = filedialog.asksaveasfilename(
            title="Save As",
            initialdir=self.default_save_folder,
            initialfile=default_name,
            filetypes=filetypes,
            defaultextension=filetypes[0][1]
        )
        root.destroy()
        return path if path else None  # Return None if cancelled

    def ask_open_file(self,
                      filetypes=[("JSON files", "*.json"), ("All files", "*.*")]):
        """Open a Tkinter Open dialog starting in the default folder."""
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(
            title="Open File",
            initialdir=self.default_save_folder,
            filetypes=filetypes
        )
        root.destroy()
        return path if path else None

    # -------------------------------------------------------------------------
    # INTERNAL PATH HELPER
    # -------------------------------------------------------------------------
    def _resolve_path(self, filename):
        """Return a full path, resolving relative paths to the default folder."""
        if not filename:
            return None
        if os.path.isabs(filename):
            return filename
        return os.path.join(self.default_save_folder, filename)

    # -------------------------------------------------------------------------
    # TEXT FILES
    # -------------------------------------------------------------------------
    def save_text(self, filename, content):
        """Save plain text data to a file."""
        path = self._resolve_path(filename)
        if not path:
            print("[CANCELLED] No save path provided.")
            return None
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] Text saved to: {path}")
        return path

    def load_text(self, filename):
        """Load plain text data from a file."""
        path = self._resolve_path(filename)
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        print(f"[WARN] Text file not found: {path}")
        return None

    # -------------------------------------------------------------------------
    # JSON FILES
    # -------------------------------------------------------------------------
    def save_json(self, filename, data):
        """Save JSON-serializable data."""
        path = self._resolve_path(filename)
        if not path:
            print("[CANCELLED] No save path provided.")
            return None
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[INFO] JSON saved to: {path}")
        return path

    def load_json(self, filename):
        """Load JSON data."""
        path = self._resolve_path(filename)
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        print(f"[WARN] JSON file not found: {path}")
        return None

    # -------------------------------------------------------------------------
    # PICKLE FILES
    # -------------------------------------------------------------------------
    def save_pickle(self, filename, obj):
        """Save a Python object using pickle."""
        path = self._resolve_path(filename)
        if not path:
            print("[CANCELLED] No save path provided.")
            return None
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(obj, f)
        print(f"[INFO] Pickle saved to: {path}")
        return path

    def load_pickle(self, filename):
        """Load a pickled Python object."""
        path = self._resolve_path(filename)
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                return pickle.load(f)
        print(f"[WARN] Pickle file not found: {path}")
        return None

