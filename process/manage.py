from process.corpus.CorpusProcess import Corpus
from process.db.structure import clean_up
from process.db.interaction import PerformanceInteraction
from os.path import expanduser


class ProcessManager:
    def __init__(self, corpus_path, corpus_name):
        self.path = corpus_path
        self.name = corpus_name

        self.corpus = Corpus(path=self.path, name=self.name)
        if self.corpus:
            print(corpus_name, corpus_path)

    def extract_candidate_features(self, signal_emitter):
        # much time
        signal_emitter.textSignal.emit("Corpus    :    " + self.name + "\nCandidate Feature Extraction started")
        print(self.name + " : Candidate Feature Extraction started")
        self.corpus.evaluate_corpus_documents(signal_emitter)
        print(self.name + " : Candidate feature extracted")
        signal_emitter.textSignal.emit("Corpus    :    " + self.name + "\nCandidate Feature Extraction completed")
        # signal_emitter.emit(QtCore.SIGNAL("update_cfe_text_browser"),
        #                     "Corpus    :    " + self.name + "\nCandidate Feature Extraction completed")
        signal_emitter.finishSignal.emit()

    def calculate_domain_relevance(self, signal_emitter, modified_weight_equation):
        completed_task = 0
        signal_emitter.textSignal.emit("Corpus    :    " + self.name + "\nDomain Relevance Calculation started")
        signal_emitter.progressSignal.emit(completed_task, 10)

        self.corpus.upload_documents()
        print(self.name + " : Document List Uploaded.")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : Document List Uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)

        # much time
        self.corpus.upload_term_frequency()
        print(self.name + " : Term Frequency uploaded.")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : Term Frequency uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)

        self.corpus.upload_document_frequency()
        print(self.name + " : Document Frequency uploaded.")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : Document Frequency uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)

        # moderate time
        self.corpus.evaluate_terms_weight(modified_weight_equation=modified_weight_equation)
        print(self.name + " : Wij calculated & uploaded")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : Wij calculated & uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)

        self.corpus.evaluate_wi()
        print(self.name + " : Wi calculated & uploaded")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : Wi calculated & uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)

        self.corpus.evaluate_si()
        print(self.name + " : Si calculated & uploaded")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : Si calculated & uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)

        self.corpus.evaluate_dispi()
        print(self.name + " : DISPERSIONi calculated & uploaded")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : DISPERSIONi calculated & uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)

        self.corpus.evaluate_wj()
        print(self.name + " : Wj calculated & uploaded")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : Wj calculated & uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)

        # moderate time
        self.corpus.evaluate_devij()
        print(self.name + " : DEVIATIONij calculated & uploaded")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : DEVIATIONij calculated & uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)

        self.corpus.evaluate_domain_relevance()
        print(self.name + " : DRi calculated & uploaded")
        completed_task += 1
        signal_emitter.textSignal.emit(self.name + " : DRi calculated & uploaded")
        signal_emitter.progressSignal.emit(completed_task, 10)
        signal_emitter.textSignal.emit("Corpus    :    " + self.name + "\nDomain Relevance Calculation completed")
        signal_emitter.finishSignal.emit()


class FeatureExtractor:
    def __init__(self, dependent_corpus, independent_corpus):
        self.dependent_corpus = dependent_corpus
        self.independent_corpus = independent_corpus
        self.pi_object = PerformanceInteraction(
            dependent_corpus_name=self.dependent_corpus,
            independent_corpus_name=self.independent_corpus
        )

    def _calculate_threshold(self, percentage=None, dependant=True):
        """
        Given parameter 'percentage' being 'None' this method returns the median value among the corresponding corpus's
        domain relevance values.
        Given parameter 'dependant' being 'True' Domain Dependent Corpus is selected else Domain Independent Corpus is
        selected.
        """
        if percentage is None:
            return self.pi_object.get_median_threshold(dependent=dependant)
        dr_max = self.pi_object.get_max_dr(dependent=dependant)
        dr_min = self.pi_object.get_min_dr(dependent=dependant)
        dr_threshold = (((dr_max - dr_min) / 100) * percentage) + dr_min
        return dr_threshold

    def extract(self, use_percentage=True, idr=None, edr=None):
        if use_percentage:
            # With the intention of using percentage values for idr and edr, are calculated if given else median
            # values for idr or edr are used
            idr_threshold = self._calculate_threshold(percentage=idr)
            edr_threshold = self._calculate_threshold(percentage=edr, dependant=False)
        else:
            # With the intention of using exact idr and edr values, are implemented if given else median values for idr
            # & edr are used
            idr_threshold = idr if idr is not None else self._calculate_threshold()
            edr_threshold = edr if edr is not None else self._calculate_threshold(dependant=False)

        feature_list = self.pi_object.get_final_features(idr_threshold=idr_threshold, edr_threshold=edr_threshold)
        with open(expanduser('~') + "/actual_corpus_features.txt", 'w', encoding='utf-8') as document:
            for feature in feature_list:
                document.write(str(feature) + "\n")
        return feature_list


def recreate_database():
    clean_up()
