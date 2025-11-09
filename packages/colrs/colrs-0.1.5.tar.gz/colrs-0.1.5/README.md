# colrs 🎨

**A radically simple Python library for coloring your terminal output.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`colrs` takes a different approach to terminal coloring. Instead of wrapping your print statements in special functions, you activate it once, and your standard `print` and `input` functions become color-aware.

---

## Philosophy

The core idea is **absolute simplicity**. No new function names to remember for printing. Just activate the magic and write your code as you normally would, but with added superpowers.

-   **Activate:** `act()`
-   **Use `print` and `input` normally:** Add colors with tags or keyword arguments.
-   **Deactivate:** `unact()`
-   **Show Animations:** `loading()`

This is the core public API, designed for simplicity and power.

## Installation

To install the library:
```bash
pip install colrs
```

## How to Use

The usage is designed to be as intuitive as possible. You import `act` and `unact`, and wrap the code you want to be color-aware.

### Basic Example

```python
from colrs import act, unact

# This print is normal
print("This is default terminal text.")

# Activate the color patching
act()

# Now, print() and input() are super-powered!
print("This is a <green>green text</> using inline tags.")
print("This is red.", color="red")
print("This is blue on a yellow background.", color="blue", bg_color="yellow")

name = input("What's your name? ", color="cyan", inp_color="magenta")
print(f"Hello, {name}!")

# It's good practice to deactivate when you're done
unact()

print("And we're back to normal.")
```

### Using `print()` with `act()`

Once `act()` is called, `print()` can accept two new keyword arguments: `color` and `bg_color`.

More powerfully, you can use inline tags for fine-grained control.

```python
act()

# Simple tags
print("<red>This will be red.</red>") # The closing tag is optional

# Nested tags
print("<yellow>This is yellow with <blue>blue text</blue> inside.</yellow>")

# Background colors
print("<white,bg_red> White text on a red background. </>") # </> resets all

unact()
```

### Using `input()` with `act()`

The patched `input()` can color three things separately:
1.  The prompt text (`color` and `bg_color` arguments, or tags).
2.  The text the user types (`inp_color` argument).

```python
act()

# The prompt will be yellow, and the user's typing will be cyan
username = input("Enter username: ", color="yellow", inp_color="cyan")

# You can also use tags in the prompt
password = input("<red>Enter password:</red> ", inp_color="red")

unact()
```

## Why `colrs`?

If you want a coloring library that "just works" in the background without forcing you to change your coding habits, `colrs` is for you. It's designed for scripts and applications where you want to enable colors globally with minimal code changes.

## License

This project is licensed under the MIT License.