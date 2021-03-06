from PyQt5.QtWidgets import QFileDialog, QFrame, QPushButton, QProgressBar, QRadioButton, QWidget
from PyQt5.QtWidgets import QLabel, QTextBrowser, QTextEdit
from PyQt5.QtWidgets import QCheckBox, QComboBox, QMessageBox, QDoubleSpinBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal as QSignal, QRect
from PyQt5.QtCore import Qt
from process.manage import recreate_database, FeatureExtractor
from interaction.thread_collection import CandidateFeatureExtractionThread, DomainRelevanceCalculationThread, \
    ActualFeatureExtractionThread


class ModifiedComboBox(QComboBox):
    popupAboutToBeShown = QSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ModifiedComboBox, self).showPopup()


class CSWidget(QWidget):
    def __init__(self, interaction_data):
        super(CSWidget, self).__init__()
        self.interaction_data = interaction_data

        self.ddc_label = QLabel(self)
        self.ddc_text_area = QTextBrowser(self)
        self.dic_text_area = QTextBrowser(self)
        self.ddc_pushbutton = QPushButton(self)
        self.sc_pushbutton = QPushButton(self)
        self.dic_pushbutton = QPushButton(self)
        self.dic_label = QLabel(self)
        self.setup_ui()

    def setup_ui(self):
        self.ddc_label.setGeometry(QRect(30, 140, 231, 31))
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.ddc_label.setFont(font)
        self.ddc_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.ddc_text_area.setGeometry(QRect(290, 140, 481, 31))
        self.dic_text_area.setGeometry(QRect(290, 200, 481, 31))

        self.ddc_pushbutton.setGeometry(QRect(790, 140, 111, 31))
        self.ddc_pushbutton.clicked.connect(self.button_click_action)
        self.sc_pushbutton.setGeometry(QRect(430, 300, 171, 41))
        self.sc_pushbutton.clicked.connect(self.button_click_action)
        self.dic_pushbutton.setGeometry(QRect(790, 200, 111, 31))
        self.dic_pushbutton.clicked.connect(self.button_click_action)

        self.dic_label.setGeometry(QRect(0, 200, 261, 31))
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.dic_label.setFont(font)
        self.dic_label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.ddc_label.setText("Dependent Corpus       :")
        self.ddc_pushbutton.setText("Select")
        self.sc_pushbutton.setText("Set Corpora")
        self.dic_pushbutton.setText("Select")
        self.dic_label.setText("Independent Corpus       :")

    def button_click_action(self):
        sender = self.sender()
        if sender == self.ddc_pushbutton:
            file = str(QFileDialog.getExistingDirectory(None, "Select Corpus Directory"))
            self.ddc_text_area.setText(file)

        if sender == self.dic_pushbutton:
            file = str(QFileDialog.getExistingDirectory(None, "Select Corpus Directory"))
            self.dic_text_area.setText(file)

        if sender == self.sc_pushbutton:
            domain_dependent_corpus_path = self.ddc_text_area.toPlainText()
            domain_independent_corpus_path = self.dic_text_area.toPlainText()
            if self.interaction_data.new_thread_allowable:
                self.sc_pushbutton.setDisabled(True)
                self.interaction_data.set_corpus_dictionary(
                    domain_dependent_corpus_path=domain_dependent_corpus_path,
                    domain_independent_corpus_path=domain_independent_corpus_path
                )

                message = "Domain Dependant Corpus :    " \
                          + domain_dependent_corpus_path \
                          + "\n\nDomain Independent Corpus :    " \
                          + domain_independent_corpus_path

                QMessageBox.about(self, "Corpora Set successful", message)
                self.sc_pushbutton.setDisabled(False)
            else:
                message = "A background process is already running.\n"
                message += "Wait for it to be completed to set corpora directories again."
                QMessageBox.about(self, "Background Process Running", message)


