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
from .. import Base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, UnicodeText, String


class Action(Base):
    """Action base model that holds the text-to-speech

    :param \*\*kwargs: can set all attributes

    .. attribute:: id

        Action id

    .. attribute:: tts

        To-be-formatted or formatted text-to-speech

    .. attribute:: associations

        Link to a list of :class:`~dobby.models.association.Association` objects by following the
        database relationship

    """
    __tablename__ = 'actions'
    id = Column(Integer, primary_key=True)
    tts = Column(UnicodeText)
    
    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    associations = relationship('Association', back_populates='action')

    def format_tts(self):
        """Format the :attr:`tts` into a valid text-to-speech
        for :class:`~dobby.tts.TTS`

        """
        return self.tts

    def __repr__(self):
        return '<' + self.__class__.__name__ + '("%s")>' % self.tts
