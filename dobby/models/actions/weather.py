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
from . import Action
from sqlalchemy.orm.mapper import reconstructor
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, String
import logging
import wunderground


API_KEY = '01b1334435fa449f'
logger = logging.getLogger(__name__)

class Weather(Action):
    __tablename__ = 'weather_actions'
    __mapper_args__ = {'polymorphic_identity': 'weather'}
    id = Column(Integer, ForeignKey('actions.id'), primary_key=True)
    query = Column(String(30))

    #TODO: Put it also in __init__? For when not retreiving from database.
    @reconstructor
    def onload(self):
        self.data = {}

    @property
    def formated_tts(self):
        """Format the tts string with the available data"""
        if not self.data:
            self.data = wunderground.request(API_KEY, ['conditions', 'forecast'], self.query)
            logger.debug(u'Retreived data: %r' % self.data)
        return self.tts.format(**self.data)
