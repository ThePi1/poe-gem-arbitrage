import sys

from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton

from gui_about import Ui_AboutMenu
from gui_main import Ui_GemArbitrageGUI

class Gui_MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_GemArbitrageGUI()
        self.ui.setupUi(self)

        self.ui.actionAbout.triggered.connect(self.onAbout)
        self.ui.actionExit.triggered.connect(self.onExit)

    def onAbout(self):
        dlg = Gui_AboutDlg(self)
        dlg.exec()

    def onExit(self):
        sys.exit(0)


class Gui_AboutDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AboutMenu()
        self.ui.setupUi(self)