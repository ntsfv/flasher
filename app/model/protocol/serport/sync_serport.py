#!/user/bin/env python
# coding:utf-8
from asyncio import Queue

import serial

from model.logger.loggable import Loggable
import model.protocol.serport.serport


class SyncSerPort(model.protocol.serport.serport.SerPort, serial.Serial, Loggable):
    def __init__(self):
        Loggable.__init__(self)
        super().__init__()

    def _open(self, port='/dev/ttyUSB0', baudrate=115200, quiet=False):
        if self.is_open:
            self.close()
        self.port = port
        self.baudrate = baudrate
        self.timeout = 5
        self.dtr = False
        self.rts = False
        if not quiet:
            self.logger.info("Открываю порт %s %s" % (port, baudrate))
        serial.Serial.open(self)

    def reset_input_buffer(self):
        serial.Serial.reset_input_buffer(self)

    def open(self, port='/dev/ttyUSB0', baudrate=115200):
        self._open(port, baudrate)

    def close(self,):
        serial.Serial.close(self)

    def write(self, blist):
        serial.Serial.write(self, bytes(blist))

    def read(self, size=1):
        bytes_str = serial.Serial.read(self, size)
        return int.from_bytes(bytes_str, byteorder='little')


if __name__ == '__main__':
    serport = SyncSerPort()
    serport.open()
    serport.write([0x7F])
    a = serport.read(1)
    print(a)
