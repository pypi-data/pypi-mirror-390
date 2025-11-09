# colorara 🎨

A simple, elegant, and easy-to-use Python library to add color to your terminal text and backgrounds.

## Features

- **Simple API:** Color your text with zero hassle.
- **Cross-Platform:** Works on Windows, macOS, and Linux thanks to `colorama`.
- **Inline Tag Coloring:** Color specific words within a string using simple tags like `<green>word</>`.
- **Colored User Input:** Control the color of the user's typed text in `input()` prompts.
- **Built-in Patching:** An optional mode to make the built-in `print()` and `input()` color-aware.
- **Lightweight:** Has only one dependency (`colorama`) for cross-platform support.

## Installation

First, navigate to the `colrs` project directory. Then, install it using `pip`:

```bash
pip install .
```
After installation, you can import it in any Python script on your system.

## Usage

`colrs` is designed for flexibility and ease of use.

---

### `cprint()` and Inline Coloring

The `cprint()` function is your main tool for printing. It supports both coloring the entire line and coloring specific parts of a string using tags.

**Syntax:** `<color_name>text</>` or `<text_color,bg_color>text</>`

```python
from colrs import cprint

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
```

### `cinput()` and Colored User Input

Use `cinput()` to get user input with a colored prompt and even colored user-typed text.

It accepts a new argument `inp_color`. If you provide it, the user's typing will be in that color. If you don't, the user's typing will have the same color as the prompt.

```python
from colrs import cinput

# The user's typed text will be cyan, just like the prompt
name = cinput("Enter your name: ", color="cyan")
print(f"Hello, {name}!")

# The prompt will be yellow, but the user's typing will be blue
age = cinput("Enter your age: ", color="yellow", inp_color="blue")
print(f"You are {age} years old.")
```

---

### Patching Built-ins (`act`/`unact`)

For maximum convenience, you can patch the built-in `print()` and `input()` functions. This makes them color-aware globally in your script.

**⚠️ Warning:** This modifies Python's built-in functions and might cause conflicts if another library tries to do the same. Use it with caution.

```python
from colrs import act, unact, cprint

# Activate the patch
act()

# The built-in print now understands tags!
print("Patch is <green>active</>!")
print("Status: <green>OK</>, Mode: <cyan,bg_black>PATCHED</>")

# The patched input also supports `inp_color`
food = input("Favorite food (prompt is red, typing is green)? ", color="red", inp_color="green")
print(f"You like {food}!")

# Deactivate the patch to restore normal behavior
unact()

# This print will be normal again
print("Patch is deactivated. This is a normal print.")
cprint("<green>But cprint still works!</>")
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
