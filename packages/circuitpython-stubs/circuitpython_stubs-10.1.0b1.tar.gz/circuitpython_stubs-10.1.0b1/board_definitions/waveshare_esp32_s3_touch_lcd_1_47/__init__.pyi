# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Waveshare ESP32-S3 Touch LCD 1.47
 - port: espressif
 - board_id: waveshare_esp32_s3_touch_lcd_1_47
 - NVM size: 8192
 - Included modules: _asyncio, _bleio, _bleio (native), _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espcamera, espidf, espnow, espulp, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, ipaddress, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, lvfontio, math, max3421e, mdns, memorymap, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, qrio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool, socketpool.socketpool.AF_INET6, ssl, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb, usb_cdc, usb_hid, usb_midi, vectorio, warnings, watchdog, wifi, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import displayio
import microcontroller


# Board Info:
board_id: str


# Pins:
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
GPIO1: microcontroller.Pin  # GPIO1
GPIO2: microcontroller.Pin  # GPIO2
GPIO3: microcontroller.Pin  # GPIO3
GPIO4: microcontroller.Pin  # GPIO4
GPIO5: microcontroller.Pin  # GPIO5
GPIO6: microcontroller.Pin  # GPIO6
GPIO7: microcontroller.Pin  # GPIO7
GPIO8: microcontroller.Pin  # GPIO8
GPIO9: microcontroller.Pin  # GPIO9
GPIO10: microcontroller.Pin  # GPIO10
GPIO11: microcontroller.Pin  # GPIO11
SCL: microcontroller.Pin  # GPIO41
SDA: microcontroller.Pin  # GPIO42
SD_CMD: microcontroller.Pin  # GPIO15
SD_CLK: microcontroller.Pin  # GPIO16
SD_D0: microcontroller.Pin  # GPIO17
SD_D1: microcontroller.Pin  # GPIO18
SD_D2: microcontroller.Pin  # GPIO13
SD_D3: microcontroller.Pin  # GPIO14
TOUCH_RST: microcontroller.Pin  # GPIO47
TOUCH_IRQ: microcontroller.Pin  # GPIO48


# Members:
def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
