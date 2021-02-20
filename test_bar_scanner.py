import logging
from time import sleep
from controllers.barcode_scanner import BarScanner

if __name__ == '__main__':
    WRITE_LOG_TO_FILE = False
    LOG_FORMAT = '%(name)s (%(levelname)s) %(asctime)s: %(message)s'
    LOG_LEVEL = logging.DEBUG
    logger = logging.getLogger('main')

    if WRITE_LOG_TO_FILE:
        logging.basicConfig(filename='leskraft_terminal.txt', filemode='w', format=LOG_FORMAT, level=LOG_LEVEL,
                            datefmt='%d/%m/%y %H:%M:%S')
    else:
        logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL, datefmt='%d/%m/%y %H:%M:%S')

    bar_scanner = BarScanner("2DD6:23AA")
    while True:
        sleep(1)