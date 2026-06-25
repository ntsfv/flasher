import os
import sys
import traceback

from model.logger.loggable import Loggable
from model.mcu.mcu import get_by_chipid
from model.protocol.commands.command_interface import CommandInterface
from model.protocol.protocol_exception import ProtException
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal
from utils.utils import read_bin, save_bin, whoami


class CommandSignals(QObject):
    data = pyqtSignal(object)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    pbar_signal = pyqtSignal(float)


class BaseCommandRunnable(QRunnable, Loggable):
    signals = CommandSignals()

    def __init__(self, mcu, serport, **kwargs):
        QRunnable.__init__(
            self,
        )
        Loggable.__init__(self)
        self.cmd = CommandInterface(mcu, serport)
        self.mcu = mcu
        self.serport = serport
        self.kwargs = kwargs

    def run(self):
        try:
            self._run()
        except ProtException as e:
            self.signals.error.emit("Ошибка протокола.")
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted_lines = traceback.format_exc()
            print(f"Трассировка:\n{formatted_lines}")
            self.signals.error.emit("Неизвестная ошибка: " + repr(e))

        finally:
            self.signals.finished.emit()

    def _run(self):
        pass


class InitPortRunnable(BaseCommandRunnable):
    def __init__(self, mcu, serport, **kwargs):
        super().__init__(mcu, serport, **kwargs)

    def _run(self):
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(self.kwargs)
        try:
            self.serport.open(port=self.kwargs["port"], baudrate=self.kwargs["baud"])
        except:
            raise ProtException("Ошибка порта!")
        self.serport.reset_input_buffer()
        self.signals.pbar_signal.emit(25)
        self.cmd.init_device(self.kwargs["is_riscv"])
        self.signals.pbar_signal.emit(50)
        mcu_info = self.cmd.cmd_get_info()
        inited_mcu = get_by_chipid(mcu_info["chipid"])
        if inited_mcu is None:
            raise ProtException("Неизвестный CHIPID!")
        else:
            self.mcu = inited_mcu
            self.cmd.mcu = self.mcu
        self.signals.pbar_signal.emit(75)
        mcu_cfgword = self.cmd.cmd_get_cfgword()
        self.mcu.apply_cfgword(mcu_cfgword)
        self.mcu.cpuid = mcu_info["cpuid"]
        self.mcu.bootver = mcu_info["bootver"]
        self.logger.info(
            "Обнаружен %s с версией загрузчика v%s"
            % (self.mcu.name_ru, self.mcu.bootver)
        )

        self.signals.pbar_signal.emit(100)
        self.signals.data.emit(self.mcu)
        self.signals.finished.emit()


