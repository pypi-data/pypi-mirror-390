# SPDX-FileCopyrightText: 2024 Justin Myers
#
# SPDX-License-Identifier: MIT
"""
Board stub for Waveshare ESP32-S3 Touch LCD 2.8
 - port: espressif
 - board_id: waveshare_esp32_s3_touch_lcd_2_8
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
LCD_SCK: microcontroller.Pin  # GPIO40
LCD_MOSI: microcontroller.Pin  # GPIO45
LCD_MISO: microcontroller.Pin  # GPIO46
LCD_CS: microcontroller.Pin  # GPIO42
LCD_DC: microcontroller.Pin  # GPIO41
LCD_RST: microcontroller.Pin  # GPIO39
LCD_BL: microcontroller.Pin  # GPIO5
SD_SCK: microcontroller.Pin  # GPIO14
SD_MOSI: microcontroller.Pin  # GPIO17
SD_MISO: microcontroller.Pin  # GPIO16
SD_CS: microcontroller.Pin  # GPIO21
TP_SCL: microcontroller.Pin  # GPIO3
TP_SDA: microcontroller.Pin  # GPIO1
TP_RST: microcontroller.Pin  # GPIO2
TP_INT: microcontroller.Pin  # GPIO4
IMU_SCL: microcontroller.Pin  # GPIO10
IMU_SDA: microcontroller.Pin  # GPIO11
IMU_INT2: microcontroller.Pin  # GPIO12
IMU_INT1: microcontroller.Pin  # GPIO13
I2S_BCK: microcontroller.Pin  # GPIO48
I2S_DIN: microcontroller.Pin  # GPIO47
I2S_LRCK: microcontroller.Pin  # GPIO38
BAT_CONTROL: microcontroller.Pin  # GPIO7
BAT_PWR: microcontroller.Pin  # GPIO6
KEY_BAT: microcontroller.Pin  # GPIO6
BAT_ADC: microcontroller.Pin  # GPIO8
TX: microcontroller.Pin  # GPIO43
RX: microcontroller.Pin  # GPIO44
I2C_SCL: microcontroller.Pin  # GPIO10
I2C_SDA: microcontroller.Pin  # GPIO11
BOOT: microcontroller.Pin  # GPIO0
BUTTON0: microcontroller.Pin  # GPIO0
SCK: microcontroller.Pin  # GPIO40
MOSI: microcontroller.Pin  # GPIO45
MISO: microcontroller.Pin  # GPIO46
SCL: microcontroller.Pin  # GPIO3
SDA: microcontroller.Pin  # GPIO1
IO10: microcontroller.Pin  # GPIO10
IO11: microcontroller.Pin  # GPIO11
IO15: microcontroller.Pin  # GPIO15
IO18: microcontroller.Pin  # GPIO18
IO19: microcontroller.Pin  # GPIO19
IO20: microcontroller.Pin  # GPIO20
IO43: microcontroller.Pin  # GPIO43
IO44: microcontroller.Pin  # GPIO44


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

"""Returns the `displayio.Display` object for the board's built in display.
The object created is a singleton, and uses the default parameter values for `displayio.Display`.
"""
DISPLAY: displayio.Display


# Unmapped:
#   none
