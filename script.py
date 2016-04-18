from PyQt4 import QtGui
import sys
from ui.mainwindow import UiMainWindow
from interaction.data import InteractionData

if __name__ == "__main__":
    interaction_data = InteractionData()
    app = QtGui.QApplication(sys.argv)
    app.setStyle("fusion")
    ui = UiMainWindow(interaction_data=interaction_data)
    sys.exit(app.exec_())
