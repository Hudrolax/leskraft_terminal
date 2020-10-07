from utility.threaded_class import Threaded_class
from views.main_window import MainWindow

class MainController(Threaded_class):
    def __init__( self, model):
        self.model = model
        self.window = MainWindow(self, model)

    def click_get_btn(self):
        self.model.get_docs()

    def click_getdoc_btn(self, doc):
        print(doc)