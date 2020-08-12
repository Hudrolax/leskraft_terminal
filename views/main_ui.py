# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './views/main_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("background-color: rgb(39, 40, 34);\n"
"font: 12pt \"Consolas\";\n"
"color: white\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tbl1 = QtWidgets.QTableWidget(self.centralwidget)
        self.tbl1.setGeometry(QtCore.QRect(90, 70, 971, 301))
        self.tbl1.setShowGrid(True)
        self.tbl1.setGridStyle(QtCore.Qt.SolidLine)
        self.tbl1.setWordWrap(True)
        self.tbl1.setCornerButtonEnabled(True)
        self.tbl1.setRowCount(5)
        self.tbl1.setColumnCount(5)
        self.tbl1.setObjectName("tbl1")
        item = QtWidgets.QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        item.setBackground(brush)
        self.tbl1.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl1.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl1.setItem(2, 1, item)
        self.tbl1.horizontalHeader().setVisible(False)
        self.tbl1.verticalHeader().setVisible(False)
        self.get_btn = QtWidgets.QPushButton(self.centralwidget)
        self.get_btn.setGeometry(QtCore.QRect(480, 400, 111, 31))
        self.get_btn.setObjectName("get_btn")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1229, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tbl1.setSortingEnabled(False)
        __sortingEnabled = self.tbl1.isSortingEnabled()
        self.tbl1.setSortingEnabled(False)
        self.tbl1.setSortingEnabled(__sortingEnabled)
        self.get_btn.setText(_translate("MainWindow", "get"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
