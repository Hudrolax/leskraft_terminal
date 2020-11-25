from utility.logger_super import LoggerSuper
import logging


class Login_model(LoggerSuper):
    logger = logging.getLogger('login_model')
    windows_states = {'set_leader': 0, 'set_teammates': 1}
    maximum_teammates = 3

    def __init__(self, controller, db):
        self.controller = controller
        self.db = db
        self.window_state = self.windows_states.get('set_leader')
        self.team_leader = None
        self.teammates = []

    def update_window_state(self):
        if self.window_state == self.windows_states.get('set_leader'):
            self.controller.window.set_create_team_screen()
        else:
            self.controller.window.set_register_teammates_screen()

    def del_employee(self, employee):
        self.teammates.remove(employee)
        self.update_window_state()

    def send_team_to_1c(self):
        pass

    def get_rfid_code(self, card_id):
        employee = self.db.get_employee(card_id)
        # Не нашли человека, покажем ошибку
        if employee == None:
            self.controller.window.team_leader_not_found_message(card_id)
            return

        # Кладовщик отметился второй за, значит формируем бригаду в 1С
        if len(self.teammates) > 0 and self.team_leader is not None:
            self.send_team_to_1c()
            return

        # слишком много участников? не порядок
        if len(self.teammates) >= self.maximum_teammates:
            self.controller.window.maximum_teammates_reached_message()
            return

        if self.window_state == self.windows_states.get('set_leader'):
            self.team_leader = employee
            self.window_state = self.windows_states.get('set_teammates')
        else:
            self.teammates.append(employee)
        self.update_window_state()