# style_3.py: Bouncing Dots
import time
import sys

def run(duration, text, color):
    """Displays a bouncing dots animation."""
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        for i in range(4):
            dots = '.' * i + ' ' * (3 - i)
            print(f"<{color}>{text}{dots}</>", end='\r', flush=True)
            time.sleep(0.15)