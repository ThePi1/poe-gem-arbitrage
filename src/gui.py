import sys
import re
import random
import csv
import os
import glob
from datetime import datetime

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QRunnable
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QListView, QListWidget, QListWidgetItem

from gui_about import Ui_AboutMenu
from gui_main import Ui_GemArbitrageGUI
from gui_updates import Ui_UpdateMenu
from gui_watcher_tracker import Ui_VividWatcherTracker

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

  def onVividTracker(self):
    dlg = Gui_VividTrackerDlg(parent=self)

  def onExit(self):
    sys.exit(0)

  def onUpdateWindow(self, ver_current, ver_latest, url_text, update_text):
    dlg = Gui_UpdatesDlg()
    dlg.updateVersion(ver_current, ver_latest, url_text, update_text)
    dlg.exec()

class Gui_VividTrackerDlg(QMainWindow):
  motd = ["\"Money often costs too much.\"\nRalph Waldo Emerson",
          "\"An investment in knowledge pays the best interest.\"\nBenjamin Franklin",
          "\"Wealth is the slave of a wise man. The master of a fool.\"\nSeneca",
          "\"A nickel ain't worth a dime anymore.\"\nYogi Berra",
          "\"You must gain control over your money or the lack of it will forever control you.\"\nDave Ramsey",
          "\"Don't tell me what you value, show me your budget, and I'll tell you what you value.\"\nJoe Biden",
          "\"No wealth can ever make a bad man at peace with himself.\"\nPlato",
          "\"If you have trouble imagining a 20% loss in the stock market, you shouldn't be in stocks.\"\nJohn Bogle",
          "\"A journey of a thousand miles must begin with a single step.\"\nLao Tzu",
          "\"Never spend your money before you have it.\"\nThomas Jefferson",
          "\"I made my money the old-fashioned way. I was very nice to a wealthy relative right before he died.\"\nMalcolm Forbes",
          "\"Wealth is but dung, useful only when spread about.\"\nChinese Proverb",
          "\"Create an account to read the full story.\"\nMedium.com",
          "\"Want a break from the ads? If you tap now to watch a short video, you'll receive 30 minutes of ad free music.\"\nSpotify",
          "\"Early to bed and early to rise, makes a man healthy, wealthy, and wise.\"\nBenjamin Franklin",
          "\"Capital as such is not evil; it is its wrong use that is evil. Capital in some form or other will always be needed.\"\nGandhi",
          "\"Money isn't everything... but it ranks right up there with oxygen.\"\nRita Davenport"]
    
  gem_names = ["Minion Damage",
              "Lightning Penetration",
              "Controlled Destruction",
              "Added Chaos Damage",
              "Melee Splash",
              "Elemental Focus",
              "Deadly Ailments",
              "Unbound Ailments",
              "Brutality",
              "Swift Affliction",
              "Added Fire Damage",
              "Melee Physical Damage",
              "Burning Damage",
              "Void Manipulation",
              "Elemental Damage with Attacks",
              "Added Cold Damage",
              "Added Lightning Damage",
              "Vicious Projectiles",
              "Fire Penetration",
              "Cold Penetration",
              "Increased Area of Effect",
              "Cast While Channelling",
              "Cast On Critical Strike",
              "Blasphemy",
              "Generosity",
              "Hextouch",
              "Greater Multiple Projectiles",
              "Fork",
              "Spell Echo",
              "Multistrike",
              "Ancestral Call",
              "Chain",
              "Arrow Nova",
              "Unleash",
              "Spell Cascade"]
    
  def __init__(self, parent=None):
    super().__init__(parent)
    self.ui = Ui_VividWatcherTracker()
    self.ui.setupUi(self)
    # Custom code in onLaunch
    self.on_launch()
    self.show()

  def debug(self):
    print(f"Debug info:\n")
    print(f"Top entry: {self.get_first_row_history()}")
    print(f"Current Gem: {self.get_current_gem()}")
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

  def get_first_row_history(self):
    list_size = self.ui.list_history.count()
    if list_size == 0:
        return "Start"
    else:
        return self.ui.list_history.item(0).text()
  
  def remove_top_entry(self):
    list_size = self.ui.list_history.count()
    if list_size == 0: return
    self.ui.list_history.takeItem(0)

  def clear(self):
    for i in range(self.ui.list_history.count()):
      self.remove_top_entry()
    self.statusBar().showMessage(f"History cleared.", 5000)

  def export(self):
    cwd = os.getcwd()
    timestamp_string = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"poearb_watcher_{timestamp_string}.csv"
    filepath = f"{cwd}\{filename}"

    rows = self.get_history_list()
    with open(filepath, 'w', newline='') as f:
      writer = csv.writer(f)
      for row in rows:
        writer.writerow(row)

    self.statusBar().showMessage(f"History saved successfully as {filepath}", 10000)
      
  def get_history_list(self):
    out = []
    for i in range(self.ui.list_history.count()):
      pre,post = self.ui.list_history.item(i).text().split(" > ")
      out.append((pre,post))
    out.reverse()
    return out
  
  def get_current_gem(self):
    list_size = self.ui.list_history.count()
    if list_size == 0:
      return "Start"
    elif self.flag_forcestart:
      self.flag_forcestart = False
      return "Start"
    else:
      pre,post = self.ui.list_history.item(0).text().split(" > ")
      return post

  def on_launch(self):
    title_text = self.ui.lb_title_text.text()
    chosen_motd = random.choice(Gui_VividTrackerDlg.motd)
    title_text = re.sub('TITLE_TEXT', chosen_motd, title_text)
    self.ui.lb_title_text.setText(QtCore.QCoreApplication.translate("VividWatcherTracker", title_text))
    self.connect_gem_buttons()
    self.flag_forcestart = False
  
  def connect_gem_buttons(self):
    # Regex my beloved
    self.ui.pb_addchaos.released.connect(lambda: self.gem_click("Added Chaos Damage"))
    self.ui.pb_addcold.released.connect(lambda: self.gem_click("Added Cold Damage"))
    self.ui.pb_addfire.released.connect(lambda: self.gem_click("Added Fire Damage"))
    self.ui.pb_addlight.released.connect(lambda: self.gem_click("Added Lightning Damage"))
    self.ui.pb_ancall.released.connect(lambda: self.gem_click("Ancestral Call"))
    self.ui.pb_anova.released.connect(lambda: self.gem_click("Arrow Nova"))
    self.ui.pb_blasph.released.connect(lambda: self.gem_click("Blasphemy"))
    self.ui.pb_brutality.released.connect(lambda: self.gem_click("Brutality"))
    self.ui.pb_burn.released.connect(lambda: self.gem_click("Burning Damage"))
    self.ui.pb_coc.released.connect(lambda: self.gem_click("Cast On Critical Strike"))
    self.ui.pb_cwc.released.connect(lambda: self.gem_click("Cast While Channelling"))
    self.ui.pb_chain.released.connect(lambda: self.gem_click("Chain"))
    self.ui.pb_coldpen.released.connect(lambda: self.gem_click("Cold Penetration"))
    self.ui.pb_contdest.released.connect(lambda: self.gem_click("Controlled Destruction"))
    self.ui.pb_deadlyail.released.connect(lambda: self.gem_click("Deadly Ailments"))
    self.ui.pb_elw.released.connect(lambda: self.gem_click("Elemental Damage with Attacks"))
    self.ui.pb_elefoc.released.connect(lambda: self.gem_click("Elemental Focus"))
    self.ui.pb_firepen.released.connect(lambda: self.gem_click("Fire Penetration"))
    self.ui.pb_fork.released.connect(lambda: self.gem_click("Fork"))
    self.ui.pb_genr.released.connect(lambda: self.gem_click("Generosity"))
    self.ui.pb_gmp.released.connect(lambda: self.gem_click("Greater Multiple Projectiles"))
    self.ui.pb_hext.released.connect(lambda: self.gem_click("Hextouch"))
    self.ui.pb_aoe.released.connect(lambda: self.gem_click("Increased Area of Effect"))
    self.ui.pb_lightpen.released.connect(lambda: self.gem_click("Lightning Penetration"))
    self.ui.pb_mpd.released.connect(lambda: self.gem_click("Melee Physical Damage"))
    self.ui.pb_meleesplash.released.connect(lambda: self.gem_click("Melee Splash"))
    self.ui.pb_mindmg.released.connect(lambda: self.gem_click("Minion Damage"))
    self.ui.pb_ms.released.connect(lambda: self.gem_click("Multistrike"))
    self.ui.pb_casc.released.connect(lambda: self.gem_click("Spell Cascade"))
    self.ui.pb_echo.released.connect(lambda: self.gem_click("Spell Echo"))
    self.ui.pb_swiftaff.released.connect(lambda: self.gem_click("Swift Affliction"))
    self.ui.pb_ubail.released.connect(lambda: self.gem_click("Unbound Ailments"))
    self.ui.pb_uhleash.released.connect(lambda: self.gem_click("Unleash"))
    self.ui.pb_vicproj.released.connect(lambda: self.gem_click("Vicious Projectiles"))
    self.ui.pb_voidman.released.connect(lambda: self.gem_click("Void Manipulation"))

    self.ui.actionDebug.triggered.connect(self.debug)
    self.ui.c_pb_remlast.released.connect(self.remove_top_entry)
    self.ui.c_pb_clear.released.connect(self.clear)
    self.ui.c_pb_export.released.connect(self.export)
    self.ui.c_pb_forcestart.released.connect(self.force_start)

    self.ui.actionMerge_Output_CSVs.triggered.connect(self.merge_csv)

  def force_start(self):
    self.statusBar().showMessage(f"Forcing current gem to 'Start' for next operation.", 5000)
    self.flag_forcestart = True

  def gem_click(self, gem_name_short):
    current_gem = self.get_current_gem()
    new_row = f"{current_gem} > {gem_name_short}"
    q_new_row = QListWidgetItem(QtCore.QCoreApplication.translate("VividWatcherTracker", new_row))
    self.ui.list_history.insertItem(0, q_new_row)
    self.statusBar().showMessage(f"Added {gem_name_short} to history.", 5000)

  def merge_csv(self):
    cwd = os.getcwd()
    timestamp_string = datetime.now().strftime("%Y%m%d_%H%M%S")
    merge_candidates = glob.glob(f"{cwd}\poearb_watcher*csv")
    num_csv = len(merge_candidates)
    merge_filename = f"poearb_merged_{num_csv}_{timestamp_string}.csv"
    weight_filename = f"poearb_weights_{num_csv}_{timestamp_string}.csv"
    merge_filepath = f"{cwd}\{merge_filename}"
    weight_filepath = f"{cwd}\{weight_filename}"
    final_csv_data = []
    for c in merge_candidates:
      with open(c, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
          final_csv_data.append(line)
    with open(merge_filepath, 'w', newline='') as f:
      writer = csv.writer(f)
      for row in final_csv_data:
        writer.writerow(row)
    # Calc final weights
    all_result_gems = [row[1] for row in final_csv_data if row[1] != "Start"]
    final_weight_data = {}
    for gem in Gui_VividTrackerDlg.gem_names:
      full_gem_name = f"Awakened {gem} Support"
      final_weight_data[full_gem_name] = 0

    for gem in all_result_gems:
      final_weight_data[full_gem_name]
      full_gem_name = f"Awakened {gem} Support"
      final_weight_data[full_gem_name] += 1

    with open(weight_filepath, 'w', newline='') as f:
      writer = csv.writer(f)
      for row in final_weight_data.items():
        writer.writerow(row)
    
    self.statusBar().showMessage(f"Matching CSVs merged into {merge_filename}, weights in {weight_filename}", 10000)



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