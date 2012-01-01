from . import Base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

class Association(Base):
    __tablename__ = 'associations'
    sentence_id = Column(Integer, ForeignKey('sentences.id'), primary_key=True)
    action_id = Column(Integer, ForeignKey('actions.id'), primary_key=True)
    order = Column(Integer)

    sentence = relationship('Sentence', back_populates='associations')
    action = relationship('Action', back_populates='associations')

    def __init__(self, action=None, sentence=None, order=None):
        self.sentence = sentence
        self.action = action
        self.order = order

    def __repr__(self):
        return '<Association("%d")>' % (self.order or 0)