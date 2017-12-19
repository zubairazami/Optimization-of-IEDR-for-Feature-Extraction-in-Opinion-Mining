from PyQt5 import QtWidgets
import sys
from ui.mainwindow import UiMainWindow
from interaction.data import InteractionData

if __name__ == "__main__":
    interaction_data = InteractionData()
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    ui = UiMainWindow(interaction_data=interaction_data)
    sys.exit(app.exec_())

# # For the very first run of this project, please run this segment of code instead of the previous segment
# # Necessary for creating database
# from process.db.structure import clean_up
# if __name__ == "__main__":
# #     clean_up()
