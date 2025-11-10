"""Main module for colortext package."""

# ANSI color codes
COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m",
}


def colorize(text, color):
    """
    Return text wrapped in ANSI color codes.
    
    Args:
        text (str): The text to colorize
        color (str): The color name (red, green, yellow, blue, magenta, cyan, white)
    
    Returns:
        str: Colorized text string
    """
    if color not in COLORS:
        raise ValueError(f"Unknown color: {color}. Available colors: {', '.join(COLORS.keys())}")
    
    return f"{COLORS[color]}{text}{COLORS['reset']}"


def print_color(text, color):
    """
    Print text in the specified color.
    
    Args:
        text (str): The text to print
        color (str): The color name (red, green, yellow, blue, magenta, cyan, white)
    """
    print(colorize(text, color))
