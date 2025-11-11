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
| **F1** | Default foreground color |
| **F2** | Red foreground |
| **F3** | Green foreground |
| **F4** | Yellow foreground |
| **F5** | Blue foreground |
| **F6** | Magenta foreground |
| **F7** | Cyan foreground |
| **Ctrl**+**F1** | Default background color |
| **Ctrl**+**F2** | Red background |
| **Ctrl**+**F3** | Green background |
| **Ctrl**+**F4** | Yellow background |
| **Ctrl**+**F5** | Blue background |
| **Ctrl**+**F6** | Magenta background |
| **Ctrl**+**F7** | Cyan background |
| **F9** | Toggle bold text |
| **F10** | Toggle bright foreground color |

The bottom right corner shows a preview of the current colors.

Quit with **Escape**.

### Write mode

Press keys to type regular text.

### Draw mode

Draw box-drawing lines and blocks using:

| Key | Action |
|-----|--------|
| **Arrow keys** | Draw the line in the direction pressed or move cursor if move mode is active |
| **-** | Switch to single-line style |
| **=** | Switch to double-line style |
| **B** | Switch to block style |
| **E** | Switch to eraser |
| **Space** | Switch to move mode (move cursor without drawing) |
| **Page Up** | Draw a full vertical line at current position |
| **Page Down** | Draw a full horizontal line at current position |
