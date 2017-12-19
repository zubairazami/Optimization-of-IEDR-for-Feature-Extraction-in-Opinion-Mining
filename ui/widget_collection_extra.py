from PyQt5 import QtCore, QtGui, QtWidgets
from os.path import expanduser
from interaction.thread_collection import TrainingThread, AnalysisThread
from math import floor
from ui.pie_chart import PieChart


class SetupWidget(QtWidgets.QWidget):
    def __init__(self, interaction_data):
        super(SetupWidget, self).__init__()
        self.interaction_data = interaction_data

        self.setup_label = QtWidgets.QLabel(self)
        self.setup_label.setGeometry(QtCore.QRect(70, 60, 770, 30))
        self.setup_label.setText("Set up Files & Directory")
        self.setup_label.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.setup_label.setFont(font)

        self.pos_file_textarea = QtWidgets.QTextBrowser(self)
        self.pickled_directory_textarea = QtWidgets.QTextBrowser(self)
        self.neg_file_textarea = QtWidgets.QTextBrowser(self)

        self.pos_file_label = QtWidgets.QLabel(self)
        self.neg_file_label = QtWidgets.QLabel(self)

        self.pfd_label = QtWidgets.QLabel(self)
        self.pscf_pushbutton = QtWidgets.QPushButton(self)
        self.nscf_pushbutton = QtWidgets.QPushButton(self)
        self.pfd_pushbutton = QtWidgets.QPushButton(self)
        self.set_pushbutton = QtWidgets.QPushButton(self)

        self.setup_ui()

    def setup_ui(self):
        self.pos_file_textarea.setGeometry(QtCore.QRect(240, 150, 501, 31))
        self.pickled_directory_textarea.setGeometry(QtCore.QRect(240, 270, 501, 31))
        self.neg_file_textarea.setGeometry(QtCore.QRect(240, 210, 501, 31))

        self.pos_file_label.setGeometry(QtCore.QRect(10, 150, 211, 31))
        self.pos_file_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        self.neg_file_label.setGeometry(QtCore.QRect(10, 210, 211, 31))
        self.neg_file_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        self.pfd_label.setGeometry(QtCore.QRect(10, 270, 211, 31))
        self.pfd_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        self.pscf_pushbutton.setGeometry(QtCore.QRect(780, 150, 41, 31))
        self.nscf_pushbutton.setGeometry(QtCore.QRect(780, 210, 41, 31))
        self.pfd_pushbutton.setGeometry(QtCore.QRect(780, 270, 41, 31))
        self.set_pushbutton.setGeometry(QtCore.QRect(390, 350, 131, 31))

        self.pscf_pushbutton.clicked.connect(self.button_action)
        self.nscf_pushbutton.clicked.connect(self.button_action)
        self.pfd_pushbutton.clicked.connect(self.button_action)
        self.set_pushbutton.clicked.connect(self.button_action)

        self.pos_file_label.setText("Positive Sentiment Containing File")
        self.neg_file_label.setText("Negative Sentiment Containing File")
        self.pfd_label.setText("Pickled Files Directory")
        self.pscf_pushbutton.setText("...")
        self.nscf_pushbutton.setText("...")
        self.pfd_pushbutton.setText("...")
        self.set_pushbutton.setText("Set")

    def button_action(self):
        sender = self.sender()

        if sender == self.pscf_pushbutton:
            file = str(QtWidgets.QFileDialog.getOpenFileName(self, "Select Positive Sentiment containing file",
                                                         expanduser('~') + "/dataset"))
            self.pos_file_textarea.setText(file)

        if sender == self.nscf_pushbutton:
            file = str(QtWidgets.QFileDialog.getOpenFileName(self, "Select Negative Sentiment containing file",
                                                         expanduser('~') + "/dataset"))
            self.neg_file_textarea.setText(file)

        if sender == self.pfd_pushbutton:
            file = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Pickled files directory",
                                                              expanduser('~') + "/dataset"))
            self.pickled_directory_textarea.setText(file)

        if self.interaction_data.new_thread_allowable:
            if sender == self.set_pushbutton:
                pos = self.pos_file_textarea.toPlainText()
                neg = self.neg_file_textarea.toPlainText()
                pickled = self.pickled_directory_textarea.toPlainText()
                self.set_pushbutton.setDisabled(True)
                self.interaction_data.set_sentiment_dictionary(pos=pos, neg=neg, pickled=pickled)
                QtWidgets.QMessageBox.about(self, "successful", "Required files and directories are set")
                self.set_pushbutton.setDisabled(False)
        else:
            message = "A background process is already running.\n"
            message += "Wait for it to be completed to set sentiment directories again."
            QtWidgets.QMessageBox.about(self, "Background Process Running", message)


