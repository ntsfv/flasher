from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class MemoryTable(QTableWidget):
    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)

        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        for i in range(0x10000):
            self.add_row()

    def add_row(self):
        row_count = self.rowCount()
        self.insertRow(row_count)
        for col in range(self.columnCount()):
            item = QTableWidgetItem(f"New Item ({row_count}, {col})")
            self.setItem(row_count, col, item)
