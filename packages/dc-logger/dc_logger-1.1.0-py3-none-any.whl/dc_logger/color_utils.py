"""ANSI color codes for console output"""

import re
from typing import Optional

# ANSI color codes
COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
    # Aliases for convenience
    "gray": "\033[90m",
    "grey": "\033[90m",
}

# ANSI reset code
RESET = "\033[0m"

# ANSI style codes
STYLES = {
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",
    "underline": "\033[4m",
}


def colorize(text: str, color: Optional[str] = None) -> str:
    """
    Apply ANSI color code to text.

    Args:
        text: The text to colorize
        color: Color name (e.g., 'red', 'green', 'blue', 'yellow', 'cyan', 'magenta')
               Can also include styles like 'bold_red', 'dim_blue', etc.

    Returns:
        Colorized text with ANSI codes, or original text if color is None or invalid

    Examples:
        >>> colorize("Error", "red")
        '\\033[31mError\\033[0m'
        >>> colorize("Success", "green")
        '\\033[32mSuccess\\033[0m'
        >>> colorize("Warning", "yellow")
        '\\033[33mWarning\\033[0m'
    """
    if not color:
        return text

    color_code = ""
    style_code = ""

    # Check if color includes a style (e.g., "bold_red", "dim_blue")
    if "_" in color:
        parts = color.split("_", 1)
        style = parts[0]
        color_name = parts[1]

        if style in STYLES:
            style_code = STYLES[style]

        if color_name in COLORS:
            color_code = COLORS[color_name]
    else:
        # Just a color, no style
        if color in COLORS:
            color_code = COLORS[color]

    # If we found a valid color or style, apply it
    if color_code or style_code:
        return f"{style_code}{color_code}{text}{RESET}"

    # Invalid color, return original text
    return text


def strip_ansi_codes(text: str) -> str:
    """
    Remove ANSI color codes from text.

    Args:
        text: Text that may contain ANSI codes

    Returns:
        Text with all ANSI codes removed
    """
    # Pattern to match all ANSI escape sequences
    # Matches sequences like \033[0m, \033[31m, \033[1;32m, etc.
    ansi_escape = re.compile(r'\033\[[0-9;]*[a-zA-Z]')
    return ansi_escape.sub('', text)
