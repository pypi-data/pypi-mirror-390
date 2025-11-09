# style_9.py: Random Blocks
import time
import sys
import random

def run(duration, text, color):
    """Fills a bar with random blocks."""
    length = 25
    blocks = [' '] * length
    start_time = time.time()

    while ' ' in blocks:
        pos = random.randint(0, length - 1)
        blocks[pos] = '█'
        sys.stdout.write(f'\r<{color}>{text} [{"".join(blocks)}]</>')
        sys.stdout.flush()
        time.sleep(duration / (length * 1.5)) # Slow down filling