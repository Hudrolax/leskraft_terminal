from PyQt5.QtWidgets import QMainWindow, QDialog, QTableWidgetItem, QPushButton, QApplication
from PyQt5.QtGui import QFont, QPixmap
from PyQt5 import QtCore, QtGui
from views.ui.main_ui import Ui_MainWindow
from utility.threaded_class import Threaded_class
from config import *
from PyQt5.QtCore import QFile, QTextStream
import logging
from utility.logger_super import LoggerSuper
import sys
from time import sleep
from datetime import datetime
from env import FULLSCREEN
from utility.qt5_timer import TimerHandler
from utility.qt5_windows import center_on_screen
# import keyboard

class GUI_Main_Window(Ui_MainWindow, LoggerSuper):
    def custom_setup(self, window):
        self.tbl1.setRowCount(1)
        self.tbl1.setColumnCount(13)

        resolution = QApplication.desktop().availableGeometry()
        window.resize(resolution.width(), resolution.height())

        pixmap = QPixmap('res/img/logo.png')
        self.logo_label.setPixmap(pixmap)
        self.init_GUI = True

        palette = self.time_lcd_hour.palette()
        palette.setColor(palette.Light, QtGui.QColor(0, 255, 0))
        palette.setColor(palette.Dark, QtGui.QColor(0, 255, 0))
        self.time_lcd_hour.setPalette(palette)
        self.time_lcd_minute.setPalette(palette)
        self.time_lcd_second.setPalette(palette)
        self.time_separator_1.setStyleSheet('color: #00FF00')
        self.time_separator_2.setStyleSheet('color: #00FF00')
        self.exit_btn.setVisible(not FULLSCREEN)

        self.error_label.setStyleSheet('color: #FF0000')
        self.error_label.setFont(QFont("Consolas", 24, QFont.Bold))
        self.error_widget.setVisible(False)

    def set_table_header_style(self):
        self.tbl1.item(0, 0).setFont(QFont("Consolas", 18, QFont.Bold))
        for col in range(1, self.tbl1.columnCount()):
            self.tbl1.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
            self.tbl1.item(0, col).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)

