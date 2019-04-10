#!/user/bin/env python
# coding:utf-8

"""
K1921VKx Flasher Utility
"""

# -- Imports ------------------------------------------------------------------
import sys
import logger
import inspect
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog)
from ui_main import Ui_MainWindow
from ui_about import Ui_AboutDialog


# -- Global variables ---------------------------------------------------------
VERSION = "1.0"

EMULATION = True
EMULATED_MCU = "k1921vk035"


# -- Misc functions -----------------------------------------------------------
def whoami():
    return inspect.getouterframes(inspect.currentframe())[1].function


# -- Special classes ----------------------------------------------------------

# -- Main window --------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Set up the user interface from QtDesigner
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.about_dialog = QDialog(self)
        self.about_dialog.ui = Ui_AboutDialog()
        self.about_dialog.ui.setupUi(self.about_dialog)

        # Set vars
        self.connected = False
        self.flashn = 0
        self.nvr = False

    # -- Events --
    def closeEvent(self, event):
        event.accept()

    # -- Slots general --
    def handle_act_about_triggered(self):
        log_dbg("Handler <%s> called" % whoami())
        text = self.about_dialog.ui.lab_version.text().replace("x.x", VERSION)
        self.about_dialog.ui.lab_version.setText(text)
        self.about_dialog.exec_()

    def handle_combo_port_changed(self, num):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % num))

    def handle_combo_baud_changed(self, num):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % num))

    def handle_btn_connect_clicked(self):
        log_dbg("Handler <%s> called" % whoami())
        if not self.connected:
            state = True
            btn_text = "Отключиться"
        else:
            state = False
            btn_text = "Подключиться"

        # TODO: check if COM selected, and try to connect
        if EMULATION:
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
            self.connected = state

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
