import sys
from PyQt5.QtWidgets import QApplication
from utility.logger_super import LoggerSuper
from models.main_model import MainModel
from controllers.main_controller import MainController
from env import PRINTER_NAME, AUTH_BASIC, API_KEY, WRITE_LOG_TO_FILE, DEBUG_MODE
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
    LOG_FORMAT = '%(name)s (%(levelname)s) %(asctime)s: %(message)s'
    LOG_LEVEL = logging.INFO
    if DEBUG_MODE:
        LOG_LEVEL = logging.DEBUG
    logger = logging.getLogger('main')

    if WRITE_LOG_TO_FILE:
        logging.basicConfig(filename='leskraft_terminal.txt', filemode='w', format=LOG_FORMAT, level=LOG_LEVEL,
                            datefmt='%d/%m/%y %H:%M:%S')
    else:
        logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt='%d/%m/%y %H:%M:%S')

    if PRINTER_NAME == "":
        print('В env.py не выбрано имя принтера. Для опреления списка доступных принтеров запустите из папки терминала:')
        print('python3 /utility/print.py')
    elif AUTH_BASIC == "":
        print('В env.py не задан ключ авторизации.')
    elif API_KEY == "":
        print('В env.py не задан API_KEY')
    else:
        try:
            main_app = Main()
            sys.exit(main_app.run())
        except Exception as ex:
            logger.critical(ex)
