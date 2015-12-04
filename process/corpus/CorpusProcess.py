from glob import glob
from process.corpus.DocumentProcess import Document
from math import log10, sqrt
from process.db.interaction import Interaction


class Corpus(object):
    def __init__(self, path, name):
        self.corpus_path = [path + "/", path][path[-1] == '/']
        # if corpus directory don't have a '/' at the end then it is added
        self.corpus_name = name
        self.corpus_raw_document_list = glob(self.corpus_path + "raw/*")
        self.corpus_evaluated_document_list = glob(self.corpus_path + "eval/*")
        # self.corpus_raw_document_count = len(self.corpus_raw_document_list)
        # self.corpus_evaluated_document_count = len(self.corpus_evaluated_document_list)

        # creating in database communication obeject of class Intersection in this Class
        # which gives all the methods of this class access to this object
        self.interaction = Interaction(self.corpus_name)
        self.interaction.create_corpus_entry()

    def _refresh(self):
        """
        Create the list of evaluated documents
        Keep the list count
        :type self: None
        """
        self.corpus_evaluated_document_list = glob(self.corpus_path + "eval/*")
        self.corpus_evaluated_document_count = len(self.corpus_evaluated_document_list)

    def evaluate_corpus_documents(self):
        """
        this method extracts candidate features for all the documents in the corpus
        creates a corresponding file for all the document with extracted features and terms
        """
        counter = 0
        for document_path in self.corpus_raw_document_list:
            Document(document_path).evaluate_term_frequency()
            counter += 1
            print(counter, end='\r')
        self._refresh()
        print(counter)

    def upload_documents(self):
        """
        this method populates the table "document". It uses the name of documents
        from corpus eval directory.
        """
        document_list = []
        for document_name in self.corpus_evaluated_document_list:

            # getting only the name of the file rather than whole directory
            position = document_name.rfind('/') + 1
            document_name = document_name[position:]

            document_list.append(document_name)
        self.interaction.create_document_entry(document_list)

    def get_evaluated_term_frequency(self, eval_document_name):
        """
        reads each of the evaluated corpus data file
        returns the collection of term and term frequency
        as a dictionary in the format -> { term : term_frequency }
        """

        with open(eval_document_name, 'r') as document:
            lines = [line.rstrip().split(':') for line in document]
            my_dictionary = {}
            for line in lines:
                word = line[0]
                try:
                    count = int(line[1])
                    my_dictionary[word] = count
                except Exception as E:
                    print(eval_document_name + " : " + str(E))
                    continue
        return my_dictionary

    def upload_term_frequency(self):
        """
        process & invoke upload of term & term frequency for each document in the corpus
        """

        # if this method is used separately when the evaluated folder list has changes
        # next two lines refresh two class variables before proceeding to process
        self.corpus_evaluated_document_list = glob(self.corpus_path + "eval/*")
        self.corpus_evaluated_document_count = len(self.corpus_evaluated_document_list)

        counter = 0
        for eval_document_name in self.corpus_evaluated_document_list:
            my_dictionary = self.get_evaluated_term_frequency(eval_document_name)

            # getting only the file name rather than whole file path
            position = eval_document_name.rfind("/") + 1
            eval_document_name = eval_document_name[position:]

            # invoking upload of term & term frequency in the database
            self.interaction.populate_term_frequency(my_dictionary, eval_document_name)
            counter += 1
            print(counter, end='\r')
        print(counter)

    def upload_document_frequency(self):
        """
        invoke the upload of document frequency in the database
        """
        self.interaction.insert_document_frequency()

    def calculate_weight(self, tf, df):
        """
        calculates the weight for each term with term & document frequency
        """
        weight = 0.0
        tf *= 1.0
        df *= 1.0
        if tf > 0:
            # weight = (1 + log10(tf)) * log10(self.corpus_evaluated_document_count / df)
            weight = (1 + log10(tf))
        return weight

    def evaluate_terms_weight(self):
        """
        process & invoke the upload of weight of each term with respect to each document
        """

        # df_dictionary { term_id : document_frequency }
        df_dictionary = self.interaction.get_document_frequency

        # dictionary { document_id : { term_id : term_frequency } }
        tf_huge = self.interaction.get_term_frequency

        # dicionary in the format-> { document_id:{ term_id:weight} }
        huge_dictionary = {}

        for doc_id in tf_huge:
            tf_dictionary = tf_huge[doc_id]
            weightij_dictionary = {}
            for term_id in tf_dictionary:
                weightij = self.calculate_weight(tf_dictionary[term_id], df_dictionary[term_id])
                weightij_dictionary[term_id] = weightij
            huge_dictionary[doc_id] = weightij_dictionary

        # invoking insertion in database
        self.interaction.insert_weightij(huge_dictionary)

    def evaluate_wi(self):
        """
        invokes the insertion of average weight for each term
        """
        self.interaction.insert_weighti()

    def evaluate_si(self):
        """
        process the standard variance for each term in the corpus
        invokes upload to database
        """

        # dictionary in format -> { (term_id, document_id):weight }
        wij_dictionary = self.interaction.get_wij
        wij_dictionary_keys = wij_dictionary.keys()

        # dictionary in format -> { term_id:average_weight }
        wi_dictionary = self.interaction.get_wi
        wi_dictionary_keys = wi_dictionary.keys()

        huge_document_list = self.interaction.get_corpus_document_id_list
        N = len(huge_document_list)
        si_dictionary = {}

        counter = 0
        for term_id in wi_dictionary_keys:
            wi = wi_dictionary[term_id]
            sum = 0.0
            for doc_id in huge_document_list:
                # as the key in wij_dictionary is a tuple of term_id & document_id
                key_tuple = (term_id, doc_id)
                if key_tuple in wij_dictionary_keys:
                    wij = wij_dictionary[key_tuple]
                    sum += (wij - wi) * (wij - wi)
                else:
                    # if weight is not found in database means its weight is 0
                    sum += wi * wi
            # as per equation
            si_value = sqrt(sum / N)
            if si_value==0:
                si_value = .000001
            si_dictionary[term_id] = si_value

            counter += 1
            print(counter, end='\r')
        # invoking upload
        self.interaction.insert_si(si_dictionary)

    def evaluate_dispi(self):
        """
        invoke upload of dispersion of each term of corpus in database
        """
        self.interaction.insert_dispi()

    def evaluate_wj(self):
        """
        invoke upload of average term-weight of each document of corpus in database
        """
        self.interaction.insert_weightj()

    def evaluate_devij(self):
        """
        process and invoke upload of deviation for each term with respect to each document
        of the corpus
        """
        # dictionary in format -> { (term_id, document_id):weight }
        wij_dic = self.interaction.get_wij

        # dictionary in format -> { document_id:weight }
        wj_dic = self.interaction.get_wj

        # dictionary in format -> { (term_id, document_id):deviation }
        devij_dic = {}

        for key in wij_dic:
            devij_dic[key] = wij_dic[key] - wj_dic[key[1]]
        self.interaction.insert_deviation(devij_dic)

    def evaluate_domain_relevance(self):
        """
        process the domain relevance for each term in the corpus
        invokes upload to database
        """

        huge_document_list = self.interaction.get_corpus_document_id_list

        # dictionary in the format -> { term_id : dispersion }
        dispi_dic = self.interaction.get_dispi

        # dictionary in the format -> { (term_id, document_id) : deviation }
        devij_dic = self.interaction.get_devij
        devij_dic_keys = devij_dic.keys()

        # dictionary in the format -> { document_id : average_weight }
        wj_dic = self.interaction.get_wj

        # dictionary in the format -> { term_id : domain relevance }
        dri_dic = {}

        counter = 0
        for term_id in dispi_dic:
            dispi = dispi_dic[term_id]
            sum = 0.0
            for doc_id in huge_document_list:
                key_tuple = (term_id, doc_id)
                if key_tuple in devij_dic_keys:
                    sum += devij_dic[key_tuple]
                else:
                    if wj_dic[doc_id]:
                        sum = (--wj_dic[doc_id])
            dri_dic[term_id] = dispi * sum
            counter += 1
            print(counter, end='\r')
        # invoking insertion of domain relevance
        self.interaction.insert_domain_relevance(dri_dic)
