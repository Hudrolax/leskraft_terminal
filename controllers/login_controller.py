from views.login_window import LoginWindow
from models.login_model import Login_model


class Login_controller:
    def __init__( self, parent, create_team):
        self.main_controller = parent # Main form controller
        self.model = Login_model(self, self.main_controller.model.db)
        self.window = LoginWindow(self, self.model, self.main_controller.window, create_team)
        self.main_controller.rfid_scanner.add_observer(self)

    def get_RFID_signal(self, card_id):
        print(f'get code {card_id}')
        self.model.get_rfid_code(card_id)

    def del_employee(self, employee):
        self.model.del_employee(employee)

    def close(self):
        self.window.close()