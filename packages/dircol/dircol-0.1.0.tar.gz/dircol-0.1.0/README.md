# dircol

`dircol` provides two small helpers, `dirc` and `dirfc`, that display the output of Python's built-in `dir()` function in a cleaner, more readable layout.

This is useful when exploring unfamiliar objects or browsing large libraries in the Python REPL.

---

## Features

| Function | Output | Color Coding | Purpose |
|---------|--------|--------------|---------|
| `dirc(obj)` | Columns | No | Simple, compact directory listing |
| `dirfc(obj)` | Columns | Yes | Highlights whether attributes are modules, classes, methods, functions, or built-ins |

`dirfc` uses **Rich** to color-code attribute names according to their type:
- **Blue** = Module  
- **Green** = Class  
- **Yellow** = Method  
- **Magenta** = Function  
- **Gray** = Built-in  
- **White** = Everything else  

---

## Example

```python
from dircol import dirc, dirfc

dirc(str)   # simple column view
dirfc(str)  # fancy, color-coded view
```

---

## Install

```bash 
pip install dircol
```
