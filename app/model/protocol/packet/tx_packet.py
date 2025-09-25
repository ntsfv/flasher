from model.protocol.constants import SignCode
from model.protocol.packet.packet import Packet
from model.protocol.serport.serport import SerPort


class TxPacket(Packet):
    def __init__(self, mcu, serport: SerPort):
        super().__init__(mcu, serport)
        self.host_sign = SignCode["HOST"]

    def transmit(self):
        packet_bytes = []
        packet_bytes += [(self.host_sign >> 0) & 0xFF]
        packet_bytes += [(self.host_sign >> 8) & 0xFF]

        packet_bytes += [(self.cmd_code >> 0) & 0xFF]
        crc = self.crc16(self.cmd_code)

        packet_bytes += [(~self.cmd_code >> 0) & 0xFF]
        crc = self.crc16(~self.cmd_code, crc)

        packet_bytes += [(self.data8_n >> 0) & 0xFF]
        packet_bytes += [(self.data8_n >> 8) & 0xFF]
        crc = self.crc16((self.data8_n >> 0) & 0xFF, crc)
        crc = self.crc16((self.data8_n >> 8) & 0xFF, crc)

        for i in range(0, self.data8_n):
            packet_bytes += [(self.data[i] >> 0) & 0xFF]
            crc = self.crc16(self.data[i], crc)

        self.logger.debug("data8_n: %d" % self.data8_n)
        self.logger.debug("crc: 0x%04x" % crc)
        packet_bytes += [(crc >> 0) & 0xFF]
        packet_bytes += [(crc >> 8) & 0xFF]

        self.serport.write(packet_bytes)