class TrainingWidget(QtWidgets.QWidget):
    def __init__(self, interaction_data):
        super(TrainingWidget, self).__init__()
        self.interaction_data = interaction_data

        self.training_label = QtWidgets.QLabel(self)
        self.training_console = QtWidgets.QTextBrowser(self)
        self.training_progressbar = QtWidgets.QProgressBar(self)
        self.train_pushbutton = QtWidgets.QPushButton(self)
        self.training_thread = None

        self.setup_ui()

    def setup_ui(self):
        self.training_label.setGeometry(QtCore.QRect(70, 20, 770, 30))
        self.training_label.setText("Training Console")
        self.training_label.setAlignment(QtCore.Qt.AlignCenter)
        self.training_console.setGeometry(QtCore.QRect(70, 60, 770, 320))
        self.training_progressbar.setGeometry(QtCore.QRect(70, 390, 770, 25))
        self.train_pushbutton.setGeometry(QtCore.QRect(420, 430, 131, 30))

        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.training_label.setFont(font)
        self.train_pushbutton.setText("Train")
        self.train_pushbutton.clicked.connect(self.button_click_action)

    def button_click_action(self):
        if self.interaction_data.is_set_sentiment_dictionary:
            if self.interaction_data.new_thread_allowable:
                self.training_thread = TrainingThread(interaction_data=self.interaction_data)
                QtCore.QObject.connect(self.training_thread, QtCore.SIGNAL("training_progress"),
                                       self.update_progress_1)
                QtCore.QObject.connect(self.training_thread, QtCore.SIGNAL("training_progress_classifier"),
                                       self.update_progress_2)
                QtCore.QObject.connect(self.training_thread, QtCore.SIGNAL("finished()"), self.on_completion)
                self.interaction_data.deny_new_thread()
                self.training_progressbar.setValue(0)
                self.training_console.clear()
                self.training_thread.start()

            else:
                message = "A background process is already running.\n"
                message += "Wait for it to be completed to set sentiment directories again."
                QtWidgets.QMessageBox.about(self, "Background Process Running", message)
        else:
            message = "Directories for Sentiment files & pickled folder are not set properly."
            message += "\nGo to 'Setup Files and Directory' tab to select properly."
            QtWidgets.QMessageBox.about(self, "Sentiment Directory Error", message)

    def update_progress_1(self, completed, total):
        value = int(floor((completed * 80.00) / total))
        msg = "Completed processing " + str(completed) + " reviews out of " + str(total) + " reviews";
        self.training_console.setText(msg)
        self.training_progressbar.setValue(value)

    def update_progress_2(self, completed, total, msg):
        value = 80 + int(floor((completed * 20.00) / total))
        self.training_console.append(msg)
        self.training_progressbar.setValue(value)

    def on_completion(self):
        message = "Completed Training & accuracy calculation of the classifiers"
        QtWidgets.QMessageBox.about(self, "Task Completed.", message)
        self.interaction_data.allow_new_thread()


