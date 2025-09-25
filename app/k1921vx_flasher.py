import getopt
import sys
import traceback

from PyQt5.QtWidgets import QApplication

from utils.constants import VERSION
from viewmodel.main_window_viewmodel import MainWindowViewModel

from dotenv import load_dotenv

class ArgParser:
    def help(self):
        print("""Утилита взаимодействия с UART загрузчиками микроконтроллеров серии К1921ВКх.
Версия v.%s

Доступные ключи: [-hDсeEwvr] [-f flash] [-n region] [-j addr] [-F first] [-L last] [-a addr] [-s size] [-p port] [-b baud] [file.bin]
        -h          Вывод этого сообщения
        -D          Включить вывод отладочной информации
        -с          Командный режим (без графического интерфейса). Наличие ключа необходимо для выполнения любой команды.
        -f flash    Выбор флеш-памяти. Допустимые значения 'flash' для разных микроконтроллеров:
                    bootflash, userflash, mflash, bflash
        -n region   Выбор области флеш-памяти. Допустимые значения 'region' для разных микроконтроллеров:
                    main, nvr, info
        -e          Стереть 'pages' страниц, начиная от 'first'
        -E          Полное стирание
        -w          Записать 'file.bin' начиная со страницы 'first'. Если добавлены ключи -e или -E - перед записью будет проведено стирание.
        -v          Верифицировать записанный 'file.bin' (может быть использовано только в паре с -w)
        -r          Прочитать в файл 'file.bin' страницы от 'first' по 'last' включительно
        -j addr     Переход на исполнение по глобальному адресу (по этому адресу расположена таблица векторов прерываний)
        -F first    Номер первой страницы для выполнения команд
        -L pages    Количество страниц для выполнения команд
        -a addr     Выбор адреса для выполнения команд
        -s size     Выбор размера области для выполнения команд
        -p port     COM-порт
        -b baud     Баудрейт

        Запись файла led.bin в основную область MFLASH К1921ВК035 с 0 страницы с полным стиранием, верификацией записанного:
        python3 k1921vkx_flasher.py -cwEv -f mflash -n main -F 0 -p /dev/ttyUSB0 -b 115200 led.bin

        Чтение 4096 байт данных с 0 адреса в файл dump.bin
        python3 k1921vkx_flasher.py -cr -p /dev/ttyUSB0 -b 115200 -f mflash -n main -a 0 -s 0x1000 dump.bin

        Чтение первых 8 страниц в файл dump.bin
        python3 k1921vkx_flasher.py -cr -p /dev/ttyUSB0 -b 115200 -f mflash -n main -F 0 -L 8 dump.bin

        Стирание первых 8 страниц
        python3 k1921vkx_flasher.py -ce -p /dev/ttyUSB0 -b 115200 -f mflash -n main -F 0 -L 8

        Полное стирание
        python3 k1921vkx_flasher.py -cE -p /dev/ttyUSB0 -b 115200 -f mflash -n main

НИИЭТ, 2025""" % VERSION)

    def do(self, app, win):
        conf = {
            "port": None,
            "baud": None,
            "flash": None,
            "region": None,
            "first_page": None,
            "pages_used": None,
            "addr": None,
            "size": None,
            "cmd_mode": None,
            "debug": None,
            "erase": None,
            "mass_erase": None,
            "write": None,
            "verify": None,
            "read": None,
            "jump_prog": None,
        }

        try:
            opts, args = getopt.getopt(sys.argv[1:], "hDceEwvrf:n:j:F:L:a:s:p:b:")
        except getopt.GetoptError:
            self.help()
            sys.exit(2)

        if args:
            conf['filepath'] = args[0]

        for o, a in opts:
            #print(o)
            #print(a)
            if o == '-h':
                self.help()
                sys.exit(0)
            elif o == '-c':
                conf['cmd_mode'] = True
            elif o == '-D':
                conf['debug'] = True
            elif o == '-e':
                conf['erase'] = True
            elif o == '-E':
                conf['mass_erase'] = True
            elif o == '-w':
                conf['write'] = True
            elif o == '-v':
                conf['verify'] = True
            elif o == '-r':
                conf['read'] = True
            elif o == '-j':
                conf['jump_prog'] = eval(a)
            elif o == '-p':
                conf['port'] = a
            elif o == '-b':
                conf['baud'] = a
            elif o == '-f':
                conf['flash'] = a
            elif o == '-n':
                conf['region'] = a
            elif o == '-F':
                conf['first_page'] = eval(a)
            elif o == '-L':
                conf['pages_used'] = eval(a)
            elif o == '-a':
                conf['addr'] = eval(a)
            elif o == '-s':
                conf['size'] = eval(a)
            else:
                self.help()
                sys.exit(1)
        return conf


