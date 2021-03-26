from views.main_window import MainWindow
from controllers.doc_form_controller import DocForm_controller
from controllers.create_team_controller import CreateTeam_controller
from controllers.team_list_controller import TeamList_controller
from utility.threaded_class import Threaded_class
from controllers.RFID_scanner import RFIDScanner
from controllers.barcode_scanner import BarScanner
from env import RFID_SCANNER_PID, BAR_SCANNER_PID
from utility.reboot import reboot
import sys
import logging

class MainController:
    logger = logging.getLogger('Main_controller')
    def __init__( self, model):
        self.model = model
        self.rfid_scanner = RFIDScanner(RFID_SCANNER_PID)
        self.rfid_scanner.add_observer(self)
        self.bar_scanner = BarScanner(BAR_SCANNER_PID)
        self.bar_scanner.add_observer(self)
        self.window = MainWindow(self, model)

        self.getted_bar_code = ''  # атрибут для хранения принятого баркода от потока сканера
        self.getted_RFID_code = ''  # атрибут для хранения принятого RFID от потока сканера

    def get_RFID_signal(self, code):
        self.logger.debug(f'get RFID_code: {code}')
        self.getted_RFID_code = code  # Помещаем код в атрибут, который проверяется в потоке формы

    def get_bar_code(self, bar_code):
        if self.window._show_create_team_error_flag or self.window._show_create_team_error_flag or self.window._show_connection_error_flag:
            return
        self.logger.debug(f'get bar_code: {bar_code}')
        self.getted_bar_code = bar_code # Помещаем код в атрибут, который проверяется в потоке формы

    def open_document_window(self, doc_link):
        doc_controller = DocForm_controller(self, doc_link)

    def click_commands_btn(self):
        login_controller = CreateTeam_controller(self)

    def click_teamslist_btn(self):
        team_list_controller = TeamList_controller(self)

    def click_reboot_btn(self):
        self.logger.info('User pressed the reboot button!')
        reboot()

    def click_exit_btn(self):
        Threaded_class.stop()
        sys.exit()