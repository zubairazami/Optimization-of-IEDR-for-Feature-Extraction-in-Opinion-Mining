from process.corpus.CorpusProcess import Corpus
from process.db.structure import clean_up


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


def recreate_database():
    clean_up()
