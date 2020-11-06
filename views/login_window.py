from views.login_ui import Ui_Login
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem
from utility.logger_super import LoggerSuper
import logging


class GUI_Login_Window(Ui_Login, LoggerSuper):
    logger = logging.getLogger('Login_form')
    def custom_setup(self, window):
        self.tbl.setRowCount(1)
        self.tbl.setColumnCount(4)

        window.resize(640, 480)
        self.init_GUI = True

    def set_table_header_style(self):
        self.tbl.item(0, 0).setFont(QFont("Consolas", 18, QFont.Bold))
        for col in range(1, self.tbl.columnCount()):
            self.tbl.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
            self.tbl.item(0, col).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

class LoginWindow(QDialog):
    def __init__(self, controller, model, parent = None, create_team = True):
        super(QDialog, self).__init__(parent)
        self.controller = controller
        self.model = model
        self.parent = parent

        # подключаем визуальное представление
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setModal(True)
        self.ui = GUI_Login_Window()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)
        if create_team:
            self.set_create_team_screen()
        else:
            self.set_register_teammates_screen()

        self.ui.exit_btn.clicked.connect(self.controller.close)
        self.ui.pushButton.clicked.connect(self.btn_register_team_clicked)

        self.showNormal()
        self.fill_table_header()
        self.center_on_screen()

    def set_create_team_screen(self):
        self.ui.tabWidget.setTabEnabled(1, False)
        self.ui.tabWidget.setTabEnabled(0, True)

    def set_register_teammates_screen(self):
        self.ui.tabWidget.setTabEnabled(0, False)
        self.ui.tabWidget.setTabEnabled(1, True)

    def center_on_screen(self):
        resolution = QApplication.desktop().availableGeometry()
        self.move(round(resolution.width() / 2 - self.geometry().width() / 2),
                  round(resolution.height() / 2 - self.geometry().height() / 2))

    def fill_table_header(self):
        if not self.ui.init_GUI:
            return
        self.ui.tbl.setItem(0, 1, QTableWidgetItem('№'))
        self.ui.tbl.setItem(0, 2, QTableWidgetItem('Имя'))
        self.ui.tbl.setItem(0, 3, QTableWidgetItem('Карта'))
        self.ui.tbl.setItem(0, 4, QTableWidgetItem('Роль'))

    def btn_register_team_clicked(self):
        self.controller.btn_register_team_clicked(self.ui.pushButton.text())
