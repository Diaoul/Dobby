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
from sqlalchemy.types import Integer, String, Unicode
import logging
import pywunderground


API_KEY = '01b1334435fa449f'
logger = logging.getLogger(__name__)


class Weather(Action):
    """Weather Action retrieves the weather from `wunderground <http://www.wunderground.com/>`_

    .. attribute:: query

        Last part of the `l` parameter in an Autocomplete API response
        For example if the `l` parameter is `/q/zmw:94125.1.99999`,
        the value should be `zmw:94125.1.99999`

        Refer to the `documentation of wunderground API <http://www.wunderground.com/weather/api/d/documentation.html>`_
        in the Autocomplete API section for more details

    :meth:`~dobby.models.actions.Action.format_tts` uses :func:`string.format` to format :attr:`~dobby.models.actions.Action.tts`
    Data used is a dict fetched with :func:`wunderground.request` using :data:`wunderground.FEATURES`
    *conditions* and *forecast*

    To save ressources, the retrieved data is stored in the instance attribute data

    """
    __tablename__ = 'weather_actions'
    __mapper_args__ = {'polymorphic_identity': 'weather'}
    id = Column(Integer, ForeignKey('actions.id'), primary_key=True)
    city_name = Column(Unicode(50))
    query = Column(String(30))

    def __init__(self, **kwargs):
        super(Weather, self).__init__(**kwargs)
        self.data = {}

    @reconstructor
    def onload(self):
        self.data = {}

    def format_tts(self):
        if not self.data:
            logger.debug(u'Fetching data from wunderground...')
            self.data = pywunderground.request(API_KEY, ['conditions', 'forecast'], self.query)
        return self.tts.format(**self.data)
