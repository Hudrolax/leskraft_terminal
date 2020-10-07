from PyQt5 import Qt


class Widget(Qt.QWidget):

    def __init__(self):
        super().__init__()
        layout = Qt.QHBoxLayout(self)
        table = Qt.QTableWidget()
        table.setRowCount(2)
        table.setColumnCount(2)
        btn = Qt.QPushButton("Some button")
        table.setCellWidget(1, 1, btn)
        layout.addWidget(table)


if __name__ == '__main__':
    app = Qt.QApplication([])
    w = Widget()
    w.show()
    app.exec()