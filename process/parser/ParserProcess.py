from nltk.parse import stanford
from nltk.tokenize import sent_tokenize
import os
import StanfordDependencies
import unicodedata

os.environ['STANFORD_PARSER'] = os.path.expanduser('~') + '/stanford-parser-full-2015-04-20'
os.environ['STANFORD_MODELS'] = os.path.expanduser('~') + '/stanford-parser-full-2015-04-20'


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


class Parse:
    def __init__(self, file_path):

        self.file_path = file_path
        path_string = "/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
        self.parser = stanford.StanfordParser(model_path=os.path.expanduser('~') + path_string)

        self.sd = StanfordDependencies.get_instance(
            jar_filename=os.path.expanduser('~') + "/stanford-parser-full-2015-04-20/stanford-parser.jar"
        )

        self.noun_list = ['NN', 'NNP', 'NNPS', 'NNS']
        self.adjective_list = ['JJ', 'JJR', 'JJS']
        self.verb_list = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

    def nominal_subject_relationship(self, c_token, t_list):
        if c_token.deprel == 'nsubj' \
                and c_token.pos in self.noun_list \
                and t_list[c_token.head - 1].pos in self.adjective_list:
            return str(c_token.form)
        return None

    def direct_object_relationship(self, c_token, t_list):
        if c_token.deprel == 'dobj' \
                and c_token.pos in self.noun_list \
                and t_list[c_token.head - 1].pos in self.verb_list:
            return str(c_token.form)
        return None

    def prepositional_object_relationship(self, c_token, t_list):
        head_token = t_list[c_token.head - 1]
        if c_token.deprel == 'case' and head_token.pos in self.noun_list:
            return head_token.form
        return None

    def conj_nsubj_dobj_check(self, c_token, t_list):
        head_token = t_list[c_token.head - 1]
        if c_token.deprel == 'conj':
            if head_token.deprel == 'nsubj' \
                    and self.nominal_subject_relationship(head_token, t_list) is not None:
                return c_token.form
            elif head_token.deprel == 'dobj' \
                    and self.direct_object_relationship(head_token, t_list) is not None:
                return c_token.form
            else:
                return None
        return None

    def adjectival_modifier(self, c_token, t_list):
        head_token = t_list[c_token.head - 1]
        if c_token.deprel == 'amod' \
                and head_token.pos in self.noun_list:
            return head_token.form
        return None

    def open_clause_complement(self, c_token, t_list):
        head_token = t_list[c_token.head - 1]
        if c_token.deprel == 'xcomp' \
                and head_token.deprel == 'root':
            new = [token for token in t_list if token.head == head_token.index][0]
            if new.pos in self.noun_list:
                return new.form
        return None

    @property
    def run(self):
        file = open(self.file_path)
        text = file.read()
        file.close()

        sentences = sent_tokenize(text)
        sentences = [sentence for sentence in sentences if len(sentence) < 176]
        parsed_sentences = self.parser.raw_parse_sents(sentences)
        candidate_feature = []

        for sentence in parsed_sentences:
            for line in sentence:
                try:
                    tokens = self.sd.convert_tree(str(line))
                except Exception as exception:
                    print("Exception found", exception)
                    break

                sentence_feature = []

                for token in tokens:
                    nsubj_result = self.nominal_subject_relationship(token, tokens)
                    if nsubj_result is not None:
                        sentence_feature.append(nsubj_result)
                        continue

                    dobj_result = self.direct_object_relationship(token, tokens)
                    if dobj_result is not None:
                        sentence_feature.append(dobj_result)
                        continue

                    conj_result = self.conj_nsubj_dobj_check(token, tokens)
                    if conj_result is not None:
                        sentence_feature.append(conj_result)
                        continue

                    prep_result = self.prepositional_object_relationship(token, tokens)
                    if prep_result is not None:
                        sentence_feature.append(prep_result)
                        continue

                    amod_result = self.adjectival_modifier(token, tokens)
                    if amod_result is not None:
                        sentence_feature.append(amod_result)
                        continue

                    xcomp_result = self.open_clause_complement(token, tokens)
                    if xcomp_result is not None:
                        sentence_feature.append(xcomp_result)
                        continue

                sentence_feature = [strip_accents(cf).lower() for cf in sentence_feature]
                candidate_feature.extend(set(sentence_feature))

        return candidate_feature
