# colors.py
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except Exception:
    COLORS_AVAILABLE = False

class Colors:
    SALT = Fore.GREEN if COLORS_AVAILABLE else ""
    NONCE = Fore.BLUE if COLORS_AVAILABLE else ""
    CIPHERTEXT = Fore.RED if COLORS_AVAILABLE else ""
    AUTH_TAG = Fore.MAGENTA if COLORS_AVAILABLE else ""
    SUCCESS = Fore.GREEN if COLORS_AVAILABLE else ""
    ERROR = Fore.RED if COLORS_AVAILABLE else ""
    INFO = Fore.CYAN if COLORS_AVAILABLE else ""
    WARNING = Fore.YELLOW if COLORS_AVAILABLE else ""
    RESULT = Fore.LIGHTGREEN_EX if COLORS_AVAILABLE else ""
    BOLD = Style.BRIGHT if COLORS_AVAILABLE else ""
    RESET = Style.RESET_ALL if COLORS_AVAILABLE else ""

def print_colored(text: str, color: str = "", style: str = ""):
    """Print text with specified color and style (no-op if colorama missing)."""
    if COLORS_AVAILABLE:
        print(f"{style}{color}{text}{Colors.RESET}")
    else:
        print(text)

