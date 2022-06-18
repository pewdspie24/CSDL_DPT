# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Dialog_Main(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(250, 143)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 30, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(90, 90, 75, 23))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Error"))
        self.label.setText(_translate("Dialog", "Not Found!"))
        self.pushButton.setText(_translate("Dialog", "OK!"))
        self.pushButton.clicked.connect(self.close_app)
        self.dialog = Dialog
    
    def close_app(self):
        self.dialog.close()

class Ui_Dialog():
    def __init__(self):
        self.ui = Dialog_Main()
        self.dialog = QtWidgets.QDialog()
        self.ui.setupUi(self.dialog)
    def show(self):
        self.dialog.show()
        