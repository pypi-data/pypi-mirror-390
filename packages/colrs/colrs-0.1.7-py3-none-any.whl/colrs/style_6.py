# style_6.py: Clock Spinner
import time
import sys
import itertools

def run(duration, text, color):
    """Displays a spinning clock-hand animation."""
    clock_chars = ['🕛', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚']
    spinner = itertools.cycle(clock_chars)
    start_time = time.time()

    while (time.time() - start_time) < duration:
        print(f"<{color}>{text} {next(spinner)}</>", end='\r', flush=True)
        time.sleep(0.1)