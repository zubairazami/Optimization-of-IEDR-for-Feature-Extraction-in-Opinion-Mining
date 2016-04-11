from PyQt4 import QtGui
import sys
from ui.mainwindow import UiMainWindow
from interaction.data import InteractionData


def main():
    interaction_data = InteractionData()
    app = QtGui.QApplication(sys.argv)
    ui = UiMainWindow(interaction_data=interaction_data)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