class CFEWidget(QWidget):
    def __init__(self, interaction_data):
        super(CFEWidget, self).__init__()
        self.interaction_data = interaction_data
        self.cfe_thread = None

        self.cfe_text_area = QTextBrowser(self)
        self.cfe_progressbar = QProgressBar(self)
        self.cfe_pushbutton = QPushButton(self)
        self.cfe_dic_radiobutton = QRadioButton(self)
        self.cfe_ddc_radiobutton = QRadioButton(self)
        self.setup_ui()

    def setup_ui(self):
        self.cfe_text_area.setGeometry(QRect(90, 30, 731, 281))

        self.cfe_dic_radiobutton.setGeometry(QRect(365, 320, 250, 22))
        self.cfe_dic_radiobutton.setText("Domain Independent Corpus")

        self.cfe_ddc_radiobutton.setChecked(True)
        self.cfe_ddc_radiobutton.setGeometry(QRect(90, 320, 250, 22))
        self.cfe_ddc_radiobutton.setText("Domain Dependent Corpus")

        self.cfe_progressbar.setGeometry(QRect(90, 360, 731, 23))

        self.cfe_pushbutton.setGeometry(QRect(330, 410, 261, 41))
        self.cfe_pushbutton.setText("Extract Candidate Feature")
        self.cfe_pushbutton.clicked.connect(self.action)

    def action(self):
        recreate_database()
        use_dependent_corpus = True
        if self.sender() == self.cfe_pushbutton:
            if self.cfe_ddc_radiobutton.isChecked():
                use_dependent_corpus = True
            elif self.cfe_dic_radiobutton.isChecked():
                use_dependent_corpus = False
            if self.interaction_data.is_set_corpus_dictionary:
                if self.interaction_data.new_thread_allowable:
                    self.cfe_thread = CandidateFeatureExtractionThread(
                        interaction_data=self.interaction_data,
                        dependant=use_dependent_corpus
                    )

                    self.cfe_thread.textSignal.connect(self.update_text_browser)
                    self.cfe_thread.progressSignal.connect(self.update_progressbar)
                    self.cfe_thread.finishSignal.connect(self.on_completion)
                    self.interaction_data.deny_new_thread()
                    self.cfe_text_area.clear()
                    self.cfe_progressbar.setValue(0)
                    self.cfe_thread.start()
                else:
                    message = "A background process is already running.\nWait for it to be completed to start a new process"
                    QMessageBox.about(self, "Background Process Running", message)

            else:
                message = "Directories for Corpora are not set properly."
                message += "\nGo to 'Corpus Selection' tab & select proper corpora directories."
                QMessageBox.about(self, "Corpora Directory Error", message)

    def update_progressbar(self, completed, total):
        value = int((completed * 100.0) / total)
        self.cfe_progressbar.setValue(value)

    def update_text_browser(self, given_message):
        self.cfe_text_area.append(given_message)

    def on_completion(self):
        self.cfe_thread = None
        self.interaction_data.allow_new_thread()
        message = "Candidate Feature Extraction Completed"
        QMessageBox.about(self, "Task Complete", message)


