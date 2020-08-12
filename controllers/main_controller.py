from views.main_view import MainView

class MainController():

    def __init__( self, model):
        self.model = model
        self.view = MainView(self, model)
        self.model.add_observer(self.view)

    def click_get_btn(self):
        self.model.get_docs()