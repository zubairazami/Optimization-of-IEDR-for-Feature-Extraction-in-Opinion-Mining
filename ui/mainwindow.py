from PyQt4 import QtCore, QtGui
from ui.widget_collection import CFEWidget, DRCWidget, AFEWidget, CSWidget


class UiMainWindow(object):
    def __init__(self, interaction_data):

        self.interaction_data = interaction_data
        self.main_window = QtGui.QMainWindow()
        self.base_widget = QtGui.QWidget(self.main_window)
        self.main_tab_widget = QtGui.QTabWidget(self.base_widget)

        self.fe_tab = QtGui.QWidget()
        # self.fbs_tab = QtGui.QWidget()
        self.fe_tab_widget = QtGui.QTabWidget(self.fe_tab)
        self.cs_tab = CSWidget(interaction_data=interaction_data)
        self.cfe_tab = CFEWidget(interaction_data=interaction_data)
        self.drc_tab = DRCWidget(interaction_data=interaction_data)
        self.afe_tab = AFEWidget(interaction_data=interaction_data)

        # self.fbs_tab_widget = QtGui.QTabWidget(self.fbs_tab)
        # self.training_tab = QtGui.QWidget()
        # self.testing_tab = QtGui.QWidget()
        # self.result_tab = QtGui.QWidget()

        self.setup_ui()
        self.main_window.show()

    def setup_ui(self):
        self.main_window.resize(940, 548)
        self.main_window.setWindowTitle("Modified IEDR & Feature based Sentiment Analysis")

        self.main_tab_widget.setGeometry(QtCore.QRect(0, 0, 931, 541))

        self.fe_tab_widget.setGeometry(QtCore.QRect(0, 0, 941, 511))
        self.fe_tab_widget.addTab(self.cs_tab, "")
        self.fe_tab_widget.addTab(self.cfe_tab, "")
        self.fe_tab_widget.addTab(self.drc_tab, "")
        self.fe_tab_widget.addTab(self.afe_tab, "")
        self.main_tab_widget.addTab(self.fe_tab, "")

        # self.fbs_tab_widget.setGeometry(QtCore.QRect(0, 0, 941, 511))
        # self.fbs_tab_widget.addTab(self.training_tab, "")
        # self.fbs_tab_widget.addTab(self.testing_tab, "")
        # self.fbs_tab_widget.addTab(self.result_tab, "")
        # self.main_tab_widget.addTab(self.fbs_tab, "")

        self.main_window.setCentralWidget(self.base_widget)

        self.fe_tab_widget.setTabText(self.fe_tab_widget.indexOf(self.cs_tab),"Corpus Selection")
        self.fe_tab_widget.setTabText(self.fe_tab_widget.indexOf(self.cfe_tab),"Candidate Feature Extraction")
        self.fe_tab_widget.setTabText(self.fe_tab_widget.indexOf(self.drc_tab),"Domain Relevance Calculation")
        self.fe_tab_widget.setTabText(self.fe_tab_widget.indexOf(self.afe_tab), "Actual Feature Extraction")
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.fe_tab),"Feature Extraction via modified IEDR")
        # self.fbs_tab_widget.setTabText(self.fbs_tab_widget.indexOf(self.training_tab), "Training")
        # self.fbs_tab_widget.setTabText(self.fbs_tab_widget.indexOf(self.testing_tab), "Testing")
        # self.fbs_tab_widget.setTabText(self.fbs_tab_widget.indexOf(self.result_tab), "Result")
        # self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.fbs_tab), "Feature based Sentiment")


