from sqlalchemy import create_engine, Column, Integer, Float, String, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('mysql+mysqlconnector://root:rootbadhon@localhost:3306/IEDR')
Base = declarative_base()


class Corpus(Base):
    __tablename__ = 'corpus'
    corpus_id = Column(Integer, primary_key=True)
    corpus_name = Column(String(100))
    document = relationship("Document")


class Document(Base):
    __tablename__ = 'document'
    document_id = Column(Integer, primary_key=True)
    corpus_id = Column(Integer, ForeignKey('corpus.corpus_id'),primary_key=True)
    document_name = Column(String(100))
    weightj = Column(Float(6))


class Term(Base):
    __tablename__ = 'term'
    term_id = Column(Integer, primary_key=True)
    term_name = Column(String(100))


class TermDocument(Base):
    __tablename__ = "term_document"
    term_id = Column(Integer, ForeignKey('term.term_id'), primary_key=True)
    document_id = Column(Integer, ForeignKey("document.document_id"), primary_key=True)
    term_frequency = Column(Integer)
    deviation = Column(Float(6))
    weightij = Column(Float(6))


class TermCorpus(Base):

    __tablename__ = "term_corpus"
    term_id = Column(Integer, ForeignKey('term.term_id'), primary_key=True)
    corpus_id = Column(Integer, ForeignKey('corpus.corpus_id'), primary_key=True)
    document_frequency = Column(Integer)
    weighti = Column(Float(6))
    si = Column(Float(6))
    dispi = Column(Float(6))
    domain_relevance = Column(Float(6))

def clean_up():
    """
    totally clear the database IEDR then create it again
    :return:None
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
