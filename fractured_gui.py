#!/usr/bin/env python3
"""
Fractured Key - Premium Modern GUI
A sleek, mysterious, and tech-inspired password manager interface
Designed with 2024-2025 UI/UX trends
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys
from PIL import Image, ImageDraw, ImageFilter
import time

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from steganography import embed_data_into_image, extract_data_from_image
from sss import split_bytes_into_shares, recover_bytes_from_shares
from crypto import encrypt_password_aes_gcm, decrypt_password_aes_gcm

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR SCHEME - "Fractured Key" Theme
# A dark, mysterious palette with cyan/teal accents
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    # Primary backgrounds (dark, layered)
    BG_DARKEST = "#0A0E14"      # Deepest background
    BG_DARK = "#0D1117"          # Main background
    BG_MEDIUM = "#161B22"        # Card background
    BG_LIGHT = "#1C2128"         # Elevated surfaces
    BG_HOVER = "#21262D"         # Hover state
    
    # Accent colors (mysterious cyan/teal)
    ACCENT_PRIMARY = "#00D9FF"   # Primary cyan
    ACCENT_GLOW = "#00B4D8"      # Glow effect
    ACCENT_MUTED = "#0891B2"     # Muted accent
    ACCENT_DARK = "#065F73"      # Dark accent
    
    # Semantic colors
    SUCCESS = "#10B981"          # Emerald green
    SUCCESS_GLOW = "#059669"
    WARNING = "#F59E0B"          # Amber
    ERROR = "#EF4444"            # Red
    ERROR_GLOW = "#DC2626"
    
    # Text colors
    TEXT_PRIMARY = "#F0F6FC"     # Primary text
    TEXT_SECONDARY = "#8B949E"   # Secondary text
    TEXT_MUTED = "#6E7681"       # Muted text
    TEXT_ACCENT = "#00D9FF"      # Accent text
    
    # Border and dividers
    BORDER = "#30363D"           # Standard border
    BORDER_GLOW = "#00D9FF33"    # Glowing border (with alpha)
    
    # Gradients (for reference)
    GRADIENT_START = "#0D1117"
    GRADIENT_END = "#161B22"

# ═══════════════════════════════════════════════════════════════════════════════
# TYPOGRAPHY
# Modern, clean fonts with good hierarchy
# ═══════════════════════════════════════════════════════════════════════════════

class Fonts:
    # Font family - Using system fonts that look modern
    # Fallback chain: Segoe UI (Windows) > SF Pro (Mac) > Ubuntu (Linux)
    FAMILY = "Segoe UI"
    FAMILY_MONO = "Cascadia Code"
    
    # Font sizes
    TITLE_XL = ("Segoe UI", 32, "bold")
    TITLE_LG = ("Segoe UI", 24, "bold")
    TITLE_MD = ("Segoe UI", 18, "bold")
    TITLE_SM = ("Segoe UI", 14, "bold")
    
    BODY_LG = ("Segoe UI", 14)
    BODY_MD = ("Segoe UI", 12)
    BODY_SM = ("Segoe UI", 11)
    
    MONO_LG = ("Cascadia Code", 12)
    MONO_MD = ("Cascadia Code", 11)
    MONO_SM = ("Cascadia Code", 10)
    
    BUTTON = ("Segoe UI", 13, "bold")
    LABEL = ("Segoe UI", 12, "bold")
    CAPTION = ("Segoe UI", 10)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# Modern, stylized UI components
# ═══════════════════════════════════════════════════════════════════════════════

class GlowingCard(ctk.CTkFrame):
    """A card with subtle glow effect on hover"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.BG_MEDIUM,
            corner_radius=16,
            border_width=1,
            border_color=Colors.BORDER,
            **kwargs
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _on_enter(self, event):
        self.configure(border_color=Colors.ACCENT_DARK)
        
    def _on_leave(self, event):
        self.configure(border_color=Colors.BORDER)


class AccentButton(ctk.CTkButton):
    """Primary action button with glow effect"""
    def __init__(self, master, height=48, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_GLOW,
            text_color=Colors.BG_DARKEST,
            corner_radius=12,
            height=height,
            font=Fonts.BUTTON,
            **kwargs
        )


class SecondaryButton(ctk.CTkButton):
    """Secondary action button"""
    def __init__(self, master, height=44, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.BG_LIGHT,
            hover_color=Colors.BG_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=12,
            height=height,
            font=Fonts.BODY_MD,
            **kwargs
        )


class SuccessButton(ctk.CTkButton):
    """Success/confirm action button"""
    def __init__(self, master, height=48, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.SUCCESS,
            hover_color=Colors.SUCCESS_GLOW,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=12,
            height=height,
            font=Fonts.BUTTON,
            **kwargs
        )


class DangerButton(ctk.CTkButton):
    """Danger/destructive action button"""
    def __init__(self, master, height=44, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.ERROR,
            hover_color=Colors.ERROR_GLOW,
            text_color=Colors.TEXT_PRIMARY,
            corner_radius=12,
            height=height,
            font=Fonts.BODY_MD,
            **kwargs
        )


class ModernEntry(ctk.CTkEntry):
    """Styled text entry with focus animation"""
    def __init__(self, master, placeholder="", is_password=False, height=48, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.BG_LIGHT,
            border_color=Colors.BORDER,
            border_width=2,
            corner_radius=10,
            height=height,
            placeholder_text=placeholder,
            placeholder_text_color=Colors.TEXT_MUTED,
            text_color=Colors.TEXT_PRIMARY,
            font=Fonts.BODY_LG,
            show="●" if is_password else "",
            **kwargs
        )
        self.bind("<FocusIn>", self._on_focus)
        self.bind("<FocusOut>", self._on_unfocus)
        
    def _on_focus(self, event):
        self.configure(border_color=Colors.ACCENT_PRIMARY)
        
    def _on_unfocus(self, event):
        self.configure(border_color=Colors.BORDER)