class AnalysisWidget(QtWidgets.QWidget):
    def __init__(self, interaction_data):
        super(AnalysisWidget, self).__init__()
        self.interaction_data = interaction_data
        self.feature_dict_with_sentiment = dict()
        self.feature_counter = 0

        self.table_widget = QtWidgets.QTableWidget(self)
        self.graphics_widget = QtWidgets.QWidget(self)
        self.graphicsView = QtWidgets.QGraphicsView(self)
        self.tbaf_textarea = QtWidgets.QTextBrowser(self)
        self.acf_textarea = QtWidgets.QTextBrowser(self)
        self.tbaf_pushbutton = QtWidgets.QPushButton(self)
        self.acf_pushbutton = QtWidgets.QPushButton(self)
        self.analysis_button = QtWidgets.QPushButton(self)
        self.analysis_thread = None

        self.feature_label = QtWidgets.QLabel(self)
        self.positive_label = QtWidgets.QLabel(self)
        self.negative_label = QtWidgets.QLabel(self)

        self.pie_chart = PieChart()

        self.setup_ui()

    def setup_ui(self):
        self.table_widget.setGeometry(QtCore.QRect(20, 40, 170, 400))
        self.table_widget.setColumnCount(1)
        self.table_widget.setHorizontalHeaderLabels(['Features'])
        self.table_widget.setColumnWidth(0, 170)
        self.table_widget.cellClicked.connect(self.show_piechart)

        self.feature_label.setAutoFillBackground(True)
        self.feature_label.setAlignment(QtCore.Qt.AlignCenter)
        self.feature_label.setText("Feature Name")
        self.feature_label.setGeometry(QtCore.QRect(200, 40, 370, 30))

        self.graphicsView.setGeometry(QtCore.QRect(200, 75, 370, 290))

        palette = QtGui.QPalette()

        self.positive_label.setText("Positive")
        self.positive_label.setAlignment(QtCore.Qt.AlignCenter)
        self.positive_label.setAutoFillBackground(True)
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor(0, 255, 0, 128))
        self.positive_label.setPalette(palette)
        self.positive_label.setGeometry(QtCore.QRect(200, 375, 370, 30))

        self.negative_label.setText("Negative")
        self.negative_label.setAlignment(QtCore.Qt.AlignCenter)
        self.negative_label.setAutoFillBackground(True)
        palette.setColor(QtGui.QPalette.Background, QtGui.QColor(255, 0, 0, 128))
        self.negative_label.setPalette(palette)
        self.negative_label.setGeometry(QtCore.QRect(200, 410, 370, 30))

        self.tbaf_textarea.setGeometry(QtCore.QRect(590, 180, 281, 31))

        self.acf_textarea.setGeometry(QtCore.QRect(590, 240, 281, 31))

        self.tbaf_pushbutton.setGeometry(QtCore.QRect(880, 180, 31, 31))
        self.tbaf_pushbutton.setText("...")
        self.tbaf_pushbutton.clicked.connect(self.button_click)

        self.acf_pushbutton.setGeometry(QtCore.QRect(880, 240, 31, 31))
        self.acf_pushbutton.setText("...")
        self.acf_pushbutton.clicked.connect(self.button_click)

        self.analysis_button.setGeometry(QtCore.QRect(690, 300, 131, 31))
        self.analysis_button.clicked.connect(self.button_click)
        self.analysis_button.setText("Analyze")

    def button_click(self):
        sender = self.sender()
        if self.interaction_data.is_set_sentiment_dictionary:
            if self.interaction_data.new_thread_allowable:

                if sender == self.analysis_button:
                    test_file = self.tbaf_textarea.toPlainText()
                    feature_file = self.acf_textarea.toPlainText()
                    if len(test_file) == 0 or len(feature_file) == 0:
                        QtWidgets.QMessageBox.about(self, "Choose files Correctly",
                                                "Either or both of the files are not selected properly.")
                    else:
                        self.analysis_thread = AnalysisThread(interaction_data=self.interaction_data,
                                                              test_file=test_file,
                                                              feature_file=feature_file)
                        QtCore.QObject.connect(self.analysis_thread, QtCore.SIGNAL("analysis_signal"), self.update)
                        QtCore.QObject.connect(self.analysis_thread, QtCore.SIGNAL("finished()"), self.on_completion)
                        self.interaction_data.deny_new_thread()

                        self.feature_dict_with_sentiment = {}
                        self.feature_counter = 0
                        self.analysis_thread.start()

                if sender == self.tbaf_pushbutton:
                    file = str(QtWidgets.QFileDialog.getOpenFileName(self, "Select the file to be analyzed",
                                                                 expanduser('~') + "/dataset"))
                    self.tbaf_textarea.setText(file)

                if sender == self.acf_pushbutton:
                    file = str(QtWidgets.QFileDialog.getOpenFileName(self, "Select the file containing extracted features",
                                                                 expanduser('~') + "/dataset"))
                    self.acf_textarea.setText(file)

            else:
                message = "A background process is already running.\n"
                message += "Wait for it to be completed to set sentiment directories again."
                QtWidgets.QMessageBox.about(self, "Background Process Running", message)
        else:
            message = "Directories for Sentiment files & pickled folder are not set properly."
            message += "\nGo to 'Setup Files and Directory' tab to select properly."
            QtWidgets.QMessageBox.about(self, "Sentiment Directory Error", message)

    def update(self, feature, pos, neg):
        self.feature_dict_with_sentiment[feature] = [pos, neg]
        self.feature_counter += 1
        self.table_widget.setRowCount(self.feature_counter + 1)
        self.table_widget.setItem(self.feature_counter - 1, 0, QtWidgets.QTableWidgetItem(feature))

    def on_completion(self):
        self.table_widget.setRowCount(self.feature_counter)
        self.interaction_data.allow_new_thread()

    def show_piechart(self):
        row = self.table_widget.currentItem().row()
        column = 0
        feature = self.table_widget.item(row, column).text()
        feature_sentiment_list = self.feature_dict_with_sentiment[feature]

        self.pie_chart.set_chart(percentage_data=self.feature_dict_with_sentiment[feature])
        self.graphicsView.setScene(self.pie_chart.get_chart())


        self.feature_label.setText(feature)
        self.positive_label.setText("Positive  ->  " + str(feature_sentiment_list[0]) + " %")
        self.negative_label.setText("Negative  ->  " + str(feature_sentiment_list[1]) + " %")
