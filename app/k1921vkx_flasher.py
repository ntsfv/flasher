#!/user/bin/env python
# coding:utf-8

"""
K1921VKx Flasher Utility
"""

# -- Imports ------------------------------------------------------------------
import sys
import os
import getopt
import logger
import inspect
import serport
import mcu
import protocol
from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog, QTableWidgetItem,
                             QHeaderView, QAction, QFileDialog, QLineEdit, QFrame, QWidget, QComboBox)
from PyQt5.QtGui import (QIcon, QPixmap, QCursor, QRegExpValidator)
from ui_main import Ui_MainWindow
from ui_about import Ui_AboutDialog
from ui_config035 import Ui_Config035
from ui_config028 import Ui_Config028
from ui_config01t import Ui_Config01T
from ui_config1921 import Ui_Config1921


# -- Global variables ---------------------------------------------------------
VERSION = "0.1"


# -- Misc functions -----------------------------------------------------------

# -- Main window --------------------------------------------------------------
class MyMainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.debug = False

        self.mcu = mcu.get_by_name('k1921vkx')
        self.serport = serport.SerPort(self)
        self.prot = protocol.Protocol(serport=self.serport, win=self)

        # Set up the user interface from QtDesigner
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.tconfig_widget_cfg = QWidget(self.ui.tab_config)
        self.ui.tconfig_vbox.addWidget(self.ui.tconfig_widget_cfg)

        self.ui.tconfig_frm_cfg = QFrame(self.ui.tab_config)

        self.ui.btn_updport.clicked.emit()

        self.ui.tedit_log.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.tedit_log.customContextMenuRequested.connect(self.handle_tedit_log_context_menu)

        allowed_nums = "^((0x|)[0-9A-Fa-f]{1,8})|([0-9]{1,10})$"
        self.ui.twrite_ledit_addr.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.twrite_ledit_size.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.twrite_ledit_page.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.twrite_ledit_pages.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.twrite_ledit_jumpaddr.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_addr.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_size.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_page.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.terase_ledit_pages.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_addr.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_size.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_page.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))
        self.ui.tread_ledit_pages.setValidator(QRegExpValidator(QtCore.QRegExp(allowed_nums)))

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
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(0).setToolTip("Номер страницы")
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(1).setToolTip("Начальный адрес страницы")
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(2).setToolTip("Размер страницы в байтах")
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(3).setToolTip("Защита страницы от чтения")
        self.ui.tinfo_tbl_flash.horizontalHeaderItem(4).setToolTip("Защита страницы от записи")

        self.ui.twrite_ledit_filepath.path_for_open = True
        self.ui.tread_ledit_filepath.path_for_open = False
        self.ui.twrite_ledit_filepath.last_text = ""
        self.ui.tread_ledit_filepath.last_text = ""

        self.about_dialog = QDialog(self)
        self.about_dialog.ui = Ui_AboutDialog()
        self.about_dialog.ui.setupUi(self.about_dialog)

        self.upd_flash_selected()
        self.upd_tconfig_widget_cfg()

    # -- Helpers --
    def whoami(self):
        return inspect.getouterframes(inspect.currentframe())[1].function

    def log_dbg(self, msg):
        if self.debug:
            logger.debug(msg)

    def log_info(self, msg):
        logger.info(msg)
        self.ui.tedit_log.appendHtml('[<span style=" color:#4e9a06;">INFO</span>]: %s' % msg)

    def log_warn(self, msg):
        logger.warning(msg)
        self.ui.tedit_log.appendHtml('[<span style=" color:#e9b96e;">WARN</span>]: %s' % msg)

    def log_err(self, msg):
        logger.error(msg)
        self.ui.tedit_log.appendHtml('[<span style=" color:#ef2929;">ERR</span>]: %s' % msg)

    def log_crit(self, msg):
        logger.critical(msg)
        self.ui.tedit_log.appendHtml('[<span style=" color:#ad7fa8;">CRIT</span>]: %s' % msg)

    def text2int(self, qobject):
        try:
            num = int(qobject.text(), 10)
            num_format = 'dec'
        except ValueError:
            num = int(qobject.text(), 16)
            num_format = 'hex'
        return (num, num_format)

    # -- Events --
    def closeEvent(self, event):
        self.prot.deinit()
        event.accept()

    # -- Slots --
    def handle_ledit_addr_edited(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        ledit_addr = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_addr$'))[0]
        ledit_page = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_page$'))[0]
        self.log_dbg("Object <%s>" % ledit_addr.objectName())
        addr, addr_format = self.text2int(ledit_addr)
        page_size = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].page_size
        pages = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].pages

        if addr >= (page_size * pages):
            self.log_warn("Адрес выходит за границы диапазона 0x00000000-0x%08X" % ((page_size * pages) - 1))
            addr = 0

        aligned_addr = ((addr & 0xFFFFFF) // page_size) * page_size
        ledit_addr.setText("%s" % ("%d" % aligned_addr if addr_format == 'dec' else "0x%08X" % aligned_addr))
        if addr != aligned_addr:
            self.log_info("Адрес 0x%08X был выровнен по размеру страницы (0x%X) - 0x%08X" % (addr, page_size, aligned_addr))

        ledit_page.setText("%d" % (aligned_addr // page_size))

    def handle_ledit_size_edited(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        ledit_addr = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_addr$'))[0]
        ledit_size = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_size$'))[0]
        ledit_pages = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_pages$'))[0]
        self.log_dbg("Object <%s>" % ledit_size.objectName())
        addr, addr_format = self.text2int(ledit_addr)
        size, size_format = self.text2int(ledit_size)
        page_size = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].page_size
        pages_total = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].pages

        if size > ((page_size * pages_total) - addr):
            self.log_warn("Размер области должен быть не более 0x%X байт" % ((page_size * pages_total) - addr))
            size = 0

        aligned_size = ((size // page_size) + (1 if size % page_size else 0)) * page_size
        ledit_size.setText("%s" % ("%d" % aligned_size if size_format == 'dec' else "0x%08X" % aligned_size))
        if size != aligned_size:
            self.log_info("Размер 0x%X был выровнен по размеру страницы (0x%X) - 0x%X" % (size, page_size, aligned_size))

        ledit_pages.setText("%d" % (aligned_size // page_size))

    def handle_ledit_page_edited(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        ledit_addr = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_addr$'))[0]
        ledit_page = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_page$'))[0]
        self.log_dbg("Object <%s>" % ledit_page.objectName())
        page, page_format = self.text2int(ledit_page)
        page_size = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].page_size
        pages = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].pages

        if page >= pages:
            self.log_warn("Номер страницы выходит за границы диапазона 0-%d" % (pages - 1))
            page = 0

        ledit_page.setText("%d" % page)
        ledit_addr.setText("0x%08X" % (page * page_size))

    def handle_ledit_pages_edited(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        ledit_size = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_size$'))[0]
        ledit_pages = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_pages$'))[0]
        ledit_page = self.sender().parent().findChildren(QLineEdit, QtCore.QRegExp('^.*_page$'))[0]
        self.log_dbg("Object <%s>" % ledit_pages.objectName())
        pages, pages_format = self.text2int(ledit_pages)
        page, page_format = self.text2int(ledit_page)
        page_size = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].page_size
        pages_total = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].pages

        if pages > (pages_total - page):
            self.log_warn("Указанное количество страниц больше максимального (%d)" % (pages_total - page))
            pages = 0

        ledit_pages.setText("%d" % pages)
        ledit_size.setText("0x%08X" % (pages * page_size))

    def handle_twrite_chbox_jump_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        self.ui.twrite_ledit_jumpaddr.setEnabled(state)

    def handle_tedit_log_context_menu(self, pos):
        self.log_dbg("Handler <%s> called" % self.whoami())
        menu = self.ui.tedit_log.createStandardContextMenu()
        menu.act_clear = QAction("Очистить")
        menu.act_clear.triggered.connect(self.ui.tedit_log.clear)
        menu.insertActions(menu.actions()[0], [menu.act_clear])
        menu.exec_(QCursor.pos())

    def handle_btn_updport_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        self.ui.combo_port.clear()
        [self.ui.combo_port.addItem(port) for port in self.serport.list_ports()]

    def handle_act_about_triggered(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        text = self.about_dialog.ui.lab_version.text().replace("x.x", VERSION)
        self.about_dialog.ui.lab_version.setText(text)
        self.about_dialog.exec_()

    def handle_btn_connect_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        update_gui = False
        port = self.ui.combo_port.currentText()
        baud = self.ui.combo_baud.currentText()
        if (not self.is_connected()):
            if not self.ui.combo_port.count():
                self.log_warn("Выберите COM-порт!")
            else:
                state = True
                btn_text = "Отключиться"
                try:
                    self.mcu = self.prot.init(port=port, baud=baud)
                    update_gui = True
                except:
                    self.prot.deinit()
                    self.log_err("Подключиться не удалось. Убедитесь что загрузчик разрешён и сбросьте устройство.")
        else:
            state = False
            btn_text = "Подключиться"
            self.prot.deinit()
            self.mcu = mcu.get_by_name('k1921vkx')
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
            self.upd_gbox_flash()
            self.upd_tinfo_values()
            self.upd_flash_selected()
            self.upd_tconfig_widget_cfg()

    def handle_flash_select_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        if state:
            if self.ui.rbtn_flash0.isChecked():
                flash_name = self.ui.rbtn_flash0.text()
            else:
                flash_name = self.ui.rbtn_flash1.text()
            self.log_info("Выбрана флеш-память %s" % flash_name)
            self.upd_flash_selected()

    def handle_region_select_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        if state:
            if self.ui.rbtn_regionmain.isChecked():
                region_name = "основная"
            else:
                region_name = "NVR/Info"
            self.log_info("Выбрана %s область" % region_name)
            self.upd_flash_selected()

    def handle_btn_exec_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        curr_tab = self.ui.tabs_cmd.currentWidget().objectName()
        self.log_dbg("Tab <%s> active" % curr_tab)
        if curr_tab == "tab_info":
            self.exec_tab_info()
        elif curr_tab == "tab_write":
            self.exec_tab_write()
        elif curr_tab == "tab_read":
            self.exec_tab_read()
        elif curr_tab == "tab_erase":
            self.exec_tab_erase()
        elif curr_tab == "tab_config":
            self.exec_tab_config()

    def handle_ledit_filepath_changed(self, text):
        self.log_dbg("Handler <%s> called" % self.whoami())
        self.log_dbg("Sender <%s>" % self.sender().objectName())

        if self.sender().path_for_open:
            if (os.path.isfile(self.sender().text()) and self.sender().text()[-4:] == '.bin' and self.sender().text() != self.sender().last_text):

                self.sender().setStyleSheet("color: black;")
            else:
                self.sender().setStyleSheet("color: red;")
        self.sender().last_text = self.sender().text()

        if ("twrite" in self.sender().objectName() and
           self.is_valid_path(self.ui.twrite_ledit_filepath)):
            filesize = os.path.getsize(self.ui.twrite_ledit_filepath.text())
            page_size = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].page_size
            addr, addr_format = self.text2int(self.ui.twrite_ledit_addr)
            pages_total = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].pages
            if filesize > ((page_size * pages_total) - addr):
                self.ui.twrite_ledit_size.setText("ошибка")
                self.ui.twrite_ledit_pages.setText("ошибка")
            else:
                self.ui.twrite_ledit_size.setText("0x%08X" % (((filesize // page_size) + (1 if filesize % page_size else 0)) * page_size))
                self.ui.twrite_ledit_pages.setText("%d" % ((filesize // page_size) + (1 if filesize % page_size else 0)))

    def handle_btn_fileopen_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
        rexp_ledit = QtCore.QRegExp('^.*_filepath$')
        linked_ledit = self.sender().parent().findChildren(QLineEdit, rexp_ledit)[0]
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Открыть бинарный файл", linked_ledit.text(), "Бинарные файлы (*.bin)",
                                                  options=options)
        if filename:
            linked_ledit.setText(filename)

    def handle_btn_filesave_clicked(self):
        self.log_dbg("Handler <%s> called" % self.whoami())
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

    def handle_terase_mode_select_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        if state:
            self.ui.terase_frm_addr.setEnabled(self.ui.terase_rbtn_erpages.isChecked())

    def handle_tconfig_mode_select_toggled(self, state):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % state))
        if state:
            self.ui.tconfig_widget_cfg.ui.tconfig_frm_cfg.setEnabled(self.ui.tconfig_rbtn_write.isChecked())

    def handle_tabs_cmd_changed(self, num):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % num))
        if self.ui.tabs_cmd.currentWidget().objectName() == 'tab_info':
            self.ui.btn_exec.setEnabled(False)
        else:
            self.ui.btn_exec.setEnabled(True)

    def handle_firstpage_select_changed(self, num):
        self.log_dbg("Handler <%s> called" % (self.whoami() + "(%d)" % num))
        self.log_dbg("Sender <%s>" % self.sender().objectName())
        if num != -1:
            rexp_combo = QtCore.QRegExp('^.*_lastpage$')
            combo_firstpage = self.sender()
            combo_lastpage = self.sender().parent().findChildren(QComboBox, rexp_combo)[0]
            combo_lastpage.clear()
            for i in range(combo_firstpage.currentIndex(), combo_firstpage.count()):
                combo_lastpage.addItem(combo_firstpage.itemText(i))
            if "twrite" in self.sender().objectName():
                self.handle_twrite_combo_lastpage_changed(0)

    # -- Application specific code --
    def is_connected(self):
        return not self.ui.combo_port.isEnabled()

    def is_valid_path(self, ledit_path):
        return False if ('red' in ledit_path.styleSheet()) or (not ledit_path.text()) else True

    def get_curr_flash(self):
        if self.ui.rbtn_flash0.isChecked():
            return 0
        else:
            return 1

    def get_curr_region(self):
        if self.ui.rbtn_regionnvr.isChecked():
            return 'region_nvr'
        else:
            return 'region_main'

    def upd_gbox_flash(self):
        self.ui.rbtn_flash0.setText(self.mcu.flash[0]['name'].upper())
        if len(self.mcu.flash) == 2:
            self.ui.rbtn_flash1.setEnabled(True)
            self.ui.rbtn_flash1.setText(self.mcu.flash[1]['name'].upper())
        else:
            self.ui.rbtn_flash1.setEnabled(False)
            self.ui.rbtn_flash1.setText('')

    def upd_tinfo_values(self):
        self.ui.tinfo_ledit_chipid.setText(self.mcu.chipid)
        self.ui.tinfo_ledit_cpuid.setText(self.mcu.cpuid)
        self.ui.tinfo_ledit_bootver.setText(self.mcu.bootver)
        self.ui.tinfo_lab_mcu.setText(self.mcu.name_ru)

    def upd_flash_selected(self):
        table = self.ui.tinfo_tbl_flash

        table.clearContents()

        for r in reversed(range(table.rowCount())):
            table.removeRow(r)
        pages = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].pages
        page_size = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].page_size
        rd_lock = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].rd_lock
        wr_lock = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()].wr_lock
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

    def exec_tab_info(self):
        pass

    def exec_tab_write(self):
        self.log_info('Подготовка к выполнению команды записи. Чтение опций ...')
        self.log_info('Флеш - %s' % self.mcu.flash[self.get_curr_flash()]["name"].upper())
        self.log_info('Область - %s' % ("основная" if self.get_curr_region() == "region_main" else "NVR/Info"))
        filepath = self.ui.twrite_ledit_filepath.text()
        filevalid = self.is_valid_path(self.ui.twrite_ledit_filepath)
        addr = self.text2int(self.ui.twrite_ledit_addr)[0]
        firstpage = self.text2int(self.ui.twrite_ledit_page)[0]
        if self.ui.twrite_ledit_size.text() == 'ошибка':
            return self.log_err('Не выполнено - размер файла превышает размер выбранной области!')
        else:
            lastpage = firstpage + self.text2int(self.ui.twrite_ledit_pages)[0] - 1

        ernone = True if self.ui.twrite_rbtn_ernone.isChecked() else False
        erall = True if self.ui.twrite_rbtn_erall.isChecked() else False
        erpages = True if self.ui.twrite_rbtn_erpages.isChecked() else False
        verif = True if self.ui.twrite_chbox_verif.isChecked() else False
        jump = True if self.ui.twrite_chbox_jump.isChecked() else False
        jumpaddr = self.text2int(self.ui.twrite_ledit_jumpaddr)[0]

        if filevalid:
            self.log_info('Файл - "%s", размер %d байт' % (filepath, os.path.getsize(filepath)))
        else:
            return self.log_err('Не выполнено - файла "%s" не существует!' % filepath)

        self.log_info('Модифицируемые страницы - %d ... %d' % (firstpage, lastpage))

        if ernone:
            self.log_info('Стирание - не выполняется')
        elif erall:
            self.log_info('Стирание - вся область')
        elif erpages:
            self.log_info('Стирание - только необходимые страницы')
        else:
            return self.log_err('Не выполнено - режим стирания не определён')

        curr_flash = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()]
        if verif:
            for p in range(firstpage, lastpage + 1):
                if curr_flash.rd_lock[p]:
                    verif = False
                    self.log_warn('Верификация невозможна - одна или несколько считываемых страниц защищены от чтения')
        self.log_info('Верификация - %sвыполняется' % ("" if verif else "не "))
        if jump:
            self.log_info('Переход к исполнению программы - адрес 0x%08X' % jumpaddr)
        else:
            self.log_info('Переход к исполнению программы - не выполняется')

        for p in range(firstpage, lastpage + 1):
            if curr_flash.wr_lock[p]:
                return self.log_err('Не выполнено - одна или несколько модифицируемых страниц защищены от записи/стирания')
        if erall:
            for page_locked in curr_flash.wr_lock:
                if page_locked:
                    return self.log_err('Не выполнено - одна или несколько модифицируемых страниц защищены от записи/стирания')

        try:
            self.prot.write(filepath=filepath, addr=addr, firstpage=firstpage, lastpage=lastpage,
                            ernone=ernone, erall=erall, erpages=erpages,
                            verif=verif, jump=jump, jumpaddr=jumpaddr)
            self.log_info('Команда записи успешно выполнена')
        except:
            return self.log_err('Команда записи не выполнена - ошибка протокола!')

    def exec_tab_erase(self):
        self.log_info('Подготовка к выполнению команды стирания. Чтение опций ...')
        self.log_info('Флеш - %s' % self.mcu.flash[self.get_curr_flash()]["name"].upper())
        self.log_info('Область - %s' % ("основная" if self.get_curr_region() == "region_main" else "NVR/Info"))

        erall = True if self.ui.terase_rbtn_erall.isChecked() else False
        erpages = True if self.ui.terase_rbtn_erpages.isChecked() else False

        curr_flash = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()]
        if erall:
            firstpage = 0
            lastpage = curr_flash.pages - 1
            self.log_info('Стирание - вся область')
        elif erpages:
            firstpage = self.text2int(self.ui.terase_ledit_page)[0]
            pages = self.text2int(self.ui.terase_ledit_pages)[0]
            if pages:
                lastpage = firstpage + pages - 1
            else:
                return self.log_err('Не выполнено - не определён размер стираемой области')
        else:
            return self.log_err('Не выполнено - режим стирания не определён')

        size = self.text2int(self.ui.terase_ledit_size)[0]
        self.log_info('Модифицируемые страницы - %d ... %d (%d байт)' % (firstpage, lastpage, size))

        for p in range(firstpage, lastpage + 1):
            if curr_flash.wr_lock[p]:
                return self.log_err('Не выполнено - одна или несколько модифицируемых страниц защищены от записи/стирания')

        try:
            self.prot.erase(firstpage=firstpage, lastpage=lastpage, erall=erall, erpages=erpages)
            self.log_info('Команда стирания успешно выполнена')
        except:
            return self.log_err('Команда стирания не выполнена - ошибка протокола!')

    def exec_tab_read(self):
        self.log_info('Подготовка к выполнению команды чтения. Чтение опций ...')
        self.log_info('Флеш - %s' % self.mcu.flash[self.get_curr_flash()]["name"].upper())
        self.log_info('Область - %s' % ("основная" if self.get_curr_region() == "region_main" else "NVR/Info"))
        filepath = self.ui.tread_ledit_filepath.text()
        try:
            open(filepath, 'w')
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            return self.log_err('Не выполнено - некорректный путь для сохранения')
        size = self.text2int(self.ui.tread_ledit_size)[0]
        self.log_info('Файл - "%s", размер %d байт' % (filepath, size))
        firstpage = self.text2int(self.ui.tread_ledit_page)[0]
        pages = self.text2int(self.ui.tread_ledit_pages)[0]
        if pages:
            lastpage = firstpage + pages - 1
        else:
            return self.log_err('Не выполнено - не определён размер считываемой области')

        self.log_info('Считываемые страницы - %d ... %d' % (firstpage, lastpage))

        curr_flash = self.mcu.flash[self.get_curr_flash()][self.get_curr_region()]
        for p in range(firstpage, lastpage + 1):
            if curr_flash.rd_lock[p]:
                return self.log_err('Не выполнено - одна или несколько считываемых страниц защищены от чтения')

        try:
            self.prot.read(filepath=filepath, firstpage=firstpage, lastpage=lastpage)
            self.log_info('Команда чтения успешно выполнена')
        except:
            return self.log_err('Команда чтения не выполнена - ошибка протокола!')

    def exec_tab_config(self):
        pass


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
        -e          Стереть страницы от 'first' по 'last' включительно
        -E          Полное стирание
        -w          Записать 'file.bin' начиная со страницы 'first'. Если добавлены ключи -e или -E - перед записью будет проведено стирание.
        -v          Верифицировать записанный 'file.bin' (может быть использовано только в паре с -w)
        -r          Прочитать в файл 'file.bin' страницы от 'first' по 'last' включительно
        -j addr     Переход на исполнение по глобальному адресу (по этому адресу расположена таблица векторов прерываний)
        -F first    Номер первой страницы для выполнения команд
        -L last     Номер последней страницы для выполнения команд
        -a addr     Выбор адреса для выполнения команд
        -s size     Выбор размера области для выполнения команд
        -p port     COM-порт
        -b baud     Баудрейт

        Запись файла led.bin в основную область MFLASH К1921ВК035 с 0 страницы с полным стиранием, верификацией записанного:
        python k1921vk035_loader.py -wEv -f mflash -n main -F 0 -p /dev/ttyUSB0 -b 115200 led.bin

НИИЭТ, 2019""" % (VERSION))

    def do(self, app, win):
        conf = {
            "port": None,
            "baud": None,
            "flash": None,
            "region": None,
            "first_page": None,
            "last_page": None,
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
            opts, args = getopt.getopt(sys.argv[1:], "hDceEwvrf:n:j:F:L:a:s:p:b")
        except getopt.GetoptError:
            self.help()
            sys.exit(2)

        for o, a in opts:
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
                conf['baud'] = eval(a)
            elif o == '-F':
                conf['first_page'] = eval(a)
            elif o == '-L':
                conf['last_page'] = eval(a)
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
    logger.init(debug=True, logfile="flasher.log")
    app = QApplication(sys.argv)
    main_window = MyMainWindow()
    arg_parser = ArgParser()
    conf = arg_parser.do(app, main_window)
    if conf['cmd_mode'] is None:
        main_window.debug = conf['debug']
        main_window.show()
        sys.exit(app.exec_())
    else:
        main_window.log_info("Режим без графического интерфейса")
        pass
