from views.doc_window import DocumentWindow
from models.doc_window_model import DocumentForm_model
from views.error_message_window import Error_window
from utility.print import get_pdf_and_print
import logging


class DocForm_controller:
    logger = logging.getLogger('Document_controller')
    def __init__( self, parent, doc_link):
        self.main_controller = parent  # Main form controller
        self.model = DocumentForm_model(self, self.main_controller.model.db, doc_link)
        self.window = DocumentWindow(self, self.model, self.main_controller.window)

        self.getted_bar_code = ''  # атрибут для хранения принятого баркода от потока сканера
        self.getted_RFID_code = ''  # атрибут для хранения принятого RFID от потока сканера

        self.main_controller.bar_scanner.remove_observer(self.main_controller)
        self.main_controller.bar_scanner.add_observer(self)
        self.main_controller.rfid_scanner.add_observer(self)
        self.main_controller.rfid_scanner.remove_observer(self.main_controller)

    def get_bar_code(self, bar_code):
        self.logger.debug(f'dget bar_code: {bar_code}')
        self.getted_bar_code = bar_code  # Помещаем код в атрибут, который проверяется в потоке формы

    def get_RFID_signal(self, rfid_code):
        self.logger.debug(f'get RFID_code: {rfid_code}')
        self.getted_RFID_code = rfid_code  # Помещаем код в атрибут, который проверяется в потоке формы

    def click_print_btn(self):
        result = get_pdf_and_print(self.model.doc_link)
        if result != "":
            Error_window(self.window, f'{result}')


    def start_work_with_document(self):
        result = self.model.start_work_with_document()
        if result != 'ok':
            Error_window(self.window , f'{result}')
            return False
        else:
            return True

    def stop_work_with_document(self):
        result = self.model.stop_work_with_document()
        if result != 'ok':
            Error_window(self.window, f'{result}')
            return False
        else:
            return True

    def close_window(self):
        self.main_controller.bar_scanner.add_observer(self.main_controller)
        self.main_controller.bar_scanner.remove_observer(self)
        self.main_controller.rfid_scanner.remove_observer(self)
        self.main_controller.rfid_scanner.add_observer(self.main_controller)
        self.window.close()

    # def click_checkbox(self, str_num, checked, reason):
    #     print(f'str {str_num} is {checked}')
    #     return self.model.cancel_string(str_num, checked, reason)