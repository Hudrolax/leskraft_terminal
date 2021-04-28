from views.ui.create_team_ui import Ui_Login
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QPushButton
from PyQt5 import QtCore
from utility.logger_super import LoggerSuper
import logging
from config import TEST_MODE
from controllers.create_team_controller import CreateTeam_controller
from models.create_team_model import CreateTeam_model

class GUI_Login_Window(Ui_Login, LoggerSuper):
    logger = logging.getLogger('Login_form')
    def custom_setup(self, window):
        self.tbl.setRowCount(1)
        self.tbl.setColumnCount(5)
        self.tbl.setStyleSheet("font: 12pt \"Consolas\";")
        self.tbl.setSortingEnabled(False)

        width = 850
        hight = 480
        window.setMinimumSize(width, hight)
        window.setMaximumSize(width, hight)
        window.resize(width, hight)


class CreateTeamWindow(QDialog):
    def __init__(self, db, parent = None):
        super(QDialog, self).__init__(parent)
        self.main_window = parent
        self.controller = CreateTeam_controller(self)
        self.model = CreateTeam_model(self, db)

        # подключаем визуальное представление
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setModal(True)
        self.ui = GUI_Login_Window()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)
        self.set_create_team_screen()

        self.ui.exit_btn.clicked.connect(self.controller.close)

        self.showNormal()
        if not TEST_MODE:
            self.setCursor(Qt.BlankCursor)

        self.fill_table_header()
        self.center_on_screen()

    def update_status_bar(self, result, text):
        self.ui.label_2.setText(text)
        if result:
            self.ui.label_2.setStyleSheet("color: green")
        else:
            self.ui.label_2.setStyleSheet("color: red")

    def set_create_team_screen(self):
        self.ui.tabWidget.setTabEnabled(0, True)
        self.ui.tabWidget.setTabEnabled(1, False)
        self.ui.tabWidget.setTabEnabled(2, False)
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.label_2.setVisible(False)
        self.ui.label_3.setVisible(True)
        self.ui.label_3.setStyleSheet("color: black")
        _text = "Отсканируйте карту кладовщика"
        self.ui.label_3.setText(_text)
        self.ui.state_label.setText(_text)
        self.ui.state_label.setStyleSheet("color: black")

    def set_register_teammates_screen(self):
        self.ui.tabWidget.setTabEnabled(0, False)
        self.ui.tabWidget.setTabEnabled(1, True)
        self.ui.tabWidget.setTabEnabled(2, False)
        self.ui.tabWidget.setCurrentIndex(1)
        self.ui.label_2.setVisible(True)
        self.ui.label_3.setVisible(False)
        _text = "Отсканируйте карту участника бригады"
        self.ui.label_2.setText(_text)
        self.ui.label_2.setStyleSheet("color: black")
        self.ui.state_label.setText(_text)
        self.ui.state_label.setStyleSheet("color: black")

    def set_register_team_screen(self, result, answer):
        self.ui.tabWidget.setTabEnabled(0, False)
        self.ui.tabWidget.setTabEnabled(1, False)
        self.ui.tabWidget.setTabEnabled(2, True)
        self.ui.tabWidget.setCurrentIndex(2)

        self.ui.label_6.setText(answer)
        self.ui.state_label.setText(answer)
        if result:
            self.ui.label_6.setStyleSheet('color: green; font: bold 16pt "Consolas"')
            self.ui.state_label.setStyleSheet("color: green")
        else:
            self.ui.label_6.setStyleSheet('color: red; font: bold 16pt "Consolas"')
            self.ui.state_label.setStyleSheet("color: red")

        self.close_window_timer = QtCore.QTimer()
        self.close_window_timer.setSingleShot(True)
        self.close_window_timer.timeout.connect(self.controller.close)
        self.close_window_timer.start(3000)

    def center_on_screen(self):
        resolution = QApplication.desktop().availableGeometry()
        self.move(round(resolution.width() / 2 - self.geometry().width() / 2),
                  round(resolution.height() / 2 - self.geometry().height() / 2))

    def fill_table_header(self):
        self.ui.tbl.setItem(0, 0, QTableWidgetItem('№'))
        self.ui.tbl.setItem(0, 1, QTableWidgetItem('Имя'))
        self.ui.tbl.setItem(0, 2, QTableWidgetItem('Карта'))
        self.ui.tbl.setItem(0, 3, QTableWidgetItem('Роль'))
        QtCore.QThread.msleep(100)
        self.ui.tbl.resizeColumnsToContents()

    def fill_table(self):
        self.ui.tbl.setRowCount(1)
        if self.model.team_leader is None:
            return

        self.ui.tbl.setRowCount(len(self.model.teammates) + 2)
        self.ui.tbl.setItem(1, 0, QTableWidgetItem('1'))
        self.ui.tbl.setItem(1, 1, QTableWidgetItem(self.model.team_leader.name))
        self.ui.tbl.setItem(1, 2, QTableWidgetItem(self.model.team_leader.card_number))
        self.ui.tbl.setItem(1, 3, QTableWidgetItem(self.model.team_leader.role))
        for emp in enumerate(self.model.teammates):
            self.ui.tbl.setItem(emp[0]+2, 0, QTableWidgetItem(str(emp[0]+2)))
            self.ui.tbl.setItem(emp[0]+2, 1, QTableWidgetItem(emp[1].name))
            self.ui.tbl.setItem(emp[0]+2, 2, QTableWidgetItem(emp[1].card_number))
            self.ui.tbl.setItem(emp[0]+2, 3, QTableWidgetItem(emp[1].role))

            btn = QPushButton(self.ui.tbl)
            btn.setText('Удалить')
            btn.clicked.connect(self._btn_del_employee_clicked)
            btn.employee = emp[1]
            """Для потомков:
                setCellWidget крашит программу, когда пытаешься вызвать его из основного потока формы
                Потому заполнение таблицы сделано в отдельном потоке"""
            self.ui.tbl.setCellWidget(emp[0]+2, 4, btn)

        QtCore.QThread.msleep(100)
        self.ui.tbl.resizeColumnsToContents()

    def _btn_register_team_clicked(self):
        self.controller.get_RFID_signal(self.ui.lineEdit.text())

    def _btn_del_employee_clicked(self):
        self.controller.del_employee(self.sender().employee)