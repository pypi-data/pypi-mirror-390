# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for M5Stack Tab5
 - port: espressif
 - board_id: m5stack_tab5
 - NVM size: 8192
 - Included modules: _asyncio, _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogbufio, analogio, array, atexit, audiobusio, audiocore, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, espidf, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, hashlib, i2cdisplaybus, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, keypad_demux, keypad_demux.DemuxKeyMatrix, locale, lvfontio, math, memorymap, microcontroller, mipidsi, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, ps2io, pulseio, pwmio, rainbowio, random, re, rotaryio, rtc, sdcardio, sdioio, select, sharpdisplay, socketpool.socketpool.AF_INET6, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, vectorio, warnings, watchdog, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
G2: microcontroller.Pin  # GPIO2
G3: microcontroller.Pin  # GPIO3
G4: microcontroller.Pin  # GPIO4
G6: microcontroller.Pin  # GPIO6
G7: microcontroller.Pin  # GPIO7
G16: microcontroller.Pin  # GPIO16
G17: microcontroller.Pin  # GPIO17
G35: microcontroller.Pin  # GPIO35
G45: microcontroller.Pin  # GPIO45
G47: microcontroller.Pin  # GPIO47
G48: microcontroller.Pin  # GPIO48
G51: microcontroller.Pin  # GPIO51
G52: microcontroller.Pin  # GPIO52
G5: microcontroller.Pin  # GPIO5
SCK: microcontroller.Pin  # GPIO5
G18: microcontroller.Pin  # GPIO18
MOSI: microcontroller.Pin  # GPIO18
G19: microcontroller.Pin  # GPIO19
MISO: microcontroller.Pin  # GPIO19
G37: microcontroller.Pin  # GPIO37
TX: microcontroller.Pin  # GPIO37
TXD0: microcontroller.Pin  # GPIO37
G38: microcontroller.Pin  # GPIO38
RX: microcontroller.Pin  # GPIO38
RXD0: microcontroller.Pin  # GPIO38
G31: microcontroller.Pin  # GPIO31
SDA: microcontroller.Pin  # GPIO31
G32: microcontroller.Pin  # GPIO32
SCL: microcontroller.Pin  # GPIO32
G23: microcontroller.Pin  # GPIO23
TP_INT: microcontroller.Pin  # GPIO23
G22: microcontroller.Pin  # GPIO22
LCD_BL: microcontroller.Pin  # GPIO22
G26: microcontroller.Pin  # GPIO26
I2S_DSDIN: microcontroller.Pin  # GPIO26
G27: microcontroller.Pin  # GPIO27
I2S_SCLK: microcontroller.Pin  # GPIO27
G28: microcontroller.Pin  # GPIO28
I2S_ASDOUT: microcontroller.Pin  # GPIO28
G29: microcontroller.Pin  # GPIO29
I2S_LRCK: microcontroller.Pin  # GPIO29
G30: microcontroller.Pin  # GPIO30
I2S_MCLK: microcontroller.Pin  # GPIO30
G36: microcontroller.Pin  # GPIO36
CAM_MCLK: microcontroller.Pin  # GPIO36
G39: microcontroller.Pin  # GPIO39
SD_DAT0: microcontroller.Pin  # GPIO39
SD_MISO: microcontroller.Pin  # GPIO39
G40: microcontroller.Pin  # GPIO40
SD_DAT1: microcontroller.Pin  # GPIO40
G41: microcontroller.Pin  # GPIO41
SD_DAT2: microcontroller.Pin  # GPIO41
G42: microcontroller.Pin  # GPIO42
SD_DAT3: microcontroller.Pin  # GPIO42
SD_CS: microcontroller.Pin  # GPIO42
G43: microcontroller.Pin  # GPIO43
SD_CLK: microcontroller.Pin  # GPIO43
SD_SCK: microcontroller.Pin  # GPIO43
G44: microcontroller.Pin  # GPIO44
SD_CMD: microcontroller.Pin  # GPIO44
SD_MOSI: microcontroller.Pin  # GPIO44
G20: microcontroller.Pin  # GPIO20
RS485_TX: microcontroller.Pin  # GPIO20
G21: microcontroller.Pin  # GPIO21
RS485_RX: microcontroller.Pin  # GPIO21
G34: microcontroller.Pin  # GPIO34
RS485_DIR: microcontroller.Pin  # GPIO34
G53: microcontroller.Pin  # GPIO53
PORTA_Y: microcontroller.Pin  # GPIO53
G54: microcontroller.Pin  # GPIO54
PORTA_W: microcontroller.Pin  # GPIO54
G8: microcontroller.Pin  # GPIO8
C6_SDIO2_D3: microcontroller.Pin  # GPIO8
G9: microcontroller.Pin  # GPIO9
C6_SDIO2_D2: microcontroller.Pin  # GPIO9
G10: microcontroller.Pin  # GPIO10
C6_SDIO2_D1: microcontroller.Pin  # GPIO10
G11: microcontroller.Pin  # GPIO11
C6_SDIO2_D0: microcontroller.Pin  # GPIO11
G12: microcontroller.Pin  # GPIO12
C6_SDIO2_CK: microcontroller.Pin  # GPIO12
G13: microcontroller.Pin  # GPIO13
C6_SDIO2_CMD: microcontroller.Pin  # GPIO13
G14: microcontroller.Pin  # GPIO14
C6_IO2: microcontroller.Pin  # GPIO14
G15: microcontroller.Pin  # GPIO15
C6_RESET: microcontroller.Pin  # GPIO15


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
