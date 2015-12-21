from process.corpus.CorpusProcess import Corpus
from process.db.structure import clean_up
from process.db.interaction import PerformanceInteraction


class ProcessManager:
    def __init__(self, corpus_path, corpus_name):
        self.path = corpus_path
        self.name = corpus_name
        self.corpus = Corpus(path=self.path, name=self.name)

    def extract_candidate_features(self):
        # much time
        self.corpus.evaluate_corpus_documents()
        print(self.name + " : Candidate feature extracted")

    def calculate_domain_relevance(self):
        self.corpus.upload_documents()
        print(self.name + " : Document List Uploaded.")

        # much time
        self.corpus.upload_term_frequency()
        print(self.name + " : Term Frequency uploaded.")

        self.corpus.upload_document_frequency()
        print(self.name + " : Document Frequency uploaded.")

        # moderate time
        self.corpus.evaluate_terms_weight()
        print(self.name + " : Wij uploaded")

        self.corpus.evaluate_wi()
        print(self.name + " : Wi")

        self.corpus.evaluate_si()
        print(self.name + " : Si")

        self.corpus.evaluate_dispi()
        print(self.name + " : DISPERSIONi")

        self.corpus.evaluate_wj()
        print(self.name + " : Wj")

        # moderate time
        self.corpus.evaluate_devij()
        print(self.name + " : DEVIATIONij")

        self.corpus.evaluate_domain_relevance()
        print(self.name + " : DRi")


class FeatureExtractor:
    def __init__(self, dependent_corpus, independent_corpus):
        self.dependent_corpus = dependent_corpus
        self.independent_corpus = independent_corpus
        self.pi_object = PerformanceInteraction(dependent_corpus_name=self.dependent_corpus,
                                                independent_corpus_name=self.independent_corpus)

    def _calculate_threshold_from_percentage(self, percentage, dependant=True):
        if percentage is None:
            return self.pi_object.get_median_threshold(dependent=dependant)
        dr_max = self.pi_object.get_max_dr(dependent=dependant)
        dr_min = self.pi_object.get_min_dr(dependent=dependant)
        dr_threshold = (((dr_max - dr_min) / 100) * percentage) + dr_min
        return dr_threshold

    def extract(self, idr_percentage=None, edr_percentage=None):
        idr_threshold = self._calculate_threshold_from_percentage(percentage=idr_percentage)
        edr_threshold = self._calculate_threshold_from_percentage(percentage=edr_percentage, dependant=False)
        print(idr_threshold, edr_threshold)
        return self.pi_object.get_final_features(idr_threshold=idr_threshold, edr_threshold=edr_threshold)


def recreate_database():
    clean_up()
