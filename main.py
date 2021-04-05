import sys
from PyQt5.QtWidgets import QApplication
from utility.logger_super import LoggerSuper
from models.main_model import MainModel
from controllers.main_controller import MainController
from env import PRINTER_NAME, AUTH_BASIC, API_KEY, WRITE_LOG_TO_FILE, LOG_LEVEL
import logging
from datetime import datetime


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
    date_format = '%d.%m.%y %H:%M:%S'

    LOG_LEVEL_WORK = logging.INFO
    if str(LOG_LEVEL).upper() == 'INFO':
        LOG_LEVEL_WORK = logging.INFO
    elif str(LOG_LEVEL).upper() == 'DEBUG':
        LOG_LEVEL_WORK = logging.DEBUG
    elif str(LOG_LEVEL).upper() == 'ERROR':
        LOG_LEVEL_WORK = logging.ERROR
    elif str(LOG_LEVEL).upper() == 'CRITICAL':
        LOG_LEVEL_WORK = logging.CRITICAL
    logger = logging.getLogger('main')

    if WRITE_LOG_TO_FILE:
        file_log = logging.FileHandler(f'log_{datetime.now().strftime("%m%d%Y%H%M%S")}.txt', mode='a')
        console_out = logging.StreamHandler()
        logging.basicConfig(handlers=(file_log, console_out), format=LOG_FORMAT, level=LOG_LEVEL_WORK,
                            datefmt=date_format)
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
