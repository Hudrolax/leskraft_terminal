from views.error_message_window import Error_window
from utility.print import get_pdf_and_print
from utility.logger_super import LoggerSuper
import logging
from PyQt5 import QtCore


class DocForm_controller(LoggerSuper):
    logger = logging.getLogger('Document_controller')
    def __init__( self, window):
        self.window = window

    def get_QR_signal(self, bar_code):
        self.logger.info(f'get QR_code: {bar_code}')
        if self.window.model.team is None:
            return

    def get_RFID_signal(self, rfid_code):
        self.logger.info(f'get RFID_code: {rfid_code}')
        if self.window.model.team is not None or self.window.model.doc().team_number != 0:
            self.window._show_status_message(f'Для этого документа уже установлена бригада!')
            self._timer = QtCore.QTimer()
            self._timer.setSingleShot(True)
            self._timer.timeout.connect(self.window.fill_header)
            self._timer.start(3000)
            return

        _teams = self.window.model.db.get_team_by_emloyee_code(rfid_code)
        if len(_teams) > 0:
            if len(_teams) > 1:
                pass
                # self._open_choice_team_window(_teams)
                # if self.choosed_team is not None:
                #     self.model.team = self.choosed_team
                #     self.choosed_team = None
                #     self.choice_team_window = None
            else:
                self.window.model.team = _teams[0]
                self.window.fill_header()
        else:
            self.window._show_status_message(f'Не найдена бригада с сотрудником с номером карты {rfid_code}')

    def click_print_btn(self):
        result = get_pdf_and_print(self.window.model.doc_link)
        if result != "":
            Error_window(self.window, f'{result}')


    def start_work_with_document(self):
        result = self.window.model.start_work_with_document()
        if result != 'ok':
            Error_window(self.window , f'{result}')
            return False
        else:
            return True

    def stop_work_with_document(self):
        result = self.window.model.stop_work_with_document()
        if result != 'ok':
            Error_window(self.window, f'{result}')
            return False
        else:
            return True

    def close_window(self):
        self.window.close()
        # отключим сканеры от формы документа и подключим их обратно к основной форме
        self.window.main_window.controller.connect_scanners_to_main_form()
        self.window.main_window.controller.create_team_window = None
        del self.window