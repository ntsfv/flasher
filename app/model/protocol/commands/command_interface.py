import time

from model.logger.loggable import Loggable
from model.protocol.commands.constants import CmdCode
from model.protocol.constants import *
from model.protocol.packet.packet import Packet
from model.protocol.packet.rx_packet import RxPacket
from model.protocol.packet.tx_packet import TxPacket
from model.protocol.protocol_exception import ProtException
from model.protocol.serport.serport import SerPort


class CommandInterface(Loggable):
    def __init__(self, mcu, serport: SerPort):
        Loggable.__init__(self)
        self.mcu = mcu
        self.serport = serport

    def open_port(self, port="/dev/ttyUSB0", baudrate=115200):
        self.serport.open(port, baudrate)

    def reset_chip(self, is_riscv: bool):
        self.logger.info(LogId["PROG"] + "Сброс микроконтроллера ...")
        time.sleep(0.1)
        if is_riscv:
            self.serport.rts = not self.serport.rts
        self.serport.dtr = True
        time.sleep(0.3)
        if is_riscv:
            self.serport.rts = not self.serport.rts
        self.serport.dtr = False
        time.sleep(0.5)

    def init_device(self, is_riscv: bool):
        self.logger.info(LogId["PROG"] + "Подключение к устройству ...")
        # try RTS active 1
        self.logger.info(LogId["PROG"] + "Активация загрузчика: 1-ый вариант ....")
        self.serport.rts = False
        self.reset_chip(is_riscv)
        self.serport.write([0x7F])
        ack = self.serport.read(2)
        self.logger.debug(LogId["DEVICE"] + "ack = 0x%04X" % ack)
        if ack == (
            (((SignCode["DEVICE"]) >> 8) & 0x00FF)
            | (((SignCode["DEVICE"]) << 8) & 0xFF00)
        ):
            self.logger.info(LogId["PROG"] + "Устройство подключено")
        else:
            # try RTS active 0
            self.logger.info(LogId["PROG"] + "Активация загрузчика: 2-ой вариант ....")
            self.serport.reset_input_buffer()
            self.serport.rts = True
            self.reset_chip(is_riscv)
            self.serport.write([0x7F])
            ack = self.serport.read(2)
            self.logger.debug(LogId["DEVICE"] + "ack = 0x%04X" % ack)
            if ack == (
                (((SignCode["DEVICE"]) >> 8) & 0x00FF)
                | (((SignCode["DEVICE"]) << 8) & 0xFF00)
            ):
                self.logger.info(LogId["PROG"] + "Устройство подключено")
            else:
                raise ProtException("Неизвестный ответ от устройства")
        self.serport.rts = not self.serport.rts
        rx_info = self.cmd_msg()
        if (rx_info["cmd_code"] != CmdCode["NONE"]) or (
            rx_info["msg_code"] != MsgCode["READY"]
        ):
            raise ProtException(
                "Получено неизвестное сообщение, когда ожидался ответ о готовности"
            )

    def release_device(self, is_riscv: bool):
        self.logger.info(LogId["PROG"] + "Отключение от устройства ...")
        self.serport.rts = not self.mcu.booten_active
        self.reset_chip(is_riscv)

    def cmd_get_info(self):
        self.logger.info(LogId["PROG"] + "Чтение идентификаторов устройства ...")
        packet = TxPacket(self.mcu, self.serport)
        packet.cmd_code = CmdCode["GET_INFO"]
        packet.data8_n = 0
        self.logger.debug(LogId["HOST"] + "GET_INFO")
        packet.transmit()
        return self.cmd_msg()

    def cmd_get_cfgword(self):
        self.logger.info(LogId["PROG"] + "Чтение CFGWORD ...")
        packet = TxPacket(self.mcu, self.serport)
        packet.cmd_code = CmdCode["GET_CFGWORD"]
        packet.data8_n = 0
        self.logger.debug(LogId["HOST"] + "GET_CFGWORD")
        packet.transmit()
        return self.cmd_msg()

    def cmd_set_cfgword(self, cfgword):
        self.logger.info(LogId["PROG"] + "Запись CFGWORD ...")
        packet = TxPacket(self.mcu, self.serport)
        data, dbg_str = self.mcu.pack_cfgword(cfgword)
        packet.cmd_code = CmdCode["SET_CFGWORD"]
        packet.data += data
        packet.data8_n = len(data)
        temp_str = "data (%d): " % len(packet.data)
        for b in packet.data:
            temp_str += "0x%x " % b
        self.logger.debug(temp_str)
        self.logger.debug("data8_n: %d" % packet.data8_n)
        self.logger.debug(LogId["HOST"] + "%s" % dbg_str)
        packet.transmit()
        self.cmd_msg()

    def cmd_erase_page(self, page, flash, region):
        self.logger.info(LogId["PROG"] + "Стирание страницы %d ..." % page)
        page_size = self.mcu.flash[flash][region].page_size
        addr = page * page_size
        packet = TxPacket(self.mcu, self.serport)
        packet.cmd_code = CmdCode["ERASE_PAGE"]
        nvr = self._set_address(packet, addr, flash, region)
        self.logger.debug(
            LogId["HOST"]
            + "ERASE_PAGE - NVR=[%01d] FLASH=[%01d] ADDR=[0x%08x] PAGE=[%0d]"
            % (nvr, flash, addr, page)
        )
        packet.transmit()

    def cmd_erase_full(self, flash, region):
        self.logger.info(LogId["PROG"] + "Стирание всей области памяти ...")
        packet = TxPacket(self.mcu, self.serport)
        packet.cmd_code = CmdCode["ERASE_FULL"]
        packet.data8_n = 4
        packet.data += [(self.mcu.flash[0]["bootflash_end_address"] >> 0) & 0xFF]
        packet.data += [(self.mcu.flash[0]["bootflash_end_address"] >> 8) & 0xFF]
        packet.data += [(self.mcu.flash[0]["bootflash_end_address"] >> 16) & 0xFF]
        nvr = 1 if "nvr" in region else 0
        packet.data += [((nvr << 7) | (flash << 5)) & 0xFF]
        self.logger.debug(
            LogId["HOST"] + "ERASE_FULL - NVR=[%01d] FLASH=[%01d]" % (nvr, flash)
        )
        packet.transmit()

    def cmd_write_page(self, page, page_data, flash, region, erpages):
        self.logger.info(LogId["PROG"] + "Запись страницы %d ..." % page)
        page_size = self.mcu.flash[flash][region].page_size
        addr = page * page_size
        packet = TxPacket(self.mcu, self.serport)
        packet.cmd_code = CmdCode["WRITE_PAGE"]
        packet.data8_n = page_size + 4
        packet.data += [(addr >> 0) & 0xFF]
        packet.data += [(addr >> 8) & 0xFF]
        packet.data += [(addr >> 16) & 0xFF]
        nvr = 1 if "nvr" in region else 0
        erase = 1 if erpages else 0
        packet.data += [((nvr << 7) | (erase << 6) | (flash << 5)) & 0xFF]
        packet.data += page_data
        self.logger.debug(
            LogId["HOST"]
            + "WRITE_PAGE - NVR=[%01d] FLASH=[%01d] ERASE=[%01d] ADDR=[0x%08x] PAGE=[%0d]"
            % (nvr, flash, erase, addr, page)
        )
        packet.transmit()

    def cmd_jump(self, address):
        self.logger.info(
            LogId["PROG"] + "Переход по адресу исполнения 0x%08x" % address
        )
        packet = TxPacket(self.mcu, self.serport)
        packet.cmd_code = CmdCode["JUMP"]
        packet.data8_n = 4
        packet.data += [(address >> 0) & 0xFF]
        packet.data += [(address >> 8) & 0xFF]
        packet.data += [(address >> 16) & 0xFF]
        packet.data += [(address >> 24) & 0xFF]
        packet.transmit()

        self.cmd_msg()
        self.cmd_dummy()

    def cmd_read_page(self, page, flash, region):
        self.logger.info(LogId["PROG"] + "Чтение страницы %d ..." % page)
        addr = page * self.mcu.flash[flash][region].page_size
        packet = TxPacket(self.mcu, self.serport)
        packet.flash_page_size = self.mcu.flash[flash][region].page_size
        packet.cmd_code = CmdCode["READ_PAGE"]
        nvr = self._set_address(packet, addr, flash, region)
        self.logger.debug(
            LogId["HOST"]
            + "READ_PAGE - NVR=[%01d] FLASH=[%01d] ADDR=[0x%08x] PAGE=[%0d]"
            % (nvr, flash, addr, page)
        )
        packet.transmit()

    def cmd_exit_bootloader(self):
        self.logger.info(LogId["PROG"] + "Software reset and exit from bootloader")
        packet = TxPacket(self.mcu, self.serport)
        packet.cmd_code = CmdCode["EXIT_BOOTLOADER"]
        packet.data8_n = 0
        self.logger.debug(LogId["HOST"] + "EXIT_BOOTLOADER")
        packet.transmit()

    def cmd_dummy(self):
        packet = TxPacket(self.mcu, self.serport)
        packet.cmd_code = CmdCode["MSG"]
        packet.data8_n = 0
        packet.transmit()

    def cmd_msg(self):
        packet = RxPacket(self.mcu, self.serport)
        return packet.receive()

    @staticmethod
    def _set_address(packet: Packet, addr, flash, region):
        packet.data8_n = 4
        packet.data += [(addr >> 0) & 0xFF]
        packet.data += [(addr >> 8) & 0xFF]
        packet.data += [(addr >> 16) & 0xFF]
        nvr = 1 if "nvr" in region else 0
        packet.data += [((nvr << 7) | (flash << 5)) & 0xFF]
        return nvr
