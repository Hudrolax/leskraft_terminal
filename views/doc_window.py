from views.ui.doc_form_ui import Ui_doc_form
from views.error_message_window import Error_window
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QAbstractItemView
from PyQt5 import QtCore
from utility.logger_super import LoggerSuper
from utility.qt5_timer import TimerHandler
from utility.qt5_windows import center_on_screen
from datetime import datetime
import logging
from views.choice_team_window import ChoiceTeamWindow
from config import TEST_MODE


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
        self.init_GUI = True

    def set_table_header_style(self):
        self.doc_tbl.item(0, 0).setFont(QFont("Consolas", 18, QFont.Bold))
        for col in range(1, self.doc_tbl.columnCount()):
            self.doc_tbl.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
            self.doc_tbl.item(0, col).setTextAlignment(Qt.AlignCenter | Qt.AlignCenter)

class DocumentWindow(QDialog):
    logger = logging.getLogger('Document_Form')
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
        self.ui.close_button.clicked.connect(self.controller.close_window)
        self.ui.printButton.clicked.connect(self._print_document)

        self.showNormal()
        if not TEST_MODE:
            self.setCursor(Qt.BlankCursor)
        center_on_screen(self)

        self.choice_team_window = None # Окно выбора команды
        self.choosed_team = None # Выбранная команда

        # создадим поток по таймеру
        self.clock_timer_thread = QtCore.QThread()
        self.clock_timer_handler = TimerHandler(500)
        self.clock_timer_handler.moveToThread(self.clock_timer_thread)
        self.clock_timer_handler.timer_signal.connect(self._timer)
        self.clock_timer_thread.started.connect(self.clock_timer_handler.run)
        self.clock_timer_thread.start()
        self._update_status = True
        self._update_status_time = datetime.now()

    def _open_choice_team_window(self, teams):
        self.choice_team_window = ChoiceTeamWindow(self, teams)

    @QtCore.pyqtSlot()
    def _timer(self):
        self._threaded_get_RFID_code()
        self._threaded_get_bar_code()
        self.fill_header()
        self.fill_table_header()
        self.fill_table()
        if (datetime.now()-self._update_status_time).total_seconds() > 3:
            self._update_status = True

    def _show_status_message(self, message, color='#960E10', font_size='24'):
        self._update_status = False
        self._update_status_time = datetime.now()
        self.ui.status_bar.setText(message)
        self.ui.status_bar.setStyleSheet(f'color: {color}; font: bold {font_size}pt \"Consolas\"')
        return

    def _threaded_get_RFID_code(self):
        if self.controller.getted_RFID_code != '':
            _code = self.controller.getted_RFID_code
            self.controller.getted_RFID_code = ''

            if self.model.doc().team_number > 0:
                return

            _teams = self.model.db.get_team_by_emloyee_code(_code)
            if len(_teams) > 0:
                if len(_teams) > 1:
                    self._open_choice_team_window(_teams)
                    if self.choosed_team is not None:
                        self.model.team = self.choosed_team
                        self.choosed_team = None
                        self.choice_team_window = None
                else:
                    self.model.team = _teams[0]
            else:
                self._show_status_message(f'Не найдена бригада с сотрудником с номером карты {_code}')

    def _threaded_get_bar_code(self):
        if self.controller.getted_bar_code != '':
            _code = self.controller.getted_bar_code
            self.controller.getted_bar_code = ''
            if self.model.team is None and self.model.doc().team_number == 0:
                self._show_status_message('Сначала отсканируйте карту сотрудника для начала работы!!!')
                return

            doc = self.model.db.get_doc(_code)
            if doc is not None:
                if doc.link == self.model.doc_link:
                    result = ''
                    if self.model.doc().status == 'На исполнение':
                        result = self.controller.start_work_with_document()
                    elif self.model.doc().status == 'В работе':
                        result = self.controller.stop_work_with_document()
                    elif self.model.doc().status == 'Выполнено':
                        self._show_status_message('Задание уже выполнено')
                        return
                    else:
                        result = 'Неизвестная ошибка'

                    if result:
                        self.controller.close_window()
                    else:
                        Error_window(self, result)
                else:
                    self._show_status_message('Вы осканировали не тот документ!')
                    return
            else:
                self._show_status_message(f'Не найден документ с кодом {_code}')

    def fill_header(self):
        if not self.ui.init_GUI:
            return
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
        if self._update_status:
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
        self.ui.doc_tbl.update()

    @pyqtSlot(bool)
    def _start_work_with_doc(self):
        result = self.controller.start_work_with_document()
        if result:
            self.close()

    @pyqtSlot(bool)
    def _stop_work_with_doc(self):
        result = self.controller.stop_work_with_document()

    def _print_document(self):
        self.ui.printButton.setEnabled(False)
        self.ui.printButton.setStyleSheet('background-color: #87939A;') # grey btn

        self._show_status_message('Идет печать...')
        self.controller.click_print_btn()