import os, sys, time

def clear_console():
    """Clear the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_animation(text="Loading", duration=3):
    """Loading animation"""
    frames = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    while time.time() < end_time:
        for frame in frames:
            sys.stdout.write(f"\r{text} {frame}")
            sys.stdout.flush()
            time.sleep(0.1)
    print("\r" + " " * (len(text) + 3) + "\r", end="")
