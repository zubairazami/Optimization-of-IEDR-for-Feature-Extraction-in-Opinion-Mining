import nltk
import random
from nltk.classify.scikitlearn import SklearnClassifier
import pickle
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from nltk.classify import ClassifierI
from statistics import mode
from nltk.tokenize import word_tokenize
from PyQt4 import QtCore


class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        return mode(votes)

    def confidence(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)

        choice_votes = votes.count(mode(votes))
        conf = float(choice_votes) / len(votes)
        return conf


class Training(object):
    def __init__(self, positive_file_directory, negative_file_directory, pickled_directory):
        self.allowed_word_types = ["J"]
        self.all_words = []
        self.documents = []
        self.positive_file_directory = positive_file_directory
        self.negative_file_directory = negative_file_directory
        self.pickled_directory = pickled_directory
        self.pickled_dictionary = dict(documents_pickle="documents.pickle",
                                       word_features_pickle="word_features5k.pickle",
                                       naive_bayes_pickle="originalnaivebayes5k.pickle",
                                       multinomial_naive_bayes_pickle="MNB_classifier5k.pickle",
                                       bernoulli_naive_bayes_pickle="BernoulliNB_classifier5k.pickle",
                                       logistic_regression_pickle="LogisticRegression_classifier5k.pickle",
                                       linear_svc_pickle="LinearSVC_classifier5k.pickle", )
        self.testing_set = None
        self.training_set = None

    def open_files(self):
        # Open Positive and Negative Review Files
        self.short_pos = open(self.positive_file_directory, "r").read()
        self.short_neg = open(self.negative_file_directory, "r").read()

    def create_training_materials(self, signal_emitter):

        self.open_files()
        self.sentences_positive = self.short_pos.split('\n')
        self.sentences_negative = self.short_neg.split('\n')

        positive_line = len(self.sentences_positive)
        negative_line = len(self.sentences_negative)
        number_of_reviews_in_both = min(positive_line, negative_line)

        self.sentences_positive = self.sentences_positive[:number_of_reviews_in_both + 1]
        self.sentences_negative = self.sentences_negative[:number_of_reviews_in_both + 1]
        total = len(self.sentences_positive) + len(self.sentences_negative)

        # print(positive_line, negative_line, number_of_reviews_in_both)
        completion_counter = 0

        # Processing the Positive Reviews
        for sentence in self.sentences_positive:
            self.documents.append((sentence, "pos"))
            self.words = word_tokenize(sentence)
            self.pos = nltk.pos_tag(self.words)

            for word in self.pos:
                if word[1][0] in self.allowed_word_types:
                    self.all_words.append(word[0].lower())
            completion_counter += 1
            print(completion_counter, end='\r')
            # send signal from here to GUI
            signal_emitter.emit(QtCore.SIGNAL("training_progress"), completion_counter, total)

        for sentence in self.sentences_negative:
            self.documents.append((sentence, "neg"))
            self.words = word_tokenize(sentence)
            self.pos = nltk.pos_tag(self.words)
            for word in self.pos:
                if word[1][0] in self.allowed_word_types:
                    self.all_words.append(word[0].lower())
            completion_counter += 1
            print(completion_counter, end='\r')
            # send signal from here to GUI
            signal_emitter.emit(QtCore.SIGNAL("training_progress"), completion_counter, total)
        self.save_trained_materials()

    def save_trained_materials(self):
        # Save documents
        self.save_documents = open(self.pickled_directory + "/" + self.pickled_dictionary["documents_pickle"], "wb")
        pickle.dump(self.documents, self.save_documents)
        self.save_documents.close()

        self.all_words = nltk.FreqDist(self.all_words)
        self.word_features = list(self.all_words.keys())[:2000]

        # Save word_features
        self.save_word_features = open(self.pickled_directory + "/" + self.pickled_dictionary["word_features_pickle"],
                                       "wb")
        pickle.dump(self.word_features, self.save_word_features)
        self.save_word_features.close()

    def open_trained_materials(self):
        self.documents_f = open(self.pickled_directory + "/" + self.pickled_dictionary["documents_pickle"], "rb")
        self.documents = pickle.load(self.documents_f)
        self.documents_f.close()
        self.word_features5k_f = open(self.pickled_directory + "/" + self.pickled_dictionary["word_features_pickle"],
                                      "rb")
        self.word_features = pickle.load(self.word_features5k_f)
        self.word_features5k_f.close()

    def find_features(self, document):
        words = word_tokenize(document)
        features = {}

        for w in self.word_features:
            features[w] = (w in words)

        return features

    def create_featuresets(self):
        featuresets = [(self.find_features(rev), category) for (rev, category) in self.documents]
        random.shuffle(featuresets)
        print(len(featuresets))
        total_features = len(featuresets)
        training_features = int(total_features * .85)
        self.testing_set = featuresets[training_features:]
        self.training_set = featuresets[:training_features]

    def train_test_classifier(self, signal_emitter):
        # Naive Bayes Classifier
        self.classifier = nltk.NaiveBayesClassifier.train(self.training_set)
        msg = "Original Naive Bayes Algo accuracy \t" + str(
            round((nltk.classify.accuracy(self.classifier, self.testing_set)),4) * 100) + " % "
        print(msg)
        signal_emitter.emit(QtCore.SIGNAL("training_progress_classifier"), 1, 5, msg)
        # classifier.show_most_informative_features(15)
        self.save_classifier = open(self.pickled_directory + "/" + self.pickled_dictionary["naive_bayes_pickle"], "wb")
        pickle.dump(self.classifier, self.save_classifier)
        self.save_classifier.close()

        # Multinomial Naive Bayes Classifier
        self.MNB_classifier = SklearnClassifier(MultinomialNB())
        self.MNB_classifier.train(self.training_set)
        msg = "MNB_classifier accuracy \t" + str(
            round((nltk.classify.accuracy(self.MNB_classifier, self.training_set)), 4) * 100) + " % "
        print(msg)
        signal_emitter.emit(QtCore.SIGNAL("training_progress_classifier"), 2, 5, msg)
        self.save_classifier = open(
            self.pickled_directory + "/" + self.pickled_dictionary["multinomial_naive_bayes_pickle"], "wb")
        pickle.dump(self.MNB_classifier, self.save_classifier)
        self.save_classifier.close()

        # Bernoulli Naive Bayes Classifier
        self.BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
        self.BernoulliNB_classifier.train(self.training_set)
        msg = "BernoulliNB_classifier accuracy \t" + str(
            round((nltk.classify.accuracy(self.BernoulliNB_classifier, self.training_set)), 4) * 100) + " % "
        print(msg)
        signal_emitter.emit(QtCore.SIGNAL("training_progress_classifier"), 3, 5, msg)

        self.save_classifier = open(
            self.pickled_directory + "/" + self.pickled_dictionary["bernoulli_naive_bayes_pickle"], "wb")
        pickle.dump(self.BernoulliNB_classifier, self.save_classifier)
        self.save_classifier.close()

        # Logistic Regression Classifier
        self.LogisticRegression_classifier = SklearnClassifier(LogisticRegression())
        self.LogisticRegression_classifier.train(self.training_set)
        msg = "LogisticRegression_classifier accuracy \t" + str(
            round((nltk.classify.accuracy(self.LogisticRegression_classifier, self.training_set)), 4) * 100) + " % "
        print(msg)
        signal_emitter.emit(QtCore.SIGNAL("training_progress_classifier"), 4, 5, msg)

        self.save_classifier = open(
            self.pickled_directory + "/" + self.pickled_dictionary["logistic_regression_pickle"], "wb")
        pickle.dump(self.LogisticRegression_classifier, self.save_classifier)
        self.save_classifier.close()

        # Linear SVC Classifier
        self.LinearSVC_classifier = SklearnClassifier(LinearSVC())
        self.LinearSVC_classifier.train(self.training_set)
        msg = "LinearSVC_classifier accuracy \t" + str(
            round((nltk.classify.accuracy(self.LinearSVC_classifier, self.training_set)), 4) * 100) + " % "
        print(msg)
        signal_emitter.emit(QtCore.SIGNAL("training_progress_classifier"), 5, 5, msg)
        self.save_classifier = open(self.pickled_directory + "/" + self.pickled_dictionary["linear_svc_pickle"], "wb")
        pickle.dump(self.LinearSVC_classifier, self.save_classifier)
        self.save_classifier.close()

    def sentiment(self, text):
        voted_classifier = VoteClassifier(
            self.classifier,
            self.LinearSVC_classifier,
            self.MNB_classifier,
            self.BernoulliNB_classifier,
            self.LogisticRegression_classifier)
        feats = self.find_features(text)
        return voted_classifier.classify(feats), voted_classifier.confidence(feats)

# t = Training()
# Obj.create_training_materials(1000,-5)
# t.open_trained_materials()
# t.create_featuresets()
# t.train_test_classifier()
