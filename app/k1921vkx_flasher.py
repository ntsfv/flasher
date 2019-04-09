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

    # -- Slots --

    # -- Application specific code --


# -- Standalone run -----------------------------------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
