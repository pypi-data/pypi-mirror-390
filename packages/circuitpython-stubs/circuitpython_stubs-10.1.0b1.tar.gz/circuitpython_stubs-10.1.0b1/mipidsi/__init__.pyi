"""Low-level routines for interacting with MIPI DSI"""

from __future__ import annotations

from typing import Optional

import microcontroller
from circuitpython_typing import ReadableBuffer

class Bus:
    def __init__(
        self,
        *,
        frequency: int = 500_000_000,
        num_lanes: int = 2,
    ) -> None:
        """Create a MIPI DSI Bus object.

        This creates a DSI bus interface. The specific pins used are determined by the board.
        DSI supports 1-4 data lanes.

        :param int frequency: the high speed clock frequency in Hz (default 500 MHz)
        :param int num_lanes: the number of data lanes to use (default 2, range 1-4)
        """

    def deinit(self) -> None:
        """Free the resources (pins, timers, etc.) associated with this
        `mipidsi.Bus` instance.  After deinitialization, no further operations
        may be performed."""
        ...

class Display:
    def __init__(
        self,
        bus: Bus,
        init_sequence: ReadableBuffer,
        *,
        width: int,
        height: int,
        hsync_pulse_width: int,
        hsync_back_porch: int,
        hsync_front_porch: int,
        vsync_pulse_width: int,
        vsync_back_porch: int,
        vsync_front_porch: int,
        pixel_clock_frequency: int,
        virtual_channel: int = 0,
        rotation: int = 0,
        color_depth: int = 16,
        backlight_pin: Optional[microcontroller.Pin] = None,
        brightness: float = 1.0,
        native_frames_per_second: int = 60,
        backlight_on_high: bool = True,
    ) -> None:
        """Create a MIPI DSI Display object connected to the given bus.

        This allocates a framebuffer and configures the DSI display to use the
        specified virtual channel for communication.

        The framebuffer pixel format varies depending on color_depth:

        * 16 - Each two bytes is a pixel in RGB565 format.
        * 24 - Each three bytes is a pixel in RGB888 format.

        A Display is often used in conjunction with a
        `framebufferio.FramebufferDisplay`.

        :param Bus bus: the DSI bus to use
        :param ~circuitpython_typing.ReadableBuffer init_sequence: Byte-packed initialization sequence for the display
        :param int width: the width of the framebuffer in pixels
        :param int height: the height of the framebuffer in pixels
        :param int hsync_pulse_width: horizontal sync pulse width in pixel clocks
        :param int hsync_back_porch: horizontal back porch in pixel clocks
        :param int hsync_front_porch: horizontal front porch in pixel clocks
        :param int vsync_pulse_width: vertical sync pulse width in lines
        :param int vsync_back_porch: vertical back porch in lines
        :param int vsync_front_porch: vertical front porch in lines
        :param int pixel_clock_frequency: pixel clock frequency in Hz
        :param int virtual_channel: the DSI virtual channel (0-3)
        :param int rotation: the rotation of the display in degrees clockwise (0, 90, 180, 270)
        :param int color_depth: the color depth of the framebuffer in bits (16 or 24)
        :param microcontroller.Pin backlight_pin: Pin connected to the display's backlight
        :param float brightness: Initial display brightness (0.0 to 1.0)
        :param int native_frames_per_second: Number of display refreshes per second
        :param bool backlight_on_high: If True, pulling the backlight pin high turns the backlight on
        """

    def deinit(self) -> None:
        """Free the resources (pins, timers, etc.) associated with this
        `mipidsi.Display` instance.  After deinitialization, no further operations
        may be performed."""
        ...
    width: int
    """The width of the framebuffer, in pixels."""
    height: int
    """The height of the framebuffer, in pixels."""

    color_depth: int
    """The color depth of the framebuffer."""
