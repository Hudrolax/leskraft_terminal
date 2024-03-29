import sys
from sys import platform
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from env import WRITE_LOG_TO_FILE, LOG_LEVEL
import logging
from datetime import datetime
import os


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

    if platform == "linux" or platform == "linux2" or platform == "darwin":
        _path = os.path.abspath(__file__)
        os.system(f'find {_path}' + ' -type f -name "log_*" -mtime +168 -exec rm -rf {} \;')
        logger.info('Удалим логи старше недели')
    else:
        logger.info('Не могу удалить логи, если мы не в unix')

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

