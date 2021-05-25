from utility.print import get_pdf_and_print
from utility.logger_super import LoggerSuper
import logging
from PyQt5 import QtCore
from views.choice_team_window import ChoiceTeamWindow


class DocForm_controller(LoggerSuper):
    logger = logging.getLogger('Document_controller')
    def __init__( self, window):
        self.window = window

    def get_QR_signal(self, bar_code):
        self.logger.info(f'get QR_code: {bar_code}')
        doc = self.window.model.db.get_doc(bar_code)
        if doc is not None:
            if doc.team_number == 0 and self.window.model.team is None:
                self.show_message_with_timer('Сначала нужно отсканировать карту сотрудника!')
                return

            if doc.link == self.window.model.doc_link:
                if self.window.model.doc().status == 'На исполнение':
                    result = self.window.model.get_task()
                    if result:
                        self.show_message_with_timer_and_exit('Задание взято в работу!', color='green')
                    else:
                        self.show_message_with_timer('Ошибка начала выполнения. Попробуйте еще раз.')
                elif self.window.model.doc().status == 'В работе':
                    result = self.window.model.finish_task()
                    if result:
                        self.show_message_with_timer_and_exit('Задание выполнено!', color='green')
                    else:
                        self.show_message_with_timer('Ошибка окончания выполнения. Попробуйте еще раз.')
                elif self.window.model.doc().status == 'Выполнено':
                    self.show_message_with_timer_and_exit('Это задание уже выполнено')
                    return
                else:
                    self.show_message_with_timer_and_exit('Неизвестная ошибка')
            else:
                self.show_message_with_timer('Вы осканировали не тот документ!')
                return
        else:
            self.window._show_status_message(f'Не найден документ с кодом {bar_code}')

    def get_RFID_signal(self, rfid_code):
        self.logger.info(f'get RFID_code: {rfid_code}')
        if self.window.model.team is not None or self.window.model.doc().team_number != 0:
            self.show_message_with_timer(f'Для этого документа уже установлена бригада!')
            return

        _teams = self.window.model.db.get_team_by_emloyee_code(rfid_code)
        if len(_teams) > 0:
            if len(_teams) > 1:
                self.choice_team_window = ChoiceTeamWindow(_teams, self.window)
                if self.choosed_team is not None:
                    self.window.model.team = self.choosed_team
                    self.choosed_team = None
                    self.choice_team_window = None
                    self.window.fill_header()
                else:
                    self.show_message_with_timer('Что-то пошло не так. Обратитесь к разработчику.')
            else:
                self.window.model.team = _teams[0]
                self.window.fill_header()
        else:
            self.window._show_status_message(f'Не найдена бригада с сотрудником с номером карты {rfid_code}')

    def show_message_with_timer(self, message, color='#960E10', font_size='24'):
        self.window._show_status_message(message, color, font_size)
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.window.fill_header)
        self._timer.start(3000)

    def show_message_with_timer_and_exit(self, message, color='#960E10', font_size='24'):
        self.window._show_status_message(message, color, font_size)
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.close_window)
        self._timer.start(3000)

    def click_print_btn(self):
        self.window.disable_print_btn()
        try:
            get_pdf_and_print(self.window.model.doc_link)
            self.show_message_with_timer('Задание отправлено на принтер!', color='green')
        except:
            self.show_message_with_timer('Ошибка связи с сервером, попробуйте еще раз!', color='red')
            self.window.enable_print_btn()

        # # Создадим и запустим поток печати файла
        # self.print_thread = QtCore.QThread()
        # self.print_handler = Print_Handler()
        # self.print_handler.moveToThread(self.print_thread)
        # self.print_thread.started.connect(lambda: self.print_handler.run(self.window.model.doc_link))
        # self.print_thread.start()

    def close_window(self):
        self.window.close()
        # отключим сканеры от формы документа и подключим их обратно к основной форме
        self.window.main_window.controller.connect_scanners_to_main_form()
        self.window.main_window.controller.create_team_window = None

# # класс для печати в отдельном потоке
# class Print_Handler(QtCore.QObject):
#     def run(self, doc_link):
#         get_pdf_and_print(doc_link)