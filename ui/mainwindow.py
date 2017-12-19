from PyQt5 import QtCore, QtWidgets
from ui.widget_collection import CFEWidget, DRCWidget, AFEWidget, CSWidget
from ui.widget_collection_extra import SetupWidget, TrainingWidget, AnalysisWidget


class UiMainWindow(object):
    def __init__(self, interaction_data):

        self.interaction_data = interaction_data
        self.main_window = QtWidgets.QMainWindow()
        self.base_widget = QtWidgets.QWidget(self.main_window)
        self.main_tab_widget = QtWidgets.QTabWidget(self.base_widget)

        self.fe_tab = QtWidgets.QWidget()
        self.fbs_tab = QtWidgets.QWidget()
        self.fe_tab_widget = QtWidgets.QTabWidget(self.fe_tab)
        self.cs_tab = CSWidget(interaction_data=interaction_data)
        self.cfe_tab = CFEWidget(interaction_data=interaction_data)
        self.drc_tab = DRCWidget(interaction_data=interaction_data)
        self.afe_tab = AFEWidget(interaction_data=interaction_data)

        self.fbs_tab_widget = QtWidgets.QTabWidget(self.fbs_tab)
        self.setup_tab = SetupWidget(interaction_data=interaction_data)
        self.training_tab = TrainingWidget(interaction_data=interaction_data)
        self.result_tab = AnalysisWidget(interaction_data=interaction_data)

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

        self.fbs_tab_widget.setGeometry(QtCore.QRect(0, 0, 941, 511))
        self.fbs_tab_widget.addTab(self.setup_tab, "")
        self.fbs_tab_widget.addTab(self.training_tab, "")
        self.fbs_tab_widget.addTab(self.result_tab, "")
        self.main_tab_widget.addTab(self.fbs_tab, "")

        self.main_window.setCentralWidget(self.base_widget)

        self.fe_tab_widget.setTabText(self.fe_tab_widget.indexOf(self.cs_tab),"Corpus Selection")
        self.fe_tab_widget.setTabText(self.fe_tab_widget.indexOf(self.cfe_tab),"Candidate Feature Extraction")
        self.fe_tab_widget.setTabText(self.fe_tab_widget.indexOf(self.drc_tab),"Domain Relevance Calculation")
        self.fe_tab_widget.setTabText(self.fe_tab_widget.indexOf(self.afe_tab), "Actual Feature Extraction")
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.fe_tab),"Feature Extraction via modified IEDR")
        self.fbs_tab_widget.setTabText(self.fbs_tab_widget.indexOf(self.setup_tab), "Setup Files and Directory")
        self.fbs_tab_widget.setTabText(self.fbs_tab_widget.indexOf(self.training_tab), "Training")
        self.fbs_tab_widget.setTabText(self.fbs_tab_widget.indexOf(self.result_tab), "Sentiment Analysis")
        self.main_tab_widget.setTabText(self.main_tab_widget.indexOf(self.fbs_tab), "Feature based Sentiment")


