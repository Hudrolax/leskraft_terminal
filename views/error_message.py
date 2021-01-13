from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QGraphicsDropShadowEffect
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont, QColor

class Error_window(QDialog):
    HEIGHT = 400
    WIDTH = 600
    def __init__(self, main_window, error, exit=False):
        super().__init__()
        self.main_window = main_window
        self.setObjectName('error_dialog')
        self.setWindowTitle('ERROR')
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.center_on_screen()
        self.add_button()
        self.add_label(error)
        self.setStyleSheet(self.main_window.styleSheet())
        self.exec_()
        if exit:
            print('exiting...')
            self.main_window.close()

    def move_to_center(self, obj1, obj2, width_offes = 0, height_offset = 0):
        """
        :param obj1: что смещать
        :param obj2: куда смещать
        :param width_offes: горизонтальное доп. смещение
        :param height_offset: вертикальное доп. смещение
        :return: None
        """
        obj1.move(round((obj2.size().width() / 2) - (obj1.frameSize().width() / 2)) + width_offes,
                  round((obj2.size().height() / 2) - (obj1.frameSize().height() / 2)) + height_offset)

    def add_label(self, text):
        self.label = QLabel(text, self)
        self.label.setGeometry(0, 0, self.WIDTH-20, self.HEIGHT - self.pushButton.frameSize().height() - 20)
        self.move_to_center(self.label, self, 0, -self.pushButton.frameSize().height())
        self.label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
        self.label.setFont(QFont("Consolas", 14, QFont.Bold))
        self.label.setWordWrap(True)

    def add_button(self):
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setObjectName('error_dialog_okButton')
        self.pushButton.setGeometry(QtCore.QRect(0, 0, 100, 30))
        self.move_to_center(self.pushButton, self, 0, round(self.size().height()/2 - self.pushButton.frameSize().height()/2 - 20))
        self.pushButton.setText("OK")
        self.pushButton.clicked.connect(self.close_dlg)
        self.pushButton.installEventFilter(self)
        shadow_effect = QGraphicsDropShadowEffect(self.pushButton)
        shadow_effect.setColor(QColor(0, 0, 0, 127))
        shadow_effect.setYOffset(0)
        shadow_effect.setXOffset(6)
        shadow_effect.setBlurRadius(12)
        # shadow_effect.setEnabled(True)
        self.pushButton.setGraphicsEffect(shadow_effect)

    def push_btn_hover(self):
        self.pushButton.graphicsEffect().setEnabled(False)

    def push_btn_unhover(self):
        self.pushButton.graphicsEffect().setEnabled(True)

    def eventFilter(self, obj, event):
        """
           Функция перехватывает события объекта. Должна быть инициализирована через self.pushButton.installEventFilter(self)
        """
        if obj == self.pushButton and event.type() == QtCore.QEvent.HoverEnter:
            self.push_btn_hover()
        elif obj == self.pushButton and event.type() == QtCore.QEvent.HoverLeave:
            self.push_btn_unhover()
        return super(Error_window, self).eventFilter(obj, event)

    def center_on_screen(self):
        resolution = QApplication.desktop().availableGeometry()
        self.move(round((resolution.width() / 2) - (self.frameSize().width() / 2)),
                  round((resolution.height() / 2) - (self.frameSize().height() / 2)))

    def close_dlg(self):
        self.close()
