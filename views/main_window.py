from PyQt5.QtWidgets import QMainWindow, QDialog, QTableWidgetItem, QPushButton, QApplication, QHeaderView
from PyQt5.QtGui import QFont, QPixmap
from PyQt5 import QtCore, QtGui
from views.ui.main_ui import Ui_MainWindow
from config import *
from PyQt5.QtCore import QFile, QTextStream, Qt
import logging
from utility.logger_super import LoggerSuper
from datetime import datetime
from env import FULLSCREEN,PRINTER_NAME,RFID_SCANNER_PID,BAR_SCANNER_PID
from utility.qt5_windows import center_on_screen
from utility.print import find_printer_by_name
from utility.com_ports import find_hwid

from controllers.main_controller import MainController
from models.main_model import MainModel
# import keyboard

class GUI_Main_Window(Ui_MainWindow, LoggerSuper):
    def custom_setup(self, window):
        self.tbl1.setRowCount(1)
        self.tbl1.setColumnCount(13)

        resolution = QApplication.desktop().availableGeometry()
        window.resize(resolution.width(), resolution.height())

        pixmap = QPixmap('res/img/logo.png')
        self.logo_label.setPixmap(pixmap)

        clock_separator_color = '#000000'
        palette = self.time_lcd_hour.palette()
        palette.setColor(palette.Light, QtGui.QColor(150, 150, 150))
        palette.setColor(palette.Dark, QtGui.QColor(150, 150, 150))
        self.time_lcd_hour.setPalette(palette)
        self.time_lcd_minute.setPalette(palette)
        self.time_lcd_second.setPalette(palette)
        self.time_separator_1.setStyleSheet(f'color: {clock_separator_color}')
        self.time_separator_2.setStyleSheet(f'color: {clock_separator_color}')

        self.error_label.setStyleSheet('color: #FF0000')
        self.error_label.setFont(QFont("Consolas", 24, QFont.Bold))
        self.error_widget.setVisible(False)

        self.exit_btn.setVisible(TEST_MODE)

        self.create_team_btn.setMinimumSize(160, 60)
        self.teamslist_btn.setMinimumSize(160, 60)

        self.rebootButton.setStyleSheet('background-color: #FF0000;')

    def set_table_header_style(self):
        self.tbl1.setColumnWidth(0, 30)
        self.tbl1.setColumnWidth(1, 140)
        self.tbl1.setColumnWidth(2, 140)
        self.tbl1.setColumnWidth(3, 120)
        self.tbl1.setColumnWidth(4, 100)
        self.tbl1.setColumnWidth(5, 150)
        self.tbl1.setColumnWidth(6, 140)
        self.tbl1.setColumnWidth(7, 140)
        self.tbl1.setColumnWidth(8, 140)
        self.tbl1.setColumnWidth(9, 150)
        self.tbl1.setColumnWidth(10, 200)
        self.tbl1.setColumnWidth(11, 140)
        self.tbl1.setColumnWidth(12, 150)

        self.tbl1.horizontalHeader().setSectionResizeMode(10, QHeaderView.Stretch)

        self.tbl1.item(0, 0).setFont(QFont("Consolas", 18, QFont.Bold))
        for col in range(1, self.tbl1.columnCount()):
            self.tbl1.item(0, col).setFont(QFont("Consolas", 14, QFont.Bold))
            self.tbl1.item(0, col).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)

