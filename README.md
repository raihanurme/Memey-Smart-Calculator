# Memey Smart Calculator

A portable Windows desktop calculator built with Python and CustomTkinter. It provides live expression previews, precise `Decimal` arithmetic, smart percentage expressions, scientific functions, conversion utilities, and JSON-backed settings/history.

## Run from source

Use Python 3.11 or newer, then install the dependencies and launch:

```powershell
py -m pip install -r requirements.txt
py main.py
```

The calculation engine has no `eval()` use; it parses expressions into an AST and evaluates only approved numeric operations and functions.

## Tests

```powershell
py -m pytest
```

## Build a portable Windows executable

On Windows, with the requirements installed:

```powershell
.\build.bat
```

The single-file executable is written to `dist\MemeySmartCalculator.exe`. `settings.json` and `history.json` are created beside the executable when the app runs. The output executable is architecture- and platform-specific; build it on Windows for Windows users.

## Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `0–9`, operators, parentheses, `.` or `,` | Enter an expression |
| `Enter` | Calculate and save to history |
| `Backspace` | Delete one character |
| `Esc` | Clear the expression |
| `Ctrl+C` | Copy the displayed result |
| `Ctrl+H` | Toggle history on compact windows |
| `Ctrl+T` | Cycle system, light, and dark themes |
| `Ctrl+M` | Toggle standard/scientific mode |
