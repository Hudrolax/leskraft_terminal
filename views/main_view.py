from PyQt5.QtWidgets import QMainWindow, QDialog
from proj_util.observer import Observer
from proj_util.meta import Meta
from views.main_ui import Ui_MainWindow


class MainView(QMainWindow, Observer, metaclass = Meta):
    def __init__(self, controller, parent = None):
        super(QMainWindow, self).__init__(parent)
        self.controller = controller

        # подключаем визуальное представление
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )

        # связываем событие завершения редактирования с методом контроллера
        # self.ui.lineEdit.editingFinished.connect(self.mController.setC)
        # self.ui.lineEdit_2.editingFinished.connect(self.mController.setD)

        self.showFullScreen()

    def show_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("HELLO!")
        dlg.exec_()

    def model_is_changed( self ):
        pass