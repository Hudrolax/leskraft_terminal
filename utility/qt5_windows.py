from PyQt5.QtWidgets import QApplication

def center_on_screen(window):
    resolution = QApplication.desktop().availableGeometry()
    window.move(round(resolution.width() / 2 - window.geometry().width() / 2),
              round(resolution.height() / 2 - window.geometry().height() / 2))