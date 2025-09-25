from model.logger.loggable import Loggable
from model.protocol.commands.constants import CmdCode
from model.protocol.serport.serport import SerPort


class Packet(Loggable):
    def __init__(self, mcu, serport: SerPort):
        Loggable.__init__(self)
        self.mcu = mcu
        self.serport = serport
        self.cmd_code = CmdCode["NONE"]
        self.data8_n = 0
        self.data = []

    @staticmethod
    def crc16(data_in, crc_in=0):
        """
        crc16 byte by byte
        """
        crc = crc_in & 0xFFFF
        data = (data_in & 0xFF) | 0x100

        while not (data & 0x10000):
            crc <<= 1
            data <<= 1
            if data & 0x100:
                crc += 1
            if crc & 0x10000:
                crc ^= 0x1021

        return crc & 0xFFFF

    @staticmethod
    def chunks(l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]
