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
    __tablename__ = 'actions'
    id = Column(Integer, primary_key=True)
    tts = Column(UnicodeText)
    discriminator = Column('type', String(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    associations = relationship('Association', back_populates='action')

    def __init__(self, tts):
        self.tts = tts

    @property
    def formated_tts(self):
        """Format the tts string with the available data"""
        return self.tts

    def __repr__(self):
        return '<' + self.__class__.__name__ + '("%s")>' % self.tts
