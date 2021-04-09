from utility.com_ports import COM_port
import threading
from time import sleep
from utility.logger_super import LoggerSuper
from utility.threaded_class import Threaded_class
import logging


class WatchDog(LoggerSuper, Threaded_class, COM_port):
    logger = logging.getLogger('WatchDog')

    def __init__(self, PID):
        super().__init__('WatchDog', PID, 9600, 1)

        if self.initialized:
            self._watchdog_thread = threading.Thread(target=self._ping, args=(), daemon=True)
            self._watchdog_thread.start()
        else:
            self.logger.info('Вотчдог не инициализирован. Работаем без него...')

    def _send_to_serial(self, _s_port, s):
        if self.initialized:
            try:
                _s_port.write(bytes(s, 'utf-8'))
            except:
                self.logger.warning(f'Write error to port {_s_port}')

    def _ping(self):
        while self.working():
            self._send_to_serial(self.serial, '~U')  # Отправка команды "я в норме" на вотчдог
            sleep(3)