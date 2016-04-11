from process.db.structure import engine, Base, Corpus, Document, Term, TermDocument, TermCorpus
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from math import floor


class Interaction:
    def __init__(self, corpus_name):
        self.corpus_name = corpus_name
        self.db_engine = engine
        self.Base = Base
        self.Base.metadata.bind = self.db_engine
        self.DBSession = sessionmaker(bind=self.db_engine)
        self.session = self.DBSession()

    def create_corpus_entry(self):
        """
        creates an instance of the corpus in database
        insert new row in table 'corpus' if doesn't exist
        """
        self.get_or_create(Corpus, corpus_name=self.corpus_name)
        self.session.commit()

    def create_document_entry(self, document_list):
        """
        creates instances of the document in database
        insert new row in table 'document' if doesn't exist
        """
        parent_corpus = self.get(Corpus, corpus_name=self.corpus_name)
        for each_document in document_list:
            self.get_or_create(Document, corpus_id=parent_corpus.corpus_id, document_name=each_document)
        self.session.commit()

    def populate_term_frequency(self, my_dictionary, eval_document_name):
        """
        insert new row in table 'term' if doesn't exist
        populate the table "term_document" with each term and it's term frequency for
        corresponding document
        """
        this_corpus_id = self.get_corpus_id
        for key in my_dictionary:
            term_frequency = my_dictionary[key]
            if any(c.isalpha() for c in key):
                try:
                    term_object = self.get_or_create(Term, term_name=key)
                    document_object = self.get(Document, document_name=eval_document_name)
                    self.get_or_create(TermDocument, term_id=term_object.term_id,
                                       document_id=document_object.document_id, term_frequency=term_frequency)
                    self.get_or_create(TermCorpus, term_id=term_object.term_id, corpus_id=this_corpus_id)
                except UnicodeEncodeError:
                    continue

        self.session.commit()

    def insert_document_frequency(self):
        """
        this method inserts document frequency for all the terms in a specific corpus in term_corpus table
        """
        term_list = self.get_corpus_term_id_list
        document_list = self.get_corpus_document_id_list
        this_corpus_id = self.get_corpus_id
        for each_term_id in term_list:
            document_frequency = self.session.query(TermDocument).filter(TermDocument.term_id == each_term_id,
                                                                         TermDocument.document_id.in_(
                                                                             document_list)).count()
            term_corpus_object = self.get(TermCorpus, term_id=each_term_id, corpus_id=this_corpus_id)
            if term_corpus_object is not None:
                term_corpus_object.document_frequency = document_frequency
        self.session.commit()

    def insert_weightij(self, huge_dictionary):
        """
        this method inserts weight for each term with respect to each document
        in term_document table for the whole corpus a time
        """
        doc_list = huge_dictionary.keys()
        counter = 0
        for doc_id in doc_list:
            term_weight_dictionary = huge_dictionary[doc_id]
            for id in term_weight_dictionary:
                term_document_object = self.get(TermDocument, term_id=id, document_id=doc_id)
                term_document_object.weightij = term_weight_dictionary[id]
            counter += 1
            print(counter, end='\r')
        self.session.commit()

    def insert_weighti(self):
        """inserts average weight for each term in the corpus in term_corpus table """
        term_id_list = self.get_corpus_term_id_list
        document_id_list = self.get_corpus_document_id_list
        N = len(document_id_list)
        c_id = self.get_corpus_id
        counter = 0
        for t_id in term_id_list:
            counter += 1
            summation = self.session.query(func.sum(TermDocument.weightij)).filter(TermDocument.term_id == t_id,
                                                                                   TermDocument.document_id.in_(
                                                                                       document_id_list))
            term_corpus_object = self.get(TermCorpus, term_id=t_id, corpus_id=c_id)
            term_corpus_object.weighti = (1.0 * summation[0][0]) / N
            print(counter, end='\r')
        self.session.commit()

    def insert_si(self, si_dictionary):
        """
        inserts the standard variance of each term of the corpus in table 'term_corpus'
        """
        keys = si_dictionary.keys()
        c_id = self.get_corpus_id
        for key in keys:
            self.get(TermCorpus, term_id=key, corpus_id=c_id).si = si_dictionary[key]
        self.session.commit()

    def insert_dispi(self):
        """
        inserts the dispersion of each term of the corpus in table 'term_corpus'
        """
        c_id = self.get_corpus_id
        object_list = self.session.query(TermCorpus.term_id, TermCorpus.weighti, TermCorpus.si).filter(
            TermCorpus.corpus_id == c_id)
        dictionary = {obj[0]: obj[1] / obj[2] for obj in object_list}
        for key in dictionary:
            self.get(TermCorpus, term_id=key, corpus_id=c_id).dispi = dictionary[key]
        self.session.commit()

    def insert_weightj(self):
        """
        inserts the average terms weight of document in table 'document'
        """
        documents = self.get_corpus_document_id_list
        temp_list = self.session.query(TermDocument.document_id, func.count(TermDocument.term_id),
                                       func.sum(TermDocument.weightij)).group_by(TermDocument.document_id).filter(
            TermDocument.document_id.in_(documents))
        dictionary = {temp[0]: temp[2] / (1.0 * temp[1]) for temp in temp_list}
        for key in dictionary:
            self.get(Document, document_id=key).weightj = dictionary[key]
        self.session.commit()

    def insert_deviation(self, deviation_dictionary):
        """
        this method inserts deviation for each term in term_document table
        """
        counter = 0
        for key in deviation_dictionary:
            self.get(TermDocument, term_id=key[0], document_id=key[1]).deviation = deviation_dictionary[key]
            counter += 1
            print(counter, end='\r')
        self.session.commit()

    def insert_domain_relevance(self, dri_dic):
        """
        inserts domain-relevance for each term in TermCorpus table
        """
        for key in dri_dic:
            c_id = self.get_corpus_id
            self.get(TermCorpus, term_id=key, corpus_id=c_id).domain_relevance = dri_dic[key]
        self.session.commit()

    @property
    def get_wij(self):
        """
        returns the collection of weight for each term  with respect to each document
        of the corpus as a dictionary in the format -> { (term_id, document_id) : weight }
        """
        huge_list = self.session.query(TermDocument.term_id, TermDocument.document_id, TermDocument.weightij).filter(
            TermDocument.document_id.in_(self.get_corpus_document_id_list))
        return {(list_item[0], list_item[1]): list_item[2] for list_item in huge_list}

    @property
    def get_wi(self):
        """
        returns the collection of average weight for each term of the corpus as a
        dictionary in the format -> { term_id : average_weight }
        """
        temp = self.session.query(TermCorpus.term_id, TermCorpus.weighti).filter(
            TermCorpus.corpus_id == self.get_corpus_id)
        return {t[0]: t[1] for t in temp}

    @property
    def get_wj(self):
        """
        returns the collection of average term weight for each document of the corpus as a
        dictionary in the format -> { document_id : average_weight }
        """
        c_id = self.get_corpus_id
        temp = self.session.query(Document.document_id, Document.weightj).filter(Document.corpus_id == c_id)
        return {t[0]: t[1] for t in temp}

    @property
    def get_dispi(self):
        """
        returns the collection of dispersion for each term of the corpus as a
        dictionary in the format -> { term_id : dispersion }
        """
        c_id = self.get_corpus_id
        temp = self.session.query(TermCorpus.term_id, TermCorpus.dispi).filter(TermCorpus.corpus_id == c_id)
        return {t[0]: t[1] for t in temp}

    @property
    def get_devij(self):
        """
        returns the collection of deviation for each term with respect to corpus documents as a
        dictionary in the format -> { (term_id, document_id) : deviation }
        """
        documents = self.get_corpus_document_id_list
        temp = self.session.query(TermDocument.term_id, TermDocument.document_id, TermDocument.deviation).filter(
            TermDocument.document_id.in_(documents))
        return {(t[0], t[1]): t[2] for t in temp}

    @property
    def get_corpus_term_id_list(self):
        """
        returns the collection of term_id of current corpus as a list
        """
        id = self.get_corpus_id
        result_list = self.session.query(TermCorpus.term_id).filter(TermCorpus.corpus_id == id).all()
        term_id_list = [term[0] for term in result_list]
        return term_id_list

    @property
    def get_corpus_document_id_list(self):
        """
        returns the collection of document_id of current corpus as a list
        """
        c_id = self.get_corpus_id
        result_list = self.session.query(Document.document_id).filter(Document.corpus_id == c_id).all()
        document_id_list = [result[0] for result in result_list]
        return document_id_list

    @property
    def get_corpus_id(self):
        """
        returns current corpus id
        """
        corpus = self.session.query(Corpus).filter(Corpus.corpus_name == self.corpus_name).first()
        if corpus is not None:
            return corpus.corpus_id
        return None

    @property
    def get_document_frequency(self):
        """
        This method gets all the term's document frequency from the table "term_corpus"
        and returns a dictionary in the format : {term_id:document_frequency}
        """
        temp_list = self.session.query(TermCorpus.term_id, TermCorpus.document_frequency).filter(
            TermCorpus.corpus_id == self.get_corpus_id).all()
        dictionary = {each_tuple[0]: each_tuple[1] for each_tuple in temp_list}
        return dictionary

    @property
    def get_term_frequency(self):
        """
        This method gets all the term's term frequency from the table "term_document"
        and returns a dictionary in the format -> {document_id:{term_id:term_frequency}}
        """
        doc_list = self.get_corpus_document_id_list
        huge_dictionary = {}
        for doc_id in doc_list:
            temp_list = self.session.query(TermDocument.term_id, TermDocument.term_frequency).filter(
                TermDocument.document_id == doc_id)
            dictionary = {each_tuple[0]: each_tuple[1] for each_tuple in temp_list}
            huge_dictionary[doc_id] = dictionary
        return huge_dictionary

    def get_or_create(self, model, **kwargs):
        """
        Creates an object or returns the object of argument 'model' if exists
        filtered or created by given argument as **kwargs
        """
        instance = self.session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            self.session.add(instance)
            return instance

    def get(self, model, **kwargs):
        """
        return an object of 'model' if exists filtered by given arguments as **kwargs
        """
        instance = self.session.query(model).filter_by(**kwargs).first()
        return instance

    def create(self, model, **kwargs):
        """
        creates on object of 'model' with given arguments as **kwargs
        """
        instance = model(**kwargs)
        self.session.add(instance)


