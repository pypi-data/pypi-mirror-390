# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for ESP32-P4-Function-EV
 - port: espressif
 - board_id: espressif_esp32p4_function_ev
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
I2C_SDA: microcontroller.Pin  # GPIO7
IO7: microcontroller.Pin  # GPIO7
I2C_SCL: microcontroller.Pin  # GPIO8
IO8: microcontroller.Pin  # GPIO8
IO23: microcontroller.Pin  # GPIO23
TX: microcontroller.Pin  # GPIO37
IO37: microcontroller.Pin  # GPIO37
RX: microcontroller.Pin  # GPIO38
IO38: microcontroller.Pin  # GPIO38
IO21: microcontroller.Pin  # GPIO21
IO22: microcontroller.Pin  # GPIO22
IO20: microcontroller.Pin  # GPIO20
C6_WAKEUP: microcontroller.Pin  # GPIO6
IO6: microcontroller.Pin  # GPIO6
IO5: microcontroller.Pin  # GPIO5
IO4: microcontroller.Pin  # GPIO4
IO3: microcontroller.Pin  # GPIO3
IO2: microcontroller.Pin  # GPIO2
IO36: microcontroller.Pin  # GPIO36
IO32: microcontroller.Pin  # GPIO32
IO24: microcontroller.Pin  # GPIO24
IO25: microcontroller.Pin  # GPIO25
IO33: microcontroller.Pin  # GPIO33
IO26: microcontroller.Pin  # GPIO26
C6_EN: microcontroller.Pin  # GPIO54
IO54: microcontroller.Pin  # GPIO54
IO48: microcontroller.Pin  # GPIO48
PA_CTRL: microcontroller.Pin  # GPIO53
IO53: microcontroller.Pin  # GPIO53
IO46: microcontroller.Pin  # GPIO46
IO47: microcontroller.Pin  # GPIO47
IO27: microcontroller.Pin  # GPIO27
I2S_DSDIN: microcontroller.Pin  # GPIO9
I2S_LRCK: microcontroller.Pin  # GPIO10
I2S_ASDOUT: microcontroller.Pin  # GPIO11
I2S_SCLK: microcontroller.Pin  # GPIO12
I2S_MCLK: microcontroller.Pin  # GPIO13
RMII_RXDV: microcontroller.Pin  # GPIO28
RMII_RXD0: microcontroller.Pin  # GPIO29
RMII_RXD1: microcontroller.Pin  # GPIO30
MDC: microcontroller.Pin  # GPIO31
RMII_TXD0: microcontroller.Pin  # GPIO34
RMII_TXD1: microcontroller.Pin  # GPIO35
RMII_TXEN: microcontroller.Pin  # GPIO49
RMII_CLK: microcontroller.Pin  # GPIO50
PHY_RSTN: microcontroller.Pin  # GPIO51
MDIO: microcontroller.Pin  # GPIO52
SD_DATA0: microcontroller.Pin  # GPIO39
SD_DATA1: microcontroller.Pin  # GPIO40
SD_DATA2: microcontroller.Pin  # GPIO41
SD_DATA3: microcontroller.Pin  # GPIO42
SD_CLK: microcontroller.Pin  # GPIO43
SD_CMD: microcontroller.Pin  # GPIO44
SD_PWRN: microcontroller.Pin  # GPIO45


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """


# Unmapped:
#   none
