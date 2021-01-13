from views.create_team import CreateTeamWindow
from models.create_team_model import CreateTeam_model


class CreateTeam_controller:
    def __init__( self, parent):
        self.main_controller = parent # Main form controller
        self.model = CreateTeam_model(self, self.main_controller.model.db)
        self.window = CreateTeamWindow(self, self.model, self.main_controller.window)
        self.main_controller.rfid_scanner.add_observer(self)

    def get_RFID_signal(self, card_id):
        print(f'get code {card_id}')
        self.model.rfid_code_got(card_id)

    def del_employee(self, employee):
        self.model.del_employee(employee)

    def close(self):
        self.main_controller.rfid_scanner.remove_observer(self)
        self.window.close()