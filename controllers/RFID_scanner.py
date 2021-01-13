from utility.com_ports import COM_port
import threading
import logging
from utility.logger_super import LoggerSuper
from time import sleep


class RFIDScanner(COM_port, LoggerSuper):
    """
    Класс RFIDScanner представляет собой реализацию модели сканера RFID.
    Класс оповещает наблюдателей о событии сканирования
    """
    logger = logging.getLogger('RFIDScanner')

    def __init__(self, PID, ID = '00'):
        super().__init__(name='RFIDScanner', PID=PID, speed=9600, timeout=500)
        self.observers = []
        self.id = ID
        self._thread = threading.Thread(target=self._get_bar_code_threaded, args=(), daemon=True)
        self._thread.start()

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def send_signal_to_observers(self, card_id):
        for observer in self.observers:
            observer.get_RFID_signal(card_id)

    def _get_bar_code_threaded(self):
        buffer = b''
        while True:
            if self.initialized:
                try:
                    buffer += self.serial.read()
                except:
                    self.initialized = False
                    continue

                str_buffer = buffer.decode()
                if str_buffer.find('#S'+self.id) > -1:
                    buffer = b''
                    continue
                if str_buffer.startswith('#F'+self.id) and len(str_buffer) == 14:
                    buffer = b''
                    str_buffer = str_buffer.replace('#F'+self.id+'2D00', '')
                    try:
                        card_id =  int(str_buffer, 16)
                    except Exception as e:
                        self.logger.error(f'decode to int error "{str_buffer}"')
                        continue
                    self.send_signal_to_observers(card_id)
            else:
                sleep(3)
                self.inicialize_com_port()

if __name__ == '__main__':
    rfid_scanner = RFIDScanner('0403:6001')
    while True:
        sleep(1)