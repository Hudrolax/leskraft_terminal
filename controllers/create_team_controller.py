from utility.logger_super import LoggerSuper
import logging

class CreateTeam_controller(LoggerSuper):
    logger = logging.getLogger('CreateTeam_controller')
    def __init__( self, window):
        self.window = window # create team window

    def get_RFID_signal(self, code):
        self.logger.info(f'got RFID code {code}')
        result, registered, answer = self.window.model.rfid_code_got(code)
        self.window.update_status_bar(registered, answer)
        if result:
            self.window.set_register_team_screen(registered, answer)
        else:
            self.update_window_state()

    def del_employee(self, employee):
        self.window.model.del_employee(employee)
        self.update_window_state()

    def update_window_state(self):
        if self.window.model.window_state == 1:
            self.window.set_create_team_screen()
        elif self.window.model.window_state == 2:
            self.window.set_register_teammates_screen()
        self.window.fill_table_header()
        self.window.fill_table()

    def close(self):
        self.window.close()
        # отключим сканеры от формы и подключим их обратно к основной форме
        self.window.main_window.controller.connect_scanners_to_main_form()
        self.window.main_window.controller.create_team_window = None
        del self.window