# Form implementation generated from reading ui file 'gui_main.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_GemArbitrageGUI(object):
    def setupUi(self, GemArbitrageGUI):
        GemArbitrageGUI.setObjectName("GemArbitrageGUI")
        GemArbitrageGUI.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        GemArbitrageGUI.setEnabled(True)
        GemArbitrageGUI.resize(1080, 720)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GemArbitrageGUI.sizePolicy().hasHeightForWidth())
        GemArbitrageGUI.setSizePolicy(sizePolicy)
        GemArbitrageGUI.setMinimumSize(QtCore.QSize(0, 0))
        GemArbitrageGUI.setMaximumSize(QtCore.QSize(1080, 720))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("data/icon.ico"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        GemArbitrageGUI.setWindowIcon(icon)
        GemArbitrageGUI.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
        self.centralwidget = QtWidgets.QWidget(parent=GemArbitrageGUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.tradeTabs = QtWidgets.QTabWidget(parent=self.centralwidget)
        self.tradeTabs.setEnabled(True)
        self.tradeTabs.setGeometry(QtCore.QRect(0, 0, 1081, 671))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tradeTabs.sizePolicy().hasHeightForWidth())
        self.tradeTabs.setSizePolicy(sizePolicy)
        self.tradeTabs.setAutoFillBackground(True)
        self.tradeTabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
        self.tradeTabs.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
        self.tradeTabs.setTabsClosable(False)
        self.tradeTabs.setMovable(False)
        self.tradeTabs.setObjectName("tradeTabs")
        self.gemTableTab = QtWidgets.QWidget()
        self.gemTableTab.setObjectName("gemTableTab")
        self.gemTable = QtWidgets.QTableView(parent=self.gemTableTab)
        self.gemTable.setGeometry(QtCore.QRect(10, 10, 1051, 621))
        self.gemTable.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.gemTable.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.gemTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.gemTable.setDragEnabled(True)
        self.gemTable.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.gemTable.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.gemTable.setShowGrid(True)
        self.gemTable.setObjectName("gemTable")
        self.gemTable.horizontalHeader().setDefaultSectionSize(64)
        self.gemTable.verticalHeader().setDefaultSectionSize(36)
        self.tradeTabs.addTab(self.gemTableTab, "")
        self.corruptTab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.corruptTab.sizePolicy().hasHeightForWidth())
        self.corruptTab.setSizePolicy(sizePolicy)
        self.corruptTab.setObjectName("corruptTab")
        self.corruptTable = QtWidgets.QTableView(parent=self.corruptTab)
        self.corruptTable.setGeometry(QtCore.QRect(10, 10, 1051, 621))
        self.corruptTable.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.corruptTable.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.corruptTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.corruptTable.setDragEnabled(True)
        self.corruptTable.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.corruptTable.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.corruptTable.setShowGrid(True)
        self.corruptTable.setObjectName("corruptTable")
        self.corruptTable.horizontalHeader().setDefaultSectionSize(64)
        self.corruptTable.verticalHeader().setDefaultSectionSize(36)
        self.tradeTabs.addTab(self.corruptTab, "")
        self.wokegemTab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wokegemTab.sizePolicy().hasHeightForWidth())
        self.wokegemTab.setSizePolicy(sizePolicy)
        self.wokegemTab.setObjectName("wokegemTab")
        self.wokegemTable = QtWidgets.QTableView(parent=self.wokegemTab)
        self.wokegemTable.setGeometry(QtCore.QRect(10, 10, 1051, 621))
        self.wokegemTable.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.wokegemTable.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.wokegemTable.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.wokegemTable.setDragEnabled(True)
        self.wokegemTable.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.wokegemTable.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.wokegemTable.setShowGrid(True)
        self.wokegemTable.setObjectName("wokegemTable")
        self.wokegemTable.horizontalHeader().setDefaultSectionSize(64)
        self.wokegemTable.verticalHeader().setDefaultSectionSize(36)
        self.tradeTabs.addTab(self.wokegemTab, "")
        GemArbitrageGUI.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(parent=GemArbitrageGUI)
        self.statusBar.setSizeGripEnabled(True)
        self.statusBar.setObjectName("statusBar")
        GemArbitrageGUI.setStatusBar(self.statusBar)
        self.menubar = QtWidgets.QMenuBar(parent=GemArbitrageGUI)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1080, 22))
        self.menubar.setDefaultUp(False)
        self.menubar.setNativeMenuBar(True)
        self.menubar.setObjectName("menubar")
        self.menuSettings = QtWidgets.QMenu(parent=self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuHelp = QtWidgets.QMenu(parent=self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")
        GemArbitrageGUI.setMenuBar(self.menubar)
        self.actionAbout = QtGui.QAction(parent=GemArbitrageGUI)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSettingsMenu = QtGui.QAction(parent=GemArbitrageGUI)
        self.actionSettingsMenu.setEnabled(True)
        self.actionSettingsMenu.setObjectName("actionSettingsMenu")
        self.actionExit = QtGui.QAction(parent=GemArbitrageGUI)
        self.actionExit.setObjectName("actionExit")
        self.actionRun_Trades = QtGui.QAction(parent=GemArbitrageGUI)
        self.actionRun_Trades.setObjectName("actionRun_Trades")
        self.actionUpdateCheck = QtGui.QAction(parent=GemArbitrageGUI)
        self.actionUpdateCheck.setObjectName("actionUpdateCheck")
        self.menuSettings.addAction(self.actionSettingsMenu)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionUpdateCheck)
        self.menuFile.addAction(self.actionRun_Trades)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(GemArbitrageGUI)
        self.tradeTabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(GemArbitrageGUI)

    def retranslateUi(self, GemArbitrageGUI):
        _translate = QtCore.QCoreApplication.translate
        GemArbitrageGUI.setWindowTitle(_translate("GemArbitrageGUI", "POE Gem Arbitrage"))
        self.tradeTabs.setTabText(self.tradeTabs.indexOf(self.gemTableTab), _translate("GemArbitrageGUI", "Gems"))
        self.tradeTabs.setTabText(self.tradeTabs.indexOf(self.corruptTab), _translate("GemArbitrageGUI", "Corrupts"))
        self.tradeTabs.setTabText(self.tradeTabs.indexOf(self.wokegemTab), _translate("GemArbitrageGUI", "Vivid Watcher"))
        self.menuSettings.setTitle(_translate("GemArbitrageGUI", "Settings"))
        self.menuHelp.setTitle(_translate("GemArbitrageGUI", "Help"))
        self.menuFile.setTitle(_translate("GemArbitrageGUI", "File"))
        self.actionAbout.setText(_translate("GemArbitrageGUI", "About"))
        self.actionSettingsMenu.setText(_translate("GemArbitrageGUI", "See settings.ini for more details."))
        self.actionExit.setText(_translate("GemArbitrageGUI", "Exit"))
        self.actionRun_Trades.setText(_translate("GemArbitrageGUI", "Reload Trades"))
        self.actionUpdateCheck.setText(_translate("GemArbitrageGUI", "Check for Updates"))
