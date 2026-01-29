#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   ███████╗██████╗  █████╗  ██████╗████████╗██╗   ██╗██████╗ ███████╗██████╗   ║
║   ██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██║   ██║██╔══██╗██╔════╝██╔══██╗  ║
║   █████╗  ██████╔╝███████║██║        ██║   ██║   ██║██████╔╝█████╗  ██║  ██║  ║
║   ██╔══╝  ██╔══██╗██╔══██║██║        ██║   ██║   ██║██╔══██╗██╔══╝  ██║  ██║  ║
║   ██║     ██║  ██║██║  ██║╚██████╗   ██║   ╚██████╔╝██║  ██║███████╗██████╔╝  ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝   ║
║                                                                               ║
║                     ██╗  ██╗███████╗██╗   ██╗                                 ║
║                     ██║ ██╔╝██╔════╝╚██╗ ██╔╝                                 ║
║                     █████╔╝ █████╗   ╚████╔╝                                  ║
║                     ██╔═██╗ ██╔══╝    ╚██╔╝                                   ║
║                     ██║  ██╗███████╗   ██║                                    ║
║                     ╚═╝  ╚═╝╚══════╝   ╚═╝                                    ║
║                                                                               ║
║              Premium Steganographic Password Vault v2.5                       ║
║              Modern UI/UX Design • 2024-2025 Edition                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import threading
import os
import sys
import math
import random
import platform
import subprocess
from typing import Callable, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-PLATFORM FILE DIALOG HELPER
# Uses native file dialogs on Linux (zenity/kdialog) for better UX
# ═══════════════════════════════════════════════════════════════════════════════

class NativeFileDialog:
    """Cross-platform native file dialog wrapper"""
    
    @staticmethod
    def _is_linux():
        return platform.system() == "Linux"
    
    @staticmethod
    def _has_zenity():
        try:
            subprocess.run(["which", "zenity"], capture_output=True, check=True)
            return True
        except:
            return False
    
    @staticmethod
    def _has_kdialog():
        try:
            subprocess.run(["which", "kdialog"], capture_output=True, check=True)
            return True
        except:
            return False
    
    @staticmethod
    def askopenfilename(title="Select File", filetypes=None, parent=None):
        """Open file dialog - uses native dialog on Linux"""
        if NativeFileDialog._is_linux():
            # Try zenity first (GNOME/GTK)
            if NativeFileDialog._has_zenity():
                try:
                    cmd = ["zenity", "--file-selection", f"--title={title}"]
                    if filetypes:
                        for name, patterns in filetypes:
                            if isinstance(patterns, tuple):
                                for p in patterns:
                                    cmd.extend(["--file-filter", f"{name} | {p}"])
                            else:
                                cmd.extend(["--file-filter", f"{name} | {patterns}"])
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        return result.stdout.strip()
                    return ""
                except Exception:
                    pass
            
            # Try kdialog (KDE)
            if NativeFileDialog._has_kdialog():
                try:
                    cmd = ["kdialog", "--getopenfilename", os.path.expanduser("~"), "--title", title]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        return result.stdout.strip()
                    return ""
                except Exception:
                    pass
        
        # Fallback to tkinter
        return filedialog.askopenfilename(title=title, filetypes=filetypes, parent=parent)
    
    @staticmethod
    def asksaveasfilename(title="Save File", filetypes=None, defaultextension="", parent=None):
        """Save file dialog - uses native dialog on Linux"""
        if NativeFileDialog._is_linux():
            # Try zenity first (GNOME/GTK)
            if NativeFileDialog._has_zenity():
                try:
                    cmd = ["zenity", "--file-selection", "--save", "--confirm-overwrite", f"--title={title}"]
                    if filetypes:
                        for name, patterns in filetypes:
                            if isinstance(patterns, tuple):
                                for p in patterns:
                                    cmd.extend(["--file-filter", f"{name} | {p}"])
                            else:
                                cmd.extend(["--file-filter", f"{name} | {patterns}"])
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        path = result.stdout.strip()
                        # Add extension if missing
                        if defaultextension and not path.endswith(defaultextension):
                            path += defaultextension
                        return path
                    return ""
                except Exception:
                    pass
            
            # Try kdialog (KDE)
            if NativeFileDialog._has_kdialog():
                try:
                    cmd = ["kdialog", "--getsavefilename", os.path.expanduser("~"), "--title", title]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        path = result.stdout.strip()
                        if defaultextension and not path.endswith(defaultextension):
                            path += defaultextension
                        return path
                    return ""
                except Exception:
                    pass
        
        # Fallback to tkinter
        return filedialog.asksaveasfilename(
            title=title, 
            filetypes=filetypes, 
            defaultextension=defaultextension,
            parent=parent
        )

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from steganography import embed_data_into_image, extract_data_from_image
    from sss import split_bytes_into_shares, recover_bytes_from_shares
    from crypto import encrypt_password_aes_gcm, decrypt_password_aes_gcm
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM - "Fractured Key" Premium Theme 2024-2025
# ═══════════════════════════════════════════════════════════════════════════════

class Theme:
    """
    Premium Color Palette - Dark Cyber Theme
    Inspired by: Encryption, Digital Fragments, Security, Futuristic Systems
    """
    
    # ─────────────────────────────────────────────────────────────────────────
    # Primary Background Colors (Deep, Layered Darkness)
    # ─────────────────────────────────────────────────────────────────────────
    BG_VOID = "#030508"           # Deepest void - pure darkness
    BG_ABYSS = "#060A10"          # Primary background
    BG_DEEP = "#0A0F18"           # Secondary background
    BG_DARK = "#0E1420"           # Card backgrounds
    BG_MEDIUM = "#141C2B"         # Elevated surfaces
    BG_LIGHT = "#1A2436"          # Input backgrounds
    BG_HOVER = "#212D42"          # Hover states
    BG_ACTIVE = "#283548"         # Active/pressed states
    
    # ─────────────────────────────────────────────────────────────────────────
    # Accent Colors (Electric Cyan - Primary)
    # ─────────────────────────────────────────────────────────────────────────
    ACCENT_BRIGHT = "#00F0FF"     # Brightest cyan - glow effects
    ACCENT_PRIMARY = "#00D4E8"    # Primary accent
    ACCENT_MEDIUM = "#00B8CC"     # Medium accent
    ACCENT_MUTED = "#0099AA"      # Muted accent
    ACCENT_DARK = "#007788"       # Dark accent
    ACCENT_DEEPER = "#005566"     # Deeper accent
    
    # ─────────────────────────────────────────────────────────────────────────
    # Secondary Accent (Purple/Violet - Mystical)
    # ─────────────────────────────────────────────────────────────────────────
    PURPLE_BRIGHT = "#A855F7"     # Bright purple
    PURPLE_PRIMARY = "#8B5CF6"    # Primary purple
    PURPLE_MUTED = "#7C3AED"      # Muted purple
    PURPLE_DARK = "#6D28D9"       # Dark purple
    
    # ─────────────────────────────────────────────────────────────────────────
    # Semantic Colors
    # ─────────────────────────────────────────────────────────────────────────
    SUCCESS_BRIGHT = "#34D399"    # Bright green
    SUCCESS = "#10B981"           # Success green
    SUCCESS_DARK = "#059669"      # Dark green
    
    WARNING_BRIGHT = "#FBBF24"    # Bright amber
    WARNING = "#F59E0B"           # Warning amber
    WARNING_DARK = "#D97706"      # Dark amber
    
    ERROR_BRIGHT = "#F87171"      # Bright red
    ERROR = "#EF4444"             # Error red
    ERROR_DARK = "#DC2626"        # Dark red
    
    # ─────────────────────────────────────────────────────────────────────────
    # Text Colors
    # ─────────────────────────────────────────────────────────────────────────
    TEXT_PRIMARY = "#F8FAFC"      # Primary text - pure white
    TEXT_SECONDARY = "#CBD5E1"    # Secondary text
    TEXT_TERTIARY = "#94A3B8"     # Tertiary text
    TEXT_MUTED = "#64748B"        # Muted text
    TEXT_DISABLED = "#475569"     # Disabled text
    TEXT_ACCENT = "#00F0FF"       # Accent text (cyan glow)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Border & Divider Colors
    # ─────────────────────────────────────────────────────────────────────────
    BORDER_DARK = "#1E293B"       # Dark border
    BORDER_DEFAULT = "#334155"    # Default border
    BORDER_LIGHT = "#475569"      # Light border
    BORDER_GLOW = "#00D4E833"     # Glowing border (with alpha)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Gradient Definitions (for reference)
    # ─────────────────────────────────────────────────────────────────────────
    GRADIENT_CYBER = ("#00D4E8", "#8B5CF6")      # Cyan to Purple
    GRADIENT_NIGHT = ("#0A0F18", "#141C2B")      # Dark gradient
    GRADIENT_GLOW = ("#00F0FF", "#00D4E8")       # Glow gradient
    

