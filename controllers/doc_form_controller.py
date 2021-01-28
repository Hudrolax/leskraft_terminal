from views.doc_form import DocumentWindow
from models.doc_form_model import DocumentForm_model
from views.error_message import Error_window
from utility.print import get_pdf_and_print


class DocForm_controller:
    def __init__( self, parent, doc):
        self.parent = parent # Main form controller
        self.model = DocumentForm_model(self, self.parent.model.db, doc)
        self.window = DocumentWindow(self, self.model, self.parent.window)

    def click_close_btn(self):
        self.window.close()

    def click_print_btn(self):
        result = get_pdf_and_print(self.model.doc.link)
        if result != "":
            Error_window(self.window, f'Ошибка: {result}')


    def start_work_with_document(self):
        result = self.model.start_work_with_document()
        if result != 'ok':
            Error_window(self.window , f'Ошибка: {result}')
            return False
        else:
            self.parent.model.update()
            return True

    def stop_work_with_document(self):
        return self.model.stop_work_with_document()

    # def click_checkbox(self, str_num, checked, reason):
    #     print(f'str {str_num} is {checked}')
    #     return self.model.cancel_string(str_num, checked, reason)