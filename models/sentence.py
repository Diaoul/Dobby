from . import Base
from association import Association
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, UnicodeText


class Sentence(Base):
    __tablename__ = 'sentences'
    id = Column(Integer, primary_key=True)
    text = Column(UnicodeText)

    associations = relationship('Association', back_populates='sentence', order_by='Association.order',
                                collection_class=attribute_mapped_collection('order'))
    actions = association_proxy('associations', 'action', creator=lambda k, v: Association(order=k, action=v))

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return '<Sentence("%s")>' % self.text