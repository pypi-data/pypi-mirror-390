# style_10.py: Pac-Man
import time
import sys
import itertools

def run(duration, text, color):
    """Displays a Pac-Man style animation."""
    pacman = itertools.cycle(['<', 'V', '>', '^'])
    dots = " · " * 5
    start_time = time.time()

    while (time.time() - start_time) < duration:
        print(f"<yellow>{next(pacman)}</> <white>{text}</> <{color}>{dots}</>", end='\r', flush=True)
        time.sleep(0.2)