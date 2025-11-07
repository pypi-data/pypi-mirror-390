import time, sys
from .style import color_text

def typewrite(text, speed=0.05, color="white"):
    """Prints text like a typewriter"""
    for ch in text:
        sys.stdout.write(color_text(ch, color))
        sys.stdout.flush()
        time.sleep(speed)
    print()

def wave(text, color1="cyan", color2="magenta", delay=0.1):
    """Alternating color wave"""
    toggle = True
    for ch in text:
        c = color1 if toggle else color2
        sys.stdout.write(color_text(ch, c))
        sys.stdout.flush()
        toggle = not toggle
        time.sleep(delay)
    print()

def sparkle(text):
    """Prints text with sparkle animation"""
    import random
    spark = ["✨", "⭐", "🌟", "💫"]
    for ch in text:
        sys.stdout.write(color_text(ch, "yellow") + random.choice(spark))
        sys.stdout.flush()
        time.sleep(0.1)
    print()
