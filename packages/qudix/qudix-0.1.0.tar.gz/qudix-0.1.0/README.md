# Qudix

Qudix is a mouse-aware text editor for the terminal. It combines a top toolbar with clickable buttons for cut, copy, paste, and delete with a central editing surface that supports cursor-based text selection similar to modern GUI editors.

## Features
- Mouse-enabled toolbar buttons for common editing actions.
- Line and intra-line text selection using the mouse.
- Keyboard shortcuts for standard editing operations.
- Lightweight terminal UI built with [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit).

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
qudix
```

While the editor is running you can also pass a file path to load or save content:

```bash
qudix path/to/file.txt
```

## Controls
- Toolbar buttons and all editing actions respond to mouse clicks.
- `F5` / `F6` / `F7` / `F8` trigger cut, copy, paste, and delete (mirroring the toolbar buttons).
- `Ctrl+S` saves back to the provided file path (if launched with a path).
- `Ctrl+X` exits the editor; `Esc` returns focus to the text area if another widget is focused.
- Click and drag with the mouse to select text within a line or across lines.

## Development

The project follows a standard `src/` layout. The main entry point lives at `src/qudix/app.py`.

## License

This project is dual-licensed under Apache-2.0 OR MIT.
You may use it under the terms of either license at your option.
See `LICENSE`, `LICENSE-APACHE`, and `LICENSE-MIT`.
