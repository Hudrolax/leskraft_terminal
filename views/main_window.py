from PyQt5.QtWidgets import QMainWindow, QDialog, QTableWidgetItem, QPushButton, QWidget, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from views.main_ui import Ui_MainWindow
from utility.threaded_class import Threaded_class
from config import *
from PyQt5.QtCore import QFile, QTextStream
import logging
from utility.logger_super import LoggerSuper
import sys
from time import sleep

class GUI_Main_Window(Ui_MainWindow, LoggerSuper):
    logger = logging.getLogger('Main_Window')
    def custom_setup(self, window):
        self.tbl1.setRowCount(1)
        self.tbl1.setColumnCount(11)
        # self.tbl1.setUpdatesEnabled(True)
        window.resize(1200, 768)
        self.init_GUI = True

    def add_row(self):
        self.tbl1.setRowCount(self.tbl1.rowCount() + 1)

    def reset_rows(self):
        self.tbl1.setRowCount(1)

    def set_table_header_style(self):
        self.tbl1.item(0, 0).setFont(QFont("Consolas", 18, QFont.Bold))
        for col in range(1, self.tbl1.columnCount()):
            self.tbl1.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
            self.tbl1.item(0, col).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)

class MainWindow(QMainWindow):
    def __init__(self, controller, model, parent = None):
        super(QMainWindow, self).__init__(parent)
        self.controller = controller
        self.model = model

        # подключаем визуальное представление
        self.ui = GUI_Main_Window()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)
        self.load_style()

        self.ui.get_btn.clicked.connect(self.controller.click_get_btn)
        # создадим поток обновления по таймеру
        self.timer_thread = QtCore.QThread()
        self.timer_handler = TimerHandler()
        self.timer_handler.moveToThread(self.timer_thread)
        self.timer_handler.timer_signal.connect(self._fill_table_by_timer)
        self.timer_thread.started.connect(self.timer_handler.run)
        self.timer_thread.start()

        self.showNormal()
        self.fill_header()

    def load_style(self):
        file = QFile(STYLE_PATH)
        if not file.open(QFile.ReadOnly | QFile.Text):
            self.logger.critical(f'Style {STYLE_PATH} not found.')
            Threaded_class.stop()
            sys.exit(self)

        qss_file = QTextStream(file)
        self.setStyleSheet(qss_file.readAll())
        file.close()

    def closeEvent(self, event):
        Threaded_class.stop()
        print("User has clicked the red x on the main window")
        event.accept()

    def show_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec_()

    def fill_header(self):
        if not self.ui.init_GUI:
            return
        self.ui.tbl1.setItem(0, 0, QTableWidgetItem('№'))
        self.ui.tbl1.setItem(0, 1, QTableWidgetItem('Поступило'))
        self.ui.tbl1.setItem(0, 2, QTableWidgetItem('Тип'))
        self.ui.tbl1.setItem(0, 3, QTableWidgetItem('Бригада'))
        self.ui.tbl1.setItem(0, 4, QTableWidgetItem('Руководитель'))
        self.ui.tbl1.setItem(0, 5, QTableWidgetItem('Начато'))
        self.ui.tbl1.setItem(0, 6, QTableWidgetItem('Исполнить к'))
        self.ui.tbl1.setItem(0, 7, QTableWidgetItem('Окончено'))
        self.ui.tbl1.setItem(0, 8, QTableWidgetItem('Статус'))
        self.ui.tbl1.setItem(0, 9, QTableWidgetItem('Номер авто'))
        self.ui.tbl1.setItem(0, 10, QTableWidgetItem(''))
        self.ui.set_table_header_style()
        self.ui.tbl1.update()

    def fill_table(self):
        if not self.ui.init_GUI:
            return
        self.ui.tbl1.setRowCount(len(self.model.db.documents) + 1)
        _str = 1
        for doc in self.model.db.documents:
            self.ui.tbl1.setItem(_str, 0, QTableWidgetItem(str(doc.get_num_str())))
            self.ui.tbl1.setItem(_str, 1, QTableWidgetItem(doc.get_date_sending_str()))
            self.ui.tbl1.setItem(_str, 2, QTableWidgetItem(doc.type))
            self.ui.tbl1.setItem(_str, 3, QTableWidgetItem(str(doc.team_number)))
            self.ui.tbl1.setItem(_str, 4, QTableWidgetItem(doc.team_leader))
            self.ui.tbl1.setItem(_str, 5, QTableWidgetItem(doc.get_start_time_str()))
            self.ui.tbl1.setItem(_str, 6, QTableWidgetItem(doc.get_execute_to_str()))
            self.ui.tbl1.setItem(_str, 7, QTableWidgetItem(doc.get_end_time_str()))
            self.ui.tbl1.setItem(_str, 8, QTableWidgetItem(doc.status))
            self.ui.tbl1.setItem(_str, 9, QTableWidgetItem(doc.autos_number))
            btn = QPushButton(parent=self.ui.tbl1)
            btn.setText('Взять')
            btn.clicked.connect(self._click_get_doc_btn)
            btn.doc = doc
            self.ui.tbl1.setCellWidget(_str, 10, btn)
            _str += 1

        # делаем ресайз колонок по содержимому
        sleep(0.5)
        self.ui.tbl1.resizeColumnsToContents()
        self.ui.tbl1.update()

    def model_is_changed( self ):
        self.fill_table()

    @QtCore.pyqtSlot()
    def _fill_table_by_timer(self):
        self.fill_table()

    def _click_get_doc_btn(self):
        self.controller.click_getdoc_btn(self.sender().doc)


class Communicate(QtCore.QObject):
    click_getdoc_btn_signal = QtCore.pyqtSignal(str)


class TimerHandler(QtCore.QObject):
    timer_signal = QtCore.pyqtSignal()

    def run(self):
        while True:
            self.timer_signal.emit()
            QtCore.QThread.msleep(1000)