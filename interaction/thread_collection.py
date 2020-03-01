from PyQt5.QtCore import pyqtSignal

from process.manage import ProcessManager, FeatureExtractor
from sentiment_analysis.manage import SentimentManager
from PyQt5 import QtCore


class CandidateFeatureExtractionThread(QtCore.QThread):
    textSignal = QtCore.pyqtSignal(str)
    progressSignal = QtCore.pyqtSignal(int, int)
    finishSignal = QtCore.pyqtSignal()

    def __init__(self, interaction_data, dependant=True):
        QtCore.QThread.__init__(self)
        self.dependent = dependant
        self.interaction_data = interaction_data
        self.process_manager = None

    def run(self):
        if self.process_manager:
            self.process_manager = None
        if self.dependent:
            corpus_name = self.interaction_data.corpus_dictionary['dependent_corpus_name']
            corpus_path = self.interaction_data.corpus_dictionary['dependent_corpus_path']
        else:
            corpus_name = self.interaction_data.corpus_dictionary['independent_corpus_name']
            corpus_path = self.interaction_data.corpus_dictionary['independent_corpus_path']
        self.process_manager = ProcessManager(corpus_name=corpus_name, corpus_path=corpus_path)
        self.process_manager.extract_candidate_features(signal_emitter=self)


class DomainRelevanceCalculationThread(QtCore.QThread):
    textSignal = QtCore.pyqtSignal(str)
    progressSignal = QtCore.pyqtSignal(int, int)
    finishSignal = QtCore.pyqtSignal()

    def __init__(self, interaction_data, dependant=True, use_modified_iedr=True):
        QtCore.QThread.__init__(self)
        self.dependent = dependant
        self.interaction_data = interaction_data
        self.use_modified_iedr = use_modified_iedr
        self.process_manager = None

    def run(self):
        if self.process_manager:
            self.process_manager = None
        if self.dependent:
            corpus_name = self.interaction_data.corpus_dictionary['dependent_corpus_name']
            corpus_path = self.interaction_data.corpus_dictionary['dependent_corpus_path']
        else:
            corpus_name = self.interaction_data.corpus_dictionary['independent_corpus_name']
            corpus_path = self.interaction_data.corpus_dictionary['independent_corpus_path']
        self.process_manager = ProcessManager(corpus_name=corpus_name, corpus_path=corpus_path)
        self.process_manager.calculate_domain_relevance(signal_emitter=self,
                                                        modified_weight_equation=self.use_modified_iedr)


class ActualFeatureExtractionThread(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)

    def __init__(self, interaction_data, idr=None, edr=None, use_percentage=False):
        QtCore.QThread.__init__(self)
        self.interaction_data = interaction_data
        self.feature_extractor = None
        self.use_percentage = use_percentage
        self.idr = idr
        self.edr = edr

    def run(self):
        if self.feature_extractor:
            self.feature_extractor = None
        self.feature_extractor = FeatureExtractor(
            dependent_corpus=self.interaction_data.corpus_dictionary['dependent_corpus_name'],
            independent_corpus=self.interaction_data.corpus_dictionary['independent_corpus_name'])
        feature_list = self.feature_extractor.extract(use_percentage=self.use_percentage, idr=self.idr, edr=self.edr)
        self.signal.emit(feature_list)


class TrainingThread(QtCore.QThread):
    trainingSignal = QtCore.pyqtSignal(int, int)
    trainingClassifierSignal = QtCore.pyqtSignal(int, int, str)
    finishSignal = QtCore.pyqtSignal()

    def __init__(self, interaction_data):
        QtCore.QThread.__init__(self)
        self.interaction_data = interaction_data
        self.sentiment_manager = None

    def run(self):
        if self.sentiment_manager:
            self.sentiment_manager = None
        self.sentiment_manager = SentimentManager(
            positive_file_directory=self.interaction_data.sentiment_dictionary['pos_filepath'],
            negative_file_directory=self.interaction_data.sentiment_dictionary['neg_filepath'],
            pickled_directory=self.interaction_data.sentiment_dictionary['pickled_path'],
            emitter=self
        )
        self.sentiment_manager.train()


class AnalysisThread(QtCore.QThread):
    analysisSignal = QtCore.pyqtSignal(str, float, float)
    finishSignal = QtCore.pyqtSignal()

    def __init__(self, interaction_data, test_file, feature_file):
        QtCore.QThread.__init__(self)
        self.interaction_data = interaction_data
        self.sentiment_manager = None
        self.test_file = test_file
        self.feature_file = feature_file

    def run(self):
        if self.sentiment_manager:
            self.sentiment_manager = None
        self.sentiment_manager = SentimentManager(
            positive_file_directory=self.interaction_data.sentiment_dictionary['pos_filepath'],
            negative_file_directory=self.interaction_data.sentiment_dictionary['neg_filepath'],
            pickled_directory=self.interaction_data.sentiment_dictionary['pickled_path'],
            emitter=self
        )
        self.sentiment_manager.result(test_file_path=self.test_file, corpus_feature_file_path=self.feature_file)


