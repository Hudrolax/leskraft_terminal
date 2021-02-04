from PyQt5 import QtCore

class TimerHandler(QtCore.QObject):
    def __init__(self, delay=1000):
        super().__init__()
        self.delay = delay
    timer_signal = QtCore.pyqtSignal()

    def run(self):
        while True:
            self.timer_signal.emit()
            QtCore.QThread.msleep(self.delay)