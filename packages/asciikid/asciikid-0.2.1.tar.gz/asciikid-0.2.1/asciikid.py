# Copyright (c) 2025 Philippe Proulx <eepp.ca>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import enum
import blessed
from typing import Any, Optional


class _Mode(enum.Enum):
    WRITE = enum.auto()
    DRAW = enum.auto()


class _Direction(enum.Enum):
    UP = enum.auto()
    DOWN = enum.auto()
    LEFT = enum.auto()
    RIGHT = enum.auto()


class _DrawPen(enum.Enum):
    SINGLE_LINE = enum.auto()
    DOUBLE_LINE = enum.auto()
    BLOCK = enum.auto()
    ERASER = enum.auto()
    MOVE = enum.auto()


class _App:
    _COLOR_NAMES = {
        1: 'red',
        2: 'green',
        3: 'yellow',
        4: 'blue',
        5: 'magenta',
        6: 'cyan',
    }

    _PRISM_COLORS = [
        (1, False),
        (1, True),
        (3, False),
        (3, True),
        (2, False),
        (2, True),
        (6, False),
        (6, True),
        (4, False),
        (4, True),
        (5, False),
        (5, True),
    ]

    _SINGLE_BOX_CHARS = {
        (_Direction.UP, _Direction.UP): '│',
        (_Direction.DOWN, _Direction.DOWN): '│',
        (_Direction.LEFT, _Direction.LEFT): '─',
        (_Direction.RIGHT, _Direction.RIGHT): '─',
        (_Direction.UP, _Direction.RIGHT): '┌',
        (_Direction.UP, _Direction.LEFT): '┐',
        (_Direction.DOWN, _Direction.RIGHT): '└',
        (_Direction.DOWN, _Direction.LEFT): '┘',
        (_Direction.LEFT, _Direction.UP): '└',
        (_Direction.LEFT, _Direction.DOWN): '┌',
        (_Direction.RIGHT, _Direction.UP): '┘',
        (_Direction.RIGHT, _Direction.DOWN): '┐',
    }

    _DOUBLE_BOX_CHARS = {
        (_Direction.UP, _Direction.UP): '║',
        (_Direction.DOWN, _Direction.DOWN): '║',
        (_Direction.LEFT, _Direction.LEFT): '═',
        (_Direction.RIGHT, _Direction.RIGHT): '═',
        (_Direction.UP, _Direction.RIGHT): '╔',
        (_Direction.UP, _Direction.LEFT): '╗',
        (_Direction.DOWN, _Direction.RIGHT): '╚',
        (_Direction.DOWN, _Direction.LEFT): '╝',
        (_Direction.LEFT, _Direction.UP): '╚',
        (_Direction.LEFT, _Direction.DOWN): '╔',
        (_Direction.RIGHT, _Direction.UP): '╝',
        (_Direction.RIGHT, _Direction.DOWN): '╗',
    }

    def __init__(self):
        self._term: blessed.Terminal = blessed.Terminal()
        self._cursor_x = 0
        self._cursor_y = 0
        self._mode: _Mode = _Mode.WRITE
        self._fg_color: Optional[int] = None
        self._bg_color: Optional[int] = None
        self._is_bright_fg = False
        self._is_bold = False
        self._is_fg_color_mode = True
        self._is_prism_mode = False
        self._prism_index = 0
        self._prev_direction: Optional[_Direction] = None
        self._draw_pen = _DrawPen.DOUBLE_LINE

    def _wrap_cursor_x(self):
        y_adjustment = 0

        if self._cursor_x < 0:
            self._cursor_x = self._term.width - 1
            y_adjustment = -1
        elif self._cursor_x >= self._term.width:
            self._cursor_x = 0
            y_adjustment = 1

        return y_adjustment

    def _wrap_cursor_y(self):
        if self._cursor_y < 0:
            self._cursor_y = self._term.height - 2
        elif self._cursor_y >= self._term.height - 1:
            self._cursor_y = 0

    def _set_color_from_prism_index(self):
        color, is_bright = self._PRISM_COLORS[self._prism_index]
        self._fg_color = color
        self._is_bright_fg = is_bright

    def _advance_prism_color(self):
        if self._is_prism_mode:
            self._prism_index = (self._prism_index + 1) % len(self._PRISM_COLORS)
            self._set_color_from_prism_index()

    def _print(self, text: str):
        print(text, end='', flush=True)

    def _print_at_cursor(self, text: str):
        self._print(f'{self._term.move(self._cursor_y, self._cursor_x)}{text}')  # type: ignore[arg-type]

    def _render_status_bar(self):
        status_y = self._term.height - 1
        status_text = ' '

        if self._mode == _Mode.WRITE:
            status_text += 'Write'
        elif self._draw_pen == _DrawPen.MOVE:
            status_text += 'Move'
        elif self._draw_pen == _DrawPen.SINGLE_LINE:
            status_text += 'Draw with ───'
        elif self._draw_pen == _DrawPen.DOUBLE_LINE:
            status_text += 'Draw with ═══'
        elif self._draw_pen == _DrawPen.BLOCK:
            status_text += 'Draw with ███'
        else:
            status_text += 'Erase'

        bar = f'{self._term.on_blue}{self._term.bold}{status_text}{self._term.normal}'
        bar += self._term.on_blue + ' ' * (self._term.width - len(status_text) - 3) + self._term.normal
        bar += f'{self._cur_fmt()}ABC{self._term.normal}'
        self._print(f'{self._term.move(status_y, 0)}{bar}')  # type: ignore[arg-type]
        self._print_at_cursor('')

    def _cur_fmt(self):
        fmt = self._term.normal

        if self._is_bold:
            fmt += self._term.bold

        if self._fg_color is not None:
            color_name = self._COLOR_NAMES[self._fg_color]

            if self._is_bright_fg:
                color_name = f'bright_{color_name}'

            fmt += getattr(self._term, color_name)

        if self._bg_color is not None:
            fmt += getattr(self._term, f'on_{self._COLOR_NAMES[self._bg_color]}')

        return fmt

    def _write_char(self, char: str):
        self._print_at_cursor(f'{self._cur_fmt()}{char}{self._term.normal}')
        self._advance_prism_color()
        self._cursor_x += 1
        self._cursor_y += self._wrap_cursor_x()
        self._wrap_cursor_y()
        self._print_at_cursor('')

    def _move_cursor(self, dx: int, dy: int):
        self._cursor_x += dx
        self._cursor_y += dy
        self._cursor_y += self._wrap_cursor_x()
        self._wrap_cursor_y()
        self._print_at_cursor('')

    def _handle_backspace(self):
        self._cursor_x -= 1
        y_adjustment = self._wrap_cursor_x()

        if self._cursor_y == 0 and y_adjustment < 0:
            self._cursor_x = 0
            self._cursor_y = 0
            self._print_at_cursor('')
            return

        self._cursor_y += y_adjustment
        self._print_at_cursor(' ')
        self._print_at_cursor('')

    def _simple_draw_char(self, is_vertical: bool):
        if self._draw_pen == _DrawPen.ERASER:
            return ' '
        elif self._draw_pen == _DrawPen.BLOCK:
            return '█'
        else:
            if is_vertical:
                return '│' if self._draw_pen == _DrawPen.SINGLE_LINE else '║'
            else:
                return '─' if self._draw_pen == _DrawPen.SINGLE_LINE else '═'

    def _draw_line(self, direction: _Direction):
        if self._draw_pen == _DrawPen.MOVE:
            pass
        elif self._draw_pen == _DrawPen.ERASER or self._draw_pen == _DrawPen.BLOCK:
            char = self._simple_draw_char(direction in (_Direction.UP, _Direction.DOWN))
            self._print_at_cursor(f'{self._cur_fmt()}{char}{self._term.normal}')
            self._advance_prism_color()
            self._prev_direction = None
        else:
            use_single = self._draw_pen == _DrawPen.SINGLE_LINE

            if self._prev_direction is None:
                is_vertical = direction in (_Direction.UP, _Direction.DOWN)
                char = self._simple_draw_char(is_vertical)
            else:
                box_chars = self._SINGLE_BOX_CHARS if use_single else self._DOUBLE_BOX_CHARS
                char = box_chars.get((self._prev_direction, direction), self._simple_draw_char(False))

            self._print_at_cursor(f'{self._cur_fmt()}{char}{self._term.normal}')
            self._advance_prism_color()
            self._prev_direction = direction

        if direction == _Direction.UP:
            self._cursor_y -= 1
            self._wrap_cursor_y()
        elif direction == _Direction.DOWN:
            self._cursor_y += 1
            self._wrap_cursor_y()
        elif direction == _Direction.LEFT:
            self._cursor_x -= 1

            if self._cursor_x < 0:
                self._cursor_x = self._term.width - 1
            elif self._cursor_x >= self._term.width:
                self._cursor_x = 0
        elif direction == _Direction.RIGHT:
            self._cursor_x += 1

            if self._cursor_x < 0:
                self._cursor_x = self._term.width - 1
            elif self._cursor_x >= self._term.width:
                self._cursor_x = 0

        self._print_at_cursor('')

    def _draw_full_vertical_line(self):
        char = self._simple_draw_char(is_vertical=True)

        for y in range(self._term.height - 1):
            self._print(f'{self._term.move(y, self._cursor_x)}{self._cur_fmt()}{char}{self._term.normal}')  # type: ignore[arg-type]

        self._advance_prism_color()
        self._print_at_cursor('')

    def _draw_full_horizontal_line(self):
        char = self._simple_draw_char(is_vertical=False)
        line = self._cur_fmt() + char * self._term.width + self._term.normal
        self._print(f'{self._term.move(self._cursor_y, 0)}{line}')  # type: ignore[arg-type]
        self._advance_prism_color()
        self._print_at_cursor('')

    def _draw_to_row(self, target_y: int):
        cur_x = self._cursor_x
        direction = _Direction.UP if target_y < self._cursor_y else _Direction.DOWN

        while self._cursor_y != target_y:
            self._draw_line(direction)

        self._draw_line(direction)
        self._cursor_x = cur_x
        self._cursor_y = target_y
        self._print_at_cursor('')

    def _draw_to_column(self, target_x: int):
        cur_y = self._cursor_y
        direction = _Direction.LEFT if target_x < self._cursor_x else _Direction.RIGHT

        while self._cursor_x != target_x:
            self._draw_line(direction)

        self._draw_line(direction)
        self._cursor_x = target_x
        self._cursor_y = cur_y
        self._print_at_cursor('')

    def _handle_write_key(self, key: Any):
        if key.name == 'KEY_BACKSPACE':
            self._handle_backspace()
        elif key.name == 'KEY_UP':
            self._move_cursor(0, -1)
        elif key.name == 'KEY_DOWN':
            self._move_cursor(0, 1)
        elif key.name == 'KEY_LEFT':
            self._move_cursor(-1, 0)
        elif key.name == 'KEY_RIGHT':
            self._move_cursor(1, 0)
        elif key.name == 'KEY_PGUP':
            self._cursor_y = 0
            self._print_at_cursor('')
        elif key.name == 'KEY_PGDOWN':
            self._cursor_y = self._term.height - 2
            self._print_at_cursor('')
        elif key.name == 'KEY_HOME':
            self._cursor_x = 0
            self._print_at_cursor('')
        elif key.name == 'KEY_END':
            self._cursor_x = self._term.width - 1
            self._print_at_cursor('')
        elif key.is_sequence:
            # ignore other special keys
            pass
        elif key and key.isprintable():
            # regular character
            self._write_char(key)

    def _handle_draw_key(self, key: Any):
        if key.name == 'KEY_UP':
            self._draw_line(_Direction.UP)
        elif key.name == 'KEY_DOWN':
            self._draw_line(_Direction.DOWN)
        elif key.name == 'KEY_LEFT':
            self._draw_line(_Direction.LEFT)
        elif key.name == 'KEY_RIGHT':
            self._draw_line(_Direction.RIGHT)
        elif key.lower() == 'h':
            self._draw_full_horizontal_line()
        elif key.lower() == 'v':
            self._draw_full_vertical_line()
        elif key.name == 'KEY_PGUP':
            self._draw_to_row(0)
        elif key.name == 'KEY_PGDOWN':
            self._draw_to_row(self._term.height - 2)
        elif key.name == 'KEY_HOME':
            self._draw_to_column(0)
        elif key.name == 'KEY_END':
            self._draw_to_column(self._term.width - 1)
        elif key == ' ':
            self._draw_pen = _DrawPen.MOVE
            self._render_status_bar()
        elif key == '-':
            self._draw_pen = _DrawPen.SINGLE_LINE
            self._render_status_bar()
        elif key == '=':
            self._draw_pen = _DrawPen.DOUBLE_LINE
            self._render_status_bar()
        elif key.lower() == 'b':
            self._draw_pen = _DrawPen.BLOCK
            self._render_status_bar()
        elif key.lower() == 'e':
            self._draw_pen = _DrawPen.ERASER
            self._render_status_bar()

    def _handle_key(self, key: Any):
        if key.name == 'KEY_ESCAPE':
            # quit
            return False

        if key.name == 'KEY_ENTER':
            # toggle mode
            self._mode = _Mode.DRAW if self._mode == _Mode.WRITE else _Mode.WRITE

            if self._mode == _Mode.DRAW:
                self._prev_direction = None

            self._render_status_bar()
            return True

        if key.name == 'KEY_F8':
            # toggle foreground/background color selection mode
            self._is_fg_color_mode = not self._is_fg_color_mode
            self._render_status_bar()
            return True

        if key.name == 'KEY_F9':
            # toggle bold
            self._is_bold = not self._is_bold
            self._render_status_bar()
            return True

        if key.name == 'KEY_F10':
            # toggle bright foreground colors
            self._is_bright_fg = not self._is_bright_fg
            self._render_status_bar()
            return True

        if key.name == 'KEY_F11':
            # toggle prism mode
            self._is_prism_mode = not self._is_prism_mode

            if self._is_prism_mode:
                self._prism_index = 0
                self._set_color_from_prism_index()

            self._render_status_bar()
            return True

        # color keys
        is_ctrl = key.name and 'CTRL' in key.name
        use_fg_mode = self._is_fg_color_mode if not is_ctrl else not self._is_fg_color_mode

        if key.name and 'F1' in key.name:
            if use_fg_mode:
                self._fg_color = None
            else:
                self._bg_color = None
        elif key.name and 'F2' in key.name:
            if use_fg_mode:
                self._fg_color = 1
            else:
                self._bg_color = 1
        elif key.name and 'F3' in key.name:
            if use_fg_mode:
                self._fg_color = 2
            else:
                self._bg_color = 2
        elif key.name and 'F4' in key.name:
            if use_fg_mode:
                self._fg_color = 3
            else:
                self._bg_color = 3
        elif key.name and 'F5' in key.name:
            if use_fg_mode:
                self._fg_color = 4
            else:
                self._bg_color = 4
        elif key.name and 'F6' in key.name:
            if use_fg_mode:
                self._fg_color = 5
            else:
                self._bg_color = 5
        elif key.name and 'F7' in key.name:
            if use_fg_mode:
                self._fg_color = 6
            else:
                self._bg_color = 6

        if self._mode == _Mode.WRITE:
            self._handle_write_key(key)
        elif self._mode == _Mode.DRAW:
            self._handle_draw_key(key)

        self._render_status_bar()
        return True

    def run(self):
        print(self._term.clear())
        self._print(self._term.move(0, 0))  # type: ignore[arg-type]

        try:
            with self._term.cbreak(), self._term.hidden_cursor():
                self._print(self._term.normal_cursor)
                self._render_status_bar()

                while True:
                    key = self._term.inkey(timeout=None)

                    if not key:
                        continue

                    if not self._handle_key(key):
                        break
        except KeyboardInterrupt:
            pass

        print(self._term.clear())
        print(self._term.move(0, 0))  # type: ignore[arg-type]


def main():
    app = _App()
    app.run()


if __name__ == '__main__':
    main()
