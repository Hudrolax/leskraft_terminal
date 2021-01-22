from views.ui.doc_form_ui import Ui_doc_form
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem
from utility.logger_super import LoggerSuper
from time import sleep
import logging


class GUI_Doc_Window(Ui_doc_form, LoggerSuper):
    logger = logging.getLogger('Document_Form')
    def custom_setup(self, window):
        self.doc_tbl.setRowCount(1)
        self.doc_tbl.setColumnCount(7)

        window.resize(1920, 700)
        self.init_GUI = True

    def set_table_header_style(self):
        self.doc_tbl.item(0, 0).setFont(QFont("Consolas", 18, QFont.Bold))
        for col in range(1, self.doc_tbl.columnCount()):
            self.doc_tbl.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
            self.doc_tbl.item(0, col).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

class DocumentWindow(QDialog):
    def __init__(self, controller, model, parent = None):
        super(QDialog, self).__init__(parent)
        self.controller = controller
        self.model = model
        self.parent = parent

        # подключаем визуальное представление
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setModal(True)
        self.ui = GUI_Doc_Window()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)
        self.ui.close_button.clicked.connect(self.controller.click_close_btn)

        self.showNormal()
        self.center_on_screen()
        self.fill_header()
        self.fill_table_header()
        self.fill_table()

    def center_on_screen(self):
        resolution = QApplication.desktop().availableGeometry()
        self.move(round(resolution.width() / 2 - self.geometry().width() / 2),
                  round(resolution.height() / 2 - self.geometry().height() / 2))

    def fill_header(self):
        if not self.ui.init_GUI:
            return
        doc = self.model.doc
        self.ui.doc_name.setText(str(doc))
        self.ui.storage.setText(str(doc.storage))
        self.ui.date_sending.setText(doc.get_date_sending_str())
        self.ui.type.setText(doc.type)
        self.ui.destination.setText(doc.destination)
        self.ui.autos_number.setText(doc.autos_number)
        self.ui.status.setText(doc.status)
        self.ui.team_leader.setText(doc.team_leader)
        if doc.team_number > 0:
            self.ui.team_number.setText(str(doc.team_number))
        else:
            self.ui.team_number.setText("")
        self.ui.execute_to.setText(doc.get_execute_to_str())
        self.ui.start_time.setText(doc.get_start_time_str())
        self.ui.end_time.setText(doc.get_end_time_str())
        try:
            self.ui.work_button.clicked.disconnect()
        except:
            pass
        if doc.status == "На исполнение":
            self.ui.work_button.setText('Взять')
            self.ui.work_button.clicked.connect(self._start_work_with_doc)
        elif doc.status == "В работе":
            self.ui.work_button.setText('Завершить')
            self.ui.work_button.clicked.connect(self._stop_work_with_doc)
        else:
            self.ui.work_button.setText('')
            self.ui.work_button.setEnabled(False)

    def fill_table_header(self):
        if not self.ui.init_GUI:
            return
        self.ui.doc_tbl.setItem(0, 1, QTableWidgetItem('Код'))
        self.ui.doc_tbl.setItem(0, 2, QTableWidgetItem('Номенклатура'))
        self.ui.doc_tbl.setItem(0, 3, QTableWidgetItem('Количество'))
        self.ui.doc_tbl.setItem(0, 4, QTableWidgetItem('Статус'))
        self.ui.doc_tbl.setItem(0, 5, QTableWidgetItem('Полка'))
        self.ui.doc_tbl.setItem(0, 6, QTableWidgetItem('Пол'))
        # self.ui.doc_tbl.setItem(0, 7, QTableWidgetItem('Отменено'))
        # self.ui.doc_tbl.setItem(0, 8, QTableWidgetItem('Причина отмены'))

    def fill_table(self):
        if not self.ui.init_GUI:
            return
        doc = self.model.doc
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
        sleep(0.01)
        self.ui.doc_tbl.resizeColumnsToContents()
        self.ui.doc_tbl.update()

    @pyqtSlot(bool)
    def _start_work_with_doc(self):
        result = self.controller.start_work_with_document()
        if result:
            self.close()

    @pyqtSlot(bool)
    def _stop_work_with_doc(self):
        result = self.controller.stop_work_with_document()
