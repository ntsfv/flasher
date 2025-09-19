from PyQt5.QtGui import QDragEnterEvent
from PyQt5.QtWidgets import QWidget, QLineEdit
from PyQt5 import QtCore


class FileWidget(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setEnabled(True)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if len(event.mimeData().urls()) != 1 and \
            not event.mimeData().urls()[0].path().startswith('.bin'):
            event.ignore()
            return

        event.acceptProposedAction()

    def dropEvent(self, event: QDragEnterEvent):
        rexp_ledit = QtCore.QRegExp('^.*_filepath$')
        linked_ledit = self.findChildren(QLineEdit, rexp_ledit)[0]
        linked_ledit.setText(event.mimeData().urls()[0].path()[1:])
        event.acceptProposedAction()
        # self.setText(event.mimeData().urls()[0].path())

