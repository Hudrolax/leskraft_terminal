from views.ui.team_list_ui import Ui_team_list
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem
from PyQt5 import QtCore
from utility.logger_super import LoggerSuper
import logging
from config import TEST_MODE


class GUI_Login_Window(Ui_team_list, LoggerSuper):
    logger = logging.getLogger('Login_form')
    def custom_setup(self, window):
        self.team_list_tbl.setRowCount(1)
        self.team_list_tbl.setColumnCount(4)
        self.team_list_tbl.setStyleSheet("font: 12pt \"Consolas\";")
        self.team_list_tbl.setSortingEnabled(False)

        width = 1100
        hight = 480
        window.setMinimumSize(width, hight)
        window.setMaximumSize(width, hight)
        window.resize(width, hight)
        self.init_GUI = True

    def set_table_header_style(self):
        self.team_list_tbl.item(0, 0).setFont(QFont("Consolas", 18, QFont.Bold))
        for col in range(1, self.team_list_tbl.columnCount()):
            self.team_list_tbl.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
            self.team_list_tbl.item(0, col).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

class TeamListWindow(QDialog):
    def __init__(self, db, parent = None):
        super(QDialog, self).__init__(parent)
        self.main_window = parent
        self.db = db

        # подключаем визуальное представление
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setModal(True)
        self.ui = GUI_Login_Window()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)

        self.ui.exitButton.clicked.connect(self._close)

        self.showNormal()
        if not TEST_MODE:
            self.setCursor(Qt.BlankCursor)
        self.fill_table_header()
        self.fill_table()
        self.center_on_screen()

    def _close(self):
        self.main_window.controller.team_list_window = None
        self.close()
        # отключим сканеры от формы и подключим их обратно к основной форме
        self.main_window.controller.connect_scanners_to_main_form()
        del self

    def center_on_screen(self):
        resolution = QApplication.desktop().availableGeometry()
        self.move(round(resolution.width() / 2 - self.geometry().width() / 2),
                  round(resolution.height() / 2 - self.geometry().height() / 2))

    def fill_table_header(self):
        self.ui.team_list_tbl.setItem(0, 0, QTableWidgetItem('№'))
        self.ui.team_list_tbl.setItem(0, 1, QTableWidgetItem('Дата'))
        self.ui.team_list_tbl.setItem(0, 2, QTableWidgetItem('Ответственный'))
        self.ui.team_list_tbl.setItem(0, 3, QTableWidgetItem('Состав'))
        QtCore.QThread.msleep(10)
        self.ui.team_list_tbl.resizeColumnsToContents()

    def fill_table(self):
        self.ui.team_list_tbl.setRowCount(len(self.db.teams) + 1)
        for team in enumerate(self.db.teams):
            self.ui.team_list_tbl.setItem(team[0] + 1, 0, QTableWidgetItem(str(team[1].num)))
            self.ui.team_list_tbl.setItem(team[0] + 1, 1, QTableWidgetItem(team[1].date_str()))
            self.ui.team_list_tbl.setItem(team[0] + 1, 2, QTableWidgetItem(str(team[1].team_leader)+' ('+team[1].team_leader.role+')'))
            teammates_str = ''
            teammates = self.db.get_team_employees(team[1])
            for teammate in teammates:
                teammates_str += f'{teammate.name} ({teammate.role})\n'
            self.ui.team_list_tbl.setItem(team[0] + 1, 3, QTableWidgetItem(teammates_str))

        QtCore.QThread.msleep(10)
        self.ui.team_list_tbl.resizeColumnsToContents()
        self.ui.team_list_tbl.resizeRowsToContents()