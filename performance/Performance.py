from process.db.interaction import PerformanceInteraction
from performance.PrecisionRecall import PrecisionRecall
import os
from random import randint


class Performance(object):
    def __init__(self, details_dictionary):
        self.dependent_corpus_name = details_dictionary['dependent_corpus_name']
        self.independent_corpus_name = details_dictionary['independent_corpus_name']
        self.actual_features_file_path = details_dictionary['actual_features_file_path']
        self.modified_weight_equation_use = details_dictionary['modified_weight_equation']
        self.pi_object = PerformanceInteraction(self.dependent_corpus_name, self.independent_corpus_name)
        self.pr_object = PrecisionRecall(self.actual_features_file_path)

    def evaluate_performance(self, performance_data_count):
        i_list = self.pi_object.get_all_domain_relevance()
        i_list_length = len(i_list)

        e_list = self.pi_object.get_all_domain_relevance(dependent=False)
        e_list_length = len(e_list)

        pre_list = []
        counter = 0
        for count in range(performance_data_count):
            counter += 1
            a = randint(0, i_list_length - 1)
            b = randint(0, e_list_length - 1)
            i = i_list[a]
            e = e_list[b]
            precision, recall = self.pr_object.get_precision_recall(idr_threshold=i, edr_threshold=e)
            precision = round(precision, 2)
            recall = round(recall, 2)
            pre_list.append((precision, recall, i, e))
            print("Completed :", counter, end='\r')

        precision_recall_list = list(set(pre_list))
        precision_recall_list = sorted(precision_recall_list, key=lambda x: x[1])

        if self.modified_weight_equation_use:
            file_path = os.path.expanduser('~') + '/dataset/tf_prt.txt'
        else:
            file_path = os.path.expanduser('~') + '/dataset/tf_idf_prt.txt'

        with open(file_path, 'w', encoding='utf-8') as document:
            for each_tuple in precision_recall_list:
                t1 = "{0:.2f}".format(each_tuple[0])
                t2 = "{0:.2f}".format(each_tuple[1])
                t3 = "{0:.2f}".format(each_tuple[2])
                t4 = "{0:.2f}".format(each_tuple[3])
                document.write(t1 + ",  " + t2 + ",  " + t3 + ",  " + t4 + "\n")
