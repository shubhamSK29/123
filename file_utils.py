# file_utils.py
import os
from colors import print_colored, Colors

def create_file_chooser(title: str, file_types: list, mode: str = "open", initial_dir: str = None) -> str:
    """
    Try to show a tkinter file dialog. If unavailable or it fails, fall back to manual input.
    file_types example: [("PNG", "*.png"), ("All files", "*.*")]
    mode: "open" or "save"
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        print_colored("tkinter not available - falling back to manual input.", Colors.WARNING)
        return input(f"Enter file path for {title}: ").strip()

    try:
        root = tk.Tk()
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        if initial_dir is None:
            initial_dir = os.getcwd()

        if mode == "save":
            path = filedialog.asksaveasfilename(title=title, filetypes=file_types, initialdir=initial_dir, defaultextension=file_types[0][1].replace('*','') if file_types else "")
        else:
            path = filedialog.askopenfilename(title=title, filetypes=file_types, initialdir=initial_dir)

        root.destroy()
        if not path:
            print_colored("File dialog cancelled.", Colors.WARNING)
        else:
            print_colored(f"Selected: {path}", Colors.SUCCESS)
        return path or ""
    except Exception as e:
        print_colored(f"File dialog error: {e}", Colors.ERROR)
        return input(f"Enter file path for {title}: ").strip()

def save_binary_file_manual(filename: str, data: bytes) -> bool:
    try:
        with open(filename, "wb") as f:
            f.write(data)
        print_colored(f"Binary saved: {filename}", Colors.SUCCESS)
        return True
    except Exception as e:
        print_colored(f"Failed to save binary file: {e}", Colors.ERROR)
        return False

def read_binary_file(file_path: str) -> bytes:
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading file: {e}")

