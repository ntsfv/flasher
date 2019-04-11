#!/user/bin/env python
# coding:utf-8

"""
K1921VKx Flasher Utility
"""

# -- Imports ------------------------------------------------------------------
import sys
import logger
import inspect
import serport
import mcu
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog)
from ui_main import Ui_MainWindow
from ui_about import Ui_AboutDialog


# -- Global variables ---------------------------------------------------------
VERSION = "1.0"


# -- Misc functions -----------------------------------------------------------
def whoami():
    return inspect.getouterframes(inspect.currentframe())[1].function


# -- Test functions -----------------------------------------------------------
def test_init(port, baud):
    log_info("Открываю порт %s %s" % (port, baud))
    return {'chipid': '0x5A298FE1', 'cpuid': '0xDEADBEEF', 'bootver': '0.1'}


def test_deinit():
    log_info("Закрываю порт")
    return True


# -- Main window --------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Set up the user interface from QtDesigner
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        [self.ui.combo_port.addItem(port) for port in serport.list_ports()]
        self.timer = QTimer()
        self.timer.timeout.connect(self.handle_timer_tick)
        self.timer.start(3000)  # parse available serial ports every 3 sec

        self.about_dialog = QDialog(self)
        self.about_dialog.ui = Ui_AboutDialog()
        self.about_dialog.ui.setupUi(self.about_dialog)

        # Set vars
        self.mcu = mcu.get_by_name('k1921vkx')

    # -- Events --
    def closeEvent(self, event):
        event.accept()

    # -- Slots general --
    def handle_timer_tick(self):
        # log_dbg("Handler <%s> called" % whoami())
        self.ui.combo_port.clear()
        [self.ui.combo_port.addItem(port) for port in serport.list_ports()]

    def handle_act_about_triggered(self):
        log_dbg("Handler <%s> called" % whoami())
        text = self.about_dialog.ui.lab_version.text().replace("x.x", VERSION)
        self.about_dialog.ui.lab_version.setText(text)
        self.about_dialog.exec_()

    def handle_btn_connect_clicked(self):
        log_dbg("Handler <%s> called" % whoami())
        update_gui = False
        port = self.ui.combo_port.currentText()
        baud = self.ui.combo_baud.currentText()
        if not self.is_connected():
            state = True
            btn_text = "Отключиться"
            mcu_info = test_init(port, baud)
            if mcu_info:
                self.timer.stop()
                self.mcu = mcu.get_by_chipid(mcu_info['chipid'])
                update_gui = True
        else:
            state = False
            btn_text = "Подключиться"
            if test_deinit():
                self.timer.start()
                self.mcu = mcu.get_by_name('k1921vkx')
                mcu_info = {'chipid': '0xFFFFFFFF', 'cpuid': '0xFFFFFFFF', 'bootver': '0.0'}
                update_gui = True

        if update_gui:
            self.ui.btn_connect.setText(btn_text)
            self.ui.combo_port.setEnabled(not state)
            self.ui.combo_baud.setEnabled(not state)
            self.ui.tab_info.setEnabled(state)
            self.ui.tab_write.setEnabled(state)
            self.ui.tab_erase.setEnabled(state)
            self.ui.tab_read.setEnabled(state)
            self.ui.tab_config.setEnabled(state)
            self.ui.frm_flash.setEnabled(state)
            self.ui.btn_exec.setEnabled(state)
            self.upd_frm_flash()
            self.upd_tinfo_values(mcu_info)

    def handle_flash_select_toggled(self, state):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % state))
        if state:
            if self.ui.rbtn_flash0.isChecked():
                self.flashn = 0
                flash_name = "FLASH0"
            else:
                self.flashn = 1
                flash_name = "FLASH1"
            log_info("Выбрана флеш-память %s" % flash_name)

    def handle_chbox_nvr_toggled(self, state):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % state))
        if self.ui.chbox_nvr.isChecked():
            self.nvr = True
            region_name = "NVR/Info"
        else:
            self.nvr = False
            region_name = "основная"
        log_info("Выбрана %s область флеш-памяти" % region_name)

    def handle_btn_exec_clicked(self):
        log_dbg("Handler <%s> called" % whoami())

    # -- Slots for Write Tab widgets --
    def handle_twrite_ledit_filepath_editint_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_twrite_ledit_addr_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_twrite_btn_fileopen_clicked(self):
        log_dbg("Handler <%s> called" % whoami())

    # -- Slots for Erase Tab widgets --
    def handle_terase_ledit_firstpage_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_terase_ledit_lastpage_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_terase_ledit_addrstart_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_terase_ledit_bytes_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    # -- Slots for Read Tab widgets --
    def handle_tread_ledit_filepath_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_tread_btn_fileopen_clicked(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_tread_ledit_firstpage_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_tread_ledit_lastpage_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_tread_ledit_addrstart_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_tread_ledit_bytes_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_tread_chbox_verif_toggled(self, state):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % state))

    def handle_tread_ledit_verif_filepath_editing_finished(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_tread_btn_verif_fileopen_clicked(self):
        log_dbg("Handler <%s> called" % whoami())

    # -- Application specific code --
    def is_connected(self):
        return not self.ui.combo_port.isEnabled()

    def upd_frm_flash(self):
        self.ui.rbtn_flash0.setText(self.mcu.flash[0]['name'].upper())
        if len(self.mcu.flash) == 2:
            self.ui.rbtn_flash1.setEnabled(True)
            self.ui.rbtn_flash1.setText(self.mcu.flash[1]['name'].upper())
        else:
            self.ui.rbtn_flash1.setEnabled(False)
            self.ui.rbtn_flash1.setText('')

    def upd_tinfo_values(self, info):
        self.ui.tinfo_ledit_chipid.setText(info['chipid'])
        self.ui.tinfo_ledit_cpuid.setText(info['cpuid'])
        self.ui.tinfo_ledit_bootver.setText(info['bootver'])
        self.ui.tinfo_lab_mcu.setText(self.mcu.name_ru)


# -- Standalone run -----------------------------------------------------------
if __name__ == '__main__':
    logger.init(debug=True, logfile="flasher.log")

    def log_dbg(msg):
        logger.debug(msg)

    def log_info(msg):
        logger.info(msg)
        main_window.ui.tedit_log.appendHtml('[<span style=" color:#4e9a06;">INFO</span>]: %s' % msg)

    def log_warn(msg):
        logger.warning(msg)
        main_window.ui.tedit_log.appendHtml('[<span style=" color:#e9b96e;">WARN</span>]: %s' % msg)

    def log_err(msg):
        logger.error(msg)
        main_window.ui.tedit_log.appendHtml('[<span style=" color:#ef2929;">ERR</span>]: %s' % msg)

    def log_crit(msg):
        logger.critical(msg)
        main_window.ui.tedit_log.appendHtml('[<span style=" color:#ad7fa8;">CRIT</span>]: %s' % msg)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
