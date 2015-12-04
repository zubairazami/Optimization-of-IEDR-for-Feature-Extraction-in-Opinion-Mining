import os
from nltk.parse import stanford
import StanfordDependencies
from nltk.tokenize import sent_tokenize

os.environ['STANFORD_PARSER'] = 'stanford-parser-full-2015-04-20'
os.environ['STANFORD_MODELS'] = 'stanford-parser-full-2015-04-20'


class Parse:
    def __init__(self, file_path):
        self.file_path = file_path
        self.parser = stanford.StanfordParser(
            model_path=os.path.expanduser('~') + "/stanford-parser-full-2015-04-20/stanford-parser-3.5.2-models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

        self.sd = StanfordDependencies.get_instance(
            jar_filename=os.path.expanduser('~') + "/stanford-parser-full-2015-04-20/stanford-parser.jar")

        self.noun_list = ['NN', 'NNP', 'NNPS', 'NNS']
        self.adjective_list = ['JJ', 'JJR', 'JJS']
        self.verb_list = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

    def noun_compound_check(self, c_token, c_dic):
        if c_token.deprel == 'compound':
            c_dic['head'] = c_token.head
            c_dic['index'] = c_token.index
            if len(c_dic['form']) > 0:
                c_dic['form'] += ' ' + c_token.form
            else:
                c_dic['form'] = c_token.form
            return c_dic
        return None

    def nominal_subject_relationship(self, c_token, t_list, c_dic):
        if c_token.deprel == 'nsubj' and c_token.pos in self.noun_list and t_list[
                    c_token.head - 1].pos in self.adjective_list:
            if c_token.index == c_dic['head'] and c_token.index == c_dic['index'] + 1:
                return str(c_dic['form'] + " " + c_token.form)
            else:
                return str(c_token.form)
        return None

    def direct_object_relationship(self, c_token, t_list, c_dic):
        if c_token.deprel == 'dobj' and c_token.pos in self.noun_list and t_list[
                    c_token.head - 1].pos in self.verb_list:
            if c_token.index == c_dic['head'] and c_token.index == c_dic['index'] + 1:
                return str(c_dic['form'] + " " + c_token.form)
            else:
                return str(c_token.form)
        return None

    def prepositional_object_relationship(self, c_token, t_list):
        head_token = t_list[c_token.head - 1]
        if c_token.deprel == 'case' and head_token.pos in self.noun_list:
            return head_token.form
        return None

    def conj_nsubj_dobj_check(self, c_token, t_list, c_dic):
        head_token = t_list[c_token.head - 1]
        if c_token.deprel == 'conj':
            if head_token.deprel == 'nsubj' and self.nominal_subject_relationship(head_token, t_list,
                                                                                  c_dic) is not None:
                return c_token.form
            elif head_token.deprel == 'dobj' and self.direct_object_relationship(head_token, t_list, c_dic) is not None:
                return c_token.form
            elif head_token.deprel == 'compound' and t_list[head_token.head - 1].deprel in ['dobj', 'nsubj']:
                return c_token.form
            else:
                return None
        return None

    def adjectival_modifier(self, c_token, t_list):
        head_token = t_list[c_token.head - 1]
        if c_token.deprel == 'amod' and head_token.pos in self.noun_list:
            return head_token.form
        return None

    def open_clause_complement(self, c_token, t_list):
        head_token = t_list[c_token.head - 1]
        if c_token.deprel == 'xcomp' and head_token.deprel == 'root':
            new = [token for token in t_list if token.head == head_token.index][0]
            if new.pos in self.noun_list:
                return new.form
        return None

    @property
    def run(self):
        # start_time = time.time()

        file = open(self.file_path)
        text = file.read()
        file.close()

        sentences = sent_tokenize(text)
        sentences = [sentence for sentence in sentences if len(sentence) < 176]

        # print("Parsing started")
        parsed_sentences = self.parser.raw_parse_sents(sentences)
        # print("Parsing completed")
        candidate_feature = []

        for sentence in parsed_sentences:

            for line in sentence:

                try:
                    tokens = self.sd.convert_tree(str(line))
                except Exception as E:
                    # print("Exception found in : "+ self.file_path)
                    break

                compound_dict = dict(head=0, form='', index=0)
                sentence_feature = []

                for token in tokens:

                    ncc = self.noun_compound_check(token, compound_dict)
                    if ncc is not None:
                        compound_dict = ncc
                        continue

                    nsubj_result = self.nominal_subject_relationship(token, tokens, compound_dict)
                    if nsubj_result is not None:
                        sentence_feature.append(nsubj_result)
                        # print(nsubj_result)
                        continue

                    dobj_result = self.direct_object_relationship(token, tokens, compound_dict)
                    if dobj_result is not None:
                        sentence_feature.append(dobj_result)
                        # print(dobj_result)
                        continue

                    conj_result = self.conj_nsubj_dobj_check(token, tokens, compound_dict)
                    if conj_result is not None:
                        sentence_feature.append(conj_result)
                        # print(conj_result)
                        continue

                    prep_result = self.prepositional_object_relationship(token, tokens)
                    if prep_result is not None:
                        sentence_feature.append(prep_result)
                        # print(prep_result)
                        continue

                    amod_result = self.adjectival_modifier(token, tokens)
                    if amod_result is not None:
                        sentence_feature.append(amod_result)
                        # print(amod_result)
                        continue

                    xcomp_result = self.open_clause_complement(token, tokens)
                    if xcomp_result is not None:
                        sentence_feature.append(xcomp_result)
                        # print(xcomp_result)
                        continue

                sentence_feature = [cf.lower() for cf in sentence_feature]
                # print(sentence_feature)
                candidate_feature.extend(set(sentence_feature))
        # second = time.time() - start_time
        # print(int(second / 3600), "hour(s)", int((second % 3600) / 60), "minute(s)", round((second % 3600) % 60, 5),
        #       "second(s)")
        return candidate_feature

        # sentences = [
        #     "The camera of the cellphone is awesome",
        #     "I like the exterior very much",
        #
        #     "It has a very nice exterior design",
        #     "The face recognition of the cellphone is awesome",
        #
        #     "I liked the exterior but they are hating the interior.",
        #
        #     "The room-service, corridor and specially the security were excellent",
        #     "We appreciate the room-service and the security ",
        #
        #     "I was astonished by its speed",
        #     "I like the power of the engine, design of the interior, sharpness of the brake ",
        #     "Power of the engine, design of the interiorand sharpness of the brake are awesome"
        #     "I like the voice recognition on gps",
        #
        #     "awesome Spoiler",
        #     "nice interior design",
        #     "nice spoiler and speedy engine",
        #     "The camera looks good",
        # ]
