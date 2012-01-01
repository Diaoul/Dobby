# Copyright 2011 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of Dobby.

# Dobby is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Dobby is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Dobby.  If not, see <http://www.gnu.org/licenses/>.
__all__ = ['engine', 'Sentence', 'Association', 'Action', 'initDb', 'Base']


from sqlalchemy.engine import create_engine
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, UnicodeText, String

engine = create_engine('sqlite:///dobby.db', echo=True)
Base = declarative_base()

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


class Action(Base):
    __tablename__ = 'actions'
    id = Column(Integer, primary_key=True)
    tts = Column(UnicodeText)

    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    associations = relationship('Association', back_populates='action')

    def __init__(self, tts):
        self.tts = tts
        self.data = {}

    def format_tts(self):
        """Format the tts string with the available data"""
        return self.tts.format(self.data)

    def __repr__(self):
        return '<' + self.__class__.__name__ + '("%s")>' % self.tts
