# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'team_list.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_team_list(object):
    def setupUi(self, team_list):
        team_list.setObjectName("team_list")
        team_list.resize(981, 646)
        self.verticalLayout = QtWidgets.QVBoxLayout(team_list)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.exitButton = QtWidgets.QPushButton(team_list)
        self.exitButton.setMinimumSize(QtCore.QSize(100, 40))
        self.exitButton.setObjectName("exitButton")
        self.horizontalLayout.addWidget(self.exitButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(team_list)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.team_list_tbl = QtWidgets.QTableWidget(team_list)
        self.team_list_tbl.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.team_list_tbl.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.team_list_tbl.setRowCount(1)
        self.team_list_tbl.setColumnCount(4)
        self.team_list_tbl.setObjectName("team_list_tbl")
        self.team_list_tbl.horizontalHeader().setVisible(False)
        self.team_list_tbl.horizontalHeader().setHighlightSections(True)
        self.team_list_tbl.verticalHeader().setVisible(False)
        self.team_list_tbl.verticalHeader().setHighlightSections(False)
        self.verticalLayout.addWidget(self.team_list_tbl)

        self.retranslateUi(team_list)
        QtCore.QMetaObject.connectSlotsByName(team_list)

    def retranslateUi(self, team_list):
        _translate = QtCore.QCoreApplication.translate
        team_list.setWindowTitle(_translate("team_list", "team list"))
        self.exitButton.setText(_translate("team_list", "Выход"))
        self.label.setText(_translate("team_list", "Список зарегистированных бригад в текущей смене"))