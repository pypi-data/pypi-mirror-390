# style_8.py: Arrow Flow
import time
import sys
import itertools

def run(duration, text, color):
    """Displays arrows moving to the right."""
    arrows = itertools.cycle(['>  ', '>> ', '>>>', ' >>', '  >'])
    start_time = time.time()

    while (time.time() - start_time) < duration:
        print(f"<{color}>{text} {next(arrows)}</>", end='\r', flush=True)
        time.sleep(0.15)