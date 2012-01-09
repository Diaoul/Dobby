# Copyright 2011 Antoine Bertin <diaoulael@gmail.com>
#
# This file is part of Dobby.
#
# Dobby is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dobby is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dobby.  If not, see <http://www.gnu.org/licenses/>.
from . import Base
from association import Association
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, UnicodeText


class Sentence(Base):
    """Sentence model that represents a sentence to be detected by a :class:`~dobby.recognizers.Recognizer`

    :param \*\*kwargs: can set all attributes

    .. attribute:: id

        Sentence id

    .. attribute:: text

        Text to be detected

    .. attribute:: associations

        Relationship to all related :class:`~dobby.models.association.Association` objects

    .. attribute:: actions

        Relationship to all related :class:`~dobby.models.actions.Action` objects in the right :attr:`~dobby.models.association.Association.order`

    """
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