class ModernTextbox(ctk.CTkTextbox):
    """Styled multiline text area"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.BG_DARKEST,
            border_color=Colors.BORDER,
            border_width=1,
            corner_radius=10,
            text_color=Colors.TEXT_PRIMARY,
            font=Fonts.MONO_MD,
            scrollbar_button_color=Colors.BG_LIGHT,
            scrollbar_button_hover_color=Colors.BG_HOVER,
            **kwargs
        )


class AnimatedProgress(ctk.CTkProgressBar):
    """Animated progress bar"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.BG_LIGHT,
            progress_color=Colors.ACCENT_PRIMARY,
            corner_radius=8,
            height=6,
            **kwargs
        )
        self._animating = False
        self._animation_pos = 0
        
    def start_animation(self):
        self._animating = True
        self.configure(mode="indeterminate")
        self.start()
        
    def stop_animation(self):
        self._animating = False
        self.stop()
        self.configure(mode="determinate")
        self.set(0)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class FracturedKeyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Window setup
        self.title("Fractured Key")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(fg_color=Colors.BG_DARK)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"1200x800+{x}+{y}")
        
        # State variables
        self.selected_images = []
        self.current_tab = "encrypt"
        
        # Create UI
        self._create_layout()
        self._create_header()
        self._create_sidebar()
        self._create_main_content()
        self._create_status_bar()
        
        # Show encrypt tab by default
        self._show_tab("encrypt")
        
    def _create_layout(self):
        """Create the main layout structure"""
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Configure grid
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
    def _create_header(self):
        """Create the app header"""
        header = ctk.CTkFrame(
            self.main_container, 
            fg_color=Colors.BG_DARKEST,
            height=80,
            corner_radius=0
        )
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        
        # Logo and title container
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=30, pady=15)
        
        # Key icon (using unicode)
        icon_label = ctk.CTkLabel(
            title_frame,
            text="🔐",
            font=("Segoe UI Emoji", 32),
            text_color=Colors.ACCENT_PRIMARY
        )
        icon_label.pack(side="left", padx=(0, 15))
        
        # Title text
        title_text = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_text.pack(side="left")
        
        ctk.CTkLabel(
            title_text,
            text="FRACTURED KEY",
            font=Fonts.TITLE_LG,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_text,
            text="Steganographic Password Vault",
            font=Fonts.BODY_SM,
            text_color=Colors.TEXT_MUTED
        ).pack(anchor="w")
        
        # Version badge
        version_badge = ctk.CTkLabel(
            header,
            text="v2.0",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_LIGHT,
            corner_radius=6,
            padx=10,
            pady=4
        )
        version_badge.pack(side="right", padx=30)
        
    def _create_sidebar(self):
        """Create the navigation sidebar"""
        sidebar = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.BG_DARKEST,
            width=240,
            corner_radius=0
        )
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", pady=20, padx=15)
        
        # Navigation items
        nav_items = [
            ("encrypt", "🔒", "Encrypt", "Hide your secrets"),
            ("decrypt", "🔓", "Decrypt", "Reveal your secrets"),
            ("manual", "📁", "Manual", "Direct file decrypt"),
            ("about", "ℹ️", "About", "Learn more"),
        ]
        
        self.nav_buttons = {}
        
        for tab_id, icon, title, subtitle in nav_items:
            btn_frame = ctk.CTkFrame(
                nav_frame, 
                fg_color="transparent",
                cursor="hand2"
            )
            btn_frame.pack(fill="x", pady=4)
            
            # Make the entire frame clickable
            btn_frame.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            # Inner content
            content = ctk.CTkFrame(btn_frame, fg_color="transparent")
            content.pack(fill="x", padx=12, pady=10)
            content.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            # Icon
            icon_lbl = ctk.CTkLabel(
                content,
                text=icon,
                font=("Segoe UI Emoji", 20),
                text_color=Colors.TEXT_SECONDARY
            )
            icon_lbl.pack(side="left", padx=(0, 12))
            icon_lbl.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            # Text container
            text_container = ctk.CTkFrame(content, fg_color="transparent")
            text_container.pack(side="left", fill="x", expand=True)
            text_container.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            title_lbl = ctk.CTkLabel(
                text_container,
                text=title,
                font=Fonts.TITLE_SM,
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            title_lbl.pack(anchor="w")
            title_lbl.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            subtitle_lbl = ctk.CTkLabel(
                text_container,
                text=subtitle,
                font=Fonts.CAPTION,
                text_color=Colors.TEXT_MUTED,
                anchor="w"
            )
            subtitle_lbl.pack(anchor="w")
            subtitle_lbl.bind("<Button-1>", lambda e, t=tab_id: self._show_tab(t))
            
            self.nav_buttons[tab_id] = {
                "frame": btn_frame,
                "icon": icon_lbl,
                "title": title_lbl,
                "subtitle": subtitle_lbl
            }
            
            # Hover effects
            def on_enter(e, f=btn_frame, t=tab_id):
                if self.current_tab != t:
                    f.configure(fg_color=Colors.BG_HOVER)
            def on_leave(e, f=btn_frame, t=tab_id):
                if self.current_tab != t:
                    f.configure(fg_color="transparent")
                    
            btn_frame.bind("<Enter>", on_enter)
            btn_frame.bind("<Leave>", on_leave)
            
        # Divider
        divider = ctk.CTkFrame(
            sidebar,
            fg_color=Colors.BORDER,
            height=1
        )
        divider.pack(fill="x", padx=15, pady=20)
        
        # Security info
        security_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        security_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            security_frame,
            text="🛡️ Security",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 8))
        
        security_items = [
            "AES-256-GCM Encryption",
            "Argon2id Key Derivation",
            "Shamir Secret Sharing",
            "LSB Steganography"
        ]
        
        for item in security_items:
            item_frame = ctk.CTkFrame(security_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                item_frame,
                text="•",
                font=Fonts.BODY_SM,
                text_color=Colors.ACCENT_MUTED
            ).pack(side="left", padx=(0, 8))
            
            ctk.CTkLabel(
                item_frame,
                text=item,
                font=Fonts.BODY_SM,
                text_color=Colors.TEXT_MUTED
            ).pack(side="left")
            
    def _create_main_content(self):
        """Create the main content area"""
        # Content container
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=Colors.BG_DARK,
            corner_radius=0
        )
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        
        # Create all tab frames
        self.tabs = {}
        self.tabs["encrypt"] = self._create_encrypt_tab()
        self.tabs["decrypt"] = self._create_decrypt_tab()
        self.tabs["manual"] = self._create_manual_tab()
        self.tabs["about"] = self._create_about_tab()
        
    def _create_encrypt_tab(self):
        """Create the encryption tab"""
        tab = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=Colors.BG_LIGHT,
            scrollbar_button_hover_color=Colors.BG_HOVER
        )
        
        # Page title
        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(30, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="Encrypt Password",
            font=Fonts.TITLE_LG,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text="Secure your password using military-grade encryption and steganography",
            font=Fonts.BODY_MD,
            text_color=Colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # Main content grid
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(0, 30))
        
        # Password input card
        password_card = GlowingCard(content)
        password_card.pack(fill="x", pady=(0, 20))
        
        card_content = ctk.CTkFrame(password_card, fg_color="transparent")
        card_content.pack(fill="x", padx=24, pady=24)
        
        # Password to encrypt
        ctk.CTkLabel(
            card_content,
            text="🔑 Password to Encrypt",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        self.encrypt_password_entry = ModernEntry(
            card_content,
            placeholder="Enter the password you want to protect...",
            is_password=True,
            width=500
        )
        self.encrypt_password_entry.pack(fill="x", pady=(0, 20))
        
        # Master password
        ctk.CTkLabel(
            card_content,
            text="🔐 Master Password",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        self.encrypt_master_entry = ModernEntry(
            card_content,
            placeholder="Enter your master password...",
            is_password=True,
            width=500
        )
        self.encrypt_master_entry.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            card_content,
            text="This password will be used to decrypt your data later",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED
        ).pack(anchor="w")
        
        # Options card
        options_card = GlowingCard(content)
        options_card.pack(fill="x", pady=(0, 20))
        
        options_content = ctk.CTkFrame(options_card, fg_color="transparent")
        options_content.pack(fill="x", padx=24, pady=24)
        
        ctk.CTkLabel(
            options_content,
            text="⚙️ Encryption Options",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 15))
        
        self.use_shares_var = ctk.BooleanVar(value=True)
        
        shares_checkbox = ctk.CTkCheckBox(
            options_content,
            text="Split into 3 shares and embed into images",
            variable=self.use_shares_var,
            font=Fonts.BODY_MD,
            text_color=Colors.TEXT_PRIMARY,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_GLOW,
            border_color=Colors.BORDER,
            checkmark_color=Colors.BG_DARKEST,
            corner_radius=6
        )
        shares_checkbox.pack(anchor="w", pady=(0, 8))
        
        ctk.CTkLabel(
            options_content,
            text="💡 Creates 3 stego images. You need at least 2 to decrypt.",
            font=Fonts.BODY_SM,
            text_color=Colors.TEXT_MUTED
        ).pack(anchor="w", padx=(26, 0))
        
        # Action button
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 20))
        
        self.encrypt_btn = AccentButton(
            button_frame,
            text="🔒  Start Encryption",
            command=self._start_encryption,
            width=220
        )
        self.encrypt_btn.pack(anchor="w")
        
        # Progress
        self.encrypt_progress = AnimatedProgress(content)
        self.encrypt_progress.pack(fill="x", pady=(0, 20))
        
        # Output card
        output_card = GlowingCard(content)
        output_card.pack(fill="both", expand=True)
        
        output_header = ctk.CTkFrame(output_card, fg_color="transparent")
        output_header.pack(fill="x", padx=24, pady=(24, 12))
        
        ctk.CTkLabel(
            output_header,
            text="📋 Output Log",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left")
        
        # Clear button
        SecondaryButton(
            output_header,
            text="Clear",
            command=lambda: self.encrypt_output.delete("1.0", "end"),
            width=80,
            height=32
        ).pack(side="right")
        
        self.encrypt_output = ModernTextbox(output_card, height=200)
        self.encrypt_output.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        
        # Initial message
        self.encrypt_output.insert("1.0", "🔒 Ready to encrypt your password.\n")
        self.encrypt_output.insert("end", "━" * 50 + "\n")
        self.encrypt_output.insert("end", "Enter your password and master password above, then click 'Start Encryption'.\n")
        
        return tab
        
    def _create_decrypt_tab(self):
        """Create the decryption tab"""
        tab = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=Colors.BG_LIGHT,
            scrollbar_button_hover_color=Colors.BG_HOVER
        )
        
        # Page title
        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(30, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="Decrypt Password",
            font=Fonts.TITLE_LG,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text="Recover your password from steganographic images",
            font=Fonts.BODY_MD,
            text_color=Colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # Main content
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(0, 30))
        
        # Instructions card
        instructions_card = GlowingCard(content)
        instructions_card.pack(fill="x", pady=(0, 20))
        
        instructions_content = ctk.CTkFrame(instructions_card, fg_color="transparent")
        instructions_content.pack(fill="x", padx=24, pady=24)
        
        ctk.CTkLabel(
            instructions_content,
            text="📖 How to Decrypt",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))
        
        steps = [
            ("1", "Select at least 2 stego images from the same encryption session"),
            ("2", "Enter your master password"),
            ("3", "Click 'Start Decryption' to recover your password")
        ]
        
        for num, text in steps:
            step_frame = ctk.CTkFrame(instructions_content, fg_color="transparent")
            step_frame.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                step_frame,
                text=num,
                font=Fonts.BODY_SM,
                text_color=Colors.BG_DARKEST,
                fg_color=Colors.ACCENT_PRIMARY,
                corner_radius=10,
                width=24,
                height=24
            ).pack(side="left", padx=(0, 12))
            
            ctk.CTkLabel(
                step_frame,
                text=text,
                font=Fonts.BODY_MD,
                text_color=Colors.TEXT_SECONDARY
            ).pack(side="left")
        
        # Image selection card
        image_card = GlowingCard(content)
        image_card.pack(fill="x", pady=(0, 20))
        
        image_content = ctk.CTkFrame(image_card, fg_color="transparent")
        image_content.pack(fill="x", padx=24, pady=24)
        
        ctk.CTkLabel(
            image_content,
            text="🖼️ Selected Images",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))
        
        # Image list
        list_frame = ctk.CTkFrame(
            image_content,
            fg_color=Colors.BG_DARKEST,
            corner_radius=10,
            border_width=1,
            border_color=Colors.BORDER
        )
        list_frame.pack(fill="x", pady=(0, 12))
        
        self.image_listbox = ctk.CTkTextbox(
            list_frame,
            height=120,
            fg_color=Colors.BG_DARKEST,
            text_color=Colors.TEXT_PRIMARY,
            font=Fonts.MONO_MD,
            state="disabled",
            corner_radius=10,
            border_width=0
        )
        self.image_listbox.pack(fill="x", padx=4, pady=4)
        
        # Image buttons
        btn_frame = ctk.CTkFrame(image_content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        SuccessButton(
            btn_frame,
            text="📁 Add Image",
            command=self._add_image_file,
            width=140,
            height=40
        ).pack(side="left", padx=(0, 10))
        
        DangerButton(
            btn_frame,
            text="🗑️ Remove Selected",
            command=self._remove_all_images,
            width=160,
            height=40
        ).pack(side="left")
        
        # Master password card
        password_card = GlowingCard(content)
        password_card.pack(fill="x", pady=(0, 20))
        
        password_content = ctk.CTkFrame(password_card, fg_color="transparent")
        password_content.pack(fill="x", padx=24, pady=24)
        
        ctk.CTkLabel(
            password_content,
            text="🔐 Master Password",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        self.decrypt_master_entry = ModernEntry(
            password_content,
            placeholder="Enter your master password...",
            is_password=True,
            width=500
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
        
        # Output card
        output_card = GlowingCard(content)
        output_card.pack(fill="both", expand=True)
        
        output_header = ctk.CTkFrame(output_card, fg_color="transparent")
        output_header.pack(fill="x", padx=24, pady=(24, 12))
        
        ctk.CTkLabel(
            output_header,
            text="📋 Decryption Results",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left")
        
        SecondaryButton(
            output_header,
            text="Clear",
            command=lambda: self.decrypt_output.delete("1.0", "end"),
            width=80,
            height=32
        ).pack(side="right")
        
        self.decrypt_output = ModernTextbox(output_card, height=200)
        self.decrypt_output.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        
        # Initial message
        self.decrypt_output.insert("1.0", "🔓 Ready to decrypt your password.\n")
        self.decrypt_output.insert("end", "━" * 50 + "\n")
        self.decrypt_output.insert("end", "Select at least 2 stego images and enter your master password.\n")
        
        return tab
        
    def _create_manual_tab(self):
        """Create the manual decryption tab"""
        tab = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=Colors.BG_LIGHT,
            scrollbar_button_hover_color=Colors.BG_HOVER
        )
        
        # Page title
        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(30, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="Manual Decryption",
            font=Fonts.TITLE_LG,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text="Decrypt .bin files directly without steganography",
            font=Fonts.BODY_MD,
            text_color=Colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # Main content
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(0, 30))
        
        # File selection card
        file_card = GlowingCard(content)
        file_card.pack(fill="x", pady=(0, 20))
        
        file_content = ctk.CTkFrame(file_card, fg_color="transparent")
        file_content.pack(fill="x", padx=24, pady=24)
        
        ctk.CTkLabel(
            file_content,
            text="📁 Select Binary File",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))
        
        file_input_frame = ctk.CTkFrame(file_content, fg_color="transparent")
        file_input_frame.pack(fill="x")
        
        self.manual_file_entry = ModernEntry(
            file_input_frame,
            placeholder="Select a .bin file...",
            width=400
        )
        self.manual_file_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        SecondaryButton(
            file_input_frame,
            text="📂 Browse",
            command=self._browse_manual_file,
            width=100,
            height=48
        ).pack(side="right")
        
        # Master password card
        password_card = GlowingCard(content)
        password_card.pack(fill="x", pady=(0, 20))
        
        password_content = ctk.CTkFrame(password_card, fg_color="transparent")
        password_content.pack(fill="x", padx=24, pady=24)
        
        ctk.CTkLabel(
            password_content,
            text="🔐 Master Password",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))
        
        self.manual_master_entry = ModernEntry(
            password_content,
            placeholder="Enter your master password...",
            is_password=True,
            width=500
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
        
        # Output card
        output_card = GlowingCard(content)
        output_card.pack(fill="both", expand=True)
        
        output_header = ctk.CTkFrame(output_card, fg_color="transparent")
        output_header.pack(fill="x", padx=24, pady=(24, 12))
        
        ctk.CTkLabel(
            output_header,
            text="📋 Results",
            font=Fonts.LABEL,
            text_color=Colors.TEXT_PRIMARY
        ).pack(side="left")
        
        SecondaryButton(
            output_header,
            text="Clear",
            command=lambda: self.manual_output.delete("1.0", "end"),
            width=80,
            height=32
        ).pack(side="right")
        
        self.manual_output = ModernTextbox(output_card, height=250)
        self.manual_output.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        
        # Initial message
        self.manual_output.insert("1.0", "🔓 Manual decryption mode.\n")
        self.manual_output.insert("end", "━" * 50 + "\n")
        self.manual_output.insert("end", "Use this if you saved encrypted data as a .bin file.\n")
        
        return tab
        
    def _create_about_tab(self):
        """Create the about tab"""
        tab = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent",
            scrollbar_button_color=Colors.BG_LIGHT,
            scrollbar_button_hover_color=Colors.BG_HOVER
        )
        
        # Page title
        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(30, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="About Fractured Key",
            font=Fonts.TITLE_LG,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w")
        
        # Main content
        content = ctk.CTkFrame(tab, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=(0, 30))
        
        # Overview card
        overview_card = GlowingCard(content)
        overview_card.pack(fill="x", pady=(0, 20))
        
        overview_content = ctk.CTkFrame(overview_card, fg_color="transparent")
        overview_content.pack(fill="x", padx=24, pady=24)
        
        ctk.CTkLabel(
            overview_content,
            text="🔐 What is Fractured Key?",
            font=Fonts.TITLE_MD,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 12))
        
        overview_text = """Fractured Key is an experimental approach to secure credential storage that avoids traditional single-point vaults. Instead of keeping an encrypted blob in one place, your data is divided, transformed, and distributed across multiple independent carriers.

The result is a system that doesn't resemble a password manager in its raw form — the stored material does not look like secrets at all."""
        
        ctk.CTkLabel(
            overview_content,
            text=overview_text,
            font=Fonts.BODY_MD,
            text_color=Colors.TEXT_SECONDARY,
            wraplength=700,
            justify="left"
        ).pack(anchor="w")
        
        # How it works card
        how_card = GlowingCard(content)
        how_card.pack(fill="x", pady=(0, 20))
        
        how_content = ctk.CTkFrame(how_card, fg_color="transparent")
        how_content.pack(fill="x", padx=24, pady=24)
        
        ctk.CTkLabel(
            how_content,
            text="⚡ How It Works",
            font=Fonts.TITLE_MD,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 16))
        
        steps = [
            ("1", "Your password is encrypted with AES-GCM using a master password"),
            ("2", "The encrypted data is split into shares using Shamir Secret Sharing"),
            ("3", "Each share is embedded into a different image using steganography"),
            ("4", "You need at least 2 out of 3 images to reconstruct your password")
        ]
        
        for num, text in steps:
            step_frame = ctk.CTkFrame(how_content, fg_color="transparent")
            step_frame.pack(fill="x", pady=6)
            
            ctk.CTkLabel(
                step_frame,
                text=num,
                font=Fonts.BODY_MD,
                text_color=Colors.BG_DARKEST,
                fg_color=Colors.ACCENT_PRIMARY,
                corner_radius=12,
                width=28,
                height=28
            ).pack(side="left", padx=(0, 16))
            
            ctk.CTkLabel(
                step_frame,
                text=text,
                font=Fonts.BODY_MD,
                text_color=Colors.TEXT_SECONDARY
            ).pack(side="left")
        
        # Features card
        features_card = GlowingCard(content)
        features_card.pack(fill="x", pady=(0, 20))
        
        features_content = ctk.CTkFrame(features_card, fg_color="transparent")
        features_content.pack(fill="x", padx=24, pady=24)
        
        ctk.CTkLabel(
            features_content,
            text="✨ Key Features",
            font=Fonts.TITLE_MD,
            text_color=Colors.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 16))
        
        features = [
            ("🔒", "Offline Security", "No reliance on online services"),
            ("🔀", "Redundancy", "Only partial components needed to recover"),
            ("🖼️", "Steganographic", "Information hidden where least expected"),
            ("🛡️", "Layered Crypto", "Multiple primitives combined for security")
        ]
        
        features_grid = ctk.CTkFrame(features_content, fg_color="transparent")
        features_grid.pack(fill="x")
        
        for i, (icon, title, desc) in enumerate(features):
            feature_frame = ctk.CTkFrame(
                features_grid,
                fg_color=Colors.BG_LIGHT,
                corner_radius=12
            )
            feature_frame.grid(row=i//2, column=i%2, padx=8, pady=8, sticky="ew")
            features_grid.grid_columnconfigure(i%2, weight=1)
            
            inner = ctk.CTkFrame(feature_frame, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=16)
            
            ctk.CTkLabel(
                inner,
                text=icon,
                font=("Segoe UI Emoji", 24),
                text_color=Colors.ACCENT_PRIMARY
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                inner,
                text=title,
                font=Fonts.TITLE_SM,
                text_color=Colors.TEXT_PRIMARY
            ).pack(anchor="w", pady=(8, 4))
            
            ctk.CTkLabel(
                inner,
                text=desc,
                font=Fonts.BODY_SM,
                text_color=Colors.TEXT_MUTED
            ).pack(anchor="w")
        
        # Warning card
        warning_card = ctk.CTkFrame(
            content,
            fg_color=Colors.BG_MEDIUM,
            corner_radius=16,
            border_width=1,
            border_color=Colors.WARNING
        )
        warning_card.pack(fill="x", pady=(0, 20))
        
        warning_content = ctk.CTkFrame(warning_card, fg_color="transparent")
        warning_content.pack(fill="x", padx=24, pady=24)
        
        warning_header = ctk.CTkFrame(warning_content, fg_color="transparent")
        warning_header.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            warning_header,
            text="⚠️",
            font=("Segoe UI Emoji", 20),
            text_color=Colors.WARNING
        ).pack(side="left", padx=(0, 12))
        
        ctk.CTkLabel(
            warning_header,
            text="Disclaimer",
            font=Fonts.TITLE_SM,
            text_color=Colors.WARNING
        ).pack(side="left")
        
        ctk.CTkLabel(
            warning_content,
            text="This is research-driven software intended for educational and experimental use. Always maintain secure backups of important credentials.",
            font=Fonts.BODY_MD,
            text_color=Colors.TEXT_SECONDARY,
            wraplength=700,
            justify="left"
        ).pack(anchor="w")
        
        return tab
        
    def _create_status_bar(self):
        """Create the status bar"""
        status_bar = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_DARKEST,
            height=36,
            corner_radius=0
        )
        status_bar.pack(side="bottom", fill="x")
        status_bar.pack_propagate(False)
        
        status_content = ctk.CTkFrame(status_bar, fg_color="transparent")
        status_content.pack(fill="both", expand=True, padx=20)
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            status_content,
            text="●",
            font=Fonts.BODY_SM,
            text_color=Colors.SUCCESS
        )
        self.status_indicator.pack(side="left", padx=(0, 8))
        
        # Status text
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            status_content,
            textvariable=self.status_var,
            font=Fonts.BODY_SM,
            text_color=Colors.TEXT_MUTED
        )
        self.status_label.pack(side="left")
        
        # Right side info
        ctk.CTkLabel(
            status_content,
            text="Fractured Key v2.0 | AES-256-GCM + Argon2id + SSS",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED
        ).pack(side="right")
        
    def _show_tab(self, tab_id):
        """Switch to a different tab"""
        # Update current tab
        self.current_tab = tab_id
        
        # Hide all tabs
        for tab in self.tabs.values():
            tab.pack_forget()
            
        # Show selected tab
        self.tabs[tab_id].pack(fill="both", expand=True)
        
        # Update navigation styling
        for btn_id, btn_info in self.nav_buttons.items():
            if btn_id == tab_id:
                btn_info["frame"].configure(fg_color=Colors.BG_LIGHT)
                btn_info["icon"].configure(text_color=Colors.ACCENT_PRIMARY)
                btn_info["title"].configure(text_color=Colors.ACCENT_PRIMARY)
            else:
                btn_info["frame"].configure(fg_color="transparent")
                btn_info["icon"].configure(text_color=Colors.TEXT_SECONDARY)
                btn_info["title"].configure(text_color=Colors.TEXT_PRIMARY)
                
    def _update_status(self, message, status_type="info"):
        """Update status bar"""
        self.status_var.set(message)
        
        if status_type == "success":
            self.status_indicator.configure(text_color=Colors.SUCCESS)
        elif status_type == "error":
            self.status_indicator.configure(text_color=Colors.ERROR)
        elif status_type == "warning":
            self.status_indicator.configure(text_color=Colors.WARNING)
        else:
            self.status_indicator.configure(text_color=Colors.ACCENT_PRIMARY)
            
    def _log_output(self, text_widget, message, msg_type="info"):
        """Add message to output text widget"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Format based on type
        prefix = ""
        if msg_type == "success":
            prefix = "✓"
        elif msg_type == "error":
            prefix = "✗"
        elif msg_type == "warning":
            prefix = "⚠"
        else:
            prefix = "▸"
            
        formatted = f"[{timestamp}] {prefix} {message}\n"
        text_widget.insert("end", formatted)
        text_widget.see("end")
        self.update_idletasks()
        
    # ═══════════════════════════════════════════════════════════════════════════
    # ENCRYPTION LOGIC
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _start_encryption(self):
        """Start the encryption process"""
        password = self.encrypt_password_entry.get().strip()
        master_password = self.encrypt_master_entry.get().strip()
        
        if not password:
            messagebox.showerror("Error", "Please enter a password to encrypt")
            return
            
        if not master_password:
            messagebox.showerror("Error", "Please enter a master password")
            return
            
        # Clear output
        self.encrypt_output.delete("1.0", "end")
        
        # Start animation
        self.encrypt_progress.start_animation()
        self.encrypt_btn.configure(state="disabled")
        self._update_status("Encrypting...", "info")
        
        # Run in thread
        thread = threading.Thread(
            target=self._encrypt_worker,
            args=(password, master_password)
        )
        thread.daemon = True
        thread.start()
        
    def _encrypt_worker(self, password, master_password):
        """Encryption worker thread"""
        try:
            self._log_output(self.encrypt_output, "Starting encryption process...", "info")
            self._log_output(self.encrypt_output, "━" * 50, "info")
            
            # Encrypt the password
            self._log_output(self.encrypt_output, f"Password length: {len(password)} characters", "info")
            self._log_output(self.encrypt_output, "Deriving key with Argon2id...", "info")
            
            salt, nonce, ciphertext_with_tag = encrypt_password_aes_gcm(password, master_password)
            
            import base64
            ciphertext = ciphertext_with_tag[:-16]
            auth_tag = ciphertext_with_tag[-16:]
            
            self._log_output(self.encrypt_output, "Encryption successful!", "success")
            self._log_output(self.encrypt_output, "━" * 50, "info")
            self._log_output(self.encrypt_output, f"Salt: {base64.b64encode(salt).decode()}", "info")
            self._log_output(self.encrypt_output, f"Nonce: {base64.b64encode(nonce).decode()}", "info")
            self._log_output(self.encrypt_output, f"Ciphertext: {base64.b64encode(ciphertext).decode()}", "info")
            self._log_output(self.encrypt_output, f"Auth Tag: {base64.b64encode(auth_tag).decode()}", "info")
            
            binary_blob = salt + nonce + ciphertext_with_tag
            
            if self.use_shares_var.get():
                self._log_output(self.encrypt_output, "━" * 50, "info")
                self._log_output(self.encrypt_output, "Splitting into SSS shares...", "info")
                self._create_shares_and_embed(binary_blob)
            else:
                filename = "encrypted_output.bin"
                with open(filename, "wb") as f:
                    f.write(binary_blob)
                self._log_output(self.encrypt_output, f"Binary file saved: {filename}", "success")
                
        except Exception as e:
            self._log_output(self.encrypt_output, f"Encryption failed: {str(e)}", "error")
        finally:
            self.after(0, self._encryption_finished)
            
    def _create_shares_and_embed(self, binary_blob):
        """Create shares and embed into images"""
        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            self._log_output(self.encrypt_output, "Generating ephemeral key...", "info")
            K2 = os.urandom(16)
            aes = AESGCM(K2)
            nonce2 = os.urandom(12)
            packaged_ct_and_tag = aes.encrypt(nonce2, binary_blob, None)
            packaged_cipher = nonce2 + packaged_ct_and_tag
            
            n_shares = 3
            threshold = 2
            self._log_output(self.encrypt_output, f"Splitting key into {n_shares} shares (threshold: {threshold})...", "info")
            shares = split_bytes_into_shares(K2, n=n_shares, k=threshold)
            
            for i, share_bytes in enumerate(shares, start=1):
                self._log_output(self.encrypt_output, f"━" * 50, "info")
                self._log_output(self.encrypt_output, f"Processing share {i}/{n_shares}...", "info")
                
                file_types = [("Images", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("All files", "*.*")]
                carrier_path = filedialog.askopenfilename(
                    title=f"Select carrier image for share {i}",
                    filetypes=file_types
                )
                
                if not carrier_path:
                    self._log_output(self.encrypt_output, f"No carrier selected for share {i}. Skipping.", "warning")
                    continue
                    
                self._log_output(self.encrypt_output, f"Carrier: {os.path.basename(carrier_path)}", "info")
                
                payload = self._wrap_share_payload(share_bytes, index=i, total=n_shares,
                                                   threshold=threshold, packaged_cipher=packaged_cipher)
                
                output_path = filedialog.asksaveasfilename(
                    title=f"Save stego image for share {i}",
                    filetypes=[("PNG image", "*.png"), ("All files", "*.*")],
                    defaultextension=".png"
                )
                
                if not output_path:
                    base = os.path.splitext(carrier_path)[0]
                    output_path = f"{base}_stego_{i}.png"
                    
                saved_path = embed_data_into_image(carrier_path, payload, output_path=output_path)
                self._log_output(self.encrypt_output, f"Share {i} embedded: {saved_path}", "success")
                
            self._log_output(self.encrypt_output, "━" * 50, "info")
            self._log_output(self.encrypt_output, "All shares processed successfully!", "success")
            self._log_output(self.encrypt_output, "Keep at least 2 stego images safe!", "warning")
            
        except Exception as e:
            self._log_output(self.encrypt_output, f"Share creation failed: {str(e)}", "error")
            
    def _wrap_share_payload(self, share_bytes, index, total, threshold, packaged_cipher):
        """Wrap share payload with metadata"""
        SHARE_MAGIC = b"FKSS01"
        SHARE_VERSION = 1
        
        header = bytearray()
        header += SHARE_MAGIC
        header.append(SHARE_VERSION & 0xFF)
        header.append(index & 0xFF)
        header.append(total & 0xFF)
        header.append(threshold & 0xFF)
        header += len(share_bytes).to_bytes(4, 'big')
        header += len(packaged_cipher).to_bytes(4, 'big')
        return bytes(header) + share_bytes + packaged_cipher
        
    def _encryption_finished(self):
        """Called when encryption is finished"""
        self.encrypt_progress.stop_animation()
        self.encrypt_btn.configure(state="normal")
        self._update_status("Encryption completed", "success")
        
    # ═══════════════════════════════════════════════════════════════════════════
    # DECRYPTION LOGIC
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _add_image_file(self):
        """Add image file to decryption list"""
        file_types = [("Images", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("All files", "*.*")]
        file_path = filedialog.askopenfilename(title="Select stego image", filetypes=file_types)
        
        if file_path and file_path not in self.selected_images:
            self.selected_images.append(file_path)
            self._update_image_list()
            
    def _remove_all_images(self):
        """Remove all selected images"""
        self.selected_images = []
        self._update_image_list()
        
    def _update_image_list(self):
        """Update the image list display"""
        self.image_listbox.configure(state="normal")
        self.image_listbox.delete("1.0", "end")
        
        if not self.selected_images:
            self.image_listbox.insert("1.0", "No images selected.\n")
        else:
            for i, path in enumerate(self.selected_images, 1):
                self.image_listbox.insert("end", f"{i}. {os.path.basename(path)}\n")
                
        self.image_listbox.configure(state="disabled")
        
    def _start_decryption(self):
        """Start decryption process"""
        if len(self.selected_images) < 2:
            messagebox.showerror("Error", "Please select at least 2 stego images")
            return
            
        master_password = self.decrypt_master_entry.get().strip()
        if not master_password:
            messagebox.showerror("Error", "Please enter master password")
            return
            
        self.decrypt_output.delete("1.0", "end")
        self.decrypt_progress.start_animation()
        self.decrypt_btn.configure(state="disabled")
        self._update_status("Decrypting...", "info")
        
        thread = threading.Thread(
            target=self._decrypt_worker,
            args=(self.selected_images.copy(), master_password)
        )
        thread.daemon = True
        thread.start()
        
    def _decrypt_worker(self, image_paths, master_password):
        """Decryption worker thread"""
        try:
            self._log_output(self.decrypt_output, "Starting decryption process...", "info")
            self._log_output(self.decrypt_output, "━" * 50, "info")
            self._log_output(self.decrypt_output, f"Processing {len(image_paths)} stego images...", "info")
            
            parsed_shares = []
            for i, path in enumerate(image_paths, 1):
                self._log_output(self.decrypt_output, f"Extracting from: {os.path.basename(path)}", "info")
                payload = extract_data_from_image(path)
                meta = self._parse_share_payload(payload)
                parsed_shares.append(meta)
                self._log_output(self.decrypt_output, f"Found share {meta['index']}/{meta['total']}", "success")
                
            if len(parsed_shares) < 2:
                self._log_output(self.decrypt_output, "Not enough valid shares found", "error")
                return
                
            # Validate compatibility
            vs = {s['version'] for s in parsed_shares}
            totals = {s['total'] for s in parsed_shares}
            thresholds = {s['threshold'] for s in parsed_shares}
            pkg_hashes = {s['packaged_cipher'] for s in parsed_shares}
            
            if len(vs) != 1 or len(totals) != 1 or len(thresholds) != 1 or len(pkg_hashes) != 1:
                self._log_output(self.decrypt_output, "Selected shares do not match!", "error")
                return
                
            threshold = parsed_shares[0]['threshold']
            if len(parsed_shares) < threshold:
                self._log_output(self.decrypt_output, f"Need at least {threshold} shares", "error")
                return
                
            self._log_output(self.decrypt_output, "━" * 50, "info")
            self._log_output(self.decrypt_output, "Recovering ephemeral key...", "info")
            
            share_bytes_list = [s['share_bytes'] for s in parsed_shares[:threshold]]
            packaged_cipher = parsed_shares[0]['packaged_cipher']
            
            recovered_k2 = recover_bytes_from_shares(share_bytes_list)
            if len(recovered_k2) < 16:
                recovered_k2 = (b'\x00' * (16 - len(recovered_k2))) + recovered_k2
            elif len(recovered_k2) > 16:
                recovered_k2 = recovered_k2[-16:]
                
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            aes = AESGCM(recovered_k2)
            nonce2 = packaged_cipher[:12]
            ct_and_tag = packaged_cipher[12:]
            binary_blob = aes.decrypt(nonce2, ct_and_tag, None)
            
            salt = binary_blob[:16]
            nonce = binary_blob[16:28]
            ciphertext_with_tag = binary_blob[28:]
            
            self._log_output(self.decrypt_output, "Decrypting with master password...", "info")
            plaintext = decrypt_password_aes_gcm(salt, nonce, ciphertext_with_tag, master_password)
            
            self._log_output(self.decrypt_output, "━" * 50, "info")
            self._log_output(self.decrypt_output, "DECRYPTION SUCCESSFUL!", "success")
            self._log_output(self.decrypt_output, "━" * 50, "info")
            self._log_output(self.decrypt_output, f"🔑 Password: {plaintext}", "success")
            self._log_output(self.decrypt_output, f"Length: {len(plaintext)} characters", "info")
            
        except Exception as e:
            self._log_output(self.decrypt_output, f"Decryption failed: {str(e)}", "error")
        finally:
            self.after(0, self._decryption_finished)
            
    def _parse_share_payload(self, payload):
        """Parse wrapped share payload"""
        SHARE_MAGIC = b"FKSS01"
        SHARE_MAGIC_LEN = len(SHARE_MAGIC)
        
        min_header = SHARE_MAGIC_LEN + 1 + 1 + 1 + 1 + 4 + 4
        if len(payload) < min_header:
            raise ValueError("Share payload too short")
        if payload[:SHARE_MAGIC_LEN] != SHARE_MAGIC:
            raise ValueError("Share magic mismatch")
            
        pos = SHARE_MAGIC_LEN
        version = payload[pos]; pos += 1
        index = payload[pos]; pos += 1
        total = payload[pos]; pos += 1
        threshold = payload[pos]; pos += 1
        share_len = int.from_bytes(payload[pos:pos+4], 'big'); pos += 4
        packaged_cipher_len = int.from_bytes(payload[pos:pos+4], 'big'); pos += 4
        
        if pos + share_len + packaged_cipher_len > len(payload):
            raise ValueError("Declared sizes exceed payload size")
            
        share_bytes = payload[pos:pos+share_len]; pos += share_len
        packaged_cipher = payload[pos:pos+packaged_cipher_len]
        
        return {
            "version": version,
            "index": index,
            "total": total,
            "threshold": threshold,
            "share_len": share_len,
            "packaged_cipher_len": packaged_cipher_len,
            "share_bytes": share_bytes,
            "packaged_cipher": packaged_cipher
        }
        
    def _decryption_finished(self):
        """Called when decryption is finished"""
        self.decrypt_progress.stop_animation()
        self.decrypt_btn.configure(state="normal")
        self._update_status("Decryption completed", "success")
        
    # ═══════════════════════════════════════════════════════════════════════════
    # MANUAL DECRYPTION LOGIC
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _browse_manual_file(self):
        """Browse for manual decryption file"""
        file_path = filedialog.askopenfilename(
            title="Select .bin file for decryption",
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if file_path:
            self.manual_file_entry.delete(0, "end")
            self.manual_file_entry.insert(0, file_path)
            
    def _start_manual_decryption(self):
        """Start manual decryption"""
        file_path = self.manual_file_entry.get().strip()
        master_password = self.manual_master_entry.get().strip()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a .bin file")
            return
            
        if not master_password:
            messagebox.showerror("Error", "Please enter master password")
            return
            
        self.manual_output.delete("1.0", "end")
        
        try:
            self._log_output(self.manual_output, "Starting manual decryption...", "info")
            self._log_output(self.manual_output, "━" * 50, "info")
            self._log_output(self.manual_output, f"File: {os.path.basename(file_path)}", "info")
            
            with open(file_path, "rb") as f:
                binary_blob = f.read()
                
            self._log_output(self.manual_output, f"File size: {len(binary_blob)} bytes", "info")
                
            if len(binary_blob) < 28:
                self._log_output(self.manual_output, "File too small to be valid", "error")
                return
                
            salt = binary_blob[:16]
            nonce = binary_blob[16:28]
            ciphertext_with_tag = binary_blob[28:]
            
            self._log_output(self.manual_output, "Decrypting with master password...", "info")
            plaintext = decrypt_password_aes_gcm(salt, nonce, ciphertext_with_tag, master_password)
            
            self._log_output(self.manual_output, "━" * 50, "info")
            self._log_output(self.manual_output, "DECRYPTION SUCCESSFUL!", "success")
            self._log_output(self.manual_output, "━" * 50, "info")
            self._log_output(self.manual_output, f"🔑 Password: {plaintext}", "success")
            self._log_output(self.manual_output, f"Length: {len(plaintext)} characters", "info")
            
            self._update_status("Manual decryption completed", "success")
            
        except Exception as e:
            self._log_output(self.manual_output, f"Manual decryption failed: {str(e)}", "error")
            self._update_status("Manual decryption failed", "error")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point"""
    app = FracturedKeyApp()
    app.mainloop()

if __name__ == "__main__":
    main()
