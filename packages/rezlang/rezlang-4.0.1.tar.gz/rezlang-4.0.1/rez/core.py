import time, random
from .style import color_text
from .console import clear_console, loading_animation

def say(text):
    """Basic output"""
    print(color_text(text, "white"))

def shout(text):
    """Yell it with style"""
    print(color_text(text.upper() + "!!!", "red"))

def whisper(text):
    """Quiet message"""
    print(color_text(text.lower(), "cyan"))

def repeat(text, times=3, delay=0.3):
    """Repeat text multiple times"""
    for _ in range(times):
        print(color_text(text, "yellow"))
        time.sleep(delay)

def glitch(text, repeats=6):
    """Glitchy print animation"""
    from random import choice
    chars = list(text)
    for _ in range(repeats):
        glitched = "".join(choice(chars + ['@','#','%','&','!']) for _ in chars)
        print(color_text(glitched, "magenta"), end="\r")
        time.sleep(0.05)
    print(color_text(text, "green"))
