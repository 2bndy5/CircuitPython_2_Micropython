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
`machine.SPI` class. This code has been customized for the CircuitPython-nRF24L01 library,
thus there is no consideration for other SPI devices (like SD cards).
"""
# pylint: disable=import-error
from machine import Pin, I2C

class SPIDevice:
    """
    Represents a single SPI device and manages initialization/deinitialization
    (psuedo-locking) the bus and the device's CS (Chip Select) pin.

    :param ~machine.SPI spi: The SPI bus that the device is on.
    :param ~machine.Pin chip_select: The chip select pin object used as a digital output.
    """
    def __init__(self, spi, *, chip_select=None,
                 baudrate=100000, polarity=0, phase=0):
        self.spi = spi
        self.spi.deinit()
        self.baudrate = baudrate
        self.polarity = polarity
        self.phase = phase
        self.chip_select = chip_select
        if self.chip_select:
            self.chip_select.switch_to_output(value=True)

    @property
    def frequency(self):
        return self.baudrate

    def __enter__(self):
        self.spi.init(
            baudrate=self.baudrate,
            polarity=self.polarity,
            phase=self.phase)
        if self.chip_select:
            self.chip_select.value = False
        return self.spi

    def __exit__(self, *exc):
        if self.chip_select:
            self.chip_select.value = True
        self.spi.deinit()
        return False

class I2CDevice:
    """Represents a single I2C device and manages initialization/deinitialization
    (psuedo-locking) the bus and the device's slave address.

    :param ~machine.I2 i2c: The I2C bus that the device is on.
    :param int address: The I2C device's address. This is a 7-bit integer.
    :param bool probe: if `True`, instantiation probes the I2C bus for a device
        with a designated slave address that matches the above ``address`` parameter.
    """
    def __init__(self, i2c, address, probe=True, scl=None, sda=None, frequency=None):
        self.i2c = i2c
        self.sda, self.scl = (scl, sda)
        self.freq = frequency
        self.device_address = address
        if probe:
            if not self.__probe_for_device():
                raise ValueError("No I2C device at address: %x" % self.device_address)

    def __probe_for_device(self):
        for addr in self.i2c.scan():
            if addr == self.device_address:
                return True
        return False

    def readinto(self, buf, *, start=0, end=None, stop=True):
        """
        Read into ``buf`` from the device. The number of bytes read will be the
        length of ``buf``.

        If ``start`` or ``end`` is provided, then the buffer will be sliced
        as if ``buf[start:end]``. This will not cause an allocation like
        ``buf[start:end]`` will so it saves memory.

        :param bytearray buffer: buffer to write into
        :param int start: Index to start writing at
        :param int end: Index to write up to but not include; if None, use ``len(buf)``
        :param bool stop: `True` sends a STOP condition (special bit); `False` doesn't.
        """
        if end is None:
            end = len(buf)
        self.i2c.readfrom_into(self.device_address,  buf[start:end], stop=stop)

    def write(self, buf, *, start=0, end=None, stop=True):
        """
        Write the bytes from ``buffer`` to the device. Transmits a stop bit if
        ``stop`` is set.

        If ``start`` or ``end`` is provided, then the buffer will be sliced
        as if ``buffer[start:end]``. This will not cause an allocation like
        ``buffer[start:end]`` will so it saves memory.

        :param bytearray buffer: buffer containing the bytes to write
        :param int start: Index to start writing from
        :param int end: Index to read up to but not include; if None, use ``len(buf)``
        :param bool stop: If true, output an I2C stop condition after the buffer is written
        """
        if end is None:
            end = len(buf)
        self.i2c.writeto(self.device_address, buf[start:end], stop=stop)

    # pylint: disable-msg=too-many-arguments
    def write_then_readinto(self, out_buffer, in_buffer, *,
                            out_start=0, out_end=None, in_start=0, in_end=None):
        """
        Write the bytes from ``out_buffer`` to the device, then immediately
        reads into ``in_buffer`` from the device. The number of bytes read
        will be the length of ``in_buffer``.

        If ``out_start`` or ``out_end`` is provided, then the output buffer
        will be sliced as if ``out_buffer[out_start:out_end]``. This will
        not cause an allocation like ``buffer[out_start:out_end]`` will so
        it saves memory.

        If ``in_start`` or ``in_end`` is provided, then the input buffer
        will be sliced as if ``in_buffer[in_start:in_end]``. This will not
        cause an allocation like ``in_buffer[in_start:in_end]`` will so
        it saves memory.

        :param bytearray out_buffer: buffer containing the bytes to write
        :param bytearray in_buffer: buffer containing the bytes to read into
        :param int out_start: Index to start writing from
        :param int out_end: Index to read up to but not include; if None, use ``len(out_buffer)``
        :param int in_start: Index to start writing at
        :param int in_end: Index to write up to but not include; if None, use ``len(in_buffer)``
        """
        if out_end is None:
            out_end = len(out_buffer)
        if in_end is None:
            in_end = len(in_buffer)
        self.write(out_buffer, start=out_start, end=out_end, stop=False)
        self.readinto(in_buffer, start=in_start, end=in_end)
    #pylint: enable-msg=too-many-arguments

    def __enter__(self):
        # in micropython we need the `Pin` objects used for sda & scl parameters to I2C.init()
        if self.scl is not None and self.sda is not None:
            if self.freq is not None:
                self.i2c = I2C(scl=self.scl, sda=self.sda, frequency=self.freq)
            else:
                self.i2c = I2C(scl=self.scl, sda=self.sda)
        return self

    def __exit__(self, *exc):
        return False
