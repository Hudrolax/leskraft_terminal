from views.main_window import MainWindow
from controllers.doc_form_controller import DocForm_controller
from controllers.create_team_controller import CreateTeam_controller
from utility.threaded_class import Threaded_class
from controllers.RFID_scanner import RFIDScanner
from env import RFID_SCANNER_PID
import sys

class MainController:
    def __init__( self, model):
        self.model = model
        self.window = MainWindow(self, model)
        self.rfid_scanner = RFIDScanner(RFID_SCANNER_PID)

    def click_getdoc_btn(self, doc):
        doc_controller = DocForm_controller(self, doc)

    def click_commands_btn(self):
        login_controller = CreateTeam_controller(self)

    def click_exit_btn(self):
        Threaded_class.stop()
        sys.exit()