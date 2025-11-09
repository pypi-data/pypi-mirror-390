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
        sys.stdout.write(f'\r<yellow>{next(pacman)}</> <white>{text}</> <{color}>{dots}</>')
        sys.stdout.flush()
        time.sleep(0.2)