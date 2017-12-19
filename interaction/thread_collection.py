from process.manage import ProcessManager, FeatureExtractor
from sentiment_analysis.manage import SentimentManager
from PyQt5.QtCore import QThread, pyqtSignal


class CandidateFeatureExtractionThread(QThread):

    update_text_browser_signal = pyqtSignal( str )
    update_progressbar_signal = pyqtSignal( int, int )
    completion_signal = pyqtSignal()

    def __init__(self, interaction_data, dependant=True):
        super(CandidateFeatureExtractionThread, self).__init__(None)
        self.dependent = dependant
        self.interaction_data = interaction_data
        self.process_manager = None

    def connect_all(self, on_text_update, on_progressbar_update, on_completion):
        self.update_text_browser_signal.connect(on_text_update)
        self.update_progressbar_signal.connect(on_progressbar_update)
        self.completion_signal.connect(on_completion)

    def emit_signal(self, text=None, completed_task_count = None, total_task_count = None):

        if text is None and completed_task_count is None and total_task_count is None:
            self.completion_signal.emit()
        elif text is not None:
            self.update_text_browser_signal.emit(text)
        else:
            self.update_progressbar_signal.emit(completed_task_count, total_task_count)

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

    def __init__(self, interaction_data, dependant=True, use_modified_iedr=True):
        QThread.__init__(self)
        self.dependent = dependant
        self.interaction_data = interaction_data
        self.use_modified_iedr = use_modified_iedr
        self.process_manager = None

        self.update_text_browser_signal = pyqtSignal(str)
        self.update_progressbar_signal = pyqtSignal(int, int)
        self.completion_signal = pyqtSignal()

        self.update_text_browser_signal = pyqtSignal(str)
        self.update_progressbar_signal = pyqtSignal(int, int)
        self.completion_signal = pyqtSignal()

    def connect_all(self, on_text_update, on_progressbar_update, on_completion):
        self.update_text_browser_signal.connect(on_text_update)
        self.update_progressbar_signal.connect(on_progressbar_update)
        self.completion_signal.connect(on_completion)

    def emit_signal(self, text=None, completed_task_count=None, total_task_count=None):

        if text is None and completed_task_count is None and total_task_count is None:
            self.completion_signal.emit()
        elif text is not None:
            self.update_text_browser_signal.emit(text)
        else:
            self.update_progressbar_signal.emit(completed_task_count, total_task_count)

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
        self.emit(QtCore.SIGNAL("afe"), feature_list)


class TrainingThread(QThread):
    def __init__(self, interaction_data):
        QThread.__init__(self)
        self.interaction_data = interaction_data
        self.sentiment_manager = None

    def run(self):
        if self.sentiment_manager:
            self.sentiment_manager = None
        self.sentiment_manager = SentimentManager(
            positive_file_directory=self.interaction_data.sentiment_dictionary['pos_filepath'],
            negative_file_directory=self.interaction_data.sentiment_dictionary['neg_filepath'],
            pickled_directory=self.interaction_data.sentiment_dictionary['pickled_path'],
            emitter=self)
        self.sentiment_manager.train()


class AnalysisThread(QThread):
    def __init__(self, interaction_data, test_file, feature_file):
        QThread.__init__(self)
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
            emitter=self)
        self.sentiment_manager.result(test_file_path=self.test_file, corpus_feature_file_path=self.feature_file)