class DRCWidget(QWidget):
    def __init__(self, interaction_data):
        super(DRCWidget, self).__init__()
        self.interaction_data = interaction_data
        self.drc_thread = None

        self.drc_text_area = QTextEdit(self)
        self.drc_progressbar = QProgressBar(self)
        self.drc_pushbutton = QPushButton(self)
        self.drc_dic_radiobutton = QRadioButton(self)
        self.drc_ddc_radiobutton = QRadioButton(self)
        self.drc_umwe_checkbox = QCheckBox(self)
        self.drc_cud_checkbox = QCheckBox(self)
        self.setup_ui()

    def setup_ui(self):
        self.drc_text_area.setGeometry(QRect(90, 30, 731, 281))

        self.drc_ddc_radiobutton.setChecked(True)
        self.drc_ddc_radiobutton.setGeometry(QRect(90, 320, 210, 22))
        self.drc_ddc_radiobutton.setText("Domain Dependent Corpus")

        self.drc_dic_radiobutton.setGeometry(QRect(305, 320, 220, 22))
        self.drc_dic_radiobutton.setText("Domain Independent Corpus")

        self.drc_umwe_checkbox.setText("Modified IEDR")
        self.drc_umwe_checkbox.setGeometry(QRect(690, 320, 150, 22))
        self.drc_umwe_checkbox.setChecked(True)

        self.drc_progressbar.setGeometry(QRect(90, 360, 731, 23))

        self.drc_pushbutton.setGeometry(QRect(330, 410, 261, 41))
        self.drc_pushbutton.setText("Calculate Domain Relevance")

        self.drc_cud_checkbox.setText("Reset Database")
        self.drc_cud_checkbox.setGeometry(QRect(540, 320, 141, 22))

        self.drc_pushbutton.clicked.connect(self.action)

    def action(self):
        use_dependent_corpus = True
        use_modified_iedr = True
        if self.sender() == self.drc_pushbutton:
            if self.drc_ddc_radiobutton.isChecked():
                use_dependent_corpus = True
            elif self.drc_dic_radiobutton.isChecked():
                use_dependent_corpus = False
            if not self.drc_umwe_checkbox.isChecked():
                use_modified_iedr = False
            if self.drc_cud_checkbox.isChecked():
                self.interaction_data.deny_new_thread()
                recreate_database()
                self.interaction_data.allow_new_thread()

            if self.interaction_data.is_set_corpus_dictionary:
                if self.interaction_data.new_thread_allowable:
                    self.drc_thread = DomainRelevanceCalculationThread(
                        interaction_data=self.interaction_data,
                        dependant=use_dependent_corpus,
                        use_modified_iedr=use_modified_iedr
                    )

                    self.drc_thread.textSignal.connect(self.update_text_browser)
                    self.drc_thread.progressSignal.connect(self.update_progressbar)
                    self.drc_thread.finishSignal.connect(self.on_completion)
                    self.interaction_data.deny_new_thread()
                    self.drc_text_area.clear()
                    self.drc_progressbar.setValue(0)
                    self.drc_thread.start()
                else:
                    message = "A background process is already running.\n\
                               Wait for it to be completed to start a new process"
                    QMessageBox.about(self,  "Background Process Running", message)

            else:
                message = "Directories for Corpora are not set properly."
                message += "\nGo to 'Corpus Selection' tab & select proper corpora directories."
                QMessageBox.about(QMessageBox.Default, self,  "Corpora Directory Error", message)

    def update_progressbar(self, completed, total):
        value = int((completed * 100.0) / total)
        self.drc_progressbar.setValue(value)

    def update_text_browser(self, given_message):
        self.drc_text_area.append(given_message)

    def on_completion(self):
        self.drc_thread = None
        self.interaction_data.allow_new_thread()
        message = "Domain Relevance Calculation Completed"
        QMessageBox.about(self,  "Task Complete", message)


