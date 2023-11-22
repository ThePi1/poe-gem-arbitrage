import sys
import re

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QRunnable
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton

from gui_about import Ui_AboutMenu
from gui_main import Ui_GemArbitrageGUI
from gui_updates import Ui_UpdateMenu

# Not currently using Worker class but might in the future to unblock GUI
class Worker(QRunnable):
  def __init__(self, fn, *args, **kwargs):
      super(Worker, self).__init__()
      self.fn = fn
      self.args = args
      self.kwargs = kwargs
      
  def run(self):
    self.fn(*self.args, **self.kwargs)

class Gui_MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_GemArbitrageGUI()
        self.ui.setupUi(self)

        self.ui.actionExit.triggered.connect(self.onExit)

    def onAbout(self, ver_current, url_text):
        dlg = Gui_AboutDlg(self)
        dlg.updateAbout(ver_current, url_text)
        dlg.exec()

    def onExit(self):
        sys.exit(0)

    def onUpdateWindow(self, ver_current, ver_latest, url_text, update_text):
        dlg = Gui_UpdatesDlg()
        dlg.updateVersion(ver_current, ver_latest, url_text, update_text)
        dlg.exec()


class Gui_AboutDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AboutMenu()
        self.ui.setupUi(self)

    def updateAbout(self, ver_current, url_text):
      text =  self.ui.label.text()
      text = re.sub('V_CUR', ver_current, text)
      text = re.sub('SRC_URL', url_text ,text)
      self.ui.label.setText(QtCore.QCoreApplication.translate("AboutMenu", text))

class Gui_UpdatesDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_UpdateMenu()
        self.ui.setupUi(self)

    def updateVersion(self, ver_current, ver_latest, url_text, update_text):
      text =  self.ui.label.text()
      text = re.sub('V_CUR', ver_current, text)
      text = re.sub('V_LAT', ver_latest, text)
      text = re.sub('UPDATE_TEXT', update_text ,text)
      text = re.sub('SRC_URL', url_text, text)
      self.ui.label.setText(QtCore.QCoreApplication.translate("UpdateMenu", text))

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
          
      if role == Qt.ItemDataRole.BackgroundRole:
        if (index.row() & 1):
          return QtGui.QColor("#ffffff")
        else:
          return QtGui.QColor("#e3e3e3")

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data['gemdata'])

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        if len(self._data['gemdata']) == 0:
           return 0
        return len(self._data['gemdata'][0])
    
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data['columns'][section])

            if orientation == Qt.Orientation.Vertical:
                return section+1
                # return str(self._data['rows'][section])