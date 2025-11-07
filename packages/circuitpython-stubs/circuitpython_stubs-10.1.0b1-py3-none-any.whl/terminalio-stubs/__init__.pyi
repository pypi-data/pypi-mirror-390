"""Displays text in a TileGrid

The `terminalio` module contains classes to display a character stream on a display. The built
in font is available as ``terminalio.FONT``.

.. note:: This module does not give access to the
    `REPL <https://learn.adafruit.com/welcome-to-circuitpython/interacting-with-the-serial-console>`_.

"""

from __future__ import annotations

from typing import Optional

import displayio
import fontio
from circuitpython_typing import ReadableBuffer

FONT: fontio.BuiltinFont
"""The built in font"""

class Terminal:
    """Terminal manages tile indices and cursor position based on VT100 commands. The ``font`` should be
    a `fontio.BuiltinFont` and the ``scroll_area`` TileGrid's bitmap should match the font's bitmap.

    Display a character stream with a TileGrid

    ASCII control:

    * ``\\r`` - Move cursor to column 1
    * ``\\n`` - Move cursor down a row
    * ``\\b`` - Move cursor left one if possible

    OSC control sequences:

    * ``ESC ] 0; <s> ESC \\`` - Set title bar to <s>
    * ``ESC ] ####; <s> ESC \\`` - Ignored

    VT100 control sequences:

    * ``ESC [ K`` - Clear the remainder of the line
    * ``ESC [ 0 K`` - Clear the remainder of the line
    * ``ESC [ 1 K`` - Clear start of the line to cursor
    * ``ESC [ 2 K`` - Clear the entire line
    * ``ESC [ #### D`` - Move the cursor to the left by ####
    * ``ESC [ 2 J`` - Erase the entire display
    * ``ESC [ nnnn ; mmmm H`` - Move the cursor to mmmm, nnnn.
    * ``ESC [ H`` - Move the cursor to 0,0.
    * ``ESC M`` - Move the cursor up one line, scrolling if necessary.
    * ``ESC D`` - Move the cursor down one line, scrolling if necessary.
    * ``ESC [ r`` - Disable scrolling range (set to fullscreen).
    * ``ESC [ nnnn ; mmmm r`` - Set scrolling range between rows nnnn and mmmm.
    * ``ESC [ ## m`` - Set the terminal display attributes.
    * ``ESC [ ## ; ## m`` - Set the terminal display attributes.
    * ``ESC [ ## ; ## ; ## m`` - Set the terminal display attributes.

    Supported Display attributes:

    +--------+------------+------------+
    | Color  | Foreground | Background |
    +========+============+============+
    | Reset  | 0          | 0          |
    +--------+------------+------------+
    | Black  | 30         | 40         |
    +--------+------------+------------+
    | Red    | 31         | 41         |
    +--------+------------+------------+
    | Green  | 32         | 42         |
    +--------+------------+------------+
    | Yellow | 33         | 43         |
    +--------+------------+------------+
    | Blue   | 34         | 44         |
    +--------+------------+------------+
    | Magenta| 35         | 45         |
    +--------+------------+------------+
    | Cyan   | 36         | 46         |
    +--------+------------+------------+
    | White  | 37         | 47         |
    +--------+------------+------------+

    Example Usage:

    .. code-block:: python

        import time
        import displayio
        import supervisor
        from displayio import Group, TileGrid
        from terminalio import FONT, Terminal

        main_group = Group()
        display = supervisor.runtime.display
        font_bb = FONT.get_bounding_box()
        screen_size = (display.width // font_bb[0], display.height // font_bb[1])
        char_size = FONT.get_bounding_box()

        palette = displayio.Palette(2)
        palette[0] = 0x000000
        palette[1] = 0xffffff

        tilegrid = TileGrid(
            bitmap=FONT.bitmap, width=screen_size[0], height=screen_size[1],
            tile_width=char_size[0], tile_height=char_size[1], pixel_shader=palette)

        terminal = Terminal(tilegrid, FONT)

        main_group.append(tilegrid)
        display.root_group = main_group

        message = "Hello World\\n"
        terminal.write(message)

        print(terminal.cursor_x, terminal.cursor_y)
        move_cursor = chr(27) + "[10;10H"
        terminal.write(f"Moving the cursor\\n{move_cursor} To here")

        cursor_home = chr(27) + f"[{screen_size[1]};0H"
        terminal.write(cursor_home)
        i = 1
        while True:
            terminal.write(f"Writing again {i}\\n")
            i = i + 1
            time.sleep(1)


    """

    def __init__(
        self,
        scroll_area: displayio.TileGrid,
        font: fontio.BuiltinFont,
        *,
        status_bar: Optional[displayio.TileGrid] = None,
    ) -> None: ...
    def write(self, buf: ReadableBuffer) -> Optional[int]:
        """Write the buffer of bytes to the bus.

        :return: the number of bytes written
        :rtype: int or None"""
        ...
    cursor_x: int
    """The x position of the cursor."""

    cursor_y: int
    """The y position of the cursor."""
