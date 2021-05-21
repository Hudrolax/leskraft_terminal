from views.create_team_window import CreateTeamWindow
from views.team_list_window import TeamListWindow
from views.doc_window import DocumentWindow

from utility.com_ports import COM_port
from env import RFID_SCANNER_PID, BAR_SCANNER_PID, WATCHDOG_PID
from utility.reboot import reboot
from PyQt5 import QtCore
from utility.logger_super import LoggerSuper
import logging

class MainController:
    logger = logging.getLogger('Main_controller')
    def __init__( self, main_window):
        self.main_window = main_window
        self.create_team_window = None
        self.team_list_window = None
        self.doc_window = None
        # поток работы с Watchdog
        self.watchdog_thread = QtCore.QThread()
        self.watchdog_handler = Watchdog_Handler()
        self.watchdog_handler.moveToThread(self.watchdog_thread)
        self.watchdog_thread.started.connect(self.watchdog_handler.run)
        self.watchdog_thread.start()
        # поток работы с QR
        self.QR_thread = QtCore.QThread()
        self.QR_handler = QR_CodeScanner_Handler()
        self.QR_handler.moveToThread(self.QR_thread)
        self.QR_handler.get_QR_code_signal.connect(self.get_QR_signal)
        self.QR_thread.started.connect(self.QR_handler.run)
        self.QR_thread.start()
        # поток работы с RFID
        self.RFID_thread = QtCore.QThread()
        self.RFID_handler = RFIF_Scanner_Handler()
        self.RFID_handler.moveToThread(self.RFID_thread)
        self.RFID_handler.get_RFID_code_signal.connect(self.get_RFID_signal)
        self.RFID_thread.started.connect(self.RFID_handler.run)
        self.RFID_thread.start()

    def get_RFID_signal(self, code):
        self.logger.info(f'get RFID_code: {code}')

    def get_QR_signal(self, code):
        self.logger.info(f'get QR_code: {code}')
        if self.main_window.model.db.get_doc(code) is not None:
            self.open_document_window(code)
        else:
            self.show_message_with_timer('Документ не найден. Возможно вы осканировали не ту бумагу.')

    def show_message_with_timer(self, message, color='#960E10', font_size='24'):
        self.main_window._show_error_message(message, color, font_size)
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.main_window._hide_error_message)
        self._timer.start(3000)

    def disconnect_scanners_from_main_form(self):
        self.QR_handler.get_QR_code_signal.disconnect(self.get_QR_signal)
        self.RFID_handler.get_RFID_code_signal.disconnect(self.get_RFID_signal)

    def connect_scanners_to_main_form(self):
        try:
            self.QR_handler.get_QR_code_signal.disconnect()
        except TypeError:
            pass
        try:
            self.RFID_handler.get_RFID_code_signal.disconnect()
        except TypeError:
            pass
        self.QR_handler.get_QR_code_signal.connect(self.get_QR_signal)
        self.RFID_handler.get_RFID_code_signal.connect(self.get_RFID_signal)

    def open_document_window(self, doc_link):
        self.doc_window = DocumentWindow(self.main_window.model.db, doc_link, self.main_window)
        # отключим сигналы сканеров от основной формы
        self.disconnect_scanners_from_main_form()
        # подключим сигналы сканнеров к форме документа
        self.RFID_handler.get_RFID_code_signal.connect(self.doc_window.controller.get_RFID_signal)
        self.QR_handler.get_QR_code_signal.connect(self.doc_window.controller.get_QR_signal)

    def click_create_team_btn(self):
        self.create_team_window = CreateTeamWindow(self.main_window.model.db, self.main_window)
        # отключим сигналы сканеров от основной формы
        self.disconnect_scanners_from_main_form()
        # подключим сигнал сканера к форме регистрации
        self.RFID_handler.get_RFID_code_signal.connect(self.create_team_window.controller.get_RFID_signal)

    def click_teamslist_btn(self):
        # отключим сигналы сканеров от основной формы
        self.disconnect_scanners_from_main_form()
        self.team_list_window = TeamListWindow(self.main_window.model.db, self.main_window)

    def click_reboot_btn(self):
        self.logger.info('User pressed the reboot button!')
        reboot()

    def click_exit_btn(self):
        self.main_window.close()

# класс для работы со сканером QR в отдельном потоке
class QR_CodeScanner_Handler(QtCore.QObject, COM_port, LoggerSuper):
    get_QR_code_signal = QtCore.pyqtSignal(str)
    logger = logging.getLogger('QR_CodeScanner_Handler')

    def __init__(self):
        super().__init__(name='QRScanner', PID=BAR_SCANNER_PID, speed=9600, timeout=1)

    def run(self):
        while True:
            _qr_code = ''
            if self.initialized:
                try:
                    _qr_code = self.serial.readline().decode().replace('\r\n', '')
                except:
                    self.initialized = False
                    self.inicialize_com_port()

                if _qr_code != '':
                    if _qr_code.find('t=') == -1:
                        self.get_QR_code_signal.emit(_qr_code)
                    else:
                        self.logger.warning(f'Got wrong code format: {_qr_code}')
            else:
                QtCore.QThread.msleep(5000)
                self.inicialize_com_port()

# класс для работы со сканером RFID в отдельном потоке
class RFIF_Scanner_Handler(QtCore.QObject, COM_port, LoggerSuper):
    get_RFID_code_signal = QtCore.pyqtSignal(str)
    logger = logging.getLogger('RFIF_Scanner_Handler')
    def __init__(self):
        super().__init__(name='RFIDScanner', PID=RFID_SCANNER_PID, speed=9600, timeout=1)
        self.id = '00'

    # метод, который будет выполнять алгоритм в другом потоке
    def run(self):
        buffer = b''
        while True:
            if self.initialized:
                try:
                    buffer += self.serial.read()
                except:
                    self.initialized = False
                    continue

                str_buffer = buffer.decode()
                if str_buffer.find('#S'+self.id) > -1:
                    buffer = b''
                    continue
                if str_buffer.startswith('#F'+self.id) and len(str_buffer) == 14:
                    buffer = b''
                    h_code = str_buffer[-8:]
                    try:
                        card_id =  int(h_code, 16)
                    except Exception as e:
                        self.logger.error(f'decode to int error "{h_code}". buffer is {str_buffer}')
                        continue
                    card_id = str(card_id)
                    self.logger.debug(f'get RFID code {card_id}')
                    self.get_RFID_code_signal.emit(card_id)
            else:
                buffer = b''
                QtCore.QThread.msleep(5000)
                self.inicialize_com_port()

# класс для работы с вотчдогом в отдельном потоке
class Watchdog_Handler(QtCore.QObject, COM_port, LoggerSuper):
    logger = logging.getLogger('Watchdog_Handler')
    def __init__(self):
        super().__init__(name='Watchdog', PID=WATCHDOG_PID, speed=9600, timeout=1)

    def run(self):
        QtCore.QThread.msleep(3000)
        if not self.initialized:
            self.logger.info('Вотчдог не инициализирован. Работаем без него...')
            return

        while True:
            if self.initialized:
                try:
                    self.serial.write(bytes('~U', 'utf-8'))
                except:
                    self.logger.warning(f'Write error to port {self.serial}')
            else:
                return
            QtCore.QThread.msleep(3000)