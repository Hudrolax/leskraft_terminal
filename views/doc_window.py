from views.ui.doc_form_ui import Ui_doc_form
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QAbstractItemView
from PyQt5 import QtCore
from utility.logger_super import LoggerSuper
from utility.qt5_windows import center_on_screen
import logging
from config import TEST_MODE
from controllers.doc_form_controller import DocForm_controller
from models.doc_window_model import DocumentForm_model


class GUI_Doc_Window(Ui_doc_form, LoggerSuper):
    def custom_setup(self, window):
        self.doc_tbl.setSelectionMode(QAbstractItemView.NoSelection)
        self.doc_tbl.setRowCount(1)
        self.doc_tbl.setColumnCount(7)
        self.autos_number.setText('')
        self.status.setText('')
        self.team_number.setText('')
        self.team_leader.setText('')
        self.execute_to.setText('')
        self.start_time.setText('')
        self.end_time.setText('')
        self.status_bar.setText('')
        self.close_button.setText('Закрыть')

        resolution = QApplication.desktop().availableGeometry()
        window.resize(round(resolution.width()*0.9), round(resolution.height()*0.9))

    def set_table_header_style(self):
        self.doc_tbl.item(0, 0).setFont(QFont("Consolas", 18, QFont.Bold))
        for col in range(1, self.doc_tbl.columnCount()):
            self.doc_tbl.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
            self.doc_tbl.item(0, col).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

class DocumentWindow(QDialog):
    logger = logging.getLogger('Document_Form')
    def __init__(self, db, doc_link, parent = None):
        super(QDialog, self).__init__(parent)
        self.main_window = parent
        self.controller = DocForm_controller(self)
        self.model = DocumentForm_model(db, doc_link, self)

        # подключаем визуальное представление
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setModal(True)
        self.ui = GUI_Doc_Window()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)
        self.ui.close_button.clicked.connect(self.controller.close_window)
        self.ui.printButton.clicked.connect(self.controller.click_print_btn)

        self.showNormal()
        if not TEST_MODE:
            self.setCursor(Qt.BlankCursor)
        center_on_screen(self)

        self.fill_header()
        self.fill_table_header()
        self.fill_table()

    def _show_status_message(self, message, color='#960E10', font_size='24'):
        self.ui.status_bar.setText(message)
        self.ui.status_bar.setStyleSheet(f'color: {color}; font: bold {font_size}pt \"Consolas\"')

    def fill_header(self):
        doc = self.model.doc()
        self.ui.doc_name.setText(str(doc))
        self.ui.storage.setText(str(doc.storage))
        self.ui.date_sending.setText(doc.get_date_sending_str())
        self.ui.type.setText(doc.type)
        self.ui.destination.setText(doc.destination)
        self.ui.autos_number.setText(doc.autos_number)
        self.ui.status.setText(doc.status)
        if doc.status == 'В работе':
            self.ui.status.setStyleSheet('color: #960E10')
        if doc.team_number > 0:
            self.ui.team_number.setText(str(doc.team_number))
            self.ui.team_number.setStyleSheet('color: #4D0557')
            self.ui.team_leader.setText(str(doc.team_leader))
            self.ui.team_leader.setStyleSheet('color: #4D0557')
        else:
            if self.model.team is not None:
                self.ui.team_number.setText(str(self.model.team.num))
                self.ui.team_number.setStyleSheet('color: #960E10')
                self.ui.team_leader.setText(str(self.model.team.team_leader))
                self.ui.team_leader.setStyleSheet('color: #960E10')
            else:
                self.ui.team_number.setText("")
                self.ui.team_leader.setText("")
        self.ui.execute_to.setText(doc.get_execute_to_str())
        self.ui.start_time.setText(doc.get_start_time_str())
        self.ui.end_time.setText(doc.get_end_time_str())

        if doc.get_end_time_str() == '':
            self.ui.start_time.setStyleSheet('color: #960E10')
            self.ui.end_time.setStyleSheet('color: #960E10')
        else:
            self.ui.start_time.setStyleSheet('color: #FF0000')

        # status bar
        if doc.team_number == 0 and self.model.team is None:
            self.ui.status_bar.setText('Отсканируйте карту сотрудника для начала работы')
            self.ui.status_bar.setStyleSheet('color: #960E10; font: bold 24pt \"Consolas\"')
        elif doc.get_start_time_str() == '':
            self.ui.status_bar.setText('Отсканируйте документ для начала работы')
            self.ui.status_bar.setStyleSheet('color: #00FF00; font: bold 24pt \"Consolas\"')
        elif doc.status == 'В работе':
            self.ui.status_bar.setText('Отсканируйте документ для окончания работы')
            self.ui.status_bar.setStyleSheet('color: #960E10; font: bold 24pt \"Consolas\"')

    def fill_table_header(self):
        self.ui.doc_tbl.setItem(0, 1, QTableWidgetItem('Код'))
        self.ui.doc_tbl.setItem(0, 2, QTableWidgetItem('Номенклатура'))
        self.ui.doc_tbl.setItem(0, 3, QTableWidgetItem('Количество'))
        self.ui.doc_tbl.setItem(0, 4, QTableWidgetItem('Статус'))
        self.ui.doc_tbl.setItem(0, 5, QTableWidgetItem('Полка'))
        self.ui.doc_tbl.setItem(0, 6, QTableWidgetItem('Пол'))

    def fill_table(self):
        doc = self.model.db.get_doc(self.model.doc_link)
        db = self.model.db
        strings = db.get_doc_strings(doc.link)
        self.ui.doc_tbl.setRowCount(len(strings) + 1)
        _str = 1
        for string in strings:
            self.ui.doc_tbl.setItem(_str, 0, QTableWidgetItem(str(string.num)))
            self.ui.doc_tbl.setItem(_str, 1, QTableWidgetItem(string.nomenclature.code))
            self.ui.doc_tbl.setItem(_str, 2, QTableWidgetItem(string.nomenclature.name))
            self.ui.doc_tbl.setItem(_str, 3, QTableWidgetItem(str(string.amount)))
            self.ui.doc_tbl.setItem(_str, 4, QTableWidgetItem(string.status))
            self.ui.doc_tbl.setItem(_str, 5, QTableWidgetItem(string.adress_shelf))
            self.ui.doc_tbl.setItem(_str, 6, QTableWidgetItem(string.adress_floor))
            _str += 1
        # делаем ресайз колонок по содержимому
        QtCore.QThread.msleep(100)
        self.ui.doc_tbl.resizeColumnsToContents()

    def disable_print_btn(self):
        self.ui.printButton.setEnabled(False)
        self.ui.printButton.setStyleSheet('background-color: #87939A;') # grey btn