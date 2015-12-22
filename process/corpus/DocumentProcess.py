from collections import Counter
from process.parser.ParserProcess import Parse


class Document(object):
    """
    This class uses Parse class to extract candidate features from raw-document, calculates each candidate feature's
    term frequency and creates a corresponding document containing the numerical data (term:term-frequency)
    So to say simply, Use of Document class :
        raw-document ------> numeric-data containing document
    Object of this class have only been used in evaluate_corpus_documents() method of class Corpus
    of CorpusProcess.py of package process.corpus
    """

    def __init__(self, file_path):
        self.file_path = file_path
        position = file_path.rfind('/') + 1
        self.file_name = file_path[position:]
        self.parent_directory = self.file_path[:position]
        eval_dir_pos = self.parent_directory[:-1].rfind('/') + 1
        self.evaluation_file_directory = self.parent_directory[:eval_dir_pos] + "eval/"
        self.document_parser = None

    def evaluate_term_frequency(self):
        """
        creates a new file with respect to each raw file in the dataset with 'term_name : term frequency'
        """
        print(self.file_name)
        evaluated_document_name = self.evaluation_file_directory + self.file_name + ".txt"
        feature_dictionary = Counter(Parse(self.file_path).run)

        with open(evaluated_document_name, 'w', encoding='utf-8') as document:
            for key in feature_dictionary:
                document.write(str(key) + ":" + str(feature_dictionary[key]) + "\n")
