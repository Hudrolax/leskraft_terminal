import sys
from PyQt5.QtWidgets import QApplication
from utility.logger_super import LoggerSuper
from models.main_model import MainModel
from controllers.main_controller import MainController
import logging


class Main(LoggerSuper):
    logger = logging.getLogger('Main')
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_model = MainModel()
        self.main_controller = MainController(self.main_model)

    def run(self):
        return self.app.exec()


if __name__ == '__main__':
    WRITE_LOG_TO_FILE = False
    LOG_FORMAT = '%(name)s (%(levelname)s) %(asctime)s: %(message)s'
    LOG_LEVEL = logging.INFO
    logger = logging.getLogger('main')

    if WRITE_LOG_TO_FILE:
        logging.basicConfig(filename='leskraft_terminal.txt', filemode='w', format=LOG_FORMAT, level=LOG_LEVEL,
                            datefmt='%d/%m/%y %H:%M:%S')
    else:
        logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt='%d/%m/%y %H:%M:%S')

    main_app = Main()
    sys.exit(main_app.run())
