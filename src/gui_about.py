# Form implementation generated from reading ui file 'gui_about.ui'
#
# Created by: PyQt6 UI code generator 6.6.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_AboutMenu(object):
    def setupUi(self, AboutMenu):
        AboutMenu.setObjectName("AboutMenu")
        AboutMenu.resize(400, 135)
        AboutMenu.setMinimumSize(QtCore.QSize(0, 0))
        AboutMenu.setMaximumSize(QtCore.QSize(400, 135))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("data/icon.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        AboutMenu.setWindowIcon(icon)
        self.label = QtWidgets.QLabel(parent=AboutMenu)
        self.label.setGeometry(QtCore.QRect(10, 10, 381, 131))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(0, 1))
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName("label")

        self.retranslateUi(AboutMenu)
        QtCore.QMetaObject.connectSlotsByName(AboutMenu)

    def retranslateUi(self, AboutMenu):
        _translate = QtCore.QCoreApplication.translate
        AboutMenu.setWindowTitle(_translate("AboutMenu", "About"))
        self.label.setText(_translate("AboutMenu", "<html><head/><body><p>Made with ♥ by ThePi</p><p>V_CUR</p><p><a href=\"SRC_URL\"><span style=\" text-decoration: underline; color:#0000ff;\">SRC_URL</span></a></p><p>Please open an issue on GitHub for issues / suggestions!</p></body></html>"))
