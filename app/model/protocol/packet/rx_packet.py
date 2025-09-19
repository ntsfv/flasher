from model.protocol.commands.constants import CmdCode
from model.protocol.constants import *
from model.protocol.packet.packet import Packet
from model.protocol.protocol_exception import ProtException
from model.protocol.serport.serport import SerPort
from utils.utils import dict_key


class RxPacket(Packet):
    def __init__(self, mcu, serport: SerPort):
        super().__init__(mcu, serport)
        self.device_sign = SignCode["DEVICE"]
        self.rxcmd_code = CmdCode["NONE"]
        self.msg_code = MsgCode["NONE"]

    def msg_err_crc(self):
        self.logger.debug(LogId["DEVICE"] + "%s - ERR_CRC - CRC error in HOST command!" % dict_key(CmdCode, self.rxcmd_code))
        raise ProtException("Ошибка CRC в команде от хоста!")

    def parse_msg(self):
        flash_page_size = 1
        info = {}
        self.msg_code = self.data[0]
        self.rxcmd_code = self.data[1]
        info['cmd_code'] = self.rxcmd_code
        info['msg_code'] = self.msg_code

        if self.rxcmd_code == CmdCode["NONE"]:
            if self.msg_code == MsgCode["ERR_CMD"]:
                self.logger.debug(LogId["DEVICE"] + "ERR_CMD - wrong command from HOST!")
                raise ProtException("Принята некорректная команда от хоста!")
            elif self.msg_code == MsgCode["READY"]:
                result = "Устройство ответило о готовности"
                self.logger.info(LogId["PROG"] + "%s" % result)
                self.logger.debug(LogId["DEVICE"] + "READY - %s" % result)

        elif self.rxcmd_code == CmdCode["GET_INFO"]:
            if self.msg_code == MsgCode["ERR_CRC"]:
                self.msg_err_crc()
            elif self.msg_code == MsgCode["OK"]:
                chipid = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                cpuid = (self.data[8] << 0) | (self.data[9] << 8) | (self.data[10] << 16) | (self.data[11] << 24)
                bootver = (self.data[12] << 0) | (self.data[13] << 8) | (self.data[14] << 16) | (self.data[15] << 24)
                result = ("SIU.CHIPID=[0x%08x] SCB.CPUID=[0x%08x] BOOTVER=[0x%08x]" %
                          (chipid, cpuid, bootver))

                info['chipid'] = "0x%08X" % chipid
                info['cpuid'] = "0x%08X" % cpuid
                info['bootver'] = "%d.%d" % ((bootver & 0xFFFF0000) >> 16, (bootver & 0x0000FFFF) >> 0)
                self.logger.info(LogId["PROG"] + result)
                self.logger.debug(LogId["DEVICE"] + "GET_INFO - OK | %s" % result)

        elif self.rxcmd_code == CmdCode["GET_CFGWORD"]:
            if self.msg_code == MsgCode["ERR_CRC"]:
                self.msg_err_crc()
            elif self.msg_code == MsgCode["OK"]:
                info.update(self.mcu.parse_cfgword(self.data[4:]))
                self.logger.info(LogId["PROG"] + "%s" % info["res_str"])
                self.logger.debug(LogId["DEVICE"] + "GET_CFGWORD - OK | %s" % info["res_str"])
            elif self.msg_code == MsgCode["FAIL"]:
                    raise ProtException("Устройство вернуло сообщение об ошибке!")

        elif self.rxcmd_code == CmdCode["SET_CFGWORD"]:
            if self.msg_code == MsgCode["ERR_CRC"]:
                self.msg_err_crc()
            elif self.msg_code == MsgCode["OK"]:
                info.update(self.mcu.parse_cfgword(self.data[4:]))
                self.logger.debug(LogId["DEVICE"] + "SET_CFGWORD - OK | %s" % info["res_str"])
            elif self.msg_code == MsgCode["FAIL"]:
                    raise ProtException("Устройство вернуло сообщение об ошибке!")

        elif self.rxcmd_code == CmdCode["WRITE_PAGE"]:
            if self.msg_code == MsgCode["ERR_CRC"]:
                self.msg_err_crc()
            elif self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]:
                temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                self.logger.debug(LogId["DEVICE"] + "WRITE_PAGE - %s | NVR=[%01d] FLASH=[%01d] ERASE=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                             (dict_key(MsgCode, self.msg_code),
                             ((temp >> 31) & 0x1), ((temp >> 29) & 0x1), ((temp >> 30) & 0x1), (temp & 0x3FFFFFFF), (temp & 0x3FFFFFFF) // flash_page_size))
                if self.msg_code == MsgCode["FAIL"]:
                    raise ProtException("Устройство вернуло сообщение об ошибке!")

        elif self.rxcmd_code == CmdCode["READ_PAGE"]:
            if self.msg_code == MsgCode["ERR_CRC"]:
                self.msg_err_crc()
            elif self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]:
                temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                info['data'] = self.data[8:]
                self.logger.debug(LogId["DEVICE"] + "READ_PAGE - %s | NVR=[%01d] FLASH=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                             (dict_key(MsgCode, self.msg_code),
                             ((temp >> 31) & 0x1), ((temp >> 29) & 0x1), (temp & 0x7FFFFFFF), (temp & 0x7FFFFFFF) // flash_page_size))
                if self.msg_code == MsgCode["FAIL"]:
                    raise ProtException("Устройство вернуло сообщение об ошибке!")

        elif self.rxcmd_code == CmdCode["ERASE_FULL"]:
            if self.msg_code == MsgCode["ERR_CRC"]:
                self.msg_err_crc()
            elif self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]:
                temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                self.logger.debug(LogId["DEVICE"] + "ERASE_FULL - %s | NVR=[%01d] FLASH=[%01d]" % (dict_key(MsgCode, self.msg_code), ((temp >> 31) & 0x1), ((temp >> 29) & 0x1)))
                if self.msg_code == MsgCode["FAIL"]:
                    raise ProtException("Устройство вернуло сообщение об ошибке!")

        elif self.rxcmd_code == CmdCode["ERASE_PAGE"]:
            if self.msg_code == MsgCode["ERR_CRC"]:
                self.msg_err_crc()
            elif self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]:
                temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                self.logger.debug(LogId["DEVICE"] + "ERASE_PAGE - %s | NVR=[%01d] FLASH=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                             (dict_key(MsgCode, self.msg_code),
                             ((temp >> 31) & 0x1), ((temp >> 29) & 0x1), (temp & 0x7FFFFFFF), (temp & 0x7FFFFFFF) // flash_page_size))
                if self.msg_code == MsgCode["FAIL"]:
                    raise ProtException("Устройство вернуло сообщение об ошибке!")

        elif self.rxcmd_code == CmdCode["EXIT_BOOTLOADER"]:
            if self.msg_code == MsgCode["ERR_CRC"]:
                self.msg_err_crc()
            elif self.msg_code == MsgCode["OK"]:
                self.logger.debug(LogId["DEVICE"] + "EXIT_BOOTLOADER - OK")

        n = 0
        for chunk in self.chunks(self.data, 4):
            temp_str = "0x%02x:" % n
            for b in chunk:
                temp_str += ' %02x' % b
                n += 1
            self.logger.debug(temp_str)
            if n > 63:
                self.logger.debug('More than 64 bytes of data, the rest are not printed')
                break

        return info

    def receive(self):
        # device signature detection
        rx_sign = 0
        while rx_sign != self.device_sign:
            temp = self.serport.read()
            rx_sign = (rx_sign >> 8) | (temp << 8)
        # read special data
        rx_cmd = self.serport.read()
        rx_cmd_inv = self.serport.read()
        rx_data_n = self.serport.read(2)
        # check command
        if (rx_cmd ^ rx_cmd_inv) != 0xFF:
            self.logger.debug(LogId["HOST"] + "MSG_CMD - ERR_CMD - wrong command from DEVICE!")
            raise ProtException("Wrong command received!")
        # start data load and crc16 calculation
        crc = self.crc16(rx_cmd)
        crc = self.crc16(rx_cmd_inv, crc)
        crc = self.crc16((rx_data_n >> 0) & 0xFF, crc)
        crc = self.crc16((rx_data_n >> 8) & 0xFF, crc)
        for i in range(0, rx_data_n):
            self.data += [self.serport.read()]
            crc = self.crc16(self.data[i], crc)
        rx_crc = self.serport.read(2)
        # check crc
        if rx_crc == crc:
            self.cmd_code = rx_cmd
            self.data8_n = rx_data_n
            if self.cmd_code == CmdCode["MSG"]:
                    return self.parse_msg()
            else:
                self.logger.debug(LogId["HOST"] + "Error! Waiting for MSG but recieve %s command" % dict_key(CmdCode, self.cmd_code))
                raise ProtException("Wrong command received!")
        else:
            self.logger.debug(LogId["HOST"] + "MSG - ERR_CRC - CRC error in DEVICE command!")
            raise ProtException("CRC error in device message!")
