import sys
from PyQt5.QtWidgets import QApplication

from models.main_model import MainModel
from controllers.main_controller import MainController


def main():
    app = QApplication(sys.argv)

    main_model = MainModel()
    main_controller = MainController(main_model)


    app.exec()

if __name__ == '__main__':
    sys.exit(main())
