from process.db.interaction import PerformanceInteraction
from nltk.stem import PorterStemmer


class PrecisionRecall:
    def __init__(self, original_feature_file_path):
        self.original_feature_file_path = original_feature_file_path
        self.original_list = []
        self.performance_object = PerformanceInteraction('cars', 'hotels')
        with open(original_feature_file_path, 'r', ) as document:
            for each_line in document:
                self.original_list.append(each_line[:-1])
        self.stemming_object = PorterStemmer()

    def is_same(self, str1, input_list):
        flag = False
        stemmed_input_list = [self.stemming_object.stem(s) for s in input_list]
        if str1 in input_list or self.stemming_object.stem(str1) in stemmed_input_list:
            flag = True
        return flag

    def get_precision_recall(self, idr_threshold, edr_threshold):
        predicted_list = self.performance_object.get_final_features(idr_threshold, edr_threshold)
        tp = 0
        for candidate in predicted_list:
            if self.is_same(candidate, self.original_list):
                tp += 1
        fp = len(predicted_list) - tp
        try:
            c_precision = tp / (tp + fp)
        except ZeroDivisionError as exception:
            c_precision = 0
            print("precision exception ", exception)
        tp = 0
        for candidate in self.original_list:
            if self.is_same(candidate, predicted_list):
                tp += 1
        fn = len(self.original_list) - tp
        try:
            c_recall = tp / (tp + fn)
        except ZeroDivisionError as exception:
            c_recall = 0
            print("precision exception ", exception)
        return c_precision, c_recall
