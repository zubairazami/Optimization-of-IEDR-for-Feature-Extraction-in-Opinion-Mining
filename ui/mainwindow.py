from PyQt5 import QtCore, QtWidgets
from ui.widget_collection import CFEWidget, DRCWidget, AFEWidget, CSWidget


class UiMainWindow(object):
    def __init__(self, interaction_data):

        self.interaction_data = interaction_data
        self.main_window = QtWidgets.QMainWindow()
        self.base_widget = QtWidgets.QWidget(self.main_window)
        self.main_tab_widget = QtWidgets.QTabWidget(self.base_widget)

        self.cs_tab = CSWidget(interaction_data=interaction_data)
        self.cfe_tab = CFEWidget(interaction_data=interaction_data)
        self.drc_tab = DRCWidget(interaction_data=interaction_data)
        self.afe_tab = AFEWidget(interaction_data=interaction_data)

        self.setup_ui()
        self.main_window.show()

    def setup_ui(self):
        self.main_window.resize(940, 548)
        self.main_window.setWindowTitle("Modified IEDR & Feature based Sentiment Analysis")
        self.main_tab_widget.setGeometry(QtCore.QRect(0, 0, 931, 541))
        self.main_tab_widget.addTab(self.cs_tab, "Corpus Selection")
        self.main_tab_widget.addTab(self.cfe_tab, "Candidate Feature Extraction")
        self.main_tab_widget.addTab(self.drc_tab, "Domain Relevance Calculation")
        self.main_tab_widget.addTab(self.afe_tab, "Actual Feature Extraction")
        self.main_window.setCentralWidget(self.base_widget)