class DeInitPortRunnable(BaseCommandRunnable):
    def __init__(self, mcu, serport, **kwargs):
        super().__init__(mcu, serport, **kwargs)

    def _run(self):
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(self.kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        self.signals.pbar_signal.emit(50)
        cmd.release_device(self.kwargs["is_riscv"])
        self.serport.close()
        self.logger.info("Произведено отключение от устройства")

        self.signals.pbar_signal.emit(100)
        self.signals.finished.emit()


class WritePortRunnable(BaseCommandRunnable):
    def __init__(self, mcu, serport, **kwargs):
        super().__init__(mcu, serport, **kwargs)

    def _run(self):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(self.kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        region = self.kwargs["current_region"]
        flash = self.kwargs["current_flash"]
        page_size = self.mcu.flash[flash][region].page_size
        jump = self.kwargs["jump"]
        jumpaddr = self.kwargs["jumpaddr"]

        raw_data = read_bin(self.kwargs["filepath"])
        self.logger.debug(
            "Прочитано %0d байт данных из файла %s"
            % (len(raw_data), self.kwargs["filepath"])
        )
        self.logger.info("Дополнение бинарного файла до размера целой страницы ...")
        data = (
            [0xFF]
            * (self.kwargs["lastpage"] - self.kwargs["firstpage"] + 1)
            * page_size
        )
        for i in range(0, len(raw_data)):
            data[i] = raw_data[i]
        state = 0.0
        self.signals.pbar_signal.emit(state)

        cmd_count = 0
        if self.kwargs["erall"]:
            cmd.cmd_erase_full(flash, region)
            cmd_count += 1
        state += 20.0
        self.signals.pbar_signal.emit(state)

        self.logger.info(
            "Запись страниц%s:"
            % (" c предварительным стиранием" if self.kwargs["erpages"] else "")
        )
        for p in range(0, self.kwargs["lastpage"] - self.kwargs["firstpage"] + 1):
            cmd.cmd_write_page(
                self.kwargs["firstpage"] + p,
                data[p * page_size : p * page_size + page_size],
                flash,
                region,
                self.kwargs["erpages"],
            )
            state += 15 / (self.kwargs["lastpage"] - self.kwargs["firstpage"] + 1)
            self.signals.pbar_signal.emit(state)
            cmd_count += 1

        self.logger.info("Ожидание выполнения команд ...")
        for i in range(0, cmd_count):
            cmd.cmd_msg()
            state += 20 / cmd_count
            self.signals.pbar_signal.emit(state)

        if self.kwargs["verif"]:
            self.logger.info("Верификация записанных данных ...")
            # read pages
            read_data = []
            for p in range(self.kwargs["firstpage"], self.kwargs["lastpage"] + 1):
                cmd.cmd_read_page(p, flash, region)
                state += 15 / (self.kwargs["lastpage"] - self.kwargs["firstpage"] + 1)
                self.signals.pbar_signal.emit(state)
            self.logger.info("Ожидание выполнения команд ...")
            for p in range(self.kwargs["firstpage"], self.kwargs["lastpage"] + 1):
                read_data += cmd.cmd_msg()["data"]
                state += 20 / (self.kwargs["lastpage"] - self.kwargs["firstpage"] + 1)
                self.signals.pbar_signal.emit(state)
            # compare
            err = 0
            err_limit = 16
            for i in range(0, len(read_data)):
                if read_data[i] != data[i]:
                    err += 1
                    if err_limit > 0:
                        self.logger.error(
                            "Адрес 0%08X, записано 0x%02X - прочитано 0x%02X"
                            % (i, data[i], read_data[i])
                        )
                        err_limit -= 1
                        if err_limit == 0:
                            self.logger.error(
                                "Показаны первые 16 ошибок верификации, дальнейшие показываться не будут"
                            )
            self.logger.info("Верификация завершилась, количество ошибок: %0d" % err)

        if jump:
            self.logger.info("Переход к исполнению программы - адрес 0x%08X" % jumpaddr)
            cmd.cmd_jump(jumpaddr)
            self.signals.data.emit(True)

        self.signals.pbar_signal.emit(100)
        self.signals.finished.emit()


class ErasePortRunnable(BaseCommandRunnable):
    def __init__(self, mcu, serport, **kwargs):
        super().__init__(mcu, serport, **kwargs)

    def _run(self):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(self.kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        region = self.kwargs["current_region"]
        flash = self.kwargs["current_flash"]
        cmd_count = 0
        state = 0.0
        self.signals.pbar_signal.emit(state)
        if self.kwargs["erall"]:
            self.signals.pbar_signal.emit(50)
            cmd.cmd_erase_full(flash, region)
            cmd.cmd_msg()
        else:
            for p in range(self.kwargs["firstpage"], self.kwargs["lastpage"] + 1):
                cmd.cmd_erase_page(p, flash, region)
                state += 50 / (self.kwargs["lastpage"] - self.kwargs["firstpage"] + 1)
                self.signals.pbar_signal.emit(state)
                cmd_count += 1
            self.logger.info("Ожидание выполнения команд ...")
            for i in range(0, cmd_count):
                cmd.cmd_msg()
                state += 50 / cmd_count
                self.signals.pbar_signal.emit(state)

        self.signals.pbar_signal.emit(100)
        self.signals.finished.emit()


class ReadPortRunnable(BaseCommandRunnable):
    def __init__(self, mcu, serport, **kwargs):
        super().__init__(mcu, serport, **kwargs)

    def _run(self):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(self.kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        region = self.kwargs["current_region"]
        flash = self.kwargs["current_flash"]
        page_data = []
        state = 10.0
        self.signals.pbar_signal.emit(state)
        for page in range(self.kwargs["firstpage"], self.kwargs["lastpage"] + 1):
            cmd.cmd_read_page(page, flash, region)
            state += 40 / (self.kwargs["lastpage"] - self.kwargs["firstpage"] + 1)
            self.signals.pbar_signal.emit(state)
        self.logger.info("Ожидание выполнения команд ...")
        for page in range(self.kwargs["firstpage"], self.kwargs["lastpage"] + 1):
            page_data += cmd.cmd_msg()["data"]
            state += 40 / (self.kwargs["lastpage"] - self.kwargs["firstpage"] + 1)
            self.signals.pbar_signal.emit(state)
        save_bin(self.kwargs["filepath"], page_data)

        self.signals.pbar_signal.emit(100)
        self.signals.finished.emit()


class GetCfgWordPortRunnable(BaseCommandRunnable):
    def __init__(self, mcu, serport, **kwargs):
        super().__init__(mcu, serport, **kwargs)

    def _run(self):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(self.kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        self.signals.pbar_signal.emit(50)
        cfgword = cmd.cmd_get_cfgword()
        self.signals.pbar_signal.emit(100)
        self.signals.data.emit(cfgword)
        self.signals.finished.emit()


class SetCfgWordPortRunnable(BaseCommandRunnable):
    def __init__(self, mcu, serport, **kwargs):
        super().__init__(mcu, serport, **kwargs)

    def _run(self):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(self.kwargs)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        self.signals.pbar_signal.emit(50)
        cmd.cmd_set_cfgword(self.kwargs["cfgword"])
        self.signals.pbar_signal.emit(100)


class JumpPortRunnable(BaseCommandRunnable):
    def __init__(self, mcu, serport, **kwargs):
        super().__init__(mcu, serport, **kwargs)

    def _run(self):
        self.serport.reset_input_buffer()
        self.logger.debug("%s->%s()" % (os.path.basename(__file__), whoami()))
        self.logger.debug(self.kwargs)
        jumpaddr = self.kwargs["jumpaddr"]
        self.logger.info("Переход к исполнению программы - адрес 0x%08X" % jumpaddr)
        cmd = CommandInterface(mcu=self.mcu, serport=self.serport)
        self.signals.pbar_signal.emit(50)
        cmd.cmd_jump(jumpaddr)
        self.signals.pbar_signal.emit(100)
