# Form implementation generated from reading ui file 'gui_updates.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_UpdateMenu(object):
    def setupUi(self, UpdateMenu):
        UpdateMenu.setObjectName("UpdateMenu")
        UpdateMenu.resize(285, 101)
        self.label = QtWidgets.QLabel(parent=UpdateMenu)
        self.label.setGeometry(QtCore.QRect(10, 10, 261, 71))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")

        self.retranslateUi(UpdateMenu)
        QtCore.QMetaObject.connectSlotsByName(UpdateMenu)

    def retranslateUi(self, UpdateMenu):
        _translate = QtCore.QCoreApplication.translate
        UpdateMenu.setWindowTitle(_translate("UpdateMenu", "About"))
        self.label.setText(_translate("UpdateMenu", "<html><head/><body><p>Current version: V_CUR</p><p>Latest version: V_LAT</p><p>UPDATE_TEXT</p></body></html>"))
