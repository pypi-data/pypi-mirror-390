"""
Beautiful UI components for Glassbox CLI
Codex-style beautiful terminal interface
"""

import sys
import os
from typing import Optional, List, Tuple
from datetime import datetime

# ANSI color codes for beautiful output
class Colors:
    """ANSI color codes for terminal output"""
    # Reset
    RESET = '\033[0m'
    
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Semantic colors (Codex-style: subtle, professional)
    SUCCESS = GREEN  # Muted green, not bright
    ERROR = RED  # Muted red, not bright
    WARNING = YELLOW  # Muted yellow, not bright
    INFO = CYAN  # Subtle cyan
    HIGHLIGHT = MAGENTA  # Subtle magenta
    PRIMARY = CYAN  # Primary color (subtle)
    SECONDARY = DIM  # Secondary text


def colorize(text: str, color: str) -> str:
    """Apply color to text"""
    if not sys.stdout.isatty():
        return text  # No colors if not a TTY
    return f"{color}{text}{Colors.RESET}"


def print_header(text: str, emoji: str = ""):
    """Print a Codex-style header (minimal, professional)"""
    width = 80
    print()
    # Codex uses single-line borders, subtle colors
    print(colorize("─" * width, Colors.DIM))
    if emoji:
        print(colorize(f"{emoji}  {text}", Colors.BOLD + Colors.PRIMARY))
    else:
        print(colorize(text, Colors.BOLD + Colors.PRIMARY))
    print(colorize("─" * width, Colors.DIM))
    print()


def print_section(text: str, emoji: str = ""):
    """Print a Codex-style section header (minimal)"""
    print()
    if emoji:
        print(colorize(f"{emoji}  {text}", Colors.BOLD + Colors.PRIMARY))
    else:
        print(colorize(text, Colors.BOLD + Colors.PRIMARY))
    # Codex doesn't always use dividers - only when needed


def print_success(text: str, emoji: str = ""):
    """Print Codex-style success message (minimal emoji)"""
    if emoji:
        print(colorize(f"{emoji}  {text}", Colors.SUCCESS))
    else:
        print(colorize(text, Colors.SUCCESS))


def print_error(text: str, emoji: str = "❌"):
    """Print error message"""
    print(colorize(f"{emoji}  {text}", Colors.ERROR))


def print_warning(text: str, emoji: str = "⚠️"):
    """Print warning message"""
    print(colorize(f"{emoji}  {text}", Colors.WARNING))


def print_info(text: str, emoji: str = "💡"):
    """Print info message"""
    print(colorize(f"{emoji}  {text}", Colors.INFO))


def print_step(step_num: int, text: str, status: Optional[str] = None):
    """Print a step in a guided workflow"""
    step_text = f"  {step_num}. {text}"
    if status == "done":
        print(colorize(step_text, Colors.SUCCESS))
    elif status == "current":
        print(colorize(step_text, Colors.BOLD + Colors.BRIGHT_CYAN))
    else:
        print(colorize(step_text, Colors.DIM))


def print_box(content: List[str], title: Optional[str] = None, color: str = Colors.PRIMARY):
    """Print content in a Codex-style box (single-line borders, subtle)"""
    if not content:
        return
    
    # Calculate width
    max_width = max(len(line) for line in content)
    if title:
        max_width = max(max_width, len(title) + 2)
    max_width = min(max_width, 76)  # Leave some margin
    
    # Codex uses single-line borders, subtle colors
    border_color = Colors.DIM  # Borders are dim
    text_color = color  # Text uses primary color
    
    # Top border
    top = "┌" + "─" * (max_width + 2) + "┐"
    print(colorize(top, border_color))
    
    # Title
    if title:
        title_line = f"│ {title:<{max_width}} │"
        print(colorize(title_line, border_color))
        print(colorize("├" + "─" * (max_width + 2) + "┤", border_color))
    
    # Content
    for line in content:
        padded = f"│ {line:<{max_width}} │"
        # Content text in primary color, borders dim
        parts = padded.split('│')
        if len(parts) >= 3:
            print(colorize("│", border_color) + colorize(parts[1], text_color) + colorize("│", border_color))
        else:
            print(colorize(padded, border_color))
    
    # Bottom border
    bottom = "└" + "─" * (max_width + 2) + "┘"
    print(colorize(bottom, border_color))


