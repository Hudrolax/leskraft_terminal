from views.main_window import MainWindow
from controllers.doc_form_controller import DocForm_controller
from utility.threaded_class import Threaded_class
import sys

class MainController:
    def __init__( self, model):
        self.model = model
        self.window = MainWindow(self, model)

    def click_get_btn(self):
        self.model.get_docs()

    def click_getdoc_btn(self, doc):
        print(doc)
        doc_controller = DocForm_controller(self, doc)

    def click_exit_btn(self):
        Threaded_class.stop()
        sys.exit()