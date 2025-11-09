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
        print(f"<{color}>{text} {char}</>", end='\r', flush=True)
        time.sleep(0.1)