class MainWindow(QMainWindow):
    logger = logging.getLogger('Main_Window')
    def __init__(self, parent = None):
        super(QMainWindow, self).__init__()
        self.controller = MainController(self) # объект для обработки действий пользователя
        self.model = MainModel(self) # объект для взаимодействия с сервером

        self._show_connection_error_flag = False
        self._show_create_team_error_flag = False
        self._block_tbl = False
        self._tbl_blink = False

        # подключаем визуальное представление
        self.ui = GUI_Main_Window()
        self.ui.setupUi(self)
        self.ui.custom_setup(self)
        self.load_style()
        self.hide_reboot_btn()

        self.ui.exit_btn.clicked.connect(self.controller.click_exit_btn)
        self.ui.create_team_btn.clicked.connect(self.controller.click_create_team_btn)
        self.ui.teamslist_btn.clicked.connect(self.controller.click_teamslist_btn)
        self.ui.rebootButton.clicked.connect(self.controller.click_reboot_btn)

        # обновления ТЧ по таймеру
        self.update_tbl_timer = QtCore.QTimer()
        self.update_tbl_timer.timeout.connect(self._fill_table_by_timer)
        self.update_tbl_timer.start(1000)

        # обновления часов по таймеру
        self.update_clock_timer = QtCore.QTimer()
        self.update_clock_timer.timeout.connect(self._fill_clock_by_timer)
        self.update_clock_timer.start(1000)  # every 1000 milliseconds

        if not FULLSCREEN:
            self.showNormal()
        else:
            self.showFullScreen()
        if not TEST_MODE:
            self.setCursor(Qt.BlankCursor)
        center_on_screen(self)
        self.fill_header()

        # keyboard.add_hotkey('Ctrl + Alt + 1', self.show_exit_btn)

    def _show_create_team_error(self):
        self._show_create_team_error_flag = True
        self._show_error_message('Необходимо сформировать хотя бы одну бригаду!', color='#FF0000', font=24)
        self._block_tbl = True

    def _hide_create_team_error(self):
        if self._show_create_team_error_flag:
            self._block_tbl = False
            self._hide_error_message()
            self._show_create_team_error_flag = False

    def _show_connection_error(self):
        self._show_connection_error_flag = True
        self._show_error_message('Ошибка связи с сервером!', color='#FF0000', font=24)
        self.ui.tbl1.setRowCount(1)
        self.ui.tbl1.update()
        self._block_tbl = True
        self.ui.create_team_btn.setEnabled(False)
        self.ui.create_team_btn.setStyleSheet('background-color: #87939A;') # grey btn
        self.ui.teamslist_btn.setEnabled(False)
        self.ui.teamslist_btn.setStyleSheet('background-color: #87939A;') # grey btn


    def _hide_connection_error(self):
        if self._show_connection_error_flag:
            self.ui.create_team_btn.setEnabled(True)
            self.ui.teamslist_btn.setEnabled(True)
            self.load_style()
            self._block_tbl = False
            self._hide_error_message()
            self._show_connection_error_flag = False

    def _show_error_message(self, message, color='#FF0000', font=24):
        self.ui.error_label.setStyleSheet(f'color: {color}; font: bold {font}pt "Consolas";')
        self.ui.error_label.setText(message)
        self.ui.error_widget.setVisible(True)

    def _hide_error_message(self):
        self.ui.error_label.setText("")
        self.ui.error_widget.setVisible(False)

    def show_reboot_btn(self):
        self.ui.rebootButton.setVisible(True)

    def hide_reboot_btn(self):
        self.ui.rebootButton.setVisible(False)

    def _update_statusbar(self):
        ok_color = '#006117'
        ok_text = 'Ok'
        error_color = '#FF0000'
        error_text = 'ERROR'

        error = False

        if find_printer_by_name(PRINTER_NAME):
            self.ui.val_printer.setStyleSheet(f'color: {ok_color}')
            self.ui.val_printer.setText(ok_text)
        else:
            self.ui.val_printer.setStyleSheet(f'color: {error_color}')
            self.ui.val_printer.setText(error_text)
            error = True

        if self.model.db.online:
            self.ui.val_server.setStyleSheet(f'color: {ok_color}')
            self.ui.val_server.setText(ok_text)
        else:
            self.ui.val_server.setStyleSheet(f'color: {error_color}')
            self.ui.val_server.setText(error_text)
            error = True

        if find_hwid(BAR_SCANNER_PID):
            self.ui.val_qr.setStyleSheet(f'color: {ok_color}')
            self.ui.val_qr.setText(ok_text)
        else:
            self.ui.val_qr.setStyleSheet(f'color: {error_color}')
            self.ui.val_qr.setText(error_text)
            error = True

        if find_hwid(RFID_SCANNER_PID):
            self.ui.val_rfid.setStyleSheet(f'color: {ok_color}')
            self.ui.val_rfid.setText(ok_text)
        else:
            self.ui.val_rfid.setStyleSheet(f'color: {error_color}')
            self.ui.val_rfid.setText(error_text)
            error = True

        if error:
            self.show_reboot_btn()
        else:
            self.hide_reboot_btn()

    def load_style(self):
        file = QFile(STYLE_PATH)
        if not file.open(QFile.ReadOnly | QFile.Text):
            self.logger.critical(f'Style {STYLE_PATH} not found.')
            self.close()

        qss_file = QTextStream(file)
        _txt = qss_file.readAll()
        self.setStyleSheet(_txt)
        self.ui.teamslist_btn.setStyleSheet(_txt)
        self.ui.create_team_btn.setStyleSheet(_txt)
        file.close()

    def closeEvent(self, event):
        print("User has clicked the red x on the main window")
        event.accept()

    def show_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec_()

    def fill_header(self):
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

    def _get_tbl_item(self, val, color=None):
        _item = QTableWidgetItem(str(val))
        if color is not None:
            _item.setBackground(color)
        return _item

    def fill_table(self):
        self.ui.tbl1.setRowCount(1)
        self.ui.tbl1.setRowCount(len(self.model.db.documents) + 1)
        _str = 1
        for doc in self.model.db.documents:
            _blnk = self._tbl_blink
            _color = None
            if doc.status == "На исполнение":
                if self._tbl_blink:
                    _color = QtGui.QColor(255, 0, 0, 127)  # light red
            elif doc.status == "В работе":
                self._tbl_blink = False
                _color = QtGui.QColor(255, 251, 125) # light yellow
            elif doc.status == "Выполнено":
                self._tbl_blink = False
                _color = QtGui.QColor(0, 255, 0, 127) # light green

            self.ui.tbl1.setItem(_str, 0, self._get_tbl_item(doc.get_num_str(), _color))
            self.ui.tbl1.setItem(_str, 1, self._get_tbl_item(doc.get_date_str(), _color))
            self.ui.tbl1.setItem(_str, 2, self._get_tbl_item(doc.get_date_sending_str(), _color))
            self.ui.tbl1.setItem(_str, 3, self._get_tbl_item(doc.type, _color))
            if doc.team_number > 0:
                self.ui.tbl1.setItem(_str, 4, self._get_tbl_item(doc.team_number, _color))
            else:
                self.ui.tbl1.setItem(_str, 4, self._get_tbl_item("", _color))
            self.ui.tbl1.setItem(_str, 5, self._get_tbl_item(doc.team_leader, _color))
            self.ui.tbl1.setItem(_str, 6, self._get_tbl_item(doc.get_execute_to_str(), _color))
            self.ui.tbl1.setItem(_str, 7, self._get_tbl_item(doc.get_start_time_str(), _color))
            self.ui.tbl1.setItem(_str, 8, self._get_tbl_item(doc.get_end_time_str(), _color))
            self.ui.tbl1.setItem(_str, 9, self._get_tbl_item(doc.status, _color))
            self.ui.tbl1.setItem(_str, 10, self._get_tbl_item(doc.destination, _color))
            self.ui.tbl1.setItem(_str, 11, self._get_tbl_item(doc.autos_number, _color))
            btn = QPushButton(parent=self.ui.tbl1)
            btn.setText('Открыть')
            btn.clicked.connect(self._click_get_doc_btn)
            btn.doc = doc
            if self._block_tbl:
                btn.setStyleSheet('background-color: #87939A;') # grey btn
            self.ui.tbl1.setCellWidget(_str, 12, btn)
            self.ui.tbl1.setRowHeight(_str, 80)

            for _col in range(0, self.ui.tbl1.columnCount() - 1):
                self.ui.tbl1.item(_str, _col).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
            _str += 1
            self._tbl_blink = _blnk

        self._tbl_blink = not self._tbl_blink

    def _fill_clock_by_timer(self):
        def format_digit(digit):
            _digit = str(digit)
            if len(_digit) == 1:
                return '0' + _digit
            return _digit

        self.ui.time_lcd_hour.display(format_digit(datetime.now().hour))
        self.ui.time_lcd_minute.display(format_digit(datetime.now().minute))
        self.ui.time_lcd_second.display(format_digit(datetime.now().second))

    def _fill_table_by_timer(self):
        if self.model.db.online:
            self._hide_connection_error()
            self.fill_table()
        else:
            self._show_connection_error()
        self.ui.tbl1.setEnabled(not self._block_tbl)

        if len(self.model.db.teams) > 0:
            self._hide_create_team_error()
        else:
            self._show_create_team_error()
        self._update_statusbar()

    def _click_get_doc_btn(self):
        self.controller.open_document_window(self.sender().doc.link)

    def _open_doc(self, link):
        doc = self.model.db.get_doc(link)
        if doc is not None:
            self.controller.open_document_window(doc.link)
