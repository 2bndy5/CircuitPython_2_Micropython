# The MIT License (MIT)
#
# Copyright (c) 2016 Scott Shawcroft for Adafruit Industries
# Copyright (c) 2019 Brendan Doherty
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# pylint: disable=too-few-public-methods

"""
SPIDevice
===========

A wrapper module to implement a context manager for SPI Bus Devices using MicroPython's
`machine.SPI` class. This code has been customized for this circuitpython_nrfl01 library,
thus there is no consideration for other SPI devices (like SD cards).
"""
from machine import Pin

class SPIDevice:
    """
    Represents a single SPI device and manages locking the bus and the device
    address.

    :param ~machine.SPI spi: The SPI bus the device is on
    :param ~machine.Pin chip_select: The chip select pin object used as a digital output.
        (Used for SD cards.)
    """
    def __init__(self, spi, chip_select=None, *,
                 baudrate=100000, polarity=0, phase=0):
        self.spi = spi
        self.spi.deinit()
        self.baudrate = baudrate
        self.polarity = polarity
        self.phase = phase
        self.chip_select = chip_select
        if self.chip_select:
            self.chip_select.init(mode=Pin.OUT, value=True)

    def __enter__(self):
        self.spi.init(
            baudrate=self.baudrate,
            polarity=self.polarity,
            phase=self.phase
        )
        if self.chip_select:
            self.chip_select.value = False
        return self.spi

    def __exit__(self, *exc):
        if self.chip_select:
            self.chip_select.value = True
        self.spi.deinit()
        return False
