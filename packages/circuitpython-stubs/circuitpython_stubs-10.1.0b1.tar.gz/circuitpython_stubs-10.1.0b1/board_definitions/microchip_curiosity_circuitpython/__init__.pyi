# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Microchip Curiosity CircuitPython
 - port: atmel-samd
 - board_id: microchip_curiosity_circuitpython
 - NVM size: 256
 - Included modules: _asyncio, _bleio, _bleio (HCI co-processor), _eve, _pixelmap, adafruit_bus_device, adafruit_pixelbuf, aesio, alarm, analogio, array, atexit, audiobusio, audiocore, audioio, audiomixer, audiomp3, binascii, bitbangio, bitmapfilter, bitmaptools, board, builtins, builtins.pow3, busdisplay, busio, busio.SPI, busio.UART, canio, codeop, collections, countio, digitalio, displayio, epaperdisplay, errno, floppyio, fontio, fourwire, framebufferio, frequencyio, getpass, gifio, i2cdisplaybus, i2ctarget, io, jpegio, json, keypad, keypad.KeyMatrix, keypad.Keys, keypad.ShiftRegisterKeys, locale, math, microcontroller, msgpack, neopixel_write, nvm, onewireio, os, os.getenv, paralleldisplaybus, ps2io, pulseio, pwmio, rainbowio, random, re, rgbmatrix, rotaryio, rtc, samd, sdcardio, select, sharpdisplay, storage, struct, supervisor, synthio, sys, terminalio, tilepalettemapper, time, touchio, traceback, ulab, usb_cdc, usb_hid, usb_midi, vectorio, warnings, zlib
 - Frozen libraries: 
"""

# Imports
import busio
import microcontroller


# Board Info:
board_id: str


# Pins:
D0: microcontroller.Pin  # PA15
D1: microcontroller.Pin  # PA20
D2: microcontroller.Pin  # PA21
D3: microcontroller.Pin  # PA27
D4: microcontroller.Pin  # PB14
D5: microcontroller.Pin  # PB15
D6: microcontroller.Pin  # PB16
LED: microcontroller.Pin  # PB23
D13: microcontroller.Pin  # PB23
NEOPIXEL: microcontroller.Pin  # PB22
VREF: microcontroller.Pin  # PA03
A0: microcontroller.Pin  # PB04
A1: microcontroller.Pin  # PB05
A2: microcontroller.Pin  # PB06
A3: microcontroller.Pin  # PB07
A4: microcontroller.Pin  # PB08
A5: microcontroller.Pin  # PB09
DAC: microcontroller.Pin  # PA02
CAP1: microcontroller.Pin  # PB09
LCD_CS: microcontroller.Pin  # PA07
LCD_MOSI: microcontroller.Pin  # PA04
LCD_SCK: microcontroller.Pin  # PA05
LCD_BL: microcontroller.Pin  # PA06
SCL: microcontroller.Pin  # PB30
SDA: microcontroller.Pin  # PB31
BLE_TX: microcontroller.Pin  # PA12
BLE_RX: microcontroller.Pin  # PA13
BLE_CLR: microcontroller.Pin  # PA14
SD_MOSI: microcontroller.Pin  # PA16
SD_MISO: microcontroller.Pin  # PA18
SD_SCK: microcontroller.Pin  # PA17
SD_CS: microcontroller.Pin  # PA19
MISO: microcontroller.Pin  # PB00
D8: microcontroller.Pin  # PB00
IMU_INT: microcontroller.Pin  # PB00
CS: microcontroller.Pin  # PB01
D9: microcontroller.Pin  # PB01
IMU_ADDR: microcontroller.Pin  # PB01
MOSI: microcontroller.Pin  # PB02
D10: microcontroller.Pin  # PB02
SCK: microcontroller.Pin  # PB03
D11: microcontroller.Pin  # PB03
DEBUG_TX: microcontroller.Pin  # PA22
DEBUG_RX: microcontroller.Pin  # PA23
CAN_RX: microcontroller.Pin  # PB13
CAN_TX: microcontroller.Pin  # PB12
CAN_STDBY: microcontroller.Pin  # PB17
D7: microcontroller.Pin  # PB17


# Members:
def I2C() -> busio.I2C:
    """Returns the `busio.I2C` object for the board's designated I2C bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.I2C`.
    """

def UART() -> busio.UART:
    """Returns the `busio.UART` object for the board's designated UART bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.UART`.
    """

def SPI() -> busio.SPI:
    """Returns the `busio.SPI` object for the board's designated SPI bus(es).
    The object created is a singleton, and uses the default parameter values for `busio.SPI`.
    """


# Unmapped:
#   none
