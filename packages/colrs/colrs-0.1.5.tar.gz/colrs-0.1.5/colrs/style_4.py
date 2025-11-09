# style_4.py: Dual-Side Progress Bar
import time
import sys

def run(duration, text, color):
    """Displays a progress bar that fills from both ends."""
    length = 40
    start_time = time.time()

    while (time.time() - start_time) < duration:
        progress = (time.time() - start_time) / duration
        filled_len = int(length * progress / 2)
        
        filled = '█' * filled_len
        empty = ' ' * (length - 2 * filled_len)
        
        sys.stdout.write(f'\r<{color}>{text} [{filled}{empty}{filled}]</>')
        sys.stdout.flush()
        time.sleep(0.05)