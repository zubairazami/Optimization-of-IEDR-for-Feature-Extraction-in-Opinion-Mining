from PyQt5.QtCore import pyqtSignal as QSignal, QThread
from process.manage import ProcessManager, FeatureExtractor


class CandidateFeatureExtractionThread(QThread):
    textSignal = QSignal(str)
    progressSignal = QSignal(int, int)
    finishSignal = QSignal()

    def __init__(self, interaction_data, dependant=True):
        QThread.__init__(self)
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


class DomainRelevanceCalculationThread(QThread):
    textSignal = QSignal(str)
    progressSignal = QSignal(int, int)
    finishSignal = QSignal()

    def __init__(self, interaction_data, dependant=True, use_modified_iedr=True):
        QThread.__init__(self)
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


class ActualFeatureExtractionThread(QThread):
    signal = QSignal(object)

    def __init__(self, interaction_data, idr=None, edr=None, use_percentage=False):
        QThread.__init__(self)
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