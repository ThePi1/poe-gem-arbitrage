import sys

from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton

from gui_about import Ui_AboutMenu
from gui_main import Ui_GemArbitrageGUI


# class Window(QMainWindow):
#     """Main window."""
#     def __init__(self, parent=None):
#         """Initializer."""
#         super().__init__(parent)
#         # Use a QPushButton for the central widget
#         self.centralWidget = QPushButton("Employee...")
#         # Connect the .clicked() signal with the .onEmployeeBtnClicked() slot
#         self.centralWidget.clicked.connect(self.onEmployeeBtnClicked)
#         self.setCentralWidget(self.centralWidget)

#     # Create a slot for launching the employee dialog
#     def onEmployeeBtnClicked(self):
#         """Launch the employee dialog."""
#         dlg = AboutDlg(self)
#         dlg.exec()

class Gui_MainWindow(QMainWindow):
    """Main window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create an instance of the GUI
        self.ui = Ui_GemArbitrageGUI()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)

        self.ui.actionAbout.triggered.connect(self.onAbout)
        self.ui.actionExit.triggered.connect(self.onExit)
        self.ui.runTradesButton.clicked.connect(self.runGemTrades)

    def onAbout(self):
        dlg = Gui_AboutDlg(self)
        dlg.exec()

    def onExit(self):
        sys.exit(0)

    def runGemTrades(self):
        self.ui.plainTextEdit.setPlainText("Hello!")

class Gui_AboutDlg(QDialog):
    """About dialog."""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create an instance of the GUI
        self.ui = Ui_AboutMenu()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)


if __name__ == "__main__":
    # Create the application
    app = QApplication(sys.argv)
    # Create and show the application's main window
    win = Gui_MainWindow()
    win.show()
    # Run the application's main loop
    sys.exit(app.exec())