class Typography:
    """
    Modern Typography System
    Primary: Inter / Segoe UI (clean, modern sans-serif)
    Mono: JetBrains Mono / Cascadia Code (technical feel)
    """
    
    # Font families with fallbacks
    FAMILY_DISPLAY = "Segoe UI"
    FAMILY_BODY = "Segoe UI"
    FAMILY_MONO = "Cascadia Code"
    
    # Display / Hero text
    HERO_XL = (FAMILY_DISPLAY, 48, "bold")
    HERO_LG = (FAMILY_DISPLAY, 40, "bold")
    HERO_MD = (FAMILY_DISPLAY, 32, "bold")
    
    # Headings
    H1 = (FAMILY_DISPLAY, 28, "bold")
    H2 = (FAMILY_DISPLAY, 24, "bold")
    H3 = (FAMILY_DISPLAY, 20, "bold")
    H4 = (FAMILY_DISPLAY, 16, "bold")
    H5 = (FAMILY_DISPLAY, 14, "bold")
    
    # Body text
    BODY_XL = (FAMILY_BODY, 18)
    BODY_LG = (FAMILY_BODY, 16)
    BODY_MD = (FAMILY_BODY, 14)
    BODY_SM = (FAMILY_BODY, 12)
    BODY_XS = (FAMILY_BODY, 11)
    
    # Monospace
    MONO_LG = (FAMILY_MONO, 14)
    MONO_MD = (FAMILY_MONO, 12)
    MONO_SM = (FAMILY_MONO, 11)
    
    # Special
    BUTTON_LG = (FAMILY_BODY, 15, "bold")
    BUTTON_MD = (FAMILY_BODY, 13, "bold")
    BUTTON_SM = (FAMILY_BODY, 11, "bold")
    LABEL = (FAMILY_BODY, 12, "bold")
    CAPTION = (FAMILY_BODY, 10)
    OVERLINE = (FAMILY_BODY, 10, "bold")


class Spacing:
    """Consistent spacing system based on 4px grid"""
    XXS = 4
    XS = 8
    SM = 12
    MD = 16
    LG = 24
    XL = 32
    XXL = 48
    XXXL = 64


class Radius:
    """Border radius tokens"""
    SM = 6
    MD = 10
    LG = 14
    XL = 18
    XXL = 24
    FULL = 9999


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM PREMIUM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class GlowFrame(ctk.CTkFrame):
    """Premium card with glow effect on hover"""
    def __init__(self, master, glow_color=Theme.ACCENT_PRIMARY, **kwargs):
        self.glow_color = glow_color
        super().__init__(
            master,
            fg_color=Theme.BG_DARK,
            corner_radius=Radius.LG,
            border_width=1,
            border_color=Theme.BORDER_DARK,
            **kwargs
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, event):
        self.configure(border_color=self.glow_color + "66")
        
    def _on_leave(self, event):
        self.configure(border_color=Theme.BORDER_DARK)


class GlassCard(ctk.CTkFrame):
    """Glassmorphism-inspired card"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_DARK + "CC",
            corner_radius=Radius.XL,
            border_width=1,
            border_color=Theme.BORDER_DARK,
            **kwargs
        )


class PrimaryButton(ctk.CTkButton):
    """Primary CTA button with glow effect"""
    def __init__(self, master, height=50, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_MEDIUM,
            text_color=Theme.BG_VOID,
            corner_radius=Radius.MD,
            height=height,
            font=Typography.BUTTON_LG,
            **kwargs
        )


class SecondaryButton(ctk.CTkButton):
    """Secondary button with border"""
    def __init__(self, master, height=44, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            border_width=1,
            border_color=Theme.BORDER_DEFAULT,
            corner_radius=Radius.MD,
            height=height,
            font=Typography.BUTTON_MD,
            **kwargs
        )


class GhostButton(ctk.CTkButton):
    """Ghost/text button"""
    def __init__(self, master, height=40, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_SECONDARY,
            corner_radius=Radius.SM,
            height=height,
            font=Typography.BUTTON_SM,
            **kwargs
        )


class SuccessButton(ctk.CTkButton):
    """Success action button"""
    def __init__(self, master, height=50, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_DARK,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Radius.MD,
            height=height,
            font=Typography.BUTTON_LG,
            **kwargs
        )


class DangerButton(ctk.CTkButton):
    """Danger/destructive button"""
    def __init__(self, master, height=44, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.ERROR,
            hover_color=Theme.ERROR_DARK,
            text_color=Theme.TEXT_PRIMARY,
            corner_radius=Radius.MD,
            height=height,
            font=Typography.BUTTON_MD,
            **kwargs
        )


class PremiumEntry(ctk.CTkEntry):
    """Premium styled input with focus animation"""
    def __init__(self, master, placeholder="", is_password=False, height=50, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_LIGHT,
            border_color=Theme.BORDER_DARK,
            border_width=2,
            corner_radius=Radius.MD,
            height=height,
            placeholder_text=placeholder,
            placeholder_text_color=Theme.TEXT_MUTED,
            text_color=Theme.TEXT_PRIMARY,
            font=Typography.BODY_LG,
            show="●" if is_password else "",
            **kwargs
        )
        self.bind("<FocusIn>", self._on_focus)
        self.bind("<FocusOut>", self._on_unfocus)
        
    def _on_focus(self, event):
        self.configure(border_color=Theme.ACCENT_PRIMARY)
        
    def _on_unfocus(self, event):
        self.configure(border_color=Theme.BORDER_DARK)


class PremiumTextbox(ctk.CTkTextbox):
    """Premium styled multiline text area"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_ABYSS,
            border_color=Theme.BORDER_DARK,
            border_width=1,
            corner_radius=Radius.MD,
            text_color=Theme.SUCCESS_BRIGHT,
            font=Typography.MONO_MD,
            scrollbar_button_color=Theme.BG_MEDIUM,
            scrollbar_button_hover_color=Theme.BG_HOVER,
            **kwargs
        )


