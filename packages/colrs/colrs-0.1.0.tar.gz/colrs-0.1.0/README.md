# colorara 🎨

A simple, elegant, and easy-to-use Python library to add color to your terminal text and backgrounds.

## Features

- **Simple API:** Color your text with zero hassle.
- **Cross-Platform:** Works on Windows, macOS, and Linux thanks to `colorama`.
- **Inline Tag Coloring:** Color specific words within a string using simple tags like `<green>word</>`.
- **Colored User Input:** Control the color of the user's typed text in `input()` prompts.
- **"Magic":** An optional mode to make the built-in `print()` and `input()` color-aware.
- **Lightweight:** Has only one dependency (`colorama`) for cross-platform support.

## Installation

First, navigate to the `colorara` project directory. Then, install it using `pip`:

```bash
pip install .
```
After installation, you can import it in any Python script on your system.

## Usage

`colorara` is designed for flexibility and ease of use.

---

### `cprint()` and Inline Coloring

The `cprint()` function is your main tool for printing. It supports both coloring the entire line and coloring specific parts of a string using tags.

**Syntax:** `<color_name>text</>` or `<text_color,bg_color>text</>`

```python
from colorara import cprint

# Overall coloring (like before)
cprint("This entire line is green.", color="green")

# --- Inline Tag Coloring ---
# Color a specific word
cprint("Status: <green>OK</>")

# Use multiple colors in one line
cprint("Results: <green>SUCCESS</>, Warnings: <yellow>3</>, Errors: <red>0</>")

# You can also color backgrounds
cprint("System State: <white,bg_green>ONLINE</>") 
cprint("Alert: <black,bg_yellow>CHECK CONFIG</>")

# If you provide a `color` argument with tags, it is ignored
cprint("The tag <green>always</> wins.", color="red") # "always" will be green
```

### `cinput()` and Colored User Input

Use `cinput()` to get user input with a colored prompt and even colored user-typed text.

It accepts a new argument `inp_color`. If you provide it, the user's typing will be in that color. If you don't, the user's typing will have the same color as the prompt.

```python
from colorara import cinput

# The user's typed text will be cyan, just like the prompt
name = cinput("Enter your name: ", color="cyan")
print(f"Hello, {name}!")

# The prompt will be yellow, but the user's typing will be blue
age = cinput("Enter your age: ", color="yellow", inp_color="blue")
print(f"You are {age} years old.")
```

---

### Magic ✨

This mode is for maximum convenience. By calling `magic()` once, `colorara` patches the built-in `print()` and `input()` functions, giving them all the powers of `cprint` and `cinput`.

**⚠️ Warning:** This modifies Python's built-in functions and might cause conflicts if another library tries to do the same. Use it with caution.

```python
from colorara import magic, revert

# Activate magic
magic()

# The built-in print now understands tags!
print("Magic <magenta>print</> supports tags too!")
print("Status: <green>OK</>, Mode: <cyan,bg_black>MAGIC</>")

# The magic input also supports `inp_color`
food = input("Favorite food (prompt is red, typing is green)? ", color="red", inp_color="green")
print(f"You like {food}!")

# You can revert the changes if needed
revert()

# This print will be normal again
print("Back to normal.")
```

## Available Colors

You can use the following color names for both `color` and `bg_color`:

- `black`
- `red`
- `green`
- `yellow`
- `blue`
- `magenta`
- `cyan`
- `white`
