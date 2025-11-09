# colorara/colrs/animations.py

import time
import importlib
import sys

def loading(style=1, duration=3, text="Loading...", color="yellow", bf_text=None, af_text="Done!", end_color="green"):
    """
    Displays a loading animation in the terminal.

    This function dynamically imports and runs a loader style. It ensures that
    the `colrs` patching is active during the animation and deactivates it
    afterwards to avoid side effects.

    :param style: The style of the loader to display (e.g., 1, 2, ...).
    :param duration: The total duration of the animation in seconds.
    :param text: The text to display alongside the animation.
    :param color: The primary color of the animation and text.
    :param bf_text: Text to print before the animation starts.
    :param af_text: Text to display upon completion.
    :param end_color: The color of the completion text.
    """
    try:
        # Print the "before" text if it exists
        if bf_text:
            print(bf_text)

        # Dynamically import the chosen style module
        loader_module = importlib.import_module(f'.loaders.style_{style}', package='colrs') # type: ignore
        
        # Run the animation from the imported module
        loader_module.run(duration, text, color)
        
        # Print completion message
        # Use \r to overwrite the loader line and clear it with spaces
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        if af_text:
            print(f"<{end_color}>{af_text}</>")

    except ImportError:
        print(f"<red>Error: Loader style '{style}' not found.</red>")
    except Exception as e:
        # Clean up the line in case of an error during animation
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        print(f"<red>An error occurred during animation: {e}</red>")