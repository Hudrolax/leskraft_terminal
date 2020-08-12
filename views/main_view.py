from PyQt5.QtWidgets import QMainWindow, QDialog, QWidget, QTableWidget, QTableWidgetItem
from utility.observer import Observer
from utility.meta import Meta
from views.main_ui import Ui_MainWindow


class MainView(QMainWindow, Observer, metaclass = Meta):
    def __init__(self, controller, model, parent = None):
        super(QMainWindow, self).__init__(parent)
        self.controller = controller
        self.model = model

        # подключаем визуальное представление
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.get_btn.clicked.connect(self.controller.click_get_btn)

        self.showNormal()

    def show_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec_()

    def fill_table(self):
        self.ui.tbl1.clear()
        self.ui.tbl1.setItem(0, 0, QTableWidgetItem('№'))
        self.ui.tbl1.setItem(0, 1, QTableWidgetItem('Дата'))
        self.ui.tbl1.setItem(0, 2, QTableWidgetItem('Тип'))
        self.ui.tbl1.setItem(0, 3, QTableWidgetItem('Склад'))
        self.ui.tbl1.setItem(0, 4, QTableWidgetItem('Статус'))
        _str = 1
        for doc in self.model.docs:
            self.ui.tbl1.setItem(_str, 0, QTableWidgetItem(str(doc.num)))
            self.ui.tbl1.setItem(_str, 1, QTableWidgetItem(str(doc.date)))
            self.ui.tbl1.setItem(_str, 2, QTableWidgetItem(str(doc.type)))
            self.ui.tbl1.setItem(_str, 3, QTableWidgetItem(str(doc.storage)))
            self.ui.tbl1.setItem(_str, 4, QTableWidgetItem(str(doc.status)))
            _str += 1
        # делаем ресайз колонок по содержимому
        self.ui.tbl1.resizeColumnsToContents()

    def model_is_changed( self ):
        self.fill_table()