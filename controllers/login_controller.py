from views.login_window import LoginWindow
from models.login_model import Login_model

class Login_controller:
    def __init__( self, parent, create_team):
        self.parent = parent # Main form controller
        self.model = Login_model(self, self.parent.model.db)
        self.window = LoginWindow(self, self.model, self.parent.window, create_team)

    def btn_register_team_clocked(card_number):
        pass


    def close(self):
        self.window.close()