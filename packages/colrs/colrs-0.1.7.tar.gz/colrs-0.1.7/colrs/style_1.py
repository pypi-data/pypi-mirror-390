# style_1.py: Progress Bar
import time
import sys

def run(duration, text, color):
    """Displays a dynamic, multi-colored progress bar."""
    length = 40
    start_time = time.time()
    
    while (time.time() - start_time) < duration:
        elapsed = time.time() - start_time
        progress = elapsed / duration
        percent = progress * 100
        
        filled_len = int(length * progress)
        filled = '█' * filled_len
        empty = '─' * (length - filled_len)
        
        bar_color = "green" if percent > 80 else "yellow" if percent > 40 else "red"
        
        print(f"<white>{text}</> <{bar_color}>[{filled}{empty}]</> {percent:.0f}%", end='\r', flush=True)
        time.sleep(0.05)