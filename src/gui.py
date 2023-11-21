import sys

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
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

class GemTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(GemTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data['gemdata'][index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data['gemdata'])

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data['gemdata'][0])
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data['columns'][section])

            if orientation == Qt.Orientation.Vertical:
                return section+1
                # return str(self._data['rows'][section])