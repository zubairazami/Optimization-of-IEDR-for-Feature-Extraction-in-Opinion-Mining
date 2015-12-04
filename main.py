from process.corpus.CorpusProcess import Corpus
from process.db.structure import clean_up
import time

def process(string, name):
    my_corpus = Corpus(path=string, name=name)
    print(name + " : ")
    # much time
    my_corpus.evaluate_corpus_documents()
    print("Corpus document evaluated")

    my_corpus.upload_documents()
    print("Document List Uploaded.")

    # much time
    my_corpus.upload_term_frequency()
    print("Term Frequency uploaded.")

    my_corpus.upload_document_frequency()
    print("Document Frequency uploaded.")

    # moderate time
    my_corpus.evaluate_terms_weight()
    print("Wij uploaded")

    my_corpus.evaluate_wi()
    print("Wi")

    my_corpus.evaluate_si()
    print("Si")

    my_corpus.evaluate_dispi()
    print("DISPERSIONi")

    my_corpus.evaluate_wj()
    print("Wj")

    # moderate time
    my_corpus.evaluate_devij()
    print("DEVIATIONij")

    my_corpus.evaluate_domain_relevance()
    print("DRi")

# start_time = time.time()
# be scared, be very very scared of the following method clean_up()
# clean_up()
# process("/home/badhon/Desktop/dataset/cars/",name='cars')
# process("/home/badhon/Desktop/dataset/hotels/",name = 'hotels')
# second = time.time() - start_time
# print(int(second/3600), "hour(s)", int((second%3600)/60), "minute(s)", round((second%3600)%60, 5), "second(s)")