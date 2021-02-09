from views.ui.choice_team_ui import Ui_choice_team_form
from utility.logger_super import LoggerSuper
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from utility.qt5_windows import center_on_screen
import logging
from time import sleep


class GUI_choice_team(Ui_choice_team_form, LoggerSuper):
    def custom_setup(self, window):
        self.tbl.setRowCount(1)
        self.tbl.setColumnCount(4)

class ChoiceTeamWindow(QDialog):
    logger = logging.getLogger('Choice_team_form')
    def __init__(self, parent, teams):
        super(QDialog, self).__init__(parent)
        self.teams = teams
        self.parent = parent

        # подключаем визуальное представление
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setModal(True)
        self.ui = GUI_choice_team()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)

        resolution = QApplication.desktop().availableGeometry()
        _height = 150 * len(self.teams)
        if _height > resolution.height():
            _height = resolution.height()
        self.resize(round(resolution.width() * 0.7), _height)

        self.showNormal()
        center_on_screen(self)
        self._fill_table_header()
        self.fill_table()
        self.exec_()

    def set_table_header_style(self):
        pass
        # for col in range(0, self.ui.tbl.columnCount()-1):
        #     self.ui.tbl.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
        #     self.ui.tbl.item(0, col).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

    def _fill_table_header(self):
        self.ui.tbl.setItem(0, 0, QTableWidgetItem('№'))
        self.ui.tbl.setItem(0, 1, QTableWidgetItem('Кладовщик'))
        self.ui.tbl.setItem(0, 2, QTableWidgetItem('Состав'))
        self.ui.tbl.setColumnWidth(0, 30)
        self.ui.tbl.setColumnWidth(1, 350)
        self.ui.tbl.setColumnWidth(2, 100)
        self.ui.tbl.setColumnWidth(3, 150)
        self.ui.tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.set_table_header_style()

    def fill_table(self):
        self.ui.tbl.setRowCount(len(self.teams) + 1)
        _str = 1
        for team in self.teams:
            self.ui.tbl.setItem(_str, 0, QTableWidgetItem(str(team.num)))
            self.ui.tbl.setItem(_str, 1, QTableWidgetItem(str(team.team_leader)))

            _emloyees = self.parent.model.db.get_team_employees(team)
            _emloyees_str = ''
            for _employee in _emloyees:
                _emloyees_str += f'{_employee.name} ({_employee.role})\n'

            self.ui.tbl.setItem(_str, 2, QTableWidgetItem(_emloyees_str))

            btn = QPushButton(parent=self.ui.tbl)
            btn.setText('Выбрать')
            btn.clicked.connect(self._click_return_btn)
            btn.team = team
            self.ui.tbl.setCellWidget(_str, 3, btn)
            self.ui.tbl.setRowHeight(_str, 80)

            _str += 1

        sleep(0.01)
        self.ui.tbl.update()

    def _click_return_btn(self):
        self.parent.choosed_team = self.sender().team
        self.close()