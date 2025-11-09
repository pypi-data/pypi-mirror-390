# style_2.py: Spinner
import time
import sys
import itertools

def run(duration, text, color):
    """Displays a simple spinning line animation."""
    spinner = itertools.cycle(['|', '/', '—', '\\'])
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        char = next(spinner)
        sys.stdout.write(f'\r<{color}>{text} {char}</>')
        sys.stdout.flush()
        time.sleep(0.1)