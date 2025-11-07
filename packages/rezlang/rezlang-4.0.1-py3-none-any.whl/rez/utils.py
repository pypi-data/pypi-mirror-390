import random
from datetime import datetime

def random_quote():
    quotes = [
        "Code like a legend."
    ]
    return random.choice(quotes)

def current_time():
    return datetime.now().strftime("%H:%M:%S")

def random_color():
    return random.choice(["red", "green", "blue", "yellow", "magenta", "cyan"])
