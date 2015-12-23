from time import time
from sys import exit
from math import ceil
from os.path import expanduser
from process.manage import ProcessManager, recreate_database
from performance.Performance import Performance


def run_process(data):
    start_time = time()

    # be scared be very very scared about this method, completely cleans the database
    recreate_database()

    process_1 = ProcessManager(corpus_path=data['dependent_corpus_path'], corpus_name=data['dependent_corpus_name'])
    process_1.extract_candidate_features()
    process_1.calculate_domain_relevance(modified_weight_equation=data['modified_iedr'])

    process_2 = ProcessManager(corpus_path=data['independent_corpus_path'], corpus_name=data['independent_corpus_name'])
    process_2.extract_candidate_features()
    process_2.calculate_domain_relevance(modified_weight_equation=data['modified_iedr'])

    second = time() - start_time
    print(int(second / 3600), "hour(s)", int((second % 3600) / 60), "minute(s)", int(ceil(second % 3600) % 60),
          "second(s)")


def run_performance(data):
    start_time = time()

    performance_object = Performance(data)
    performance_object.evaluate_performance(50)

    second = time() - start_time
    print(int(second / 3600), "hour(s)", int((second % 3600) / 60), "minute(s)", int(ceil(second % 3600) % 60),
          "second(s)")


def main():
    process_dictionary = dict(
        dependent_corpus_name='cars',
        dependent_corpus_path=expanduser('~') + '/dataset/cars/',
        independent_corpus_name='hotels',
        independent_corpus_path=expanduser('~') + '/dataset/hotels/',
        modified_iedr=True,
    )
    performance_dictionary = dict(
        dependent_corpus_name='cars',
        independent_corpus_name='hotels',
        actual_features_file_path=expanduser('~') + '/dataset/actual_car_features.txt',
        modified_weight_equation=True,
    )
    run_process(process_dictionary)
    run_performance(performance_dictionary)


if __name__ == "__main__":
    exit(main())
