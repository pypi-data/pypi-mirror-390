# colorara/colorara/magic.py

import builtins
from .core import _get_colored_input_prompt, _process_text_for_printing

_original_print = builtins.print
_original_input = builtins.input

def _magic_print(*args, **kwargs):
    """
    A patched version of print that handles color arguments, including
    inline color tags.
    """
    # Extract our custom color arguments, removing them from kwargs
    color = kwargs.pop("color", None)
    bg_color = kwargs.pop("bg_color", None)
    
    text = " ".join(map(str, args))
    processed_text = _process_text_for_printing(text, color, bg_color)
    
    _original_print(processed_text, **kwargs)

def _magic_input(prompt: str = "", **kwargs) -> str:
    """
    A patched version of input that handles color arguments for the prompt
    and for the user's typed input.
    """
    # Extract our custom color arguments from kwargs
    color = kwargs.get("color")
    bg_color = kwargs.get("bg_color")
    inp_color = kwargs.get("inp_color")
    color_rules = kwargs.get("color_rules")
    
    # We need to call our cinput function which contains the logic for color_rules
    from .core import cinput
    return cinput(prompt, color=color, bg_color=bg_color, inp_color=inp_color, color_rules=color_rules)

def act():
    """
    Activates the patching of the built-in print and input functions.
    
    This allows you to use 'color' and 'bg_color' arguments directly in print()
    and input() without calling a special function.
    
    Warning: This modifies built-in functions and may conflict with other
    libraries that also modify them. Use with caution.
    """
    if builtins.print is _magic_print:
        return

    builtins.print = _magic_print
    builtins.input = _magic_input

def unact():
    """
    Deactivates the patching and restores the original built-in functions.
    """
    if builtins.print is not _magic_print:
        return
        
    builtins.print = _original_print
    builtins.input = _original_input
