#!/user/bin/env python
# coding:utf-8

import os
import time
import mcu


LogId = {
    "DEVICE": "@D: ",
    "HOST": "@H: ",
    "PROG": "",
}

SignCode = {
    "DEVICE": 0x7EA3,
    "HOST": 0x5C81,
}

CmdCode = {
    # Get commands
    "GET_INFO": 0x35,
    "GET_CFGWORD": 0x3A,
    # Set commands
    "SET_CFGWORD": 0x65,
    # Write commands
    "WRITE_PAGE": 0x9A,
    # Read commands
    "READ_PAGE": 0xA5,
    # Erase commands
    "ERASE_FULL": 0xC5,
    "ERASE_PAGE": 0xCA,
    # Misc
    "NONE": 0x00,
    "EXIT_BOOTLOADER": 0xF5,
    "MSG": 0xFA
}

MsgCode = {
    "NONE": 0,
    "ERR_CMD": 1,
    "ERR_CRC": 2,
    "READY": 3,
    "OK": 4,
    "FAIL": 5
}


# -- Misc functions -----------------------------------------------------------
def dict_key(mydict, dict_value):
    return list(mydict.keys())[list(mydict.values()).index(dict_value)]


# -- Classes ----------------------------------------------------------------
class ProtException(Exception):
    def __init__(self, msg, win=None):
        if win:
            win.log_err(msg)
        super().__init__(msg)


class Packet:
    def __init__(self, mcu, serport, win=None):
        self.mcu = mcu
        self.serport = serport
        self.win = win
        self.cmd_code = CmdCode["NONE"]
        self.data8_n = 0
        self.data = []

    def log_dbg(self, msg):
        if self.win:
            self.win.log_dbg(msg)
        else:
            print("DBG: %s" % msg)

    def log_info(self, msg):
        if self.win:
            self.win.log_info(msg)
        else:
            print("INFO: %s" % msg)

    def log_err(self, msg):
        if self.win:
            self.win.log_err(msg)
        else:
            print("ERR: %s" % msg)

    def crc16(self, data_in, crc_in=0):
        '''crc16 byte by byte'''
        crc = crc_in & 0xFFFF
        data = (data_in & 0xFF) | 0x100

        while not (data & 0x10000):
            crc <<= 1
            data <<= 1
            if (data & 0x100):
                crc += 1
            if (crc & 0x10000):
                crc ^= 0x1021

        return crc & 0xFFFF


class TxPacket(Packet):
    def __init__(self, mcu, serport, win=None):
        super().__init__(mcu, serport, win)
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

        packet_bytes += [(crc >> 0) & 0xFF]
        packet_bytes += [(crc >> 8) & 0xFF]

        self.serport.write_bytes(packet_bytes)