class MainWindow(QMainWindow):
    logger = logging.getLogger('Main_Window')
    def __init__(self, controller, model, parent = None):
        super(QMainWindow, self).__init__(parent)
        self.controller = controller
        self.model = model

        self._show_connection_error_flag = False
        self._show_create_team_error_flag = False

        # подключаем визуальное представление
        self.ui = GUI_Main_Window()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)
        self.load_style()

        self.ui.exit_btn.clicked.connect(self.controller.click_exit_btn)
        self.ui.create_team_btn.clicked.connect(self.controller.click_commands_btn)
        # создадим поток обновления ТЧ по таймеру
        self.table_timer_thread = QtCore.QThread()
        self.table_timer_handler = TimerHandler(1000)
        self.table_timer_handler.moveToThread(self.table_timer_thread)
        self.table_timer_handler.timer_signal.connect(self._fill_table_by_timer)
        self.table_timer_thread.started.connect(self.table_timer_handler.run)
        self.table_timer_thread.start()
        # создадим поток обновления часов по таймеру
        self.clock_timer_thread = QtCore.QThread()
        self.clock_timer_handler = TimerHandler(100)
        self.clock_timer_handler.moveToThread(self.clock_timer_thread)
        self.clock_timer_handler.timer_signal.connect(self._fill_clock_by_timer)
        self.clock_timer_thread.started.connect(self.clock_timer_handler.run)
        self.clock_timer_thread.start()

        if not FULLSCREEN:
            self.showNormal()
        else:
            self.showFullScreen()
        center_on_screen(self)
        self.fill_header()
        # keyboard.add_hotkey('Ctrl + Alt + 1', self.show_exit_btn)

    def _show_create_team_error(self):
        self._show_create_team_error_flag = True
        self._show_error_message('Необходимо сформировать хотя бы одну бригаду!', color='#FF5809', font=24)
        self.ui.tbl1.setEnabled(False)

    def _hide_create_team_error(self):
        if self._show_create_team_error_flag:
            self.ui.tbl1.setEnabled(True)
            self._hide_error_message()
            self._show_create_team_error_flag = False

    def _show_connection_error(self):
        self._show_connection_error_flag = True
        self._show_error_message('Ошибка связи с сервером!', color='#FF0000', font=24)
        self.ui.tbl1.setRowCount(1)
        self.ui.tbl1.update()
        self.ui.tbl1.setEnabled(False)
        self.ui.create_team_btn.setEnabled(False)
        self.ui.teamslist_btn.setEnabled(False)

    def _hide_connection_error(self):
        if self._show_connection_error_flag:
            self.ui.create_team_btn.setEnabled(True)
            self.ui.teamslist_btn.setEnabled(True)
            self.ui.tbl1.setEnabled(True)
            self._hide_error_message()
            self._show_connection_error_flag = False

    def _show_error_message(self, message, color='#FF0000', font=24):
        self.ui.error_label.setStyleSheet(f'color: {color}')
        self.ui.error_label.setFont(QFont("Consolas", font, QFont.Bold))
        self.ui.error_label.setText(message)
        self.ui.error_widget.setVisible(True)

    def _hide_error_message(self):
        self.ui.error_label.setText("")
        self.ui.error_widget.setVisible(False)

    # def show_exit_btn(self):
    #     self.ui.exit_btn.setVisible(not self.ui.exit_btn.isVisible())

    def load_style(self):
        file = QFile(STYLE_PATH)
        if not file.open(QFile.ReadOnly | QFile.Text):
            self.logger.critical(f'Style {STYLE_PATH} not found.')
            Threaded_class.stop()
            sys.exit(self)

        qss_file = QTextStream(file)
        self.setStyleSheet(qss_file.readAll())
        file.close()

    def closeEvent(self, event):
        Threaded_class.stop()
        print("User has clicked the red x on the main window")
        event.accept()

    def show_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec_()

    def fill_header(self):
        if not self.ui.init_GUI:
            return
        self.ui.tbl1.setItem(0, 0, QTableWidgetItem('№'))
        self.ui.tbl1.setItem(0, 1, QTableWidgetItem('От'))
        self.ui.tbl1.setItem(0, 2, QTableWidgetItem('Поступило'))
        self.ui.tbl1.setItem(0, 3, QTableWidgetItem('Тип'))
        self.ui.tbl1.setItem(0, 4, QTableWidgetItem('Бригада'))
        self.ui.tbl1.setItem(0, 5, QTableWidgetItem('Руководитель'))
        self.ui.tbl1.setItem(0, 6, QTableWidgetItem('Исполнить к'))
        self.ui.tbl1.setItem(0, 7, QTableWidgetItem('Начато'))
        self.ui.tbl1.setItem(0, 8, QTableWidgetItem('Окончено'))
        self.ui.tbl1.setItem(0, 9, QTableWidgetItem('Статус'))
        self.ui.tbl1.setItem(0, 10, QTableWidgetItem('Направление'))
        self.ui.tbl1.setItem(0, 11, QTableWidgetItem('Номер авто'))
        self.ui.tbl1.setItem(0, 12, QTableWidgetItem(''))
        self.ui.set_table_header_style()
        self.ui.tbl1.update()

    def fill_table(self):
        if not self.ui.init_GUI:
            return
        self.ui.tbl1.setRowCount(len(self.model.db.documents) + 1)
        _str = 1
        for doc in self.model.db.documents:
            self.ui.tbl1.setItem(_str, 0, QTableWidgetItem(str(doc.get_num_str())))
            self.ui.tbl1.setItem(_str, 1, QTableWidgetItem(str(doc.get_date_str())))
            self.ui.tbl1.setItem(_str, 2, QTableWidgetItem(doc.get_date_sending_str()))
            self.ui.tbl1.setItem(_str, 3, QTableWidgetItem(doc.type))
            if doc.team_number > 0:
                self.ui.tbl1.setItem(_str, 4, QTableWidgetItem(str(doc.team_number)))
            else:
                self.ui.tbl1.setItem(_str, 4, QTableWidgetItem(""))
            self.ui.tbl1.setItem(_str, 5, QTableWidgetItem(doc.team_leader))
            self.ui.tbl1.setItem(_str, 6, QTableWidgetItem(doc.get_execute_to_str()))
            self.ui.tbl1.setItem(_str, 7, QTableWidgetItem(doc.get_start_time_str()))
            self.ui.tbl1.setItem(_str, 8, QTableWidgetItem(doc.get_end_time_str()))
            self.ui.tbl1.setItem(_str, 9, QTableWidgetItem(doc.status))
            self.ui.tbl1.setItem(_str, 10, QTableWidgetItem(doc.destination))
            self.ui.tbl1.setItem(_str, 11, QTableWidgetItem(doc.autos_number))
            btn = QPushButton(parent=self.ui.tbl1)
            btn.setText('Открыть')
            btn.clicked.connect(self._click_get_doc_btn)
            btn.doc = doc
            self.ui.tbl1.setCellWidget(_str, 12, btn)
            self.ui.tbl1.setRowHeight(_str, 80)
            _str += 1

        # делаем ресайз колонок по содержимому
        sleep(0.01)
        self.ui.tbl1.resizeColumnsToContents()
        self.ui.tbl1.update()

    @QtCore.pyqtSlot()
    def _fill_clock_by_timer(self):
        def format_digit(digit):
            _digit = str(digit)
            if len(_digit) == 1:
                return '0' + _digit
            return _digit

        if not self.ui.init_GUI:
            return
        self.ui.time_lcd_hour.display(format_digit(datetime.now().hour))
        self.ui.time_lcd_minute.display(format_digit(datetime.now().minute))
        self.ui.time_lcd_second.display(format_digit(datetime.now().second))

        if self.controller.getted_bar_code != '':
            _bar_code = self.controller.getted_bar_code
            self.controller.getted_bar_code = ''
            self._open_doc(_bar_code)

    @QtCore.pyqtSlot()
    def _fill_table_by_timer(self):
        if self.model.get_online_status():
            self._hide_connection_error()
            self.fill_table()
        else:
            self._show_connection_error()

        if len(self.model.db.teams) > 0:
            self._hide_create_team_error()
        else:
            self._show_create_team_error()

    def _click_get_doc_btn(self):
        self.controller.open_document_window(self.sender().doc.link)

    def _open_doc(self, link):
        doc = self.model.db.get_doc(link)
        if doc is not None:
            self.controller.open_document_window(doc.link)