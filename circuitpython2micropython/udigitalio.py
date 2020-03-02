""" a wrapper for micropython's :py:class:`~machine.Pin` object """
# pylint: disable=import-error
from machine import Pin

class DriveMode:
    PUSH_PULL = Pin.PULL_HOLD
    OPEN_DRAIN = Pin.OPEN_DRAIN

class Pull:
    UP = Pin.PULL_UP
    DOWN = Pin.PULL_DOWN

class DigitalInOut:
    """A class to control micropython's :py:class:`~machine.Pin` object like
    a circuitpython DigitalInOut object

    :param ~machine.Pin pin: the digital pin alias.
    """
    def __init__(self, pin_number):
        self._pin = machine.Pin(pin_number, machine.Pin.IN)

    def deinit(self):
        """ deinitialize the GPIO pin """
        # deinit() not implemented in micropython
        pass # avoid raiseing a NotImplemented Error

    def switch_to_output(self, value=False, drive_mode=DriveMode.PUSH_PULL):
        """ change pin into output """
        self._pin.init(machine.Pin.OUT, value=value)

    def switch_to_input(self, pull=None):
        """ change pin into input """
        self._pin.init(machine.Pin.IN)

    @property
    def value(self):
        """ the value of the pin """
        return self._pin.value()

    @value.setter
    def value(self, val):
        self._pin.value(val)

    def __del__(self):
        del self._pin
