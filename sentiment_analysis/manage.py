from sentiment_analysis.training_module import *
from sentiment_analysis.testing_module import *


class SentimentManager(object):
    def __init__(self, positive_file_directory, negative_file_directory, pickled_directory, emitter):
        self.training_obj = None
        self.testing_obj = None
        self.positive_file_directory = positive_file_directory
        self.negative_file_directory = negative_file_directory
        self.pickled_directory = pickled_directory
        self.emitter = emitter

    def train(self):
        if self.training_obj:
            self.training_obj = None

        training_obj = Training(positive_file_directory=self.positive_file_directory,
                                negative_file_directory=self.negative_file_directory,
                                pickled_directory=self.pickled_directory)

        training_obj.create_training_materials(signal_emitter=self.emitter)
        training_obj.create_featuresets()
        training_obj.train_test_classifier(signal_emitter=self.emitter)

    def result(self, test_file_path, corpus_feature_file_path):
        if self.training_obj:
            self.training_obj = None
        self.training_obj = Training(positive_file_directory=self.positive_file_directory,
                                     negative_file_directory=self.negative_file_directory,
                                     pickled_directory=self.pickled_directory)

        if self.testing_obj:
            self.testing_obj = None
        self.testing_obj = SentimentTesting(training_object=self.training_obj, analysed_file_path=test_file_path,
                                            corpus_feature_file_path=corpus_feature_file_path, emitter=self.emitter)

        self.testing_obj.import_data()

        self.testing_obj.feature_based_sentiment_analysis()
