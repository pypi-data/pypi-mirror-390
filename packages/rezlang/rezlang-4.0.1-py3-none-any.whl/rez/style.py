colors = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m",
}

def color_text(text, color="white"):
    return f"{colors.get(color, colors['white'])}{text}{colors['reset']}"

def bold(text):
    return f"\033[1m{text}\033[0m"

def italic(text):
    return f"\033[3m{text}\033[0m"

def underline(text):
    return f"\033[4m{text}\033[0m"
