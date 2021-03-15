from views.ui.team_list_ui import Ui_team_list
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QPushButton
from PyQt5 import QtCore
from utility.logger_super import LoggerSuper
import logging
from time import sleep


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
    def __init__(self, controller, model, parent = None):
        super(QDialog, self).__init__(parent)
        self.controller = controller
        self.model = model
        self.parent = parent

        self._close_window = False
        """Для потомков: Закрывать окно судя по всему нужно из потока самой формы, иначе иногда виснет!"""

        # подключаем визуальное представление
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)
        self.setModal(True)
        self.ui = GUI_Login_Window()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)

        self.ui.exitButton.clicked.connect(self.controller.close)

        self.showNormal()
        self.fill_table_header()
        self.center_on_screen()

        # создадим поток обновления ТЧ по таймеру
        self.table_timer_thread = QtCore.QThread()
        self.table_timer_handler = TimerHandler()
        self.table_timer_handler.delay = 100
        self.table_timer_handler.moveToThread(self.table_timer_thread)
        self.table_timer_handler.timer_signal.connect(self._fill_table_by_timer)
        self.table_timer_thread.started.connect(self.table_timer_handler.run)
        self.table_timer_thread.start()

    def close_window(self):
        self._close_window = True

    def center_on_screen(self):
        resolution = QApplication.desktop().availableGeometry()
        self.move(round(resolution.width() / 2 - self.geometry().width() / 2),
                  round(resolution.height() / 2 - self.geometry().height() / 2))

    def fill_table_header(self):
        if not self.ui.init_GUI:
            return
        self.ui.team_list_tbl.setItem(0, 0, QTableWidgetItem('№'))
        self.ui.team_list_tbl.setItem(0, 1, QTableWidgetItem('Дата'))
        self.ui.team_list_tbl.setItem(0, 2, QTableWidgetItem('Ответственный'))
        self.ui.team_list_tbl.setItem(0, 3, QTableWidgetItem('Состав'))
        sleep(0.01)
        self.ui.team_list_tbl.resizeColumnsToContents()
        self.ui.team_list_tbl.update()

    @QtCore.pyqtSlot()
    def _fill_table_by_timer(self):
        if self._close_window:
            self.close()
        self.fill_table()

    def fill_table(self):
        if not self.ui.init_GUI:
            return
        db = self.model.db
        self.ui.team_list_tbl.setRowCount(len(db.teams) + 1)
        for team in enumerate(db.teams):
            self.ui.team_list_tbl.setItem(team[0] + 1, 0, QTableWidgetItem(str(team[1].num)))
            self.ui.team_list_tbl.setItem(team[0] + 1, 1, QTableWidgetItem(team[1].date_str()))
            self.ui.team_list_tbl.setItem(team[0] + 1, 2, QTableWidgetItem(str(team[1].team_leader)+' ('+team[1].team_leader.role+')'))
            teammates_str = ''
            teammates = db.get_team_employees(team[1])
            for teammate in teammates:
                teammates_str += f'{teammate.name} ({teammate.role})\n'
            self.ui.team_list_tbl.setItem(team[0] + 1, 3, QTableWidgetItem(teammates_str))


        sleep(0.01)
        self.ui.team_list_tbl.resizeColumnsToContents()
        self.ui.team_list_tbl.resizeRowsToContents()
        self.ui.team_list_tbl.update()


class TimerHandler(QtCore.QObject):
    timer_signal = QtCore.pyqtSignal()
    delay = 1000

    def run(self):
        while True:
            self.timer_signal.emit()
            QtCore.QThread.msleep(self.delay)