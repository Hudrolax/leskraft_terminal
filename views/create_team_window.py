from views.ui.create_team_ui import Ui_Login
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QPushButton
from PyQt5 import QtCore
from utility.logger_super import LoggerSuper
import logging
from time import sleep
from config import TEST_MODE


class GUI_Login_Window(Ui_Login, LoggerSuper):
    logger = logging.getLogger('Login_form')
    def custom_setup(self, window):
        self.tbl.setRowCount(1)
        self.tbl.setColumnCount(5)
        self.tbl.setStyleSheet("font: 12pt \"Consolas\";")
        self.tbl.setSortingEnabled(False)

        width = 800
        hight = 480
        window.setMinimumSize(width, hight)
        window.setMaximumSize(width, hight)
        window.resize(width, hight)
        self.init_GUI = True

    def set_table_header_style(self):
        self.tbl.item(0, 0).setFont(QFont("Consolas", 18, QFont.Bold))
        for col in range(1, self.tbl.columnCount()):
            self.tbl.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
            self.tbl.item(0, col).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

class CreateTeamWindow(QDialog):
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
        self.set_create_team_screen()

        self.ui.exit_btn.clicked.connect(self.controller.close)
        self.ui.pushButton.clicked.connect(self._btn_register_team_clicked)

        self.showNormal()
        if not TEST_MODE:
            self.setCursor(Qt.BlankCursor)
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
        self._update_table = False

    def close_window(self):
        self._close_window = True

    def maximum_teammates_reached_message(self):
        self.ui.label_2.setText(f'Количество участников бригады не может быть больше {self.model.maximum_teammates+1}')
        self.ui.label_2.setStyleSheet("color: red")

    def employee_not_found_message(self, card_id):
        _text = f'Сотрудник с картой {card_id} не найден. Попробуйте другую карту.'
        self.ui.state_label.setText(_text)
        self.ui.state_label.setStyleSheet("color: red")

    def it_is_not_team_leader_error(self, card_id):
        _text = f'Сотрудник с картой {card_id} не является кладовщиком!.'
        self.ui.state_label.setText(_text)
        self.ui.state_label.setStyleSheet("color: red")

    def employee_already_exist_message(self, card_id):
        _text = f'Сотрудник с картой {card_id} уже является участником команды!.'
        self.ui.state_label.setText(_text)
        self.ui.state_label.setStyleSheet("color: red")

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
        _text = "Отсканируйте карту участника команды"
        self.ui.label_2.setText(_text)
        self.ui.label_2.setStyleSheet("color: black")
        self.ui.state_label.setText(_text)
        self.ui.state_label.setStyleSheet("color: black")
        self._update_table = True

    def set_register_team_screen(self, result, answer):
        self.ui.tabWidget.setTabEnabled(0, False)
        self.ui.tabWidget.setTabEnabled(1, False)
        self.ui.tabWidget.setTabEnabled(2, True)
        self.ui.tabWidget.setCurrentIndex(2)

        if result:
            _text = "Команда зарегистрирована"
            self.ui.label_6.setText(_text)
            self.ui.label_6.setStyleSheet("color: green")
            self.ui.state_label.setText(_text)
            self.ui.state_label.setStyleSheet("color: green")
        else:
            _text = answer
            self.ui.label_6.setText(_text)
            self.ui.label_6.setStyleSheet("color: red")
            self.ui.state_label.setText(_text)
            self.ui.state_label.setStyleSheet("color: red")
        sleep(3)
        self.controller.close()

    def center_on_screen(self):
        resolution = QApplication.desktop().availableGeometry()
        self.move(round(resolution.width() / 2 - self.geometry().width() / 2),
                  round(resolution.height() / 2 - self.geometry().height() / 2))

    def fill_table_header(self):
        if not self.ui.init_GUI:
            return
        self.ui.tbl.setItem(0, 0, QTableWidgetItem('№'))
        self.ui.tbl.setItem(0, 1, QTableWidgetItem('Имя'))
        self.ui.tbl.setItem(0, 2, QTableWidgetItem('Карта'))
        self.ui.tbl.setItem(0, 3, QTableWidgetItem('Роль'))
        sleep(0.01)
        self.ui.tbl.resizeColumnsToContents()
        self.ui.tbl.update()

    @QtCore.pyqtSlot()
    def _fill_table_by_timer(self):
        if self._close_window:
            self.close()
        self.fill_table()

    def fill_table(self):
        if not self.ui.init_GUI:
            return
        if self.model.team_leader is None:
            return
        if self._update_table:
            self._update_table = False
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

        sleep(0.01)
        self.ui.tbl.resizeColumnsToContents()
        self.ui.tbl.update()

    def _btn_register_team_clicked(self):
        self.controller.get_RFID_signal(self.ui.lineEdit.text())

    def _btn_del_employee_clicked(self):
        self.controller.del_employee(self.sender().employee)

class TimerHandler(QtCore.QObject):
    timer_signal = QtCore.pyqtSignal()
    delay = 100

    def run(self):
        while True:
            self.timer_signal.emit()
            QtCore.QThread.msleep(self.delay)