def strip_ansi(text: str) -> str:
    """Strip ANSI color codes from text for width calculation."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', str(text))


def print_table(headers: List[str], rows: List[List[str]], title: Optional[str] = None):
    """Print a Codex-style table (subtle borders, clean)"""
    if not rows:
        return
    
    # Calculate column widths (strip ANSI codes for accurate width)
    num_cols = len(headers)
    col_widths = [len(strip_ansi(h)) for h in headers]
    
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                # Strip ANSI codes to get actual display width
                col_widths[i] = max(col_widths[i], len(strip_ansi(str(cell))))
    
    # Add padding
    col_widths = [w + 2 for w in col_widths]
    total_width = sum(col_widths) + num_cols + 1
    
    # Title (Codex style: minimal)
    if title:
        print()
        print(colorize(title, Colors.BOLD + Colors.PRIMARY))
        print()
    
    # Codex uses subtle borders (dim color)
    border_color = Colors.DIM
    header_color = Colors.BOLD + Colors.PRIMARY
    text_color = Colors.RESET
    
    # Top border
    top = "┌" + "".join("─" * w + "┬" for w in col_widths[:-1]) + "─" * col_widths[-1] + "┐"
    print(colorize(top, border_color))
    
    # Headers
    header_row = colorize("│", border_color)
    for i, header in enumerate(headers):
        # Calculate padding needed (account for ANSI codes if header is colored)
        header_str = str(header)
        header_display_width = len(strip_ansi(header_str))
        padding_needed = col_widths[i] - 1 - header_display_width
        header_row += colorize(f" {header_str}{' ' * padding_needed}", header_color) + colorize("│", border_color)
    print(header_row)
    
    # Separator
    sep = "├" + "".join("─" * w + "┼" for w in col_widths[:-1]) + "─" * col_widths[-1] + "┤"
    print(colorize(sep, border_color))
    
    # Rows
    for row in rows:
        row_text = colorize("│", border_color)
        for i, cell in enumerate(row):
            if i < len(col_widths):
                # Calculate padding needed (account for ANSI codes in cell)
                cell_str = str(cell)
                cell_display_width = len(strip_ansi(cell_str))
                padding_needed = col_widths[i] - 1 - cell_display_width
                row_text += f" {cell_str}{' ' * padding_needed}" + colorize("│", border_color)
        print(row_text)
    
    # Bottom border
    bottom = "└" + "".join("─" * w + "┴" for w in col_widths[:-1]) + "─" * col_widths[-1] + "┘"
    print(colorize(bottom, border_color))
    print()


def print_progress_bar(current: int, total: int, width: int = 40, label: str = ""):
    """Print a progress bar"""
    if total == 0:
        return
    
    percent = current / total
    filled = int(width * percent)
    bar = "█" * filled + "░" * (width - filled)
    percent_text = f"{percent * 100:.1f}%"
    
    if label:
        print(f"\r{label} [{bar}] {percent_text}", end="", flush=True)
    else:
        print(f"\r[{bar}] {percent_text}", end="", flush=True)
    
    if current >= total:
        print()  # New line when complete


def print_code_block(code: str, language: str = "python"):
    """Print code in a beautiful block"""
    lines = code.strip().split('\n')
    max_width = max(len(line) for line in lines) if lines else 0
    max_width = min(max_width, 76)
    
    print(colorize("┌" + "─" * (max_width + 2) + "┐", Colors.BRIGHT_BLUE))
    print(colorize(f"│ {language:<{max_width}} │", Colors.BRIGHT_BLUE))
    print(colorize("├" + "─" * (max_width + 2) + "┤", Colors.BRIGHT_BLUE))
    
    for line in lines:
        padded = f"│ {line:<{max_width}} │"
        print(colorize(padded, Colors.BRIGHT_BLUE))
    
    print(colorize("└" + "─" * (max_width + 2) + "┘", Colors.BRIGHT_BLUE))
    print()


def print_key_value(key: str, value: str, indent: int = 0):
    """Print key-value pair beautifully"""
    indent_str = " " * indent
    key_text = colorize(f"{key}:", Colors.BOLD)
    print(f"{indent_str}{key_text} {value}")


def print_list(items: List[str], emoji: str = "•", indent: int = 0):
    """Print a beautiful list"""
    indent_str = " " * indent
    for item in items:
        print(f"{indent_str}{emoji}  {item}")


def print_divider(char: str = "─", color: str = Colors.DIM):
    """Print a divider line"""
    print(colorize(char * 80, color))


def clear_line():
    """Clear the current line"""
    print("\r" + " " * 80 + "\r", end="")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """Ask a yes/no question interactively"""
    default_text = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_text}]: ").strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes', '1', 'true']


def ask_input(prompt: str, default: Optional[str] = None) -> str:
    """Ask for input with optional default"""
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "
    
    response = input(prompt_text).strip()
    return response if response else (default or "")


def print_welcome():
    """Print Codex-style welcome (minimal, professional)"""
    print()
    # Codex uses minimal welcome - just a clean header
    print(colorize("Glassbox", Colors.BOLD + Colors.PRIMARY))
    print(colorize("See Your AI Costs in Real-Time", Colors.SECONDARY))
    print()


def print_footer(text: str = ""):
    """Print Codex-style footer (minimal or none)"""
    # Codex doesn't always show footers - only when needed
    if text:
        print()
        print(colorize(text, Colors.SECONDARY))
        print()


def format_number(num: float, decimals: int = 2) -> str:
    """Format number beautifully"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.{decimals}f}M"
    elif num >= 1_000:
        return f"{num/1_000:.{decimals}f}K"
    else:
        return f"{num:.{decimals}f}"


def format_currency(amount: float) -> str:
    """Format currency beautifully"""
    if amount >= 1:
        return f"${amount:,.2f}"
    elif amount >= 0.01:
        return f"${amount:.4f}"
    else:
        return f"${amount:.6f}"


def format_duration(ms: float) -> str:
    """Format duration beautifully"""
    if ms >= 1000:
        return f"{ms/1000:.2f}s"
    else:
        return f"{ms:.0f}ms"


def format_timestamp(timestamp: str) -> str:
    """Format timestamp beautifully"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%H:%M:%S')
    except:
        return timestamp[:19] if timestamp else '--:--:--'

