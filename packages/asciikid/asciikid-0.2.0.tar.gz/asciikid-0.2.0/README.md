# asciikid

_**asciikid**_ is a simple terminal-based ASCII art editor made for kids with two [modes](#modes): _write mode_ for text and _draw mode_ to draw lines.

## Install

Install from PyPI:

```
$ pipx install asciikid
```

## Launch

```
$ asciikid
```

## Modes

**asciikid** operates in one of two modes that you can switch between at any time by pressing **Enter**: [write mode](#write-mode) and [draw mode](#draw-mode).

In any mode, change the current colors with:

| Key | Action |
|-----|--------|
| **F1** | Default color |
| **F2** | Red |
| **F3** | Green |
| **F4** | Yellow |
| **F5** | Blue |
| **F6** | Magenta |
| **F7** | Cyan |
| **Ctrl**+**F1** | Default alternate color |
| **Ctrl**+**F2** | Red alternate |
| **Ctrl**+**F3** | Green alternate |
| **Ctrl**+**F4** | Yellow alternate |
| **Ctrl**+**F5** | Blue alternate |
| **Ctrl**+**F6** | Magenta alternate |
| **Ctrl**+**F7** | Cyan alternate |
| **F8** | Toggle alternate color is background vs. foreground color |
| **F9** | Toggle bold text |
| **F10** | Toggle bright foreground color |
| **F11** | Toggle prism mode |

**F8** exists so that you can choose a background color even when your terminal doesn't support **Ctrl**+**Fx**.

The bottom right corner shows a preview of the current colors.

Quit with **Escape**.

### Write mode

Press keys to type regular text.

Also:

| Key | Action |
|-----|--------|
| **Home** | Move cursor to the beginning of the row |
| **End** | Move cursor to the end of the row |
| **Page Up** | Move cursor to the beginning of the column |
| **Page Up** | Move cursor to the end of the column |

### Draw mode

Draw box-drawing lines and blocks using:

| Key | Action |
|-----|--------|
| **Arrow keys** | Draw the line in the direction pressed or move cursor if move mode is active |
| **-** | Switch to single-line style |
| **=** | Switch to double-line style |
| **B** | Switch to block style |
| **E** | Switch to eraser |
| **Space** | Toggle move mode (move cursor without drawing) |
| **Home** | Draw/move to the beginning of the row |
| **End** | Draw/move to the end of the row |
| **Page Up** | Draw/move to the beginning of the column |
| **Page Down** | Draw/move to the end of the column |
| **V** | Draw a full vertical line at current position |
| **H** | Draw a full horizontal line at current position |