# -- Standalone run -----------------------------------------------------------
if __name__ == '__main__':
    load_dotenv()
    app = QApplication(sys.argv)

    main_window = MainWindowViewModel()
    arg_parser = ArgParser()
    conf = arg_parser.do(app, main_window)
    main_window.debug = conf['debug']
    if conf['cmd_mode'] is None:
        main_window.show()
        sys.exit(app.exec_())
    else:
        def cmd_exit():
            global main_window
            if main_window.serport.is_open:
                main_window._protocol_deinit()
            sys.exit()

        main_window.logger.info("Режим без графического интерфейса")
        main_window.ui.btn_updport.clicked.emit()
        try:
            port_i = main_window.ui.combo_port.findText(conf['port'])
            main_window.ui.combo_port.setCurrentIndex(port_i)
            baud_i = main_window.ui.combo_baud.findText(conf['baud'])
            main_window.ui.combo_baud.setCurrentIndex(baud_i)
        except:
            main_window.logger.error("Заданы некорректные параметры порта!")
            traceback.print_exc()
            cmd_exit()
        main_window.ui.btn_connect.clicked.emit()
        if main_window.mcu.name == 'k1921':
            cmd_exit()
        flash = {'bootflash': 0, 'userflash': 1, 'mflash': 0, 'bflash': 1}
        region = {'main': 0, 'nvr': 1, 'info': 1}
        flash_rbtn = [main_window.ui.rbtn_flash0, main_window.ui.rbtn_flash1]
        region_rbtn = [main_window.ui.rbtn_regionmain, main_window.ui.rbtn_regionnvr]
        try:
            flash_rbtn[flash[conf['flash']]].setChecked(True)
            region_rbtn[region[conf['region']]].setChecked(True)
        except:
            main_window.logger.error("Заданы некорректные параметры флеш-памяти!")
            traceback.print_exc()
            cmd_exit()
        if conf['read']:
            main_window.logger.debug("CMD_READ")
            main_window.ui.tabs_cmd.setCurrentIndex(3)
            if conf['filepath']:
                main_window.ui.tread_ledit_filepath.setText(conf['filepath'])
                main_window.ui.tread_ledit_filepath.textEdited['QString'].emit(conf['filepath'])
            if conf['addr']:
                main_window.ui.tread_ledit_addr.setText('0x%08X' % conf['addr'])
                main_window.ui.tread_ledit_addr.editingFinished.emit()
            if conf['size']:
                main_window.ui.tread_ledit_size.setText('0x%08X' % conf['size'])
                main_window.ui.tread_ledit_size.editingFinished.emit()
            if conf['first_page']:
                main_window.ui.tread_ledit_page.setText('%d' % conf['first_page'])
                main_window.ui.tread_ledit_page.editingFinished.emit()
            if conf['pages_used']:
                main_window.ui.tread_ledit_pages.setText('%d' % conf['pages_used'])
                main_window.ui.tread_ledit_pages.editingFinished.emit()
            main_window.ui.btn_exec.clicked.emit()
        elif conf['write']:
            main_window.logger.debug("CMD_WRITE")
            main_window.ui.tabs_cmd.setCurrentIndex(1)
            if conf['filepath']:
                main_window.ui.twrite_ledit_filepath.setText(conf['filepath'])
                main_window.ui.twrite_ledit_filepath.textEdited['QString'].emit(conf['filepath'])
            if conf['addr']:
                main_window.ui.twrite_ledit_addr.setText('0x%08X' % conf['addr'])
                main_window.ui.twrite_ledit_addr.editingFinished.emit()
            if conf['first_page']:
                main_window.ui.twrite_ledit_page.setText('%d' % conf['first_page'])
                main_window.ui.twrite_ledit_page.editingFinished.emit()
            if conf['erase']:
                main_window.ui.twrite_rbtn_erpages.setChecked(True)
            elif conf['mass_erase']:
                main_window.ui.twrite_rbtn_erall.setChecked(True)
            else:
                main_window.ui.twrite_rbtn_ernone.setChecked(True)
            if conf['verify']:
                main_window.ui.twrite_chbox_verif.setChecked(True)
            # TODO: добавить софтварный выход из загрузчика
            # if conf['jump_prog']:
            #     main_window.ui.twrite_chbox_jump.setEnabled(True)
            #     main_window.ui.twrite_ledit_jumpaddr.setText('0x%08X' % conf['jump_prog'])
            #     main_window.ui.twrite_ledit_jumpaddr.editingFinished.emit()
            main_window.ui.btn_exec.clicked.emit()
        elif conf['mass_erase']:
            main_window.logger.debug("CMD_MASS_ERASE")
            main_window.ui.tabs_cmd.setCurrentIndex(2)
            main_window.ui.terase_rbtn_erall.setChecked(True)
            main_window.ui.btn_exec.clicked.emit()
        elif conf['erase']:
            main_window.logger.debug("CMD_ERASE")
            main_window.ui.tabs_cmd.setCurrentIndex(2)
            main_window.ui.terase_rbtn_erpages.setChecked(True)
            if conf['addr']:
                main_window.ui.terase_ledit_addr.setText('0x%08X' % conf['addr'])
                main_window.ui.terase_ledit_addr.editingFinished.emit()
            if conf['size']:
                main_window.ui.terase_ledit_size.setText('0x%08X' % conf['size'])
                main_window.ui.terase_ledit_size.editingFinished.emit()
            if conf['first_page']:
                main_window.ui.terase_ledit_page.setText('%d' % conf['first_page'])
                main_window.ui.terase_ledit_page.editingFinished.emit()
            if conf['pages_used']:
                main_window.ui.terase_ledit_pages.setText('%d' % conf['pages_used'])
                main_window.ui.terase_ledit_pages.editingFinished.emit()
            main_window.ui.btn_exec.clicked.emit()
        else:
            main_window.logger.error("Команда не задана. Запустите программу с ключом -h чтобы увидеть подсказки")
        cmd_exit()
