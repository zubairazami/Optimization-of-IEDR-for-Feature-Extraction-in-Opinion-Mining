import nltk
from nltk.tokenize import PunktSentenceTokenizer
from collections import Counter
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from process.parser.ParserProcess import parse


class Document(object):
    """
    This class mainly helps only to read a raw-document and extract features from it with that features
    term frequency and write on another file.
    So to say simply Use of Document class :
        raw-document ------> numeric-data containing document of raw one
    Objects of this class have only been used in evaluate_corpus_documents() method of class Corpus
    of CorpusProcess.py of package corpus_process
    """

    def __init__(self, file_path):
        self.file_path = file_path
        position = file_path.rfind('/') + 1
        self.file_name = file_path[position:]
        self.parent_directory = self.file_path[:position]
        eval_dir_pos = self.parent_directory[:-1].rfind('/') + 1
        self.evaluation_file_directory = self.parent_directory[:eval_dir_pos] + "eval/"
        self.document_parser = None

    # @property
    # def extract_features(self):
    #     """
    #     All approach of extracting features from raw data implemented here
    #     """
    #     custom_tokenizer = PunktSentenceTokenizer()
    #     regex_tokenizer = RegexpTokenizer(r'[a-zA-Z]+')
    #     ps = PorterStemmer()
    #     tokenized = []
    #
    #     with open(self.file_path, 'r') as current_document:
    #         for each_line in current_document:
    #             tokenized.extend(custom_tokenizer.tokenize(each_line))  # tokenizing words line by line
    #     feature_list = []
    #     try:
    #         for each_sentence in tokenized:
    #             # words = nltk.word_tokenize(each_sentence)
    #             words = regex_tokenizer.tokenize(each_sentence)
    #             tagged = nltk.pos_tag(words)
    #             feature_list.extend([ps.stem(pos[0].lower()) for pos in tagged if pos[1] == 'NN'])  # listing the nouns in a list
    #     except Exception as E:
    #         print(str(E))
    #     feature_dictionary = Counter(feature_list)  # converts an iterable object(in this case, LIST) to dictionary
    #     return feature_dictionary
    #
    #
    # def evaluate_term_frequency(self):
    #     """
    #     creates a new file with respect to each raw file in the dataset with 'term_name : term frequency'
    #     """
    #     evaluated_document_name = self.evaluation_file_directory + self.file_name + ".txt"
    #     feature_dictionary = self.extract_features
    #     with open(evaluated_document_name, 'w', encoding='utf-8') as document:
    #         for key in feature_dictionary:
    #             document.write(str(key) + ":" + str(feature_dictionary[key]) + "\n")

    # @property
    # def extract_features(self):
    #     """
    #     All approach of extracting features from raw data implemented here
    #     """
    #     self.document_parser = parse(self.file_path)
    #     feature_dictionary = Counter(self.document_parser.run())
    #     return feature_dictionary



    def evaluate_term_frequency(self):
        """
        creates a new file with respect to each raw file in the dataset with 'term_name : term frequency'
        """
        print(self.file_name)
        evaluated_document_name = self.evaluation_file_directory + self.file_name + ".txt"
        feature_dictionary = Counter(parse(self.file_path).run)

        with open(evaluated_document_name, 'w', encoding='utf-8') as document:
            for key in feature_dictionary:
                document.write(str(key) + ":" + str(feature_dictionary[key]) + "\n")