class PerformanceInteraction:
    def __init__(self, dependent_corpus_name, independent_corpus_name):
        self.db_engine = engine
        self.Base = Base
        self.Base.metadata.bind = self.db_engine
        self.DBSession = sessionmaker(bind=self.db_engine)
        self.session = self.DBSession()
        self.dependent_corpus_name = dependent_corpus_name
        self.independent_corpus_name = independent_corpus_name
        self.dependant_corpus_id = self.session.query(Corpus.corpus_id).filter(
            Corpus.corpus_name == self.dependent_corpus_name).first()[0]
        self.independent_corpus_id = self.session.query(Corpus.corpus_id).filter(
            Corpus.corpus_name == self.independent_corpus_name).first()[0]

    def get_all_domain_relevance(self, dependent=True, rounded_up_to=3):
        """
        returns domain relevance of all features of either dependent or independent corpus
        as a list, based on the value of input parameter 'dependent'.
        """
        if dependent:
            corpus_id = self.dependant_corpus_id
        else:
            corpus_id = self.independent_corpus_id
        temp_list = self.session.query(TermCorpus.domain_relevance).filter(TermCorpus.corpus_id == corpus_id).all()
        temp_list = [round(each_tuple[0], rounded_up_to) for each_tuple in temp_list]
        relevance_list = list(set(temp_list))
        return relevance_list

    def get_max_dr(self, dependent=True):
        """
        returns the highest value from domain relevance among all features of either dependent
        or independent corpus, based on the value of input parameter 'dependent'.
        """
        if dependent:
            corpus_id = self.dependant_corpus_id
        else:
            corpus_id = self.independent_corpus_id
        return self.session.query(func.max(TermCorpus.domain_relevance).label("max")).filter(
            TermCorpus.corpus_id == corpus_id).one().max

    def get_min_dr(self, dependent=True):
        """
        returns the lowest value of domain relevance among all features of either dependent
        or independent corpus, based on the value of input parameter 'dependent'.
        """
        if dependent:
            corpus_id = self.dependant_corpus_id
        else:
            corpus_id = self.independent_corpus_id
        return self.session.query(func.min(TermCorpus.domain_relevance).label("min")).filter(
            TermCorpus.corpus_id == corpus_id).one().min

    def get_count(self, dependent=True):
        """
        returns the count of candidate features of either dependent
        or independent corpus, based on the value of input parameter 'dependent'.
        """
        if dependent:
            corpus_id = self.dependant_corpus_id
        else:
            corpus_id = self.independent_corpus_id
        return self.session.query(TermCorpus.term_id).filter(TermCorpus.corpus_id == corpus_id).count()

    def get_median_threshold(self, dependent=True):
        """
        returns a threshold (median, measurement of central tendency) domain relevance value
        of either dependent or independent corpus,  based on the value of input parameter 'dependent'.
        """
        if dependent:
            corpus_id = self.dependant_corpus_id
        else:
            corpus_id = self.independent_corpus_id

        temp_list = self.session.query(TermCorpus.domain_relevance).filter(TermCorpus.corpus_id == corpus_id).all()
        relevance_list = [each_tuple[0] for each_tuple in temp_list]
        count = self.get_count(dependent=dependent)

        if not count % 2 == 0:
            threshold = relevance_list[floor(count / 2)]
        else:
            i = int(count / 2)
            threshold = (relevance_list[i] + relevance_list[i - 1]) / 2
        return threshold

    @property
    def get_domain_relevance_dictionary(self):
        """
        returns one list, two dictionaries:
            1. candidate_feature_id_list : Contains ids of all the candidate features ( of dependent corpus )
            2. idr_score_dictionary : Contains id (of candidate features) as key and their intrinsic domain
        relevance as value.
            3. edr_score_dictionary : Contains id (of candidate features) as key and their extrinsic domain
        relevance as value.
        """
        temp_list = self.session.query(TermCorpus.term_id, TermCorpus.domain_relevance).filter(
            TermCorpus.corpus_id == self.dependant_corpus_id).all()

        candidate_feature_id_list = [each_tuple[0] for each_tuple in temp_list]
        idr_score_dictionary = {each_tuple[0]: each_tuple[1] for each_tuple in temp_list}

        temp_list = self.session.query(TermCorpus.term_id, TermCorpus.domain_relevance).filter(
            TermCorpus.corpus_id == self.independent_corpus_id,
            TermCorpus.term_id.in_(candidate_feature_id_list)).all()

        edr_score_dictionary = {each_tuple[0]: each_tuple[1] for each_tuple in temp_list}
        return candidate_feature_id_list, idr_score_dictionary, edr_score_dictionary

    def get_final_features(self, idr_threshold, edr_threshold):
        """
        returns all the resultant features of this IEDR method for feature extraction as a list,
        based on two input parameter idr_threshold, edr_threshold
        """
        candidate_feature_id_list, idr_dictionary, edr_dictionary = self.get_domain_relevance_dictionary
        for feature_id in candidate_feature_id_list:
            if feature_id not in edr_dictionary:
                edr_dictionary[feature_id] = float(0)

        feature_id_list = [feature_id for feature_id in candidate_feature_id_list if
                           idr_dictionary[feature_id] >= idr_threshold and edr_dictionary[feature_id] <= edr_threshold]
        if len(feature_id_list) > 0:
            temp_list = self.session.query(Term.term_name).filter(Term.term_id.in_(feature_id_list)).all()
            final_features = [each_tuple[0] for each_tuple in temp_list]
            return final_features
        return []
