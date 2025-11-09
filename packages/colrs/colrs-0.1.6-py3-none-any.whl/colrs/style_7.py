# style_7.py: Gradient Wave
import time
import sys

def run(duration, text, color):
    """Displays a wave of characters with changing intensity."""
    chars = " ▂▃▄▅▆▇█▇▆▅▄▃▂ "
    start_time = time.time()

    while (time.time() - start_time) < duration:
        offset = int(time.time() * 10) % len(chars)
        wave = "".join([chars[(i + offset) % len(chars)] for i in range(15)])
        
        sys.stdout.write(f'\r<{color}>{text} {wave}</>')
        sys.stdout.flush()
        time.sleep(0.05)