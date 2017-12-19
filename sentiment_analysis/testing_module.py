import random
import nltk
from PyQt5 import QtCore


class SentimentTesting():
    def __init__(self, training_object, analysed_file_path, corpus_feature_file_path, emitter):

        self.test_data = []
        self.corpus_features = []
        self.training_obj = training_object
        self.signal_emitter = emitter
        self.training_obj.open_trained_materials()

        self.training_obj.create_featuresets()
        self.training_obj.train_test_classifier(signal_emitter=self.signal_emitter)
        self.to_be_sentiment_analysed = analysed_file_path
        self.corpus_features_file_path = corpus_feature_file_path

    # import data and features
    def import_data(self):
        # import raw data
        self.file_content = open(self.to_be_sentiment_analysed).read()
        sentences = nltk.sent_tokenize(self.file_content)

        # import corpus features
        f = open(self.corpus_features_file_path, "r")
        feature_list = f.read().split("\n")
        self.corpus_features = feature_list
        f.close()

        # extract sentences with corpus features only
        for feature in self.corpus_features:
            for sentence in sentences:
                if feature in sentence:
                    self.test_data.append(sentence)
        self.test_data = list(set(self.test_data))
        random.shuffle(self.test_data)


    # calculate feature sentiments
    def feature_sentiment(self, feature):
        feature_dictionary_with_sentiment = dict()
        feature_pos = 0
        feature_neg = 0
        feature_neutral = 0
        counter = 0

        for i in range(len(self.test_data)):
            if feature in self.test_data[i]:
                # print self.test_data[i]
                result = self.training_obj.sentiment(self.test_data[i])
                # print result
                if result[0] == 'pos' and result[1] >= 0.6:
                    feature_pos += 1
                    counter += 1
                elif result[0] == 'neg' and result[1] >= 0.6:
                    feature_neg += 1
                    counter += 1

        if counter == 0:
            return
        pospercent = round((float(feature_pos) / counter) * 100, 2)
        negpercent = round((float(feature_neg) / counter) * 100, 2)
        #neautralpercent = round((float(feature_neutral) / counter) * 100, 2)

        self.signal_emitter.emit(QtCore.SIGNAL("analysis_signal"), feature, pospercent, negpercent)
        print(feature, ":--- \t\t", "Positive: ", pospercent, "%, Negative: \t", negpercent, "%")

    # detemines the polarity and confidence of each review
    def test_run(self):
        for i in range(len(self.test_data)):
            print(self.test_data[i])
            print(self.training_obj.sentiment(self.test_data[i]))
            print("... ... ...")

    # determines the sentiment of each feature
    def feature_based_sentiment_analysis(self):
        for feature in self.corpus_features:
            self.feature_sentiment(feature)