class AFEWidget(QWidget):
    def __init__(self, interaction_data):
        super(AFEWidget, self).__init__()
        self.interaction_data = interaction_data

        self.extracted_features_taxt_area = QTextBrowser(self)
        self.vertical_line = QFrame(self)
        self.horizontal_line = QFrame(self)
        self.domain_relevance_parcentage_label = QLabel(self)
        self.domain_relevance_actual_label = QLabel(self)
        self.extracted_features_label = QLabel(self)
        self.dr_p_button = QPushButton(self)
        self.dr_a_button = QPushButton(self)
        self.idr_p_combo = QDoubleSpinBox(self)
        self.edr_p_combo = QDoubleSpinBox(self)
        self.idr_p_label = QLabel(self)
        self.edr_p_label = QLabel(self)
        self.idr_a_combo = ModifiedComboBox(self)
        self.edr_a_combo = ModifiedComboBox(self)
        self.idr_a_label = QLabel(self)
        self.edr_a_label = QLabel(self)
        self.umidr_a_checkbutton = QCheckBox(self)
        self.umedr_a_checkbutton = QCheckBox(self)
        self.afe_thread = None
        self.setup_ui()

    def setup_ui(self):
        self.extracted_features_taxt_area.setGeometry(QRect(20, 60, 411, 381))
        self.extracted_features_label.setText("Extracted Features")

        self.vertical_line.setGeometry(QRect(440, 20, 20, 431))
        self.vertical_line.setFrameShape(QFrame.VLine)
        self.vertical_line.setFrameShadow(QFrame.Sunken)

        self.horizontal_line.setGeometry(QRect(460, 210, 451, 20))
        self.horizontal_line.setFrameShape(QFrame.HLine)
        self.horizontal_line.setFrameShadow(QFrame.Sunken)

        self.domain_relevance_parcentage_label.setGeometry(QRect(460, 20, 461, 20))
        self.domain_relevance_parcentage_label.setText("Domain Relevance ( Percentage )")

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        self.domain_relevance_parcentage_label.setFont(font)
        self.domain_relevance_parcentage_label.setAlignment(Qt.AlignCenter)

        self.domain_relevance_actual_label.setGeometry(QRect(460, 240, 451, 20))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.domain_relevance_actual_label.setFont(font)
        self.domain_relevance_actual_label.setAlignment(Qt.AlignCenter)
        self.domain_relevance_actual_label.setText("Domain Relevance ( Actual )")

        self.extracted_features_label.setGeometry(QRect(10, 20, 431, 31))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.extracted_features_label.setFont(font)
        self.extracted_features_label.setAlignment(Qt.AlignCenter)

        self.dr_p_button.setGeometry(QRect(600, 160, 181, 31))
        self.dr_p_button.clicked.connect(self.button_action)
        self.dr_p_button.setText("Extract")

        self.dr_a_button.setGeometry(QRect(600, 410, 181, 31))
        self.dr_a_button.clicked.connect(self.button_action)
        self.dr_a_button.setText("Extract")

        self.idr_p_combo.setGeometry(QRect(670, 70, 241, 27))
        self.idr_p_combo.setMaximum(100.00)

        self.edr_p_combo.setGeometry(QRect(670, 110, 241, 27))
        self.idr_p_combo.setMaximum(100.00)

        self.idr_p_label.setGeometry(QRect(480, 70, 171, 21))
        self.idr_p_label.setText("Intrinsic Domain Relevance :")
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.idr_p_label.setFont(font)

        self.edr_p_label.setGeometry(QRect(480, 110, 171, 21))
        self.edr_p_label.setText("Extrinsic Domain Relevance :")
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.edr_p_label.setFont(font)

        self.idr_a_combo.setGeometry(QRect(670, 290, 100, 33))
        self.idr_a_combo.popupAboutToBeShown.connect(self.populate_combo)
        self.idr_a_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")

        self.edr_a_combo.setGeometry(QRect(670, 330, 100, 33))
        self.edr_a_combo.popupAboutToBeShown.connect(self.populate_combo)
        self.edr_a_combo.setStyleSheet("QComboBox { combobox-popup: 0; }")

        self.idr_a_label.setGeometry(QRect(480, 290, 181, 31))
        self.idr_a_label.setText("Intrinsic Domain Relevance :")

        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.idr_a_label.setFont(font)

        self.edr_a_label.setGeometry(QRect(480, 330, 181, 31))
        self.edr_a_label.setText("Extrinsic Domain Relevance :")
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.edr_a_label.setFont(font)

        self.umidr_a_checkbutton.setGeometry(QRect(780, 295, 130, 22))
        self.umidr_a_checkbutton.setText("Use median")
        self.umidr_a_checkbutton.setChecked(False)
        self.umidr_a_checkbutton.stateChanged.connect(self.median_action)

        self.umedr_a_checkbutton.setGeometry(QRect(780, 335, 130, 22))
        self.umedr_a_checkbutton.setText("Use Median")
        self.umedr_a_checkbutton.setChecked(False)
        self.umedr_a_checkbutton.stateChanged.connect(self.median_action)

    def populate_combo(self):
        if self.interaction_data.is_set_corpus_dictionary:
            if self.idr_a_combo.count() == 0 or self.edr_a_combo.count() == 0:
                temp_feature_extractor = FeatureExtractor(
                    dependent_corpus=self.interaction_data.corpus_dictionary['dependent_corpus_name'],
                    independent_corpus=self.interaction_data.corpus_dictionary['dependent_corpus_name']
                )

                idr_list = sorted(
                    temp_feature_extractor.pi_object.get_all_domain_relevance(dependent=True, rounded_up_to=6)
                )

                edr_list = sorted(
                    temp_feature_extractor.pi_object.get_all_domain_relevance(dependent=False, rounded_up_to=6)
                )

                idr_list_str = [str(i) for i in idr_list]
                edr_list_str = [str(i) for i in edr_list]

                self.idr_a_combo.clear()
                self.edr_a_combo.clear()
                self.idr_a_combo.addItems(idr_list_str)
                self.edr_a_combo.addItems(edr_list_str)
        else:
            message = "Directories for Corpora are not set properly."
            message += "\nGo to 'Corpus Selection' tab & select proper corpora directories."
            QMessageBox.about(self,  "Corpora Directory Error", message)

    def median_action(self):
        status_sender = self.sender()
        checked = status_sender.isChecked()
        if checked:
            if status_sender == self.umidr_a_checkbutton:
                self.idr_a_combo.setDisabled(True)
            if status_sender == self.umedr_a_checkbutton:
                self.edr_a_combo.setDisabled(True)
        else:
            if status_sender == self.umidr_a_checkbutton:
                self.idr_a_combo.setDisabled(False)
            if status_sender == self.umedr_a_checkbutton:
                self.edr_a_combo.setDisabled(False)
            self.populate_combo()

    def button_action(self):
        sender_button = self.sender()
        use_percentage = False
        idr = edr = None
        if self.interaction_data.is_set_corpus_dictionary:
            if self.interaction_data.new_thread_allowable:
                if sender_button == self.dr_p_button:
                    use_percentage = True
                    idr = float(self.idr_p_combo.value())
                    edr = float(self.edr_p_combo.value())

                if sender_button == self.dr_a_button:
                    if self.idr_a_combo.currentIndex() >= 0 and self.edr_a_combo.currentIndex() >= 0:
                        idr = None if self.umidr_a_checkbutton.isChecked() else float(self.idr_a_combo.currentText())
                        edr = None if self.umedr_a_checkbutton.isChecked() else float(self.edr_a_combo.currentText())
                    else:
                        self.umidr_a_checkbutton.setChecked(True)
                        self.umedr_a_checkbutton.setChecked(True)

                self.afe_thread = ActualFeatureExtractionThread(
                    interaction_data=self.interaction_data,
                    idr=idr,
                    edr=edr,
                    use_percentage=use_percentage
                )
                self.afe_thread.signal.connect(self.show_features)
                self.interaction_data.deny_new_thread()
                self.extracted_features_taxt_area.clear()
                self.afe_thread.start()
            else:
                message = "A background process is already running.\n\
                               Wait for it to be completed to start a new process"
                QMessageBox.about(self,  "Background Process Running", message)

        else:
            message = "Directories for Corpora are not set properly."
            message += "\nGo to 'Corpus Selection' tab & select proper corpora directories."
            QMessageBox.about(self,  "Corpora Directory Error", message)

    def show_features(self, feature_list):
        self.afe_thread = None
        feature_list = sorted(feature_list)
        self.extracted_features_taxt_area.clear()
        print(len(feature_list))
        for feature in feature_list:
            self.extracted_features_taxt_area.append(feature)

        QMessageBox.about(self,  "Task Complete", "Feature extraction Completed")
        self.interaction_data.allow_new_thread()
