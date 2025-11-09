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
        sys.stdout.write(f'\r<{color}>{text} {next(spinner)}</>')
        sys.stdout.flush()
        time.sleep(0.1)