from views.team_list_window import TeamListWindow
from models.team_list_model import TeamList_model


class TeamList_controller:
    def __init__( self, parent):
        self.main_controller = parent # Main form controller
        self.model = TeamList_model(self, self.main_controller.model.db)
        self.window = TeamListWindow(self, self.model, self.main_controller.window)

    def close(self):
        self.window.close_window()