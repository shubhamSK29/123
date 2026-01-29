#!/usr/bin/env python3
"""
Fractured Key - GUI Launcher
Run this file to start the modern GUI application
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check for customtkinter
try:
    import customtkinter
except ImportError:
    print("=" * 60)
    print("CustomTkinter not found. Installing...")
    print("=" * 60)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter

# Launch the application
from fractured_gui import main

if __name__ == "__main__":
    print("=" * 60)
    print("  FRACTURED KEY - Modern Password Manager")
    print("  Starting GUI...")
    print("=" * 60)
    main()
