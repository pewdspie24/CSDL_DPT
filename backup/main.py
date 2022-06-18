# -*- coding: utf-8 -*-

import time
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from dialog import Ui_Dialog as Form
import app_run

my_module = app_run.MainProcess()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(250, 30, 331, 51))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(32)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setGeometry(QtCore.QRect(190, 100, 451, 121))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(360, 260, 81, 31))
        self.pushButton.setObjectName("pushButton")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(520, 260, 141, 31))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.Cosine_Table = QtWidgets.QTableWidget(self.centralwidget)
        self.Cosine_Table.setGeometry(QtCore.QRect(410, 360, 361, 181))
        self.Cosine_Table.setObjectName("Cosine_Table")
        self.Cosine_Table.setColumnCount(3)
        self.Cosine_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.Cosine_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Cosine_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Cosine_Table.setHorizontalHeaderItem(2, item)
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(480, 320, 241, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.Matching_Table = QtWidgets.QTableWidget(self.centralwidget)
        self.Matching_Table.setGeometry(QtCore.QRect(30, 360, 361, 181))
        self.Matching_Table.setObjectName("Matching_Table")
        self.Matching_Table.setColumnCount(3)
        self.Matching_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.Matching_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Matching_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Matching_Table.setHorizontalHeaderItem(2, item)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(110, 320, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(True)
        font.setUnderline(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(110, 120, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "QN Searcher"))
        self.label.setText(_translate("MainWindow", "Searching Machine"))
        self.pushButton.setText(_translate("MainWindow", "Search"))
        item = self.Cosine_Table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Text Filename"))
        item = self.Cosine_Table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Titles"))
        item = self.Cosine_Table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Score"))
        self.label_4.setText(_translate(
            "MainWindow", "Using Cosine Similarity Score"))
        item = self.Matching_Table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Text Filename"))
        item = self.Matching_Table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Titles"))
        item = self.Matching_Table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Score"))
        self.label_3.setText(_translate("MainWindow", "Using Matching Score"))
        self.label_2.setText(_translate("MainWindow", "Input:"))
        self.menuMenu.setTitle(_translate("MainWindow", "Menu"))
        self.Matching_Table.doubleClicked.connect(self.open_matching)
        self.Cosine_Table.doubleClicked.connect(self.open_cosine)
        self.Matching_Table.setEditTriggers(
            QtWidgets.QTableWidget.NoEditTriggers)
        self.Cosine_Table.setEditTriggers(
            QtWidgets.QTableWidget.NoEditTriggers)
        self.a = Form()
        self.backend()

    def backend(self):
        self.pushButton.clicked.connect(self.search)

    def search(self):
        self.progressBar.setValue(0)
        sentence = self.plainTextEdit.toPlainText()
        matching_seq = my_module.matching_score(k=10, query=sentence)
        self.update_progress_bar(0)
        cos_seg = my_module.cosine_similarity(k=10, query=sentence)
        self.update_progress_bar(33)
        self.Matching_Table.setRowCount(0)
        self.Cosine_Table.setRowCount(0)
        self.Matching_Table.setRowCount(len(matching_seq))
        self.Cosine_Table.setRowCount(len(matching_seq))
        for i in range(len(matching_seq)):
            self.Matching_Table.setItem(
                i, 0, QtWidgets.QTableWidgetItem(matching_seq[i][0]))
            self.Matching_Table.setItem(
                i, 1, QtWidgets.QTableWidgetItem(matching_seq[i][1]))
            self.Matching_Table.setItem(
                i, 2, QtWidgets.QTableWidgetItem(str(matching_seq[i][2])))
            self.Cosine_Table.setItem(
                i, 0, QtWidgets.QTableWidgetItem(cos_seg[i][0]))
            self.Cosine_Table.setItem(
                i, 1, QtWidgets.QTableWidgetItem(cos_seg[i][1]))
            self.Cosine_Table.setItem(
                i, 2, QtWidgets.QTableWidgetItem(str(cos_seg[i][2])))
        if len(matching_seq) == 0 or len(cos_seg) == 0:
            self.a.show()
        self.update_progress_bar(67)

    def update_progress_bar(self, value):
        count = 0
        while count < 33:
            count += 1
            time.sleep(0.001)
            self.progressBar.setValue(count+value)

    def open_matching(self):
        for idx in self.Matching_Table.selectionModel().selectedIndexes():
            row_number = idx.row()
        filename = self.Matching_Table.item(row_number, 0).text()
        os.startfile(os.path.join('txt', filename))

    def open_cosine(self):
        for idx in self.Cosine_Table.selectionModel().selectedIndexes():
            row_number = idx.row()
        filename = self.Cosine_Table.item(row_number, 0).text()
        os.startfile(os.path.join('txt', filename))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
