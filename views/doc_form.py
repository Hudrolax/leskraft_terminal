from views.doc_form_ui import Ui_doc_form
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication
from utility.logger_super import LoggerSuper
import logging


class GUI_Doc_Window(Ui_doc_form, LoggerSuper):
    logger = logging.getLogger('Document_Form')
    def custom_setup(self, window):
        self.doc_tbl.setRowCount(1)
        self.doc_tbl.setColumnCount(7)

        window.resize(1200, 768)
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

    def center_on_screen(self):
        resolution = QApplication.desktop().availableGeometry()
        self.move(round(resolution.width() / 2 - self.geometry().width() / 2),
                  round(resolution.height() / 2 - self.geometry().height() / 2))

    def fill_header(self):
        if not self.ui.init_GUI:
            return
        doc = self.model
        self.ui.doc_name.setText(str(doc))
        self.ui.storage.setText(str(doc.storage))
        self.ui.date_sending.setText(doc.get_date_sending_str())
        self.ui.type.setText(doc.type)
        self.ui.destination.setText(doc.destination)
        self.ui.autos_number.setText(doc.autos_number)
        self.ui.status.setText(doc.status)
        self.ui.team_leader.setText(doc.team_leader)
        self.ui.team_number.setText(doc.team_number)
        self.ui.execute_to.setText(doc.get_execute_to_str())
        self.ui.start_time.setText(doc.get_start_time_str())
        self.ui.end_time.setText(doc.get_end_time_str())

    def fill_table(self):
        if not self.ui.init_GUI:
            return
