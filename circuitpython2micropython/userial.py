""" a UART wrapper class to allow circuitpython code to be used in micropython """
from machine import UART

class USART(UART):
    """ this class inherits from `machine.UART` """
    def __init__(self, tx, rx, *, baudrate=9600, bits=8, parity=None, stop=1, timeout=1, receiver_buffer_size=64):
        self._baudrate = baudrate
        super(USART, self).__init__(
            tx=tx, rx=rx,
            baudrate=baudrate,
            bits=bits,
            parity=parity,
            stop=stop,
            timeout=timeout,
            rxbuf=receiver_buffer_size)
    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, val):
        super().init(baudrate=val)

    @property
    def in_waiting(self):
        return self.any()