class AnimatedProgress(ctk.CTkProgressBar):
    """Animated progress bar with glow"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_MEDIUM,
            progress_color=Theme.ACCENT_PRIMARY,
            corner_radius=Radius.SM,
            height=4,
            **kwargs
        )
        
    def start_animation(self):
        self.configure(mode="indeterminate")
        self.start()
        
    def stop_animation(self):
        self.stop()
        self.configure(mode="determinate")
        self.set(0)


# ═══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE - Cinematic Premium Introduction
# ═══════════════════════════════════════════════════════════════════════════════

class LandingPage(ctk.CTkScrollableFrame):
    """
    Premium Landing Page for Fractured Key with:
    - Animated hero section
    - Feature highlights with icons
    - How it works section
    - Security stats
    - Call-to-action buttons
    - Smooth animations
    """
    
    def __init__(self, master, on_start_callback: Callable):
        super().__init__(
            master, 
            fg_color=Theme.BG_ABYSS,
            scrollbar_button_color=Theme.BG_MEDIUM,
            scrollbar_button_hover_color=Theme.BG_HOVER
        )
        self.on_start = on_start_callback
        self.animation_running = True
        self.animation_step = 0
        
        self._create_layout()
        self._start_animations()
        
    def _create_layout(self):
        """Create the landing page layout"""
        
        # ═══════════════════════════════════════════════════════════════════════
        # HERO SECTION
        # ═══════════════════════════════════════════════════════════════════════
        hero_section = ctk.CTkFrame(self, fg_color="transparent")
        hero_section.pack(fill="x", pady=(50, 40))
        
        # Centered hero content
        hero_content = ctk.CTkFrame(hero_section, fg_color="transparent")
        hero_content.pack(expand=True)
        
        # Animated Logo with glow ring effect
        logo_container = ctk.CTkFrame(hero_content, fg_color="transparent")
        logo_container.pack(pady=(0, 24))
        
        # Outer glow ring
        self.glow_ring = ctk.CTkFrame(
            logo_container,
            fg_color=Theme.BG_DARK,
            corner_radius=80,
            width=160,
            height=160,
            border_width=2,
            border_color=Theme.ACCENT_DARK
        )
        self.glow_ring.pack()
        self.glow_ring.pack_propagate(False)
        
        # Inner icon
        self.key_icon = ctk.CTkLabel(
            self.glow_ring,
            text="🔐",
            font=("Segoe UI Emoji", 64),
            text_color=Theme.ACCENT_PRIMARY
        )
        self.key_icon.place(relx=0.5, rely=0.5, anchor="center")
        
        # Main Title
        title_container = ctk.CTkFrame(hero_content, fg_color="transparent")
        title_container.pack(pady=(0, 12))
        
        self.title_label = ctk.CTkLabel(
            title_container,
            text="FRACTURED KEY",
            font=Typography.HERO_XL,
            text_color=Theme.TEXT_PRIMARY
        )
        self.title_label.pack()
        
        # Subtitle badge
        subtitle_badge = ctk.CTkFrame(
            hero_content,
            fg_color=Theme.BG_MEDIUM,
            corner_radius=20,
            border_width=1,
            border_color=Theme.ACCENT_DARK
        )
        subtitle_badge.pack(pady=(0, 24))
        
        ctk.CTkLabel(
            subtitle_badge,
            text="✦  STEGANOGRAPHIC PASSWORD VAULT  ✦",
            font=Typography.OVERLINE,
            text_color=Theme.ACCENT_PRIMARY
        ).pack(padx=20, pady=8)
        
        # Tagline with typewriter effect
        self.tagline = ctk.CTkLabel(
            hero_content,
            text="Your Secrets. Fragmented. Hidden. Secure.",
            font=Typography.H3,
            text_color=Theme.TEXT_SECONDARY
        )
        self.tagline.pack(pady=(0, 20))
        
        # Description
        description = ctk.CTkLabel(
            hero_content,
            text="A next-generation offline password manager that encrypts your credentials,\nsplits them into fragments, and hides them inside ordinary-looking images.\nNo cloud. No servers. Just pure cryptographic security.",
            font=Typography.BODY_LG,
            text_color=Theme.TEXT_TERTIARY,
            justify="center"
        )
        description.pack(pady=(0, 40))
        
        # CTA Buttons
        cta_frame = ctk.CTkFrame(hero_content, fg_color="transparent")
        cta_frame.pack(pady=(0, 20))
        
        self.cta_button = PrimaryButton(
            cta_frame,
            text="🚀  Launch the Vault",
            command=self._on_enter_click,
            width=220,
            height=56
        )
        self.cta_button.pack(side="left", padx=(0, 16))
        
        SecondaryButton(
            cta_frame,
            text="📖  Learn More",
            command=lambda: self._scroll_to_features(),
            width=160,
            height=56
        ).pack(side="left")
        
        # Scroll indicator
        scroll_indicator = ctk.CTkFrame(hero_content, fg_color="transparent")
        scroll_indicator.pack(pady=(30, 0))
        
        self.scroll_arrow = ctk.CTkLabel(
            scroll_indicator,
            text="▼",
            font=Typography.BODY_LG,
            text_color=Theme.TEXT_MUTED
        )
        self.scroll_arrow.pack()
        
        ctk.CTkLabel(
            scroll_indicator,
            text="Scroll to explore",
            font=Typography.CAPTION,
            text_color=Theme.TEXT_DISABLED
        ).pack()
        
        # ═══════════════════════════════════════════════════════════════════════
        # SECURITY STATS BAR
        # ═══════════════════════════════════════════════════════════════════════
        stats_section = ctk.CTkFrame(self, fg_color=Theme.BG_VOID, corner_radius=0)
        stats_section.pack(fill="x", pady=(20, 40))
        
        stats_container = ctk.CTkFrame(stats_section, fg_color="transparent")
        stats_container.pack(pady=30)
        
        stats = [
            ("256", "Bit Encryption"),
            ("3", "Image Shares"),
            ("2", "Required to Decrypt"),
            ("100%", "Offline Security"),
        ]
        
        for i, (value, label) in enumerate(stats):
            stat_item = ctk.CTkFrame(stats_container, fg_color="transparent")
            stat_item.pack(side="left", padx=50)
            
            ctk.CTkLabel(
                stat_item,
                text=value,
                font=Typography.HERO_MD,
                text_color=Theme.ACCENT_PRIMARY
            ).pack()
            
            ctk.CTkLabel(
                stat_item,
                text=label,
                font=Typography.BODY_SM,
                text_color=Theme.TEXT_MUTED
            ).pack()
            
            # Divider (except last)
            if i < len(stats) - 1:
                divider = ctk.CTkFrame(
                    stats_container,
                    fg_color=Theme.BORDER_DARK,
                    width=1,
                    height=50
                )
                divider.pack(side="left", padx=20)
        
        # ═══════════════════════════════════════════════════════════════════════
        # HOW IT WORKS SECTION
        # ═══════════════════════════════════════════════════════════════════════
        self.how_section = ctk.CTkFrame(self, fg_color="transparent")
        self.how_section.pack(fill="x", padx=60, pady=(0, 50))
        
        # Section header
        how_header = ctk.CTkFrame(self.how_section, fg_color="transparent")
        how_header.pack(pady=(0, 40))
        
        ctk.CTkLabel(
            how_header,
            text="HOW IT WORKS",
            font=Typography.OVERLINE,
            text_color=Theme.ACCENT_PRIMARY
        ).pack()
        
        ctk.CTkLabel(
            how_header,
            text="Four Steps to Unbreakable Security",
            font=Typography.H2,
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(8, 0))
        
        # Steps flow
        steps_frame = ctk.CTkFrame(self.how_section, fg_color="transparent")
        steps_frame.pack(fill="x")
        
        steps = [
            ("1", "🔑", "ENCRYPT", "Enter your password and master key.\nAES-256-GCM encrypts your data\nwith Argon2id key derivation."),
            ("2", "🧩", "FRAGMENT", "Your encrypted data is split into\n3 shares using Shamir's Secret\nSharing algorithm."),
            ("3", "🖼️", "HIDE", "Each fragment is invisibly embedded\ninto ordinary images using LSB\nsteganography."),
            ("4", "🔓", "RECOVER", "Use any 2 of your 3 images\nplus your master password to\nreconstruct your secret."),
        ]
        
        for i, (num, icon, title, desc) in enumerate(steps):
            step_card = GlowFrame(
                steps_frame, 
                glow_color=Theme.ACCENT_PRIMARY if i % 2 == 0 else Theme.PURPLE_PRIMARY
            )
            step_card.grid(row=0, column=i, padx=8, pady=10, sticky="nsew")
            steps_frame.grid_columnconfigure(i, weight=1)
            
            card_content = ctk.CTkFrame(step_card, fg_color="transparent")
            card_content.pack(expand=True, fill="both", padx=20, pady=24)
            
            # Step number badge
            num_badge = ctk.CTkLabel(
                card_content,
                text=num,
                font=Typography.BUTTON_SM,
                text_color=Theme.BG_VOID,
                fg_color=Theme.ACCENT_PRIMARY if i % 2 == 0 else Theme.PURPLE_PRIMARY,
                corner_radius=15,
                width=30,
                height=30
            )
            num_badge.pack(pady=(0, 12))
            
            # Icon
            ctk.CTkLabel(
                card_content,
                text=icon,
                font=("Segoe UI Emoji", 32),
                text_color=Theme.ACCENT_PRIMARY if i % 2 == 0 else Theme.PURPLE_PRIMARY
            ).pack(pady=(0, 12))
            
            # Title
            ctk.CTkLabel(
                card_content,
                text=title,
                font=Typography.H5,
                text_color=Theme.TEXT_PRIMARY
            ).pack(pady=(0, 8))
            
            # Description
            ctk.CTkLabel(
                card_content,
                text=desc,
                font=Typography.BODY_XS,
                text_color=Theme.TEXT_MUTED,
                justify="center"
            ).pack()
            
            # Note: Arrows removed for cleaner look - the numbered badges show flow
        
        # ═══════════════════════════════════════════════════════════════════════
        # FEATURES SECTION
        # ═══════════════════════════════════════════════════════════════════════
        features_section = ctk.CTkFrame(self, fg_color="transparent")
        features_section.pack(fill="x", padx=60, pady=(0, 50))
        
        # Section header
        features_header = ctk.CTkFrame(features_section, fg_color="transparent")
        features_header.pack(pady=(0, 40))
        
        ctk.CTkLabel(
            features_header,
            text="SECURITY FEATURES",
            font=Typography.OVERLINE,
            text_color=Theme.ACCENT_PRIMARY
        ).pack()
        
        ctk.CTkLabel(
            features_header,
            text="Built for Maximum Protection",
            font=Typography.H2,
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(8, 0))
        
        # Features grid (2 rows x 3 columns)
        features_grid = ctk.CTkFrame(features_section, fg_color="transparent")
        features_grid.pack(fill="x")
        
        features = [
            ("🔒", "AES-256-GCM", "Military-grade authenticated encryption that's impossible to crack without the key."),
            ("🔑", "Argon2id KDF", "Memory-hard key derivation that resists GPU and ASIC brute-force attacks."),
            ("🧩", "Shamir SSS", "Mathematically proven secret sharing - fragments reveal nothing individually."),
            ("🖼️", "LSB Steganography", "Data hidden in image pixels - your secrets look like ordinary photos."),
            ("🌐", "100% Offline", "No cloud, no servers, no internet required. Your secrets never leave your device."),
            ("🔄", "Redundancy", "Lose one image? No problem. Any 2 of 3 shares can recover your password."),
        ]
        
        for i, (icon, title, desc) in enumerate(features):
            row = i // 3
            col = i % 3
            
            feature_card = GlowFrame(features_grid, glow_color=Theme.ACCENT_PRIMARY)
            feature_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            features_grid.grid_columnconfigure(col, weight=1)
            
            card_content = ctk.CTkFrame(feature_card, fg_color="transparent")
            card_content.pack(expand=True, fill="both", padx=24, pady=24)
            
            # Icon
            ctk.CTkLabel(
                card_content,
                text=icon,
                font=("Segoe UI Emoji", 36),
                text_color=Theme.ACCENT_PRIMARY
            ).pack(anchor="w", pady=(0, 12))
            
            # Title
            ctk.CTkLabel(
                card_content,
                text=title,
                font=Typography.H4,
                text_color=Theme.TEXT_PRIMARY
            ).pack(anchor="w", pady=(0, 8))
            
            # Description
            ctk.CTkLabel(
                card_content,
                text=desc,
                font=Typography.BODY_SM,
                text_color=Theme.TEXT_MUTED,
                wraplength=250,
                justify="left"
            ).pack(anchor="w")
        
        # ═══════════════════════════════════════════════════════════════════════
        # USE CASES SECTION
        # ═══════════════════════════════════════════════════════════════════════
        usecases_section = ctk.CTkFrame(self, fg_color=Theme.BG_DEEP, corner_radius=Radius.XL)
        usecases_section.pack(fill="x", padx=60, pady=(0, 50))
        
        usecases_inner = ctk.CTkFrame(usecases_section, fg_color="transparent")
        usecases_inner.pack(fill="x", padx=40, pady=40)
        
        # Header
        ctk.CTkLabel(
            usecases_inner,
            text="PERFECT FOR",
            font=Typography.OVERLINE,
            text_color=Theme.PURPLE_PRIMARY
        ).pack()
        
        ctk.CTkLabel(
            usecases_inner,
            text="Who Should Use Fractured Key?",
            font=Typography.H2,
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(8, 30))
        
        # Use cases grid
        usecases_grid = ctk.CTkFrame(usecases_inner, fg_color="transparent")
        usecases_grid.pack(fill="x")
        
        usecases = [
            ("👨‍💻", "Privacy Enthusiasts", "Keep your passwords away from cloud services and prying eyes."),
            ("🏢", "Security Professionals", "Store sensitive credentials with defense-in-depth approach."),
            ("📱", "Digital Nomads", "Distribute key shares across devices for travel security."),
            ("🏠", "Families", "Share password recovery among trusted family members."),
        ]
        
        for i, (icon, title, desc) in enumerate(usecases):
            usecase_item = ctk.CTkFrame(usecases_grid, fg_color="transparent")
            usecase_item.grid(row=0, column=i, padx=20, sticky="nsew")
            usecases_grid.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                usecase_item,
                text=icon,
                font=("Segoe UI Emoji", 40),
                text_color=Theme.PURPLE_PRIMARY
            ).pack(pady=(0, 12))
            
            ctk.CTkLabel(
                usecase_item,
                text=title,
                font=Typography.H5,
                text_color=Theme.TEXT_PRIMARY
            ).pack(pady=(0, 8))
            
            ctk.CTkLabel(
                usecase_item,
                text=desc,
                font=Typography.BODY_SM,
                text_color=Theme.TEXT_MUTED,
                wraplength=200,
                justify="center"
            ).pack()
        
        # ═══════════════════════════════════════════════════════════════════════
        # FINAL CTA SECTION
        # ═══════════════════════════════════════════════════════════════════════
        final_cta = ctk.CTkFrame(self, fg_color="transparent")
        final_cta.pack(fill="x", pady=(0, 40))
        
        cta_container = ctk.CTkFrame(final_cta, fg_color="transparent")
        cta_container.pack()
        
        ctk.CTkLabel(
            cta_container,
            text="Ready to Secure Your Secrets?",
            font=Typography.H2,
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(0, 12))
        
        ctk.CTkLabel(
            cta_container,
            text="Start using Fractured Key now — it's free and works entirely offline.",
            font=Typography.BODY_LG,
            text_color=Theme.TEXT_TERTIARY
        ).pack(pady=(0, 30))
        
        PrimaryButton(
            cta_container,
            text="🔐  Enter the Vault Now",
            command=self._on_enter_click,
            width=260,
            height=60
        ).pack()
        
        # ═══════════════════════════════════════════════════════════════════════
        # FOOTER
        # ═══════════════════════════════════════════════════════════════════════
        footer = ctk.CTkFrame(self, fg_color=Theme.BG_VOID, corner_radius=0)
        footer.pack(fill="x", pady=(40, 0))
        
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(pady=24)
        
        # Footer logo
        ctk.CTkLabel(
            footer_content,
            text="🔐 FRACTURED KEY",
            font=Typography.H5,
            text_color=Theme.TEXT_PRIMARY
        ).pack(pady=(0, 8))
        
        # Footer links/info
        footer_info = ctk.CTkFrame(footer_content, fg_color="transparent")
        footer_info.pack()
        
        info_items = ["AES-256-GCM", "Argon2id", "Shamir SSS", "LSB Steganography"]
        
        for i, item in enumerate(info_items):
            ctk.CTkLabel(
                footer_info,
                text=item,
                font=Typography.BODY_XS,
                text_color=Theme.TEXT_MUTED
            ).pack(side="left", padx=10)
            
            if i < len(info_items) - 1:
                ctk.CTkLabel(
                    footer_info,
                    text="•",
                    font=Typography.BODY_XS,
                    text_color=Theme.TEXT_DISABLED
                ).pack(side="left")
        
        # Copyright
        ctk.CTkLabel(
            footer_content,
            text="v2.5 Premium Edition  •  2024-2025  •  100% Open Source",
            font=Typography.CAPTION,
            text_color=Theme.TEXT_DISABLED
        ).pack(pady=(16, 0))
        
    def _scroll_to_features(self):
        """Scroll to features section"""
        # Scroll down smoothly
        self._parent_canvas.yview_moveto(0.3)
        
    def _start_animations(self):
        """Start all animations"""
        self._animate_glow()
        self._animate_scroll_arrow()
        
    def _animate_glow(self):
        """Animate the glow ring around the logo"""
        if not self.animation_running:
            return
            
        try:
            if not self.winfo_exists():
                return
                
            # Cycle through glow colors
            colors = [Theme.ACCENT_DARK, Theme.ACCENT_MUTED, Theme.ACCENT_PRIMARY, Theme.ACCENT_MUTED]
            color = colors[self.animation_step % len(colors)]
            
            self.glow_ring.configure(border_color=color)
            self.key_icon.configure(text_color=color if self.animation_step % 2 == 0 else Theme.ACCENT_PRIMARY)
            
            self.animation_step += 1
            self.after(600, self._animate_glow)
        except:
            pass
            
    def _animate_scroll_arrow(self):
        """Animate the scroll indicator"""
        if not self.animation_running:
            return
            
        try:
            if not self.winfo_exists():
                return
                
            # Pulse opacity effect (simulated with color)
            colors = [Theme.TEXT_MUTED, Theme.TEXT_TERTIARY, Theme.TEXT_MUTED, Theme.TEXT_DISABLED]
            color = colors[self.animation_step % len(colors)]
            
            self.scroll_arrow.configure(text_color=color)
            self.after(500, self._animate_scroll_arrow)
        except:
            pass
        
    def _on_enter_click(self):
        """Handle CTA click with transition"""
        self.animation_running = False
        self.on_start()
        
    def destroy(self):
        self.animation_running = False
        super().destroy()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class FracturedKeyApp(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Window setup
        self.title("Fractured Key")
        self.geometry("1280x850")
        self.minsize(1100, 750)
        self.configure(fg_color=Theme.BG_ABYSS)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1280 // 2)
        y = (self.winfo_screenheight() // 2) - (850 // 2)
        self.geometry(f"1280x850+{x}+{y}")
        
        # State
        self.selected_images = []
        self.current_tab = "encrypt"
        self.showing_landing = True
        
        # Show landing page first
        self._show_landing_page()
        
    def _show_landing_page(self):
        """Show the landing/intro page"""
        self.landing_page = LandingPage(self, self._transition_to_main)
        self.landing_page.pack(fill="both", expand=True)
        
    def _transition_to_main(self):
        """Transition from landing to main app"""
        # Fade out landing page
        self.landing_page.destroy()
        self.showing_landing = False
        
        # Create main app interface
        self._create_main_interface()
        
    def _create_main_interface(self):
        """Create the main application interface"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Configure grid
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_sidebar()
        self._create_content_area()
        self._create_status_bar()
        
        # Show default tab
        self._show_tab("encrypt")
        
    def _create_header(self):
        """Create premium header"""
        header = ctk.CTkFrame(
            self.main_container,
            fg_color=Theme.BG_VOID,
            height=70,
            corner_radius=0
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        
        # Left side - Logo
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.pack(side="left", padx=24, pady=12)
        
        ctk.CTkLabel(
            logo_frame,
            text="🔐",
            font=("Segoe UI Emoji", 28),
            text_color=Theme.ACCENT_PRIMARY
        ).pack(side="left", padx=(0, 12))
        
        title_container = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_container.pack(side="left")
        
        ctk.CTkLabel(
            title_container,
            text="FRACTURED KEY",
            font=Typography.H4,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_container,
            text="Premium Password Vault",
            font=Typography.CAPTION,
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w")
        
        # Right side - Version badge
        badge_frame = ctk.CTkFrame(
            header,
            fg_color=Theme.BG_MEDIUM,
            corner_radius=Radius.SM
        )
        badge_frame.pack(side="right", padx=24, pady=20)
        
        ctk.CTkLabel(
            badge_frame,
            text="v2.5",
            font=Typography.CAPTION,
            text_color=Theme.ACCENT_PRIMARY
        ).pack(padx=12, pady=4)
        
    def _create_sidebar(self):
        """Create premium sidebar navigation"""
        sidebar = ctk.CTkFrame(
            self.main_container,
            fg_color=Theme.BG_VOID,
            width=260,
            corner_radius=0
        )
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Navigation container
        nav_container = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_container.pack(fill="x", pady=24, padx=16)
        
        # Section label
        ctk.CTkLabel(
            nav_container,
            text="NAVIGATION",
            font=Typography.OVERLINE,
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(0, 16))
        
        # Nav items
        nav_items = [
            ("encrypt", "🔒", "Encrypt", "Protect your secrets"),
            ("decrypt", "🔓", "Decrypt", "Recover your data"),
            ("manual", "📁", "Manual", "Direct file mode"),
            ("about", "✨", "About", "Learn more"),
        ]
        
        self.nav_buttons = {}
        
        for tab_id, icon, title, subtitle in nav_items:
            nav_btn = ctk.CTkFrame(
                nav_container,
                fg_color="transparent",
                corner_radius=Radius.MD,
                cursor="hand2"
            )
            nav_btn.pack(fill="x", pady=2)
            
            # Bind click
            nav_btn.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            # Content
            content = ctk.CTkFrame(nav_btn, fg_color="transparent")
            content.pack(fill="x", padx=12, pady=12)
            content.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            # Icon
            icon_lbl = ctk.CTkLabel(
                content,
                text=icon,
                font=("Segoe UI Emoji", 20),
                text_color=Theme.TEXT_MUTED
            )
            icon_lbl.pack(side="left", padx=(0, 12))
            icon_lbl.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            # Text
            text_frame = ctk.CTkFrame(content, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            text_frame.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            title_lbl = ctk.CTkLabel(
                text_frame,
                text=title,
                font=Typography.H5,
                text_color=Theme.TEXT_PRIMARY,
                anchor="w"
            )
            title_lbl.pack(anchor="w")
            title_lbl.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            subtitle_lbl = ctk.CTkLabel(
                text_frame,
                text=subtitle,
                font=Typography.CAPTION,
                text_color=Theme.TEXT_MUTED,
                anchor="w"
            )
            subtitle_lbl.pack(anchor="w")
            subtitle_lbl.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            self.nav_buttons[tab_id] = {
                "frame": nav_btn,
                "icon": icon_lbl,
                "title": title_lbl
            }
            
            # Hover effects
            def on_enter(e, f=nav_btn, t=tab_id):
                if self.current_tab != t:
                    f.configure(fg_color=Theme.BG_HOVER)
            def on_leave(e, f=nav_btn, t=tab_id):
                if self.current_tab != t:
                    f.configure(fg_color="transparent")
                    
            nav_btn.bind("<Enter>", on_enter)
            nav_btn.bind("<Leave>", on_leave)
        
        # Divider
        divider = ctk.CTkFrame(sidebar, fg_color=Theme.BORDER_DARK, height=1)
        divider.pack(fill="x", padx=24, pady=24)
        
        # Security info
        security_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        security_frame.pack(fill="x", padx=24)
        
        ctk.CTkLabel(
            security_frame,
            text="SECURITY STACK",
            font=Typography.OVERLINE,
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", pady=(0, 12))
        
        security_items = [
            ("🔐", "AES-256-GCM"),
            ("🔑", "Argon2id KDF"),
            ("🧩", "Shamir SSS"),
            ("🖼️", "LSB Stego"),
        ]
        
        for icon, text in security_items:
            item = ctk.CTkFrame(security_frame, fg_color="transparent")
            item.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                item,
                text=icon,
                font=("Segoe UI Emoji", 12),
                text_color=Theme.ACCENT_MUTED
            ).pack(side="left", padx=(0, 8))
            
            ctk.CTkLabel(
                item,
                text=text,
                font=Typography.BODY_XS,
                text_color=Theme.TEXT_TERTIARY
            ).pack(side="left")
            
    def _create_content_area(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=Theme.BG_DEEP,
            corner_radius=0
        )
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        
        # Create all tabs
        self.tabs = {}
        self.tabs["encrypt"] = self._create_encrypt_tab()
        self.tabs["decrypt"] = self._create_decrypt_tab()
        self.tabs["manual"] = self._create_manual_tab()
        self.tabs["about"] = self._create_about_tab()
        
    def _create_encrypt_tab(self):
        """Create encryption tab"""
        tab = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=Theme.BG_MEDIUM,
            scrollbar_button_hover_color=Theme.BG_HOVER
        )
        
        # Page header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(32, 24))
        
        ctk.CTkLabel(
            header,
            text="Encrypt Password",
            font=Typography.H1,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header,
            text="Protect your password with military-grade encryption and steganography",
            font=Typography.BODY_MD,
            text_color=Theme.TEXT_TERTIARY
        ).pack(anchor="w", pady=(8, 0))
        
        # Content
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(0, 32))
        
        # Password Card
        password_card = GlowFrame(content)
        password_card.pack(fill="x", pady=(0, 20))
        
        card_inner = ctk.CTkFrame(password_card, fg_color="transparent")
        card_inner.pack(fill="x", padx=28, pady=28)
        
        # Password input
        ctk.CTkLabel(
            card_inner,
            text="🔑  Password to Encrypt",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        self.encrypt_password_entry = PremiumEntry(
            card_inner,
            placeholder="Enter the password you want to protect...",
            is_password=True
        )
        self.encrypt_password_entry.pack(fill="x", pady=(0, 20))
        
        # Master password
        ctk.CTkLabel(
            card_inner,
            text="🔐  Master Password",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        self.encrypt_master_entry = PremiumEntry(
            card_inner,
            placeholder="Enter your master password...",
            is_password=True
        )
        self.encrypt_master_entry.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            card_inner,
            text="This will be required to decrypt your data later",
            font=Typography.CAPTION,
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w")
        
        # Options Card
        options_card = GlowFrame(content)
        options_card.pack(fill="x", pady=(0, 20))
        
        options_inner = ctk.CTkFrame(options_card, fg_color="transparent")
        options_inner.pack(fill="x", padx=28, pady=28)
        
        ctk.CTkLabel(
            options_inner,
            text="⚙️  Encryption Options",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 16))
        
        self.use_shares_var = ctk.BooleanVar(value=True)
        
        checkbox = ctk.CTkCheckBox(
            options_inner,
            text="Split into 3 shares and embed into images",
            variable=self.use_shares_var,
            font=Typography.BODY_MD,
            text_color=Theme.TEXT_PRIMARY,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_MEDIUM,
            border_color=Theme.BORDER_DEFAULT,
            checkmark_color=Theme.BG_VOID
        )
        checkbox.pack(anchor="w", pady=(0, 8))
        
        ctk.CTkLabel(
            options_inner,
            text="💡 Creates 3 stego images. You need at least 2 to decrypt.",
            font=Typography.BODY_SM,
            text_color=Theme.TEXT_MUTED
        ).pack(anchor="w", padx=(26, 0))
        
        # Action button
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 20))
        
        self.encrypt_btn = PrimaryButton(
            button_frame,
            text="🔒  Start Encryption",
            command=self._start_encryption,
            width=220
        )
        self.encrypt_btn.pack(anchor="w")
        
        # Progress
        self.encrypt_progress = AnimatedProgress(content)
        self.encrypt_progress.pack(fill="x", pady=(0, 20))
        
        # Output Card
        output_card = GlowFrame(content)
        output_card.pack(fill="both", expand=True)
        
        output_header = ctk.CTkFrame(output_card, fg_color="transparent")
        output_header.pack(fill="x", padx=28, pady=(28, 12))
        
        ctk.CTkLabel(
            output_header,
            text="📋  Output Log",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")
        
        GhostButton(
            output_header,
            text="Clear",
            command=lambda: self.encrypt_output.delete("1.0", "end"),
            width=70,
            height=32
        ).pack(side="right")
        
        self.encrypt_output = PremiumTextbox(output_card, height=180)
        self.encrypt_output.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        
        # Initial message
        self.encrypt_output.insert("1.0", "▸ Ready to encrypt your password.\n")
        self.encrypt_output.insert("end", "━" * 50 + "\n")
        
        return tab
        
    def _create_decrypt_tab(self):
        """Create decryption tab"""
        tab = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=Theme.BG_MEDIUM,
            scrollbar_button_hover_color=Theme.BG_HOVER
        )
        
        # Page header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(32, 24))
        
        ctk.CTkLabel(
            header,
            text="Decrypt Password",
            font=Typography.H1,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header,
            text="Recover your password from steganographic images",
            font=Typography.BODY_MD,
            text_color=Theme.TEXT_TERTIARY
        ).pack(anchor="w", pady=(8, 0))
        
        # Content
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(0, 32))
        
        # Instructions Card
        instructions_card = GlowFrame(content)
        instructions_card.pack(fill="x", pady=(0, 20))
        
        instructions_inner = ctk.CTkFrame(instructions_card, fg_color="transparent")
        instructions_inner.pack(fill="x", padx=28, pady=28)
        
        ctk.CTkLabel(
            instructions_inner,
            text="📖  How to Decrypt",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 16))
        
        steps = [
            ("1", "Select at least 2 stego images from the same session"),
            ("2", "Enter your master password"),
            ("3", "Click 'Start Decryption' to recover your password")
        ]
        
        for num, text in steps:
            step_frame = ctk.CTkFrame(instructions_inner, fg_color="transparent")
            step_frame.pack(fill="x", pady=6)
            
            ctk.CTkLabel(
                step_frame,
                text=num,
                font=Typography.BUTTON_SM,
                text_color=Theme.BG_VOID,
                fg_color=Theme.ACCENT_PRIMARY,
                corner_radius=12,
                width=24,
                height=24
            ).pack(side="left", padx=(0, 12))
            
            ctk.CTkLabel(
                step_frame,
                text=text,
                font=Typography.BODY_MD,
                text_color=Theme.TEXT_SECONDARY
            ).pack(side="left")
        
        # Image Selection Card
        image_card = GlowFrame(content)
        image_card.pack(fill="x", pady=(0, 20))
        
        image_inner = ctk.CTkFrame(image_card, fg_color="transparent")
        image_inner.pack(fill="x", padx=28, pady=28)
        
        ctk.CTkLabel(
            image_inner,
            text="🖼️  Selected Images",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))
        
        # Image list
        list_frame = ctk.CTkFrame(
            image_inner,
            fg_color=Theme.BG_ABYSS,
            corner_radius=Radius.MD,
            border_width=1,
            border_color=Theme.BORDER_DARK
        )
        list_frame.pack(fill="x", pady=(0, 12))
        
        self.image_listbox = ctk.CTkTextbox(
            list_frame,
            height=100,
            fg_color=Theme.BG_ABYSS,
            text_color=Theme.TEXT_SECONDARY,
            font=Typography.MONO_MD,
            state="disabled"
        )
        self.image_listbox.pack(fill="x", padx=4, pady=4)
        
        # Image buttons
        btn_frame = ctk.CTkFrame(image_inner, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        SuccessButton(
            btn_frame,
            text="📁 Add Image",
            command=self._add_image_file,
            width=140,
            height=44
        ).pack(side="left", padx=(0, 12))
        
        DangerButton(
            btn_frame,
            text="🗑️ Clear All",
            command=self._remove_all_images,
            width=130
        ).pack(side="left")
        
        # Master Password Card
        password_card = GlowFrame(content)
        password_card.pack(fill="x", pady=(0, 20))
        
        password_inner = ctk.CTkFrame(password_card, fg_color="transparent")
        password_inner.pack(fill="x", padx=28, pady=28)
        
        ctk.CTkLabel(
            password_inner,
            text="🔐  Master Password",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        self.decrypt_master_entry = PremiumEntry(
            password_inner,
            placeholder="Enter your master password...",
            is_password=True
        )
        self.decrypt_master_entry.pack(fill="x")
        
        # Action button
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 20))
        
        self.decrypt_btn = SuccessButton(
            button_frame,
            text="🔓  Start Decryption",
            command=self._start_decryption,
            width=220
        )
        self.decrypt_btn.pack(anchor="w")
        
        # Progress
        self.decrypt_progress = AnimatedProgress(content)
        self.decrypt_progress.pack(fill="x", pady=(0, 20))
        
        # Output Card
        output_card = GlowFrame(content)
        output_card.pack(fill="both", expand=True)
        
        output_header = ctk.CTkFrame(output_card, fg_color="transparent")
        output_header.pack(fill="x", padx=28, pady=(28, 12))
        
        ctk.CTkLabel(
            output_header,
            text="📋  Decryption Results",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")
        
        GhostButton(
            output_header,
            text="Clear",
            command=lambda: self.decrypt_output.delete("1.0", "end"),
            width=70,
            height=32
        ).pack(side="right")
        
        self.decrypt_output = PremiumTextbox(output_card, height=180)
        self.decrypt_output.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        
        self.decrypt_output.insert("1.0", "▸ Ready to decrypt your password.\n")
        self.decrypt_output.insert("end", "━" * 50 + "\n")
        
        return tab
        
    def _create_manual_tab(self):
        """Create manual decryption tab"""
        tab = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=Theme.BG_MEDIUM,
            scrollbar_button_hover_color=Theme.BG_HOVER
        )
        
        # Page header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(32, 24))
        
        ctk.CTkLabel(
            header,
            text="Manual Decryption",
            font=Typography.H1,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header,
            text="Decrypt .bin files directly without steganography",
            font=Typography.BODY_MD,
            text_color=Theme.TEXT_TERTIARY
        ).pack(anchor="w", pady=(8, 0))
        
        # Content
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(0, 32))
        
        # File Selection Card
        file_card = GlowFrame(content)
        file_card.pack(fill="x", pady=(0, 20))
        
        file_inner = ctk.CTkFrame(file_card, fg_color="transparent")
        file_inner.pack(fill="x", padx=28, pady=28)
        
        ctk.CTkLabel(
            file_inner,
            text="📁  Select Binary File",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))
        
        file_input_frame = ctk.CTkFrame(file_inner, fg_color="transparent")
        file_input_frame.pack(fill="x")
        
        self.manual_file_entry = PremiumEntry(
            file_input_frame,
            placeholder="Select a .bin file..."
        )
        self.manual_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        SecondaryButton(
            file_input_frame,
            text="📂 Browse",
            command=self._browse_manual_file,
            width=100,
            height=50
        ).pack(side="right")
        
        # Password Card
        password_card = GlowFrame(content)
        password_card.pack(fill="x", pady=(0, 20))
        
        password_inner = ctk.CTkFrame(password_card, fg_color="transparent")
        password_inner.pack(fill="x", padx=28, pady=28)
        
        ctk.CTkLabel(
            password_inner,
            text="🔐  Master Password",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        self.manual_master_entry = PremiumEntry(
            password_inner,
            placeholder="Enter your master password...",
            is_password=True
        )
        self.manual_master_entry.pack(fill="x")
        
        # Action button
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 20))
        
        self.manual_decrypt_btn = SuccessButton(
            button_frame,
            text="🔓  Decrypt File",
            command=self._start_manual_decryption,
            width=180
        )
        self.manual_decrypt_btn.pack(anchor="w")
        
        # Output Card
        output_card = GlowFrame(content)
        output_card.pack(fill="both", expand=True)
        
        output_header = ctk.CTkFrame(output_card, fg_color="transparent")
        output_header.pack(fill="x", padx=28, pady=(28, 12))
        
        ctk.CTkLabel(
            output_header,
            text="📋  Results",
            font=Typography.LABEL,
            text_color=Theme.TEXT_PRIMARY
        ).pack(side="left")
        
        GhostButton(
            output_header,
            text="Clear",
            command=lambda: self.manual_output.delete("1.0", "end"),
            width=70,
            height=32
        ).pack(side="right")
        
        self.manual_output = PremiumTextbox(output_card, height=220)
        self.manual_output.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        
        self.manual_output.insert("1.0", "▸ Manual decryption mode ready.\n")
        self.manual_output.insert("end", "━" * 50 + "\n")
        
        return tab
        
    def _create_about_tab(self):
        """Create about tab"""
        tab = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=Theme.BG_MEDIUM,
            scrollbar_button_hover_color=Theme.BG_HOVER
        )
        
        # Page header
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(32, 24))
        
        ctk.CTkLabel(
            header,
            text="About Fractured Key",
            font=Typography.H1,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Content
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(0, 32))
        
        # Overview Card
        overview_card = GlowFrame(content)
        overview_card.pack(fill="x", pady=(0, 20))
        
        overview_inner = ctk.CTkFrame(overview_card, fg_color="transparent")
        overview_inner.pack(fill="x", padx=28, pady=28)
        
        ctk.CTkLabel(
            overview_inner,
            text="🔐  What is Fractured Key?",
            font=Typography.H3,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 16))
        
        overview_text = """Fractured Key is a next-generation password vault that takes a fundamentally different approach to security. Instead of storing your encrypted credentials in a single location, it fragments, encrypts, and hides them across multiple ordinary-looking images.

The result? Your secrets become invisible — distributed among innocent-looking photos that reveal nothing about their hidden cargo."""
        
        ctk.CTkLabel(
            overview_inner,
            text=overview_text,
            font=Typography.BODY_MD,
            text_color=Theme.TEXT_SECONDARY,
            wraplength=700,
            justify="left"
        ).pack(anchor="w")
        
        # How it Works Card
        how_card = GlowFrame(content)
        how_card.pack(fill="x", pady=(0, 20))
        
        how_inner = ctk.CTkFrame(how_card, fg_color="transparent")
        how_inner.pack(fill="x", padx=28, pady=28)
        
        ctk.CTkLabel(
            how_inner,
            text="⚡  How It Works",
            font=Typography.H3,
            text_color=Theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 20))
        
        steps = [
            ("1", "Encryption", "Your password is encrypted with AES-256-GCM using Argon2id key derivation"),
            ("2", "Fragmentation", "The encrypted data is split into 3 shares using Shamir's Secret Sharing"),
            ("3", "Concealment", "Each share is hidden inside an image using LSB steganography"),
            ("4", "Recovery", "Any 2 of the 3 images can reconstruct your original password")
        ]
        
        for num, title, desc in steps:
            step_frame = ctk.CTkFrame(how_inner, fg_color="transparent")
            step_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                step_frame,
                text=num,
                font=Typography.BUTTON_LG,
                text_color=Theme.BG_VOID,
                fg_color=Theme.ACCENT_PRIMARY,
                corner_radius=16,
                width=32,
                height=32
            ).pack(side="left", padx=(0, 16))
            
            text_frame = ctk.CTkFrame(step_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                text_frame,
                text=title,
                font=Typography.H5,
                text_color=Theme.TEXT_PRIMARY
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                text_frame,
                text=desc,
                font=Typography.BODY_SM,
                text_color=Theme.TEXT_MUTED
            ).pack(anchor="w")
        
        # Warning Card
        warning_card = ctk.CTkFrame(
            content,
            fg_color=Theme.BG_DARK,
            corner_radius=Radius.LG,
            border_width=1,
            border_color=Theme.WARNING_DARK
        )
        warning_card.pack(fill="x", pady=(0, 20))
        
        warning_inner = ctk.CTkFrame(warning_card, fg_color="transparent")
        warning_inner.pack(fill="x", padx=28, pady=28)
        
        warning_header = ctk.CTkFrame(warning_inner, fg_color="transparent")
        warning_header.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            warning_header,
            text="⚠️",
            font=("Segoe UI Emoji", 20),
            text_color=Theme.WARNING
        ).pack(side="left", padx=(0, 12))
        
        ctk.CTkLabel(
            warning_header,
            text="Disclaimer",
            font=Typography.H5,
            text_color=Theme.WARNING
        ).pack(side="left")
        
        ctk.CTkLabel(
            warning_inner,
            text="This is research-driven software intended for educational and experimental use. Always maintain secure backups of important credentials through multiple methods.",
            font=Typography.BODY_MD,
            text_color=Theme.TEXT_SECONDARY,
            wraplength=700,
            justify="left"
        ).pack(anchor="w")
        
        return tab
        
    def _create_status_bar(self):
        """Create status bar"""
        status_bar = ctk.CTkFrame(
            self.main_container,
            fg_color=Theme.BG_VOID,
            height=36,
            corner_radius=0
        )
        status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        status_bar.grid_propagate(False)
        
        content = ctk.CTkFrame(status_bar, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20)
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            content,
            text="●",
            font=Typography.BODY_SM,
            text_color=Theme.SUCCESS
        )
        self.status_indicator.pack(side="left", padx=(0, 8), pady=8)
        
        # Status text
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            content,
            textvariable=self.status_var,
            font=Typography.BODY_SM,
            text_color=Theme.TEXT_MUTED
        )
        self.status_label.pack(side="left", pady=8)
        
        # Right info
        ctk.CTkLabel(
            content,
            text="Fractured Key v2.5  •  Premium Edition",
            font=Typography.CAPTION,
            text_color=Theme.TEXT_DISABLED
        ).pack(side="right", pady=8)
        
    def _show_tab(self, tab_id):
        """Switch to a tab"""
        self.current_tab = tab_id
        
        # Hide all tabs
        for tab in self.tabs.values():
            tab.pack_forget()
            
        # Show selected
        self.tabs[tab_id].pack(fill="both", expand=True)
        
        # Update nav styling
        for btn_id, btn_info in self.nav_buttons.items():
            if btn_id == tab_id:
                btn_info["frame"].configure(fg_color=Theme.BG_MEDIUM)
                btn_info["icon"].configure(text_color=Theme.ACCENT_PRIMARY)
                btn_info["title"].configure(text_color=Theme.ACCENT_PRIMARY)
            else:
                btn_info["frame"].configure(fg_color="transparent")
                btn_info["icon"].configure(text_color=Theme.TEXT_MUTED)
                btn_info["title"].configure(text_color=Theme.TEXT_PRIMARY)
                
    def _update_status(self, message, status_type="info"):
        """Update status bar"""
        self.status_var.set(message)
        colors = {
            "success": Theme.SUCCESS,
            "error": Theme.ERROR,
            "warning": Theme.WARNING,
            "info": Theme.ACCENT_PRIMARY
        }
        self.status_indicator.configure(text_color=colors.get(status_type, Theme.ACCENT_PRIMARY))
        
    def _log_output(self, widget, message, msg_type="info"):
        """Log message to output widget"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        prefix = {"success": "✓", "error": "✗", "warning": "⚠", "info": "▸"}.get(msg_type, "▸")
        widget.insert("end", f"[{timestamp}] {prefix} {message}\n")
        widget.see("end")
        self.update_idletasks()
        
    # ═══════════════════════════════════════════════════════════════════════════
    # ENCRYPTION LOGIC
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _start_encryption(self):
        """Start encryption"""
        if not CRYPTO_AVAILABLE:
            messagebox.showerror("Error", "Cryptography modules not available")
            return
            
        password = self.encrypt_password_entry.get().strip()
        master_password = self.encrypt_master_entry.get().strip()
        
        if not password:
            messagebox.showerror("Error", "Please enter a password to encrypt")
            return
        if not master_password:
            messagebox.showerror("Error", "Please enter a master password")
            return
            
        self.encrypt_output.delete("1.0", "end")
        self.encrypt_progress.start_animation()
        self.encrypt_btn.configure(state="disabled")
        self._update_status("Encrypting...", "info")
        
        thread = threading.Thread(target=self._encrypt_worker, args=(password, master_password))
        thread.daemon = True
        thread.start()
        
    def _encrypt_worker(self, password, master_password):
        """Encryption worker"""
        try:
            self._log_output(self.encrypt_output, "Starting encryption...", "info")
            self._log_output(self.encrypt_output, "━" * 45, "info")
            
            salt, nonce, ciphertext_with_tag = encrypt_password_aes_gcm(password, master_password)
            
            import base64
            self._log_output(self.encrypt_output, "Encryption successful!", "success")
            self._log_output(self.encrypt_output, f"Salt: {base64.b64encode(salt).decode()}", "info")
            self._log_output(self.encrypt_output, f"Nonce: {base64.b64encode(nonce).decode()}", "info")
            
            binary_blob = salt + nonce + ciphertext_with_tag
            
            if self.use_shares_var.get():
                self._log_output(self.encrypt_output, "━" * 45, "info")
                self._log_output(self.encrypt_output, "Splitting into SSS shares...", "info")
                self._create_shares_and_embed(binary_blob)
            else:
                filename = "encrypted_output.bin"
                with open(filename, "wb") as f:
                    f.write(binary_blob)
                self._log_output(self.encrypt_output, f"Saved: {filename}", "success")
                
        except Exception as e:
            self._log_output(self.encrypt_output, f"Error: {str(e)}", "error")
        finally:
            self.after(0, self._encryption_finished)
            
    def _create_shares_and_embed(self, binary_blob):
        """Create shares and embed"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            K2 = os.urandom(16)
            aes = AESGCM(K2)
            nonce2 = os.urandom(12)
            packaged_cipher = nonce2 + aes.encrypt(nonce2, binary_blob, None)
            
            shares = split_bytes_into_shares(K2, n=3, k=2)
            
            for i, share_bytes in enumerate(shares, start=1):
                self._log_output(self.encrypt_output, f"Processing share {i}/3...", "info")
                
                carrier_path = NativeFileDialog.askopenfilename(
                    title=f"Select carrier image for share {i}",
                    filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")],
                    parent=self
                )
                
                if not carrier_path:
                    self._log_output(self.encrypt_output, f"Skipped share {i}", "warning")
                    continue
                    
                payload = self._wrap_share_payload(share_bytes, i, 3, 2, packaged_cipher)
                
                output_path = NativeFileDialog.asksaveasfilename(
                    title=f"Save stego image {i}",
                    filetypes=[("PNG", "*.png")],
                    defaultextension=".png",
                    parent=self
                )
                
                if not output_path:
                    output_path = os.path.splitext(carrier_path)[0] + f"_stego_{i}.png"
                    
                saved = embed_data_into_image(carrier_path, payload, output_path=output_path)
                self._log_output(self.encrypt_output, f"Share {i} saved: {os.path.basename(saved)}", "success")
                
            self._log_output(self.encrypt_output, "━" * 45, "info")
            self._log_output(self.encrypt_output, "All shares processed!", "success")
            
        except Exception as e:
            self._log_output(self.encrypt_output, f"Error: {str(e)}", "error")
            
    def _wrap_share_payload(self, share_bytes, index, total, threshold, packaged_cipher):
        header = bytearray(b"FKSS01")
        header.append(1)
        header.append(index)
        header.append(total)
        header.append(threshold)
        header += len(share_bytes).to_bytes(4, 'big')
        header += len(packaged_cipher).to_bytes(4, 'big')
        return bytes(header) + share_bytes + packaged_cipher
        
    def _encryption_finished(self):
        self.encrypt_progress.stop_animation()
        self.encrypt_btn.configure(state="normal")
        self._update_status("Encryption completed", "success")
        
    # ═══════════════════════════════════════════════════════════════════════════
    # DECRYPTION LOGIC
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _add_image_file(self):
        path = NativeFileDialog.askopenfilename(
            title="Select stego image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")],
            parent=self
        )
        if path and path not in self.selected_images:
            self.selected_images.append(path)
            self._update_image_list()
            
    def _remove_all_images(self):
        self.selected_images = []
        self._update_image_list()
        
    def _update_image_list(self):
        self.image_listbox.configure(state="normal")
        self.image_listbox.delete("1.0", "end")
        if not self.selected_images:
            self.image_listbox.insert("1.0", "No images selected.\n")
        else:
            for i, path in enumerate(self.selected_images, 1):
                self.image_listbox.insert("end", f"{i}. {os.path.basename(path)}\n")
        self.image_listbox.configure(state="disabled")
        
    def _start_decryption(self):
        if not CRYPTO_AVAILABLE:
            messagebox.showerror("Error", "Cryptography modules not available")
            return
            
        if len(self.selected_images) < 2:
            messagebox.showerror("Error", "Select at least 2 stego images")
            return
            
        master_password = self.decrypt_master_entry.get().strip()
        if not master_password:
            messagebox.showerror("Error", "Enter master password")
            return
            
        self.decrypt_output.delete("1.0", "end")
        self.decrypt_progress.start_animation()
        self.decrypt_btn.configure(state="disabled")
        self._update_status("Decrypting...", "info")
        
        thread = threading.Thread(target=self._decrypt_worker, args=(self.selected_images.copy(), master_password))
        thread.daemon = True
        thread.start()
        
    def _decrypt_worker(self, image_paths, master_password):
        try:
            self._log_output(self.decrypt_output, "Starting decryption...", "info")
            self._log_output(self.decrypt_output, "━" * 45, "info")
            
            parsed_shares = []
            for path in image_paths:
                self._log_output(self.decrypt_output, f"Extracting: {os.path.basename(path)}", "info")
                payload = extract_data_from_image(path)
                meta = self._parse_share_payload(payload)
                parsed_shares.append(meta)
                
            if len(parsed_shares) < 2:
                self._log_output(self.decrypt_output, "Not enough shares", "error")
                return
                
            threshold = parsed_shares[0]['threshold']
            share_bytes_list = [s['share_bytes'] for s in parsed_shares[:threshold]]
            packaged_cipher = parsed_shares[0]['packaged_cipher']
            
            recovered_k2 = recover_bytes_from_shares(share_bytes_list)
            if len(recovered_k2) < 16:
                recovered_k2 = (b'\x00' * (16 - len(recovered_k2))) + recovered_k2
            elif len(recovered_k2) > 16:
                recovered_k2 = recovered_k2[-16:]
                
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            aes = AESGCM(recovered_k2)
            binary_blob = aes.decrypt(packaged_cipher[:12], packaged_cipher[12:], None)
            
            salt = binary_blob[:16]
            nonce = binary_blob[16:28]
            ciphertext_with_tag = binary_blob[28:]
            
            plaintext = decrypt_password_aes_gcm(salt, nonce, ciphertext_with_tag, master_password)
            
            self._log_output(self.decrypt_output, "━" * 45, "info")
            self._log_output(self.decrypt_output, "DECRYPTION SUCCESSFUL!", "success")
            self._log_output(self.decrypt_output, f"🔑 Password: {plaintext}", "success")
            
        except Exception as e:
            self._log_output(self.decrypt_output, f"Error: {str(e)}", "error")
        finally:
            self.after(0, self._decryption_finished)
            
    def _parse_share_payload(self, payload):
        pos = 6
        version = payload[pos]; pos += 1
        index = payload[pos]; pos += 1
        total = payload[pos]; pos += 1
        threshold = payload[pos]; pos += 1
        share_len = int.from_bytes(payload[pos:pos+4], 'big'); pos += 4
        packaged_cipher_len = int.from_bytes(payload[pos:pos+4], 'big'); pos += 4
        share_bytes = payload[pos:pos+share_len]; pos += share_len
        packaged_cipher = payload[pos:pos+packaged_cipher_len]
        return {"version": version, "index": index, "total": total, "threshold": threshold,
                "share_bytes": share_bytes, "packaged_cipher": packaged_cipher}
        
    def _decryption_finished(self):
        self.decrypt_progress.stop_animation()
        self.decrypt_btn.configure(state="normal")
        self._update_status("Decryption completed", "success")
        
    # ═══════════════════════════════════════════════════════════════════════════
    # MANUAL DECRYPTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _browse_manual_file(self):
        path = NativeFileDialog.askopenfilename(
            title="Select .bin file",
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")],
            parent=self
        )
        if path:
            self.manual_file_entry.delete(0, "end")
            self.manual_file_entry.insert(0, path)
            
    def _start_manual_decryption(self):
        if not CRYPTO_AVAILABLE:
            messagebox.showerror("Error", "Cryptography modules not available")
            return
            
        file_path = self.manual_file_entry.get().strip()
        master_password = self.manual_master_entry.get().strip()
        
        if not file_path:
            messagebox.showerror("Error", "Select a .bin file")
            return
        if not master_password:
            messagebox.showerror("Error", "Enter master password")
            return
            
        self.manual_output.delete("1.0", "end")
        
        try:
            self._log_output(self.manual_output, "Starting manual decryption...", "info")
            
            with open(file_path, "rb") as f:
                binary_blob = f.read()
                
            salt = binary_blob[:16]
            nonce = binary_blob[16:28]
            ciphertext_with_tag = binary_blob[28:]
            
            plaintext = decrypt_password_aes_gcm(salt, nonce, ciphertext_with_tag, master_password)
            
            self._log_output(self.manual_output, "━" * 45, "info")
            self._log_output(self.manual_output, "DECRYPTION SUCCESSFUL!", "success")
            self._log_output(self.manual_output, f"🔑 Password: {plaintext}", "success")
            self._update_status("Manual decryption completed", "success")
            
        except Exception as e:
            self._log_output(self.manual_output, f"Error: {str(e)}", "error")
            self._update_status("Decryption failed", "error")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    app = FracturedKeyApp()
    app.mainloop()

if __name__ == "__main__":
    main()
