#!/user/bin/env python

"""
Description
"""

# -- Imports ------------------------------------------------------------------
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow)
from ui_main import Ui_MainWindow


# -- Global variables ---------------------------------------------------------
VERSION = "1.0"


# -- Special classes ----------------------------------------------------------

# -- Main window --------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Set up the user interface from QtDesigner
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    # -- Events --
    def closeEvent(self, event):
        event.accept()

    # -- Slots general --
    def handle_act_about_triggered(self):
        pass

    def handle_combo_port_activated(self):
        pass

    def handle_combo_port_changed(self, num):
        pass

    def handle_combo_baud_changed(self, num):
        pass

    def handle_btn_connect_clicked(self):
        pass

    def handle_flash_select_toggled(self, state):
        pass

    def handle_btn_exec_clicked(self):
        pass

    # -- Slots for Write Tab widgets --
    def handle_twrite_ledit_filepath_editint_finished(self):
        pass

    def handle_twrite_ledit_addr_editing_finished(self):
        pass

    def handle_twrite_btn_fileopen_clicked(self):
        pass

    # -- Slots for Erase Tab widgets --
    def handle_terase_ledit_firstpage_editing_finished(self):
        pass

    def handle_terase_ledit_lastpage_editing_finished(self):
        pass

    def handle_terase_ledit_addrstart_editing_finished(self):
        pass

    def handle_terase_ledit_bytes_editing_finished(self):
        pass

    # -- Slots for Read Tab widgets --
    def handle_tread_ledit_filepath_editing_finished(self):
        pass

    def handle_tread_btn_fileopen_clicked(self):
        pass

    def handle_tread_ledit_firstpage_editing_finished(self):
        pass

    def handle_tread_ledit_lastpage_editing_finished(self):
        pass

    def handle_tread_ledit_addrstart_editing_finished(self):
        pass

    def handle_tread_ledit_bytes_editing_finished(self):
        pass

    def handle_tread_chbox_verif_toggled(self, state):
        pass

    def handle_tread_ledit_verif_filepath_editing_finished(self):
        pass

    def handle_tread_btn_verif_fileopen_clicked(self):
        pass

    # -- Application specific code --


# -- Standalone run -----------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
