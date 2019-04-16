#!/user/bin/env python
# coding:utf-8

"""
K1921VKx Flasher Utility
"""

# -- Imports ------------------------------------------------------------------
import sys
import os
import logger
import inspect
import serport
import mcu
import protocol as prot
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QTableWidgetItem,
                             QHeaderView, QAction, QFileDialog, QLineEdit, QFrame, QWidget)
from PyQt5.QtGui import (QIcon, QPixmap, QCursor, QRegExpValidator)
from ui_main import Ui_MainWindow
from ui_about import Ui_AboutDialog
from ui_config035 import Ui_Config035
from ui_config028 import Ui_Config028
from ui_config01t import Ui_Config01T
from ui_config1921 import Ui_Config1921


# -- Global variables ---------------------------------------------------------
VERSION = "1.0"


# -- Misc functions -----------------------------------------------------------
def whoami():
    return inspect.getouterframes(inspect.currentframe())[1].function


# -- Main window --------------------------------------------------------------
class MyMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Set up the user interface from QtDesigner
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.tconfig_widget_cfg = QWidget(self.ui.tab_config)
        self.ui.tconfig_vbox.addWidget(self.ui.tconfig_widget_cfg)

        self.ui.tconfig_frm_cfg = QFrame(self.ui.tab_config)

        self.ui.btn_updport.clicked.emit()

        self.ui.tedit_log.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tedit_log.customContextMenuRequested.connect(self.handle_tedit_log_context_menu)

        self.icon_lock = QIcon()
        self.icon_unlock = QIcon()
        self.icon_lock.addPixmap(QPixmap(":/icons/lock.png"))
        self.icon_unlock.addPixmap(QPixmap(":/icons/unlock.png"))
        self.ui.tinfo_tbl_flash.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(0, 120)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(1, 120)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(2, 120)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(3, 40)
        self.ui.tinfo_tbl_flash.horizontalHeader().resizeSection(4, 40)
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(3).setToolTip("Чтение")
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(4).setToolTip("Запись")

        self.mcu = mcu.get_by_name('k1921vkx')
        self.upd_tinfo_table()
        self.upd_tconfig_widget_cfg()

        self.ui.twrite_ledit_filepath.path_for_open = True
        self.ui.tread_ledit_filepath.path_for_open = False
        self.ui.tread_ledit_verif_filepath.path_for_open = True
        self.ui.twrite_ledit_filepath.last_text = ""
        self.ui.tread_ledit_filepath.last_text = ""
        self.ui.tread_ledit_verif_filepath.last_text = ""

        allowed_nums = "^((0x|)[0-9A-Fa-f]{1,8})|([0-9]{1,10})$"
        self.ui.twrite_ledit_addrstart.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_firstpage.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_lastpage.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_addrstart.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_bytes.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))

        self.about_dialog = QDialog(self)
        self.about_dialog.ui = Ui_AboutDialog()
        self.about_dialog.ui.setupUi(self.about_dialog)

    # -- Events --
    def closeEvent(self, event):
        prot.deinit()
        event.accept()

    # -- Slots --
    def handle_tedit_log_context_menu(self, pos):
        log_dbg("Handler <%s> called" % whoami())
        menu = self.ui.tedit_log.createStandardContextMenu()
        menu.act_clear = QAction("Очистить")
        menu.act_clear.triggered.connect(self.ui.tedit_log.clear)
        menu.insertActions(menu.actions()[0], [menu.act_clear])
        menu.exec_(QCursor.pos())

    def handle_btn_updport_clicked(self):
        log_dbg("Handler <%s> called" % whoami())
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
        if (not self.is_connected()):
            if not self.ui.combo_port.count():
                log_err("Выберите COM-порт!")
            else:
                state = True
                btn_text = "Отключиться"
                mcu_info = prot.init(port=port, baud=baud)
                if mcu_info:
                    self.mcu = mcu.get_by_chipid(mcu_info['chipid'])
                    update_gui = True
        else:
            state = False
            btn_text = "Подключиться"
            if prot.deinit():
                self.mcu = mcu.get_by_name('k1921vkx')
                mcu_info = {'chipid': '0xFFFFFFFF', 'cpuid': '0xFFFFFFFF', 'bootver': '0.0'}
                update_gui = True

        if update_gui:
            self.ui.btn_connect.setText(btn_text)
            self.ui.combo_port.setEnabled(not state)
            self.ui.combo_baud.setEnabled(not state)
            self.ui.btn_updport.setEnabled(not state)
            self.ui.tab_info.setEnabled(state)
            self.ui.tab_write.setEnabled(state)
            self.ui.tab_erase.setEnabled(state)
            self.ui.tab_read.setEnabled(state)
            self.ui.tab_config.setEnabled(state)
            self.ui.gbox_flash.setEnabled(state)
            self.ui.gbox_region.setEnabled(state)
            self.ui.btn_exec.setEnabled(state)
            self.upd_gbox_flash()
            self.upd_tinfo_values(mcu_info)
            self.upd_tinfo_table()
            self.upd_tconfig_widget_cfg()

    def handle_flash_select_toggled(self, state):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % state))
        if state:
            if self.ui.rbtn_flash0.isChecked():
                flash_name = self.ui.rbtn_flash0.text()
            else:
                flash_name = self.ui.rbtn_flash1.text()
            log_info("Выбрана флеш-память %s" % flash_name)
            self.upd_tinfo_table()

    def handle_region_select_toggled(self, state):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % state))
        if state:
            if self.ui.rbtn_regionmain.isChecked():
                region_name = "основная"
            else:
                region_name = "NVR/Info"
            log_info("Выбрана %s область" % region_name)
            self.upd_tinfo_table()

    def handle_btn_exec_clicked(self):
        log_dbg("Handler <%s> called" % whoami())

    def handle_ledit_filepath_changed(self, text):
        log_dbg("Handler <%s> called" % whoami())

        if self.sender().path_for_open:
            if (os.path.isfile(self.sender().text()) and self.sender().text()[-4:] == '.bin' and self.sender().text() != self.sender().last_text):

                # TODO: поместить это в секцию исполнения
                log_info('Выбран файл "%s"' % self.sender().text())
                log_info('Размер %d байт' % os.path.getsize(self.sender().text()))

                self.sender().setStyleSheet("color: black;")
            else:
                self.sender().setStyleSheet("color: red;")
        self.sender().last_text = self.sender().text()

    def handle_btn_fileopen_clicked(self):
        log_dbg("Handler <%s> called" % whoami())
        rexp_ledit = QtCore.QRegExp('^.*_filepath$')
        linked_ledit = self.sender().parent().findChildren(QLineEdit, rexp_ledit)[0]
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть бинарный файл", linked_ledit.text(), "Бинарные файлы (*.bin)",
                                                  options=options)
        if filename:
            linked_ledit.setText(filename)

    def handle_btn_filesave_clicked(self):
        log_dbg("Handler <%s> called" % whoami())
        rexp_ledit = QtCore.QRegExp('^.*_filepath$')
        linked_ledit = self.sender().parent().findChildren(QLineEdit, rexp_ledit)[0]
        options = QFileDialog.Options()
        if linked_ledit.text():
            save_name = linked_ledit.text()
        else:
            save_name = "dump.bin"
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить бинарный файл", save_name, "Бинарные файлы (*.bin)",
                                                  options=options)
        if filename:
            linked_ledit.setText(filename)

    def handle_tread_chbox_verif_toggled(self, state):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % state))
        self.ui.tread_ledit_verif_filepath.setEnabled(state)
        self.ui.tread_btn_verif_fileopen.setEnabled(state)
        self.ui.tread_lab_verif_fileopen.setEnabled(state)

    def handle_terase_mode_select_toggled(self, state):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % state))
        if state:
            self.ui.terase_frm_addr.setEnabled(self.ui.terase_rbtn_erpages.isChecked())

    def handle_tconfig_mode_select_toggled(self, state):
        log_dbg("Handler <%s> called" % (whoami() + "(%d)" % state))
        if state:
            self.ui.tconfig_widget_cfg.ui.tconfig_frm_cfg.setEnabled(self.ui.tconfig_rbtn_write.isChecked())

    # -- Application specific code --
    def is_connected(self):
        return not self.ui.combo_port.isEnabled()

    def is_nvr(self):
        return self.ui.rbtn_regionnvr.isChecked()

    def curr_flash(self):
        if self.ui.rbtn_flash0.isChecked():
            return 0
        else:
            return 1

    def upd_tconfig(self, state):
        if state:
            pass
        else:
            for child in self.ui.tconfig_frm_cfg.children():
                if not (child.objectName() == 'tconfig_lbl_warn0'):
                    child.deleteLater()

    def upd_gbox_flash(self):
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

    def upd_tinfo_table(self):
        table = self.ui.tinfo_tbl_flash
        table.clearContents()
        for r in reversed(range(table.rowCount())):
            table.removeRow(r)
        if self.is_nvr():
            region = 'region_nvr'
        else:
            region = 'region_main'
        pages = self.mcu.flash[self.curr_flash()][region].pages
        page_size = self.mcu.flash[self.curr_flash()][region].page_size
        rd_lock = self.mcu.flash[self.curr_flash()][region].rd_lock
        wr_lock = self.mcu.flash[self.curr_flash()][region].wr_lock
        for r in range(0, pages):
            table.insertRow(r)
            table.setItem(r, 0, QTableWidgetItem("Страница %d" % r))
            table.setItem(r, 1, QTableWidgetItem("0x%x" % (r * page_size)))
            if page_size < 1024:
                page_size_str = "0x%08x (%d)" % (page_size, page_size)
            else:
                page_size_str = "0x%x (%dK)" % (page_size, page_size // 1024)
            table.setItem(r, 2, QTableWidgetItem("%s" % page_size_str))
            if rd_lock[r]:
                rd_cell = QTableWidgetItem(self.icon_lock, "")
                rd_cell.setToolTip("Заблокировано")
            else:
                rd_cell = QTableWidgetItem(self.icon_unlock, "")
                rd_cell.setToolTip("Разблокировано")
            table.setItem(r, 3, rd_cell)
            if wr_lock[r]:
                wr_cell = QTableWidgetItem(self.icon_lock, "")
                wr_cell.setToolTip("Заблокировано")
            else:
                wr_cell = QTableWidgetItem(self.icon_unlock, "")
                wr_cell.setToolTip("Разблокировано")
            table.setItem(r, 4, wr_cell)

    def upd_tconfig_widget_cfg(self):
        self.ui.tconfig_rbtn_read.setChecked(True)
        self.ui.tconfig_vbox.removeWidget(self.ui.tconfig_widget_cfg)
        self.ui.tconfig_widget_cfg.deleteLater()
        self.ui.tconfig_widget_cfg = None

        self.ui.tconfig_widget_cfg = QWidget(self.ui.tab_config)
        self.ui.tconfig_vbox.addWidget(self.ui.tconfig_widget_cfg)
        # pre-setup
        if self.mcu.name == 'k1921vk035':
            self.ui.tconfig_widget_cfg.ui = Ui_Config035()
        elif self.mcu.name == 'k1921vk028':
            self.ui.tconfig_widget_cfg.ui = Ui_Config028()
        elif self.mcu.name == 'k1921vk01t':
            self.ui.tconfig_widget_cfg.ui = Ui_Config01T()
        elif self.mcu.name == 'k1921vkx':
            self.ui.tconfig_widget_cfg.ui = Ui_Config1921()
        # setup
        self.ui.tconfig_widget_cfg.ui.setupUi(self.ui.tconfig_widget_cfg)
        # post-setup
        if self.mcu.name == 'k1921vk035':
            pass
        elif self.mcu.name == 'k1921vk028':
            allowed_nums = "^((0x|)[0-9A-Fa-f]{1,3})|([0-9]{1,4})$"
            self.ui.tconfig_widget_cfg.ui.ledit_mask.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
            allowed_nums = "^((0x|)[0-9A-Fa-f]{1})|([0-9]{1,2})$"
            self.ui.tconfig_widget_cfg.ui.ledit_wrc.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
            self.ui.tconfig_widget_cfg.ui.ledit_rdc.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
            self.ui.tconfig_widget_cfg.ui.ledit_tac.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        elif self.mcu.name == 'k1921vk01t':
            allowed_nums = "^((0x|)[0-9A-Fa-f]{1})|([0-9]{1,2})$"
            self.ui.tconfig_widget_cfg.ui.ledit_pinnum.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        elif self.mcu.name == 'k1921vkx':
            pass


def log_dbg(msg):
    logger.debug(msg)


def log_info(msg):
    logger.info(msg)
    MainWindow.ui.tedit_log.appendHtml('[<span style=" color:#4e9a06;">INFO</span>]: %s' % msg)


def log_warn(msg):
    logger.warning(msg)
    MainWindow.ui.tedit_log.appendHtml('[<span style=" color:#e9b96e;">WARN</span>]: %s' % msg)


def log_err(msg):
    logger.error(msg)
    MainWindow.ui.tedit_log.appendHtml('[<span style=" color:#ef2929;">ERR</span>]: %s' % msg)


def log_crit(msg):
    logger.critical(msg)
    MainWindow.ui.tedit_log.appendHtml('[<span style=" color:#ad7fa8;">CRIT</span>]: %s' % msg)


logger.init(debug=True, logfile="flasher.log")
App = QApplication(sys.argv)
MainWindow = MyMainWindow()


# -- Standalone run -----------------------------------------------------------
if __name__ == '__main__':
    MainWindow.show()
    sys.exit(App.exec_())
