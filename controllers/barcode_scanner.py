from utility.com_ports import COM_port
import threading
import logging
from datetime import datetime
from utility.logger_super import LoggerSuper
from time import sleep


class BarScanner(COM_port, LoggerSuper):
    """
    Класс BarScanner представляет собой реализацию модели сканера ШК.
    Класс оповещает наблюдателей о событии сканирования
    Модель наблюдателя должна реализовывать метод get_bar_code, получающий в качестве параметра код
    """
    logger = logging.getLogger('BarScanner')

    def __init__(self, PID):
        super().__init__(name='BarScanner', PID=PID, speed=9600, timeout=500)
        self.observers = []
        self._thread = threading.Thread(target=self._get_bar_code_threaded, args=(), daemon=True)
        self._thread.start()

    def add_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def remove_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)

    def _send_signal_to_observers(self, bar_code):
        for observer in self.observers:
            observer.get_bar_code(bar_code)

    def _get_bar_code_threaded(self):
        _last_barcode = None
        _time_last_wait_for_scan = datetime.now()
        _attempts = 0
        while True:
            _answer = ""
            if self.initialized:
                if _last_barcode != '':
                    self.logger.debug('Wait for scan barcode...')
                try:
                    _answer = self.serial.readline().decode().replace('\r\n', '')
                    if _answer != '':
                        self.logger.debug(f'{datetime.strftime(datetime.now(), "%d.%m.%y %H:%M:%S")}: {repr(_answer)}')
                        _attempts = 0
                except:
                    self.initialized = False
                    self.inicialize_com_port()

                if _answer != "":
                    if _answer.find('t=') == -1:
                        self._send_signal_to_observers(_answer)
                    else:
                        self.logger.warning(f'Got wrong code format: {_answer}')
            else:
                sleep(0.2)

            if (datetime.now() - _time_last_wait_for_scan).total_seconds() < 1:
                _attempts += 1
            else:
                _attempts = 0
            _time_last_wait_for_scan = datetime.now()
            if _attempts > 50:
                self.logger.error("scanner: need reboot")
                # reboot()

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