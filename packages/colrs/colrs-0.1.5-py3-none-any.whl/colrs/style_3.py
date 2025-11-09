# style_3.py: Bouncing Dots
import time
import sys

def run(duration, text, color):
    """Displays a bouncing dots animation."""
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        for i in range(4):
            dots = '.' * i + ' ' * (3 - i)
            sys.stdout.write(f'\r<{color}>{text}{dots}</>')
            sys.stdout.flush()
            time.sleep(0.15)