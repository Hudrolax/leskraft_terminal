from views.main_view import MainView

class MainController():

    def __init__( self, model):
        self.model = model
        self.view = MainView(self)
        self.model.add_observer(self.view)