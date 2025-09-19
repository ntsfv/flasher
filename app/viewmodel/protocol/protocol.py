import os

from model.logger.loggable import Loggable
from model.mcu import mcu
from model.protocol.commands.command_interface import CommandInterface
from model.protocol.protocol_exception import ProtException
from model.protocol.serport.serport import SerPort
from utils.utils import whoami, save_bin


class Protocol(Loggable):
    def __init__(self, mcu, serport: SerPort):
        Loggable.__init__(self)
        self.mcu = mcu
        self.serport = serport

    def open_bin(self, name):
        binfile = open(name, "rb")
        data = []
        while True:
            current_byte = binfile.read(1)
            if not current_byte:
                break
            data += [ord(current_byte)]
        binfile.close()
        self.logger.debug("Прочитано %0d байт данных из файла %s" % (len(data), name))
        return data

    # -- API --
    def init(self, **kwargs):
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport.open(port=kwargs['port'], baudrate=kwargs['baud']))
        # try:
        #     self.serport.open(port=kwargs['port'], baudrate=kwargs['baud'])
        # except:
        #     raise ProtException("Ошибка порта!")
        self.serport.reset_input_buffer()
        # self.win.pbar_set(25)
        cmd.init_device(kwargs['is_riscv'])
        # self.win.pbar_set(50)
        mcu_info = cmd.cmd_get_info()
        inited_mcu = mcu.get_by_chipid(mcu_info["chipid"])
        if inited_mcu is None:
            raise ProtException("Неизвестный CHIPID!")
        else:
            self.mcu = inited_mcu
            cmd.mcu = self.mcu
        # self.win.pbar_set(75)
        mcu_cfgword = cmd.cmd_get_cfgword()
        self.mcu.apply_cfgword(mcu_cfgword)
        self.mcu.cpuid = mcu_info['cpuid']
        self.mcu.bootver = mcu_info['bootver']
        self.logger.info("Обнаружен %s с версией загрузчика v%s" % (self.mcu.name_ru, self.mcu.bootver))
        # self.win.pbar_set(100)
        return self.mcu

    def deinit(self, **kwargs):
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        # self.win.pbar_set(50)
        cmd.release_device(kwargs['is_riscv'])
        self.serport.close()
        self.logger.info("Произведено отключение от устройства")
        # self.win.pbar_set(100)
        return True

    def write(self, **kwargs):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        region = kwargs['current_region'] # self.win.get_curr_region()
        flash = kwargs['current_flash'] # self.win.get_curr_flash()
        page_size = self.mcu.flash[flash][region].page_size
        jump = kwargs['jump']
        jumpaddr = kwargs['jumpaddr']

        raw_data = self.open_bin(kwargs['filepath'])
        self.logger.info("Дополнение бинарного файла до размера целой страницы ...")
        data = [0xFF] * (kwargs['lastpage'] - kwargs['firstpage'] + 1) * page_size
        for i in range(0, len(raw_data)):
            data[i] = raw_data[i]
        state = 0.0
        # self.win.pbar_set(state)

        cmd_count = 0
        if kwargs['erall']:
            cmd.cmd_erase_full(flash, region)
            cmd_count += 1
        state += 20.0
        # self.win.pbar_set(state)

        self.logger.info("Запись страниц%s:" % (" c предварительным стиранием" if kwargs['erpages'] else ""))
        for p in range(0, kwargs['lastpage'] - kwargs['firstpage'] + 1):
            cmd.cmd_write_page(kwargs['firstpage'] + p, data[p * page_size:p * page_size + page_size], flash, region, kwargs['erpages'])
            state += 15 / (kwargs['lastpage'] - kwargs['firstpage'] + 1)
            # self.win.pbar_set(state)
            cmd_count += 1

        self.logger.info("Ожидание выполнения команд ...")
        for i in range(0, cmd_count):
            cmd.cmd_msg()
            state += 20 / cmd_count
            # self.win.pbar_set(state)

        if kwargs["verif"]:
            self.logger.info("Верификация записанных данных ...")
            # read pages
            read_data = []
            for p in range(kwargs['firstpage'], kwargs['lastpage'] + 1):
                cmd.cmd_read_page(p, flash, region)
                state += 15 / (kwargs['lastpage'] - kwargs['firstpage'] + 1)
                # self.win.pbar_set(state)
            self.logger.info("Ожидание выполнения команд ...")
            for p in range(kwargs['firstpage'], kwargs['lastpage'] + 1):
                read_data += cmd.cmd_msg()['data']
                state += 20 / (kwargs['lastpage'] - kwargs['firstpage'] + 1)
                # self.win.pbar_set(state)
            # compare
            err = 0
            err_limit = 16
            for i in range(0, len(read_data)):
                if read_data[i] != data[i]:
                    err += 1
                    if err_limit > 0:
                        self.logger.error("Адрес 0%08X, записано 0x%02X - прочитано 0x%02X" % (i, data[i], read_data[i]), msgbox_en=False)
                        err_limit -= 1
                        if err_limit == 0:
                            self.logger.error("Показаны первые 16 ошибок верификации, дальнейшие показываться не будут")
            self.logger.info("Верификация завершилась, количество ошибок: %0d" % err)

        if jump:
            self.logger.info('Переход к исполнению программы - адрес 0x%08X' % jumpaddr)
            cmd.cmd_jump(jumpaddr)

        # self.win.pbar_set(100)

    def erase(self, **kwargs):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        region = kwargs['current_region'] # self.win.get_curr_region()
        flash = kwargs['current_region'] # self.win.get_curr_flash()
        cmd_count = 0
        state = 0.0
        # self.win.pbar_set(state)
        if kwargs['erall']:
            # self.win.pbar_set(50)
            cmd.cmd_erase_full(flash, region)
            cmd.cmd_msg()
        else:
            for p in range(kwargs['firstpage'], kwargs['lastpage'] + 1):
                cmd.cmd_erase_page(p, flash, region)
                state += 50 / (kwargs['lastpage'] - kwargs['firstpage'] + 1)
                # self.win.pbar_set(state)
                cmd_count += 1
            self.logger.info("Ожидание выполнения команд ...")
            for i in range(0, cmd_count):
                cmd.cmd_msg()
                state += 50 / cmd_count
                # self.win.pbar_set(state)
        # self.win.pbar_set(100)

    def read(self, **kwargs):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__),whoami()))
        self.logger.debug(kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        region = kwargs['current_region'] # self.win.get_curr_region()
        flash = kwargs['current_region'] # self.win.get_curr_flash()
        page_data = []
        state = 10.0
        # self.win.pbar_set(state)
        for page in range(kwargs['firstpage'], kwargs['lastpage'] + 1):
            cmd.cmd_read_page(page, flash, region)
            state += 40 / (kwargs['lastpage'] - kwargs['firstpage'] + 1)
            # self.win.pbar_set(state)
        self.logger.info("Ожидание выполнения команд ...")
        for page in range(kwargs['firstpage'], kwargs['lastpage'] + 1):
            page_data += cmd.cmd_msg()['data']
            state += 40 / (kwargs['lastpage'] - kwargs['firstpage'] + 1)
            # self.win.pbar_set(state)
        save_bin(kwargs['filepath'], page_data)
        # self.win.pbar_set(100)

    def get_cfgword(self, **kwargs):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        # self.win.pbar_set(50)
        cfgword = cmd.cmd_get_cfgword()
        # self.win.pbar_set(100)
        return cfgword

    def set_cfgword(self, **kwargs):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        # self.win.pbar_set(50)
        cmd.cmd_set_cfgword(kwargs['cfgword'])
        # self.win.pbar_set(100)

    def jump(self, **kwargs):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(kwargs)
        jumpaddr = kwargs['jumpaddr']
        self.logger.info('Переход к исполнению программы - адрес 0x%08X' % jumpaddr)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        # self.win.pbar_set(50)
        cmd.cmd_jump(jumpaddr)
        # self.win.pbar_set(100)

