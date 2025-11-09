# style_5.py: Scanner Effect
import time
import sys

def run(duration, text, color):
    """Displays a 'Knight Rider' style scanner."""
    length = 20
    start_time = time.time()

    while (time.time() - start_time) < duration:
        # Ping-pong effect for the scanner position
        pos = int((time.time() * 10) % (length * 2 - 2))
        if pos >= length:
            pos = (length * 2 - 2) - pos

        bar = ['─'] * length
        bar[pos] = '█'
        
        print(f"<{color}>{text} [{''.join(bar)}]</>", end='\r', flush=True)
        time.sleep(0.03)