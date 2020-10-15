from views.doc_form import DocumentWindow

class DocForm_controller:
    def __init__( self, parent, doc):
        self.parent = parent
        self.model = doc
        self.window = DocumentWindow(self, self.model, self.parent.window)

    def click_close_btn(self):
        self.window.close()