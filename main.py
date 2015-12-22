import time
import sys
from process.manage import ProcessManager, recreate_database


def run_process(modified_iedr=True):
    start_time = time.time()

    # be scared be very very scared about this method, completely cleans the database
    recreate_database()

    process_1 = ProcessManager(corpus_path="/home/badhon/Desktop/dataset/cars/", corpus_name='cars')
    process_1.extract_candidate_features()
    process_1.calculate_domain_relevance(modified_weight_equation=modified_iedr)

    process_2 = ProcessManager(corpus_path="/home/badhon/Desktop/dataset/hotels/", corpus_name='hotels')
    process_2.extract_candidate_features()
    process_2.calculate_domain_relevance(modified_weight_equation=modified_iedr)

    second = time.time() - start_time
    print(int(second / 3600), "hour(s)", int((second % 3600) / 60), "minute(s)", round((second % 3600) % 60, 5),
          "second(s)")


def evaluate_performance():
    pass


def main():
    # run_process(modified_iedr=False)
    # evaluate_performance()
    pass


if __name__ == "__main__":
    sys.exit(main())
