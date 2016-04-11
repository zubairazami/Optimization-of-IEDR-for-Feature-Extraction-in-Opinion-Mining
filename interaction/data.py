from interaction.thread_collection import CandidateFeatureExtractionThread


class InteractionData(object):
    def __init__(self):
        self.corpus_dictionary = dict(dependent_corpus_name='', dependent_corpus_path='', independent_corpus_name='',
                                      independent_corpus_path='')
        self.thread_running = False

    @property
    def is_set_corpus_dictionary(self):
        flag1 = not self.corpus_dictionary['dependent_corpus_name'] == ''
        flag2 = not self.corpus_dictionary['dependent_corpus_path'] == ''
        flag3 = not self.corpus_dictionary['independent_corpus_name'] == ''
        flag4 = not self.corpus_dictionary['independent_corpus_path'] == ''
        if flag1 and flag2 and flag3 and flag4:
            return True

    def set_corpus_dictionary(self, domain_dependent_corpus_path, domain_independent_corpus_path):
        self.corpus_dictionary['dependent_corpus_name'] = domain_dependent_corpus_path[
                                                          domain_dependent_corpus_path.rfind('/') + 1:]
        self.corpus_dictionary['dependent_corpus_path'] = domain_dependent_corpus_path
        self.corpus_dictionary['independent_corpus_name'] = domain_independent_corpus_path[
                                                            domain_independent_corpus_path.rfind('/') + 1:]
        self.corpus_dictionary['independent_corpus_path'] = domain_independent_corpus_path

    def clean_corpus_dictionary(self):
        self.corpus_dictionary['dependent_corpus_name'] = ''
        self.corpus_dictionary['dependent_corpus_path'] = ''
        self.corpus_dictionary['independent_corpus_name'] = ''
        self.corpus_dictionary['independent_corpus_path'] = ''

    def allow_new_thread(self):
        self.thread_running = False

    def deny_new_thread(self):
        self.thread_running = True

    @property
    def new_thread_allowable(self):
        return not self.thread_running