class RxPacket(Packet):
    def __init__(self, mcu, serport, win=None):
        super().__init__(mcu, serport, win)
        self.device_sign = SignCode["DEVICE"]
        self.device_data_n_max = 2048
        self.rxcmd_code = CmdCode["NONE"]
        self.msg_code = MsgCode["NONE"]

    def _msgErrCRC(self):
        self.log_dbg(LogId["DEVICE"] + "%s - ERR_CRC - CRC error in HOST command!" % self.dict_key(CmdCode, self.rxcmd_code))
        raise ProtException("Ошибка CRC в команде от хоста!", self.win)

    def _parseMsg(self):
            self.msg_code = self.data[0]
            self.rxcmd_code = self.data[1]

            if (self.rxcmd_code == CmdCode["NONE"]):
                if (self.msg_code == MsgCode["ERR_CMD"]):
                    self.log_dbg(LogId["DEVICE"] + "ERR_CMD - wrong command from HOST!")
                    raise ProtException("Принята некорректная команда от хоста!", self.win)
                elif (self.msg_code == MsgCode["READY"]):
                    result = "Устройство готово!"
                    self.log_info(LogId["PROG"] + "%s" % result)
                    self.log_dbg(LogId["DEVICE"] + "READY - %s" % result)

            elif (self.rxcmd_code == CmdCode["GET_INFO"]):
                if (self.msg_code == MsgCode["ERR_CRC"]):
                    self._msgErrCRC()
                elif (self.msg_code == MsgCode["OK"]):
                    result = ("SIU.CHIPID=[0x%08x] SCB.CPUID=[0x%08x] BOOTVER=[0x%08x]" %
                              ((self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24),
                               (self.data[8] << 0) | (self.data[9] << 8) | (self.data[10] << 16) | (self.data[11] << 24),
                               (self.data[12] << 0) | (self.data[13] << 8) | (self.data[14] << 16) | (self.data[15] << 24)))
                    self.log_info(LogId["PROG"] + "\t%s" % result)
                    self.log_dbg(LogId["DEVICE"] + "GET_INFO - OK | %s" % result)

            elif (self.rxcmd_code == CmdCode["GET_CFGWORD"]):
                if (self.msg_code == MsgCode["ERR_CRC"]):
                    self._msgErrCRC()
                elif (self.msg_code == MsgCode["OK"]):
                    result = ("READEN=[%01d] JTAGEN=[%01d] DEBUGEN=[%01d] NVRWE=[%01d] FLASHWE=[%01d] BMODEDIS=[%01d]" %
                              ((self.data[4] & CFGWORD_READEN_MSK) >> CFGWORD_READEN_POS,
                               (self.data[4] & CFGWORD_JTAGEN_MSK) >> CFGWORD_JTAGEN_POS,
                               (self.data[4] & CFGWORD_DEBUGEN_MSK) >> CFGWORD_DEBUGEN_POS,
                               (self.data[4] & CFGWORD_NVRWE_MSK) >> CFGWORD_NVRWE_POS,
                               (self.data[4] & CFGWORD_FLASHWE_MSK) >> CFGWORD_FLASHWE_POS,
                               (self.data[4] & CFGWORD_BMODEDIS_MSK) >> CFGWORD_BMODEDIS_POS))
                    self.log_info(LogId["PROG"] + "\t%s" % result)
                    self.log_dbg(LogId["DEVICE"] + "GET_CFGWORD - OK | %s" % result)

            elif (self.rxcmd_code == CmdCode["SET_CFGWORD"]):
                if (self.msg_code == MsgCode["ERR_CRC"]):
                    self._msgErrCRC()
                elif (self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]):
                    self.log_dbg(LogId["DEVICE"] + "SET_CFGWORD - %s | READEN=[%01d] JTAGEN=[%01d] DEBUGEN=[%01d] NVRWE=[%01d] FLASHWE=[%01d] BMODEDIS=[%01d]" %
                        (dict_key(MsgCode, self.msg_code),
                        (self.data[4] & CFGWORD_READEN_MSK) >> CFGWORD_READEN_POS,
                        (self.data[4] & CFGWORD_JTAGEN_MSK) >> CFGWORD_JTAGEN_POS,
                        (self.data[4] & CFGWORD_DEBUGEN_MSK) >> CFGWORD_DEBUGEN_POS,
                        (self.data[4] & CFGWORD_NVRWE_MSK) >> CFGWORD_NVRWE_POS,
                        (self.data[4] & CFGWORD_FLASHWE_MSK) >> CFGWORD_FLASHWE_POS,
                        (self.data[4] & CFGWORD_BMODEDIS_MSK) >> CFGWORD_BMODEDIS_POS))
                    if (self.msg_code == MsgCode["FAIL"]):
                        raise ProtException("Command failed!", self.win)

            elif (self.rxcmd_code == CmdCode["WRITE_PAGE"]):
                if (self.msg_code == MsgCode["ERR_CRC"]):
                    self._msgErrCRC()
                elif (self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]):
                    temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                    self.log_dbg(LogId["DEVICE"] + "WRITE_PAGE - %s | NVR=[%01d] ERASE=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                                 (dict_key(MsgCode, self.msg_code),
                                 ((temp >> 31) & 0x1), ((temp >> 30) & 0x1), (temp & 0x3FFFFFFF), (temp & 0x3FFFFFFF) // FLASH_PAGE_SIZE))
                    if (self.msg_code == MsgCode["FAIL"]):
                        raise ProtException("Command failed!", self.win)

            elif (self.rxcmd_code == CmdCode["READ_PAGE"]):
                if (self.msg_code == MsgCode["ERR_CRC"]):
                    self._msgErrCRC()
                elif (self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]):
                    temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                    self.log_dbg(LogId["DEVICE"] + "READ_PAGE - %s | NVR=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                                 (dict_key(MsgCode, self.msg_code),
                                 ((temp >> 31) & 0x1), (temp & 0x7FFFFFFF), (temp & 0x7FFFFFFF) // FLASH_PAGE_SIZE))
                    if (self.msg_code == MsgCode["FAIL"]):
                        raise ProtException("Command failed!", self.win)

            elif (self.rxcmd_code == CmdCode["ERASE_FULL"]):
                if (self.msg_code == MsgCode["ERR_CRC"]):
                    self._msgErrCRC()
                elif (self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]):
                    self.log_dbg(LogId["DEVICE"] + "ERASE_FULL - %s" % self.dict_key(MsgCode, self.msg_code))
                    if (self.msg_code == MsgCode["FAIL"]):
                        raise ProtException("Command failed!", self.win)

            elif (self.rxcmd_code == CmdCode["ERASE_PAGE"]):
                if (self.msg_code == MsgCode["ERR_CRC"]):
                    self._msgErrCRC()
                elif (self.msg_code == MsgCode["OK"] or self.msg_code == MsgCode["FAIL"]):
                    temp = (self.data[4] << 0) | (self.data[5] << 8) | (self.data[6] << 16) | (self.data[7] << 24)
                    self.log_dbg(LogId["DEVICE"] + "ERASE_PAGE - %s | NVR=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
                                 (dict_key(MsgCode, self.msg_code),
                                 ((temp >> 31) & 0x1), (temp & 0x7FFFFFFF), (temp & 0x7FFFFFFF) // FLASH_PAGE_SIZE))
                    if (self.msg_code == MsgCode["FAIL"]):
                        raise ProtException("Command failed!", self.win)

            elif (self.rxcmd_code == CmdCode["EXIT_BOOTLOADER"]):
                if (self.msg_code == MsgCode["ERR_CRC"]):
                    self._msgErrCRC()
                elif (self.msg_code == MsgCode["OK"]):
                    self.log_dbg(LogId["DEVICE"] + "EXIT_BOOTLOADER - OK")

    def receive(self):
        # device signature detection
        rx_sign = 0
        while (rx_sign != self.device_sign):
            temp = self.serport.read_int()
            rx_sign = (rx_sign >> 8) | (temp << 8)
        # read special data
        rx_cmd = self.serport.read_int()
        rx_cmd_inv = self.serport.read_int()
        rx_data_n = self.serport.read_int(2)
        # check command
        if ((rx_cmd ^ rx_cmd_inv) != 0xFF):
            self.log_dbg(LogId["HOST"], "MSG_CMD - ERR_CMD - wrong command from DEVICE!")
            raise ProtException("Wrong command received!", self.win)
        # check N
        if (rx_data_n > self.device_data_n_max):
            self.log_dbg(LogId["HOST"], "MSG_CMD - ERR_N - wrong N number from DEVICE!")
            raise ProtException("Wrong N received!", self.win)
        # start data load and _crc16 calculation
        crc = self._crc16(rx_cmd)
        crc = self._crc16(rx_cmd_inv, crc)
        crc = self._crc16((rx_data_n >> 0) & 0xFF, crc)
        crc = self._crc16((rx_data_n >> 8) & 0xFF, crc)
        for i in range(0, rx_data_n):
            self.data += [self.serport.read_int()]
            crc = self._crc16(self.data[i], crc)
        rx_crc = self.serport.read_int(2)
        # check crc
        if (rx_crc == crc):
            self.cmd_code = rx_cmd
            self.data8_n = rx_data_n
            if (self.cmd_code == CmdCode["MSG"]):
                    self._parseMsg()
            else:
                self.log_dbg(LogId["HOST"], "Error! Waiting for MSG but recieve %s command" % self.dict_key(CmdCode, self.cmd_code))
                raise ProtException("Wrong command received!", self.win)
        else:
            self.log_dbg(LogId["HOST"], "MSG - ERR_CRC - CRC error in DEVICE command!")
            raise ProtException("CRC error in device message!", self.win)


class CmdInterface:
    def __init__(self, mcu, serport, win=None):
        self.mcu = mcu
        self.serport = serport
        self.win = win

    def log_dbg(self, msg):
        if self.win:
            self.win.log_dbg(msg)
        else:
            print("DBG: %s" % msg)

    def log_info(self, msg):
        if self.win:
            self.win.log_info(msg)
        else:
            print("INFO: %s" % msg)

    def log_err(self, msg):
        if self.win:
            self.win.log_err(msg)
        else:
            print("ERR: %s" % msg)

    def reset_chip(self):
        time.sleep(0.1)
        self.serport.dtr = True
        time.sleep(0.3)
        self.serport.dtr = False
        time.sleep(0.1)

    def initDevice(self):
        self.log_info(LogId["PROG"] + "Init device")
        self.serport.rts = True
        self.reset_chip()
        self.serport.write_bytes([0x7F])
        ack = self.serport.read_int(2)
        if (ack == ((((SignCode["DEVICE"]) >> 8) & 0x00FF) | (((SignCode["DEVICE"]) << 8) & 0xFF00))):
            self.log_info(LogId["PROG"] + "Device is connected!")
        else:
            self.log_info(LogId["PROG"] + "Unknown response from device!")
            raise ProtException("Unknown response from device!", self.win)
        self.serport.rts = False
        rxpacket = self.cmd_msg()
        if ((rxpacket.rxcmd_code != CmdCode["NONE"]) or (rxpacket.msg_code != MsgCode["READY"])):
            self.log_info(LogId["PROG"] + "Wait for DEVICE ready, but other message received!")
            raise ProtException("Wait for DEVICE ready, but other message received!", self.win)

    def release_device(self):
        self.log_info(LogId["PROG"] + "Release device")
        self.serport.rts = False
        self.reset_chip()

    def cmd_get_info(self):
        self.log_info(LogId["PROG"] + "Read device ID's:")
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["GET_INFO"]
        packet.data8_n = 0
        self.log_dbg(LogId["HOST"] + "GET_INFO")
        packet.transmit()
        self.cmd_msg()

    def cmd_get_cfgword(self):
        self.log_info(LogId["PROG"] + "Read device CFGWORD:")
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["GET_CFGWORD"]
        packet.data8_n = 0
        self.log_dbg(LogId["HOST"] + "GET_CFGWORD")
        packet.transmit()
        self.cmd_msg()

    def cmd_set_cfgword(self, cfgword):
        self.log_info(LogId["PROG"] + "Set new CFGWORD 0x%08x" % cfgword)
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["SET_CFGWORD"]
        packet.data8_n = 4
        packet.data += [(cfgword >> 0) & 0xFF]
        packet.data += [(cfgword >> 8) & 0xFF]
        packet.data += [(cfgword >> 16) & 0xFF]
        packet.data += [(cfgword >> 24) & 0xFF]
        self.log_dbg(LogId["HOST"] + "SET_CFGWORD - READEN=[%01d] JTAGEN=[%01d] DEBUGEN=[%01d] NVRWE=[%01d] FLASHWE=[%01d] BMODEDIS=[%01d]" %
            ((packet.data[0] & CFGWORD_READEN_MSK) >> CFGWORD_READEN_POS,
            (packet.data[0] & CFGWORD_JTAGEN_MSK) >> CFGWORD_JTAGEN_POS,
            (packet.data[0] & CFGWORD_DEBUGEN_MSK) >> CFGWORD_DEBUGEN_POS,
            (packet.data[0] & CFGWORD_NVRWE_MSK) >> CFGWORD_NVRWE_POS,
            (packet.data[0] & CFGWORD_FLASHWE_MSK) >> CFGWORD_FLASHWE_POS,
            (packet.data[0] & CFGWORD_BMODEDIS_MSK) >> CFGWORD_BMODEDIS_POS))
        packet.transmit()
        self.cmd_msg()

    def cmd_erase_page(self, page, nvr=0):
        self.log_info(LogId["PROG"] + "Erase page %d" % page)
        addr = page * FLASH_PAGE_SIZE
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["ERASE_PAGE"]
        packet.data8_n = 4
        packet.data += [(addr >> 0) & 0xFF]
        packet.data += [(addr >> 8) & 0xFF]
        packet.data += [(addr >> 16) & 0xFF]
        packet.data += [(nvr >> 7) & 0xFF]
        self.log_dbg(LogId["HOST"] + "ERASE_PAGE - NVR=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
            (nvr, addr, page))
        packet.transmit()

    def cmd_erase_full(self):
        self.log_info(LogId["PROG"] + "Erase full flash")
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["ERASE_FULL"]
        packet.data8_n = 0
        self.log_dbg(LogId["HOST"] + "ERASE_FULL")
        packet.transmit()

    def cmd_write_page(self, page, page_data, nvr=0, erase=0):
        self.log_info(LogId["PROG"] + "Write page %d" % page)
        addr = page * FLASH_PAGE_SIZE
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["WRITE_PAGE"]
        packet.data8_n = FLASH_PAGE_SIZE + 4
        packet.data += [(addr >> 0) & 0xFF]
        packet.data += [(addr >> 8) & 0xFF]
        packet.data += [(addr >> 16) & 0xFF]
        packet.data += [((nvr >> 7) | (erase >> 6)) & 0xFF]
        for i in range(0, FLASH_PAGE_SIZE):
            packet.data += [page_data[i]]
        self.log_dbg(LogId["HOST"] + "WRITE_PAGE - NVR=[%01d] ERASE=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
            (nvr, erase, addr, page))
        packet.transmit()

    def cmd_read_page(self, page, nvr=0):
        self.log_info(LogId["PROG"] + "Read page %d" % page)
        addr = page * FLASH_PAGE_SIZE
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["READ_PAGE"]
        packet.data8_n = 4
        packet.data += [(addr >> 0) & 0xFF]
        packet.data += [(addr >> 8) & 0xFF]
        packet.data += [(addr >> 16) & 0xFF]
        packet.data += [(nvr >> 7) & 0xFF]
        self.log_dbg(LogId["HOST"] + "READ_PAGE - NVR=[%01d] ADDR=[0x%08x] PAGE=[%0d]" %
            (nvr, addr, page))
        packet.transmit()
        rx_packet = self.cmd_msg()
        page_data = []
        for i in range(0, rx_packet.data8_n - 8):
            page_data += [rx_packet.data[i + 8]]
        return page_data

    def cmd_exit_bootloader(self):
        self.log_info(LogId["PROG"] + "Software reset and exit from bootloader")
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.cmd_code = CmdCode["EXIT_BOOTLOADER"]
        packet.data8_n = 0
        self.log_dbg(LogId["HOST"] + "EXIT_BOOTLOADER")
        packet.transmit()

    def cmd_msg(self):
        packet = TxPacket(self.mcu, self.serport, self.win)
        packet.receive()
        return packet


class Protocol:
    def __init__(self, serport, win=None):
        self.mcu = mcu.get_by_name('k1921vkx')
        self.serport = serport
        self.win = win

    # -- Helpers --
    def log_dbg(self, msg):
        if self.win:
            self.win.log_dbg(msg)
        else:
            print("DBG: %s" % msg)

    def log_info(self, msg):
        if self.win:
            self.win.log_info(msg)
        else:
            print("INFO: %s" % msg)

    def log_err(self, msg):
        if self.win:
            self.win.log_err(msg)
        else:
            print("ERR: %s" % msg)

    def save_bin(self, name, data):
        self.log_dbg("Save %0d bytes of data to %s" % (len(data), name))
        binfile = open(name, "wb")
        binfile.write(bytes(data))
        binfile.close()

    def open_bin(self, name):
        binfile = open(name, "rb")
        data = []
        while True:
            current_byte = binfile.read(1)
            if (not current_byte):
                break
            data += [ord(current_byte)]
        binfile.close()
        self.log_dbg("Loaded %0d bytes of data from %s" % (len(data), name))
        return data

    # -- API --
    def init(self, **kwargs):
        self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        self.log_dbg(kwargs)
        mcu_info = {'chipid': '0x5A298FE1', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}
        #mcu_info = {'chipid': '0x3ABF2FD1', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}
        #mcu_info = {'chipid': '0x00000000', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}

        inited_mcu = mcu.get_by_chipid(mcu_info["chipid"])
        if inited_mcu is None:
            raise ProtException("Неизвестный CHIPID!", self.win)
        else:
            self.mcu = inited_mcu
        self.mcu.cpuid = mcu_info['cpuid']
        self.mcu.bootver = mcu_info['bootver']
        return self.mcu

    def deinit(self, **kwargs):
        self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        self.log_dbg(kwargs)
        return True

    def write(self, **kwargs):
        self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        self.log_dbg(kwargs)
        self.log_dbg(self.mcu.name)
        return True

    def erase(self, **kwargs):
        self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        self.log_dbg(kwargs)
        return True

    def read(self, **kwargs):
        self.log_dbg("%s->%s()" % (os.path.basename(__file__), self.win.whoami()))
        self.log_dbg(kwargs)
